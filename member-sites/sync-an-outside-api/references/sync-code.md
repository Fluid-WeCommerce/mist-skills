# Reference: sync code

Generic code for the pattern in the skill: Linear issues into an `issues` table, through one area function (`work`) and a schedule (`work-tick`). The functions use the global types `fluid sites functions new` writes into `functions/fluid-env.d.ts` (`FluidContext`, `FluidFunction`, `FluidResult`), and typecheck against them with `strict` on. Rename `work`, `issues` and `linear` to fit the site.

## db/schema.json (the two tables)

```json
{
  "version": 1,
  "tables": {
    "issues": {
      "columns": {
        "source": { "type": "text", "required": true },
        "source_id": { "type": "text", "required": true },
        "synced_at": { "type": "timestamp" },
        "identifier": { "type": "text", "required": true },
        "title": { "type": "text", "required": true },
        "status": { "type": "text" },
        "assignee_name": { "type": "text" },
        "url": { "type": "text" }
      },
      "rules": { "read": "signed_in", "insert": "nobody", "update": "nobody", "delete": "nobody" },
      "unique": [["source", "source_id"]]
    },
    "sync_runs": {
      "columns": {
        "source": { "type": "text", "required": true },
        "scope": { "type": "text", "required": true },
        "state": { "type": "text", "required": true, "default": "ok" },
        "last_attempt_at": { "type": "timestamp" },
        "last_manual_at": { "type": "timestamp" },
        "last_good_at": { "type": "timestamp" },
        "items": { "type": "integer" },
        "cursor": { "type": "text" },
        "error": { "type": "text" }
      },
      "rules": { "read": "signed_in", "insert": "nobody", "update": "nobody", "delete": "nobody" },
      "unique": [["source", "scope"]]
    }
  }
}
```

## config/functions.json

```json
{
  "version": 1,
  "functions": {
    "work": { "access": "signed_in" },
    "work-tick": { "access": "key", "schedule": "*/15 * * * *" }
  }
}
```

## functions/lib/sync.ts: claim, finish and reconcile

```ts
/// <reference path="../fluid-env.d.ts" />
// functions/lib/sync.ts: shared by every sync. Not a function: functions/lib/ is plain code.

type Row = Record<string, unknown>;

/** How long Sync now waits after the last Sync now. The schedule never waits. */
export const MIN_GAP_MS = 60_000;

/** A database answer's data, or throw its error. */
export function must<T>(answer: FluidResult<T>): T {
  if (answer.error) throw new Error(`${answer.error.code}: ${answer.error.message}`);
  return answer.data as T;
}

export type Claim = { ok: true; cursor: string | null } | { ok: false; retryAt: string };

/**
 * Start a run of `source`. A person's run (manual) is refused within
 * MIN_GAP_MS of the last person's run. The schedule passes manual: false: it
 * is never refused and never moves last_manual_at, so a tick can't take the
 * Sync now slot.
 */
export async function beginSync(ctx: FluidContext, source: string, manual: boolean): Promise<Claim> {
  const db = ctx.fluid.db;
  const run = must(
    await db.from("sync_runs").select("id,last_manual_at,cursor").eq("source", source).eq("scope", "global").maybeSingle(),
  );
  // Date.now() here, inside the call: at module scope a Worker's clock reads 0.
  const now = Date.now();
  const last = run?.last_manual_at ? Date.parse(String(run.last_manual_at)) : NaN;
  if (manual && now - last < MIN_GAP_MS) {
    return { ok: false, retryAt: new Date(last + MIN_GAP_MS).toISOString() };
  }
  const at = new Date(now).toISOString();
  const patch: Row = { state: "running", last_attempt_at: at, error: null };
  if (manual) patch.last_manual_at = at;
  if (run) {
    must(await db.from("sync_runs").update(patch).eq("id", String(run.id)));
    return { ok: true, cursor: (run.cursor as string | null) ?? null };
  }
  const inserted = await db.from("sync_runs").insert({ source, scope: "global", ...patch });
  // Two first runs raced on the unique (source, scope): the loser backs off.
  if (inserted.error?.code === "unique_violation") {
    return { ok: false, retryAt: new Date(now + MIN_GAP_MS).toISOString() };
  }
  must(inserted);
  return { ok: true, cursor: null };
}

export type Finish = { ok: true; items: number; cursor: string | null } | { ok: false; error: string };

/** Record how a run ended. Only a good run moves last_good_at, so a failure keeps "last good data at …". */
export async function finishSync(ctx: FluidContext, source: string, finish: Finish): Promise<void> {
  const patch: Row = finish.ok
    ? { state: "ok", last_good_at: new Date().toISOString(), items: finish.items, cursor: finish.cursor, error: null }
    : { state: "failed", error: finish.error.slice(0, 500) };
  must(await ctx.fluid.db.from("sync_runs").update(patch).eq("source", source).eq("scope", "global"));
}

/**
 * fluid.db has no upsert. Make `table`'s rows from `source` match `rows`
 * (each with a source_id): one select, one insert for the new rows, and one
 * update per distinct change. Only `compare` columns are written, so a column
 * people set (a note, a pin, a visibility) survives every sync. Returns how
 * many rows changed. Requests: 2 + the number of distinct changes, at most
 * 2 + rows.length.
 */
export async function reconcile(
  ctx: FluidContext,
  table: string,
  source: string,
  rows: Row[],
  compare: string[],
): Promise<number> {
  if (rows.length === 0) return 0;
  const db = ctx.fluid.db;
  const existing = must(
    await db
      .from(table)
      .select(["id", "source_id", ...compare].join(","))
      .eq("source", source)
      .in("source_id", rows.map((r) => String(r.source_id))),
  );
  const bySourceId = new Map(existing.map((r) => [String(r.source_id), r]));
  const syncedAt = new Date().toISOString();
  const fresh: Row[] = [];
  const groups = new Map<string, { patch: Row; ids: string[] }>();
  for (const row of rows) {
    const current = bySourceId.get(String(row.source_id));
    if (!current) {
      fresh.push({ ...row, source, synced_at: syncedAt });
      continue;
    }
    const patch: Row = {};
    for (const column of compare) {
      if ((current[column] ?? null) !== (row[column] ?? null)) patch[column] = row[column] ?? null;
    }
    if (Object.keys(patch).length === 0) continue;
    // Rows that changed the same way (a status flip) share one update.
    const key = JSON.stringify(patch);
    const group = groups.get(key) ?? { patch: { ...patch, synced_at: syncedAt }, ids: [] };
    group.ids.push(String(current.id));
    groups.set(key, group);
  }
  if (fresh.length > 0) must(await db.from(table).insert(fresh));
  for (const { patch, ids } of groups.values()) must(await db.from(table).update(patch).in("id", ids));
  return fresh.length + [...groups.values()].reduce((n, g) => n + g.ids.length, 0);
}
```

## functions/lib/linear.ts: a GraphQL source, one page per call

```ts
/// <reference path="../fluid-env.d.ts" />
// functions/lib/linear.ts: Linear issues, one page per call.
import { MOCK_ISSUES } from "./fixtures/linear-issues";

export interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  url: string;
  state: { name: string } | null;
  assignee: { name: string } | null;
}

/**
 * Issues per call. A run makes 1 fetch + at most PAGE_SIZE + 2 database
 * calls for the rows + 3 for sync_runs: 31 of the 50 a call may make.
 */
export const PAGE_SIZE = 25;

/** One page of issues after `cursor`, and the cursor for the next run (null when this was the last page). */
export async function issuePage(
  ctx: FluidContext,
  cursor: string | null,
): Promise<{ issues: LinearIssue[]; next: string | null }> {
  // Mock unless LINEAR_SOURCE says live: the page and the sync work with no token.
  if (ctx.secrets.LINEAR_SOURCE !== "live") return { issues: MOCK_ISSUES.data.issues.nodes, next: null };
  const key = ctx.secrets.LINEAR_API_KEY;
  if (!key) throw new Error("LINEAR_SOURCE is live but LINEAR_API_KEY isn't set");
  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    // A Linear personal API key goes in as is, with no "Bearer".
    headers: { authorization: key, "content-type": "application/json" },
    body: JSON.stringify({
      query: `query($first: Int!, $after: String) {
        issues(first: $first, after: $after) {
          pageInfo { hasNextPage endCursor }
          nodes { id identifier title url state { name } assignee { name } }
        }
      }`,
      variables: { first: PAGE_SIZE, after: cursor },
    }),
  });
  const answer = (await response.json().catch(() => null)) as {
    data?: { issues: { pageInfo: { hasNextPage: boolean; endCursor: string | null }; nodes: LinearIssue[] } };
    errors?: { message: string }[];
  } | null;
  if (!response.ok || !answer?.data) {
    throw new Error(`Linear: ${answer?.errors?.map((e) => e.message).join("; ") ?? `HTTP ${response.status}`}`);
  }
  const { pageInfo, nodes } = answer.data.issues;
  return { issues: nodes, next: pageInfo.hasNextPage ? pageInfo.endCursor : null };
}
```

## functions/lib/fixtures/linear-issues.ts: mock data in the API's shape

```ts
// functions/lib/fixtures/linear-issues.ts: Linear's own response shape, so live and mock share one code path.
export const MOCK_ISSUES = {
  data: {
    issues: {
      pageInfo: { hasNextPage: false, endCursor: null },
      nodes: [
        {
          id: "mock-issue-1",
          identifier: "ENG-1",
          title: "Sample: import the product catalog",
          url: "https://linear.app/example/issue/ENG-1",
          state: { name: "In Progress" },
          assignee: { name: "Sample Person" },
        },
        {
          id: "mock-issue-2",
          identifier: "ENG-2",
          title: "Sample: connect the payment provider",
          url: "https://linear.app/example/issue/ENG-2",
          state: { name: "Todo" },
          assignee: null,
        },
      ],
    },
  },
};
```

## functions/lib/work-sync.ts: the one sync both callers run

```ts
/// <reference path="../fluid-env.d.ts" />
// functions/lib/work-sync.ts: the one sync both Sync now and the schedule run.
import { issuePage } from "./linear";
import { beginSync, finishSync, reconcile } from "./sync";

export async function syncIssues(ctx: FluidContext, opts: { manual: boolean }): Promise<Response> {
  const claim = await beginSync(ctx, "linear", opts.manual);
  if (!claim.ok) return Response.json({ error: "too_soon", retry_at: claim.retryAt }, { status: 429 });
  try {
    const page = await issuePage(ctx, claim.cursor);
    const rows = page.issues.map((issue) => ({
      source_id: issue.id,
      identifier: issue.identifier,
      title: issue.title,
      status: issue.state?.name ?? null,
      assignee_name: issue.assignee?.name ?? null,
      url: issue.url,
    }));
    const changed = await reconcile(ctx, "issues", "linear", rows, ["title", "status", "assignee_name", "url"]);
    // The next run carries on from page.next; null starts the next pass from the top.
    await finishSync(ctx, "linear", { ok: true, items: changed, cursor: page.next });
    return Response.json({ changed, more: page.next !== null });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    // The rows are untouched, so the page keeps showing the last good data.
    await finishSync(ctx, "linear", { ok: false, error: message }).catch(() => undefined);
    return Response.json({ error: "sync_failed", message }, { status: 502 });
  }
}
```

## functions/work.ts: the area function (Sync now)

```ts
/// <reference path="./fluid-env.d.ts" />
// functions/work.ts: the "work" area's one function, routed by sub-path:
//   POST /api/work/sync   Sync now   → 200 {changed, more} | 429 {retry_at} | 502 {message}
// Add the area's other actions as more cases, not more functions (a site has at most 20).
import { syncIssues } from "./lib/work-sync";

/** The part of the path after /api/<fn>/: "sync" for /api/work/sync. */
function subPath(request: Request, fn: string): string {
  const path = new URL(request.url).pathname;
  return path.slice(path.indexOf(`/api/${fn}`) + `/api/${fn}`.length).replace(/^\/+|\/+$/g, "");
}

export default (async (request, ctx) => {
  if (request.method !== "POST") return Response.json({ error: "method_not_allowed" }, { status: 405 });
  // The function writes as the site, so no table rule protects these rows: check the caller here.
  const viewer = ctx.caller.kind === "page" ? ctx.caller.viewer : null;
  if (!viewer || viewer.relation === "other_company") {
    return Response.json({ error: "sign_in_required" }, { status: 401 });
  }
  switch (subPath(request, ctx.fn)) {
    case "sync":
      return syncIssues(ctx, { manual: true });
    default:
      return Response.json({ error: "not_found" }, { status: 404 });
  }
}) satisfies FluidFunction;
```

## functions/work-tick.ts: the schedule

```ts
/// <reference path="./fluid-env.d.ts" />
// functions/work-tick.ts: the schedule. access "key" keeps pages and the public
// out, but any of the site's API keys could still call it, so refuse everyone
// but the scheduler.
import { syncIssues } from "./lib/work-sync";

export default (async (_request, ctx) => {
  if (ctx.caller.kind !== "schedule") return Response.json({ error: "schedule_only" }, { status: 403 });
  // The answer's status is what the live log shows (it carries no console.log), so a failed run reads as a 502.
  return syncIssues(ctx, { manual: false });
}) satisfies FluidFunction;
```

## A second source: GitHub releases (REST)

The same shape fits a REST API. One request a run returns the 20 newest releases. Map each to a row with `source_id: String(release.id)`, then `reconcile(ctx, "releases", "github", rows, ["name", "url"])`. Use a second `sync_runs` row with `source: "github"`. A slow source can run less often than the tick: skip it while its `last_good_at` is under an hour old.

```ts
/// <reference path="../fluid-env.d.ts" />
// functions/lib/github.ts: a REST source. One request per run.

export interface Release {
  id: number;
  tag_name: string;
  name: string | null;
  html_url: string;
  published_at: string | null;
}

export async function latestReleases(ctx: FluidContext): Promise<Release[]> {
  if (ctx.secrets.GITHUB_SOURCE !== "live") {
    return [{ id: 1, tag_name: "v1.0.0", name: "Sample release", html_url: "https://github.com/your-org/your-repo/releases/tag/v1.0.0", published_at: "2026-01-15T00:00:00Z" }];
  }
  const token = ctx.secrets.GITHUB_TOKEN;
  const repo = ctx.secrets.GITHUB_REPO; // "owner/name", a plain env var
  if (!token || !repo) throw new Error("GITHUB_SOURCE is live but GITHUB_TOKEN or GITHUB_REPO isn't set");
  const response = await fetch(`https://api.github.com/repos/${repo}/releases?per_page=20`, {
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${token}`,
      "user-agent": "fluid-site", // GitHub refuses a request without one
      "x-github-api-version": "2022-11-28",
    },
  });
  if (!response.ok) throw new Error(`GitHub answered ${response.status}`);
  return (await response.json()) as Release[];
}
```

## The page

```ts
// src/sync.ts: the page side. fluid.db reads the rows; Sync now calls the function.
import { fluid } from "@fluid-app/sites";

const SCHEDULE_MS = 15 * 60_000;

export interface SyncRun {
  state: "ok" | "running" | "failed";
  last_good_at: string | null;
  last_attempt_at: string | null;
  error: string | null;
}

/** The source's latest run, or null before the first one. */
export async function readSyncRun(source: string): Promise<SyncRun | null> {
  const { data, error } = await fluid.db
    .from("sync_runs")
    .select("state,last_good_at,last_attempt_at,error")
    .eq("source", source)
    .eq("scope", "global")
    .limit(1);
  if (error) throw new Error(error.message);
  return (data?.[0] as SyncRun | undefined) ?? null;
}

/** What the pill says: failed, stale (three missed ticks) or fine. */
export function syncLabel(run: SyncRun | null, now = Date.now()): "never" | "failed" | "stale" | "ok" {
  if (!run?.last_good_at) return run?.state === "failed" ? "failed" : "never";
  if (run.state === "failed") return "failed";
  return now - Date.parse(run.last_good_at) > 3 * SCHEDULE_MS ? "stale" : "ok";
}

/** Sync now. Re-read the rows after any answer; a 429 means someone synced a moment ago. */
export async function syncNow(): Promise<string | null> {
  const response = await fluid.fn.fetch("work/sync", { method: "POST" });
  const body = (await response.json().catch(() => ({}))) as { retry_at?: string; message?: string };
  if (response.status === 429 && body.retry_at) {
    return `Synced a moment ago. Try again at ${new Date(body.retry_at).toLocaleTimeString()}.`;
  }
  if (!response.ok) return body.message ?? "The sync didn't work. The page still shows the last good data.";
  return null;
}
```

## Local checks

```sh
# .fluid/secrets.env (never committed). Leave LINEAR_SOURCE unset for mock mode.
LINEAR_SOURCE=live
LINEAR_API_KEY=<a read-only key>

# Fire the schedule once, as the scheduler would:
curl -X POST http://127.0.0.1:<port>/_fluid/fn/_dev/fire/work-tick
```

## Request budget per call

| Step | Requests |
| --- | --- |
| `beginSync`: select, then update or insert | 2 |
| One API page | 1 |
| `reconcile`: select, insert, one update per distinct change | 2 to 2 + `PAGE_SIZE` |
| `finishSync` | 1 |
| **Total with `PAGE_SIZE` 25** | **at most 31 of 50** |

If a source needs more per row (a detail request for each record), shrink `PAGE_SIZE` until the worst case stays under 50.
