# Reference: sync code

Generic code for the pattern in the skill. It syncs Linear issues into an `issues` table through one area function (`work`) and a schedule (`work-tick`).
- The functions use the global types `fluid sites functions new` writes into `functions/fluid-env.d.ts` (`FluidContext`, `FluidFunction`, `FluidResult`), and typecheck against them with `strict` on.
- The page code typechecks against `@fluid-app/sites`.
- The Linear query was checked against Linear's published GraphQL schema (`packages/sdk/src/schema.graphql`). The claim, lease and watermark logic is typechecked, not yet run on a live site.
- Rename `work`, `issues` and `linear` to fit the site.

## db/schema.json (the two tables)

`watermark` and `pass_max` hold ISO times from the API as text, so they compare as strings exactly as the API wrote them.

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
        "run_no": { "type": "integer", "required": true, "default": 0 },
        "state": { "type": "text", "required": true, "default": "ok" },
        "last_attempt_at": { "type": "timestamp" },
        "lease_until": { "type": "timestamp" },
        "last_manual_at": { "type": "timestamp" },
        "last_good_at": { "type": "timestamp" },
        "items": { "type": "integer" },
        "cursor": { "type": "text" },
        "watermark": { "type": "text" },
        "pass_max": { "type": "text" },
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

/** How long Sync now waits after the last Sync now. The schedule never waits for it. */
export const MIN_GAP_MS = 60_000;
/** A call lasts at most 30 s, so a run still holding its lease after this was stopped and never finished. */
export const LEASE_MS = 60_000;

/** A database answer's data, or throw its error. */
export function must<T>(answer: FluidResult<T>): T {
  if (answer.error) throw new Error(`${answer.error.code}: ${answer.error.message}`);
  return answer.data as T;
}

const iso = (ms: number) => new Date(ms).toISOString();
const time = (at: unknown) => (at ? Date.parse(String(at)) : NaN);
const text = (value: unknown) => (typeof value === "string" ? value : null);

/** Where the source's paging stands between runs. */
export interface SyncPosition {
  /** The API's page cursor inside the current pass; null at the start of a pass. */
  cursor: string | null;
  /** Records updated after this were not synced yet; null before the first full pass. */
  watermark: string | null;
  /** The newest update seen so far in the current pass: the next watermark. */
  passMax: string | null;
}

/** Before the first run: a full pass from the top. */
export const START: SyncPosition = { cursor: null, watermark: null, passMax: null };

/**
 * The position after one page. A pass pages with the cursor under a fixed
 * watermark; when its last page is read, the newest update it saw becomes
 * the watermark. So after the first full pass a run reads only what changed.
 *
 * nextCursor - The API's cursor for the next page, or null after the last page.
 * newest     - The newest update time on this page, or null for an empty page.
 */
export function advance(at: SyncPosition, nextCursor: string | null, newest: string | null): SyncPosition {
  // ISO times from one API compare as strings.
  const passMax = at.passMax && (!newest || at.passMax > newest) ? at.passMax : newest;
  return nextCursor
    ? { cursor: nextCursor, watermark: at.watermark, passMax }
    : { cursor: null, watermark: passMax ?? at.watermark, passMax: null };
}

export type Claim = ({ ok: true } & SyncPosition) | { ok: false; retryAt: string };

/**
 * Claim a run of `source`. Refused while another run holds the lease, and a
 * person's run (manual) within MIN_GAP_MS of the last person's run. The
 * schedule passes manual: false and never writes last_manual_at, so a tick
 * can't take the Sync now slot.
 */
export async function beginSync(ctx: FluidContext, source: string, manual: boolean): Promise<Claim> {
  const db = ctx.fluid.db;
  const run = must(
    await db
      .from("sync_runs")
      .select("id,run_no,state,lease_until,last_manual_at,cursor,watermark,pass_max")
      .eq("source", source)
      .eq("scope", "global")
      .maybeSingle(),
  );
  // Date.now() here, inside the call: at module scope a Worker's clock reads 0.
  const now = Date.now();
  const lastManual = time(run?.last_manual_at);
  if (manual && now - lastManual < MIN_GAP_MS) return { ok: false, retryAt: iso(lastManual + MIN_GAP_MS) };
  const leaseUntil = time(run?.lease_until);
  if (run?.state === "running" && now < leaseUntil) return { ok: false, retryAt: iso(leaseUntil) };
  const busy = { ok: false, retryAt: iso(now + LEASE_MS) } as const;

  // run_no counts claims. The update below matches only while it still holds the number read above.
  const runNo = Number(run?.run_no ?? 0);
  const patch: Row = {
    run_no: runNo + 1,
    state: "running",
    last_attempt_at: iso(now),
    lease_until: iso(now + LEASE_MS),
    error: null,
  };
  if (manual) patch.last_manual_at = patch.last_attempt_at;
  if (run) {
    // Compare and set on an integer, so another run that claimed the row since the read makes this match nothing.
    const claimed = must(
      await db.from("sync_runs").update(patch).eq("id", String(run.id)).eq("run_no", runNo).select("id"),
    );
    if (claimed.length === 0) return busy;
  } else {
    const inserted = await db.from("sync_runs").insert({ source, scope: "global", ...patch });
    // Two first runs raced on the unique (source, scope): the loser backs off.
    if (inserted.error?.code === "unique_violation") return busy;
    must(inserted);
  }
  return { ok: true, cursor: text(run?.cursor), watermark: text(run?.watermark), passMax: text(run?.pass_max) };
}

export type Finish = ({ ok: true; items: number } & SyncPosition) | { ok: false; error: string };

/**
 * Record how a run ended and release the lease. Only a good run moves
 * last_good_at, so a failure keeps "last good data at …". A failure also
 * drops the page cursor: a cursor the API no longer accepts would otherwise
 * fail every later run. The next run starts the pass again from the
 * watermark, which is safe because reconcile is idempotent. The cost: a
 * transient error during a long first fill starts that fill over.
 */
export async function finishSync(ctx: FluidContext, source: string, finish: Finish): Promise<void> {
  const patch: Row = finish.ok
    ? {
        state: "ok",
        last_good_at: iso(Date.now()),
        items: finish.items,
        cursor: finish.cursor,
        watermark: finish.watermark,
        pass_max: finish.passMax,
        error: null,
      }
    : { state: "failed", error: finish.error.slice(0, 500), cursor: null, pass_max: null };
  must(await ctx.fluid.db.from("sync_runs").update({ ...patch, lease_until: null }).eq("source", source).eq("scope", "global"));
}

/** Equal as stored: a json column comes back as a new object, so compare its JSON. */
function same(a: unknown, b: unknown): boolean {
  return a === b || (typeof a === "object" && a !== null && JSON.stringify(a) === JSON.stringify(b));
}

/**
 * fluid.db has no upsert. Make `table`'s rows from `source` match `rows`
 * (each with a source_id), and delete the `removed` source ids: one select,
 * then in parallel one insert for the new rows, one update per distinct
 * change and one delete. Only `compare` columns are written, so a column
 * people set (a note, a pin, a visibility) survives every sync. Returns how
 * many rows changed. Requests: at most 3 + rows.length.
 */
export async function reconcile(
  ctx: FluidContext,
  table: string,
  source: string,
  rows: Row[],
  compare: string[],
  removed: string[] = [],
): Promise<number> {
  const db = ctx.fluid.db;
  const existing =
    rows.length === 0
      ? []
      : must(
          await db
            .from(table)
            .select(["id", "source_id", ...compare].join(","))
            .eq("source", source)
            .in("source_id", rows.map((r) => String(r.source_id))),
        );
  const bySourceId = new Map(existing.map((r) => [String(r.source_id), r]));
  const syncedAt = iso(Date.now());
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
      if (!same(current[column] ?? null, row[column] ?? null)) patch[column] = row[column] ?? null;
    }
    if (Object.keys(patch).length === 0) continue;
    // Rows that changed the same way (a status flip) share one update.
    const key = JSON.stringify(patch);
    const group = groups.get(key) ?? { patch: { ...patch, synced_at: syncedAt }, ids: [] };
    group.ids.push(String(current.id));
    groups.set(key, group);
  }
  // The writes touch different rows, so they run together.
  await Promise.all([
    fresh.length > 0 && db.from(table).insert(fresh).then(must),
    ...[...groups.values()].map(({ patch, ids }) => db.from(table).update(patch).in("id", ids).then(must)),
    removed.length > 0 && db.from(table).delete().eq("source", source).in("source_id", removed).then(must),
  ]);
  return fresh.length + removed.length + [...groups.values()].reduce((n, g) => n + g.ids.length, 0);
}
```

## functions/lib/linear.ts: a GraphQL source, incremental, one page per call

```ts
/// <reference path="../fluid-env.d.ts" />
// functions/lib/linear.ts: Linear issues, incrementally, one page per call.
// Only the query and its answer live here; lib/sync.ts owns the paging rules.
import { MOCK_ISSUES } from "./fixtures/linear-issues";
import { advance, START, type SyncPosition } from "./sync";

export interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  url: string;
  updatedAt: string;
  /** Set when the issue was archived or deleted: its row goes. */
  archivedAt: string | null;
  state: { name: string } | null;
  assignee: { name: string } | null;
}

/**
 * Issues per call. A run makes 1 fetch and at most PAGE_SIZE + 7 database
 * calls: 33 of the 50 a call may make (see the budget below).
 */
export const PAGE_SIZE = 25;

/** One page of the issues updated after the watermark, and where the next run goes on. */
export async function issuePage(
  ctx: FluidContext,
  at: SyncPosition,
): Promise<{ issues: LinearIssue[]; next: SyncPosition }> {
  // Mock unless LINEAR_SOURCE says live: the page and the sync work with no token.
  if (ctx.secrets.LINEAR_SOURCE !== "live") return { issues: MOCK_ISSUES.data.issues.nodes, next: START };
  const key = ctx.secrets.LINEAR_API_KEY;
  if (!key) throw new Error("LINEAR_SOURCE is live but LINEAR_API_KEY isn't set");
  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    // A Linear personal API key goes in as is, with no "Bearer".
    headers: { authorization: key, "content-type": "application/json" },
    body: JSON.stringify({
      query: `query($first: Int!, $after: String, $filter: IssueFilter) {
        issues(first: $first, after: $after, filter: $filter, orderBy: updatedAt, includeArchived: true) {
          pageInfo { hasNextPage endCursor }
          nodes { id identifier title url updatedAt archivedAt state { name } assignee { name } }
        }
      }`,
      variables: {
        first: PAGE_SIZE,
        after: at.cursor,
        filter: at.watermark ? { updatedAt: { gt: at.watermark } } : null,
      },
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
  const newest = nodes.reduce<string | null>((max, n) => (max && max > n.updatedAt ? max : n.updatedAt), null);
  return { issues: nodes, next: advance(at, pageInfo.hasNextPage ? pageInfo.endCursor : null, newest) };
}
```

## functions/lib/fixtures/linear-issues.ts: mock data in the API's shape

```ts
// functions/lib/fixtures/linear-issues.ts: Linear's own response shape, so live and mock share one code path.
// The "mock-" ids let the live sync delete these rows once it takes over.
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
          updatedAt: "2026-01-15T00:00:00.000Z",
          archivedAt: null,
          state: { name: "In Progress" },
          assignee: { name: "Sample Person" },
        },
        {
          id: "mock-issue-2",
          identifier: "ENG-2",
          title: "Sample: connect the payment provider",
          url: "https://linear.app/example/issue/ENG-2",
          updatedAt: "2026-01-14T00:00:00.000Z",
          archivedAt: null,
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
import { beginSync, finishSync, must, reconcile } from "./sync";

export async function syncIssues(ctx: FluidContext, opts: { manual: boolean }): Promise<Response> {
  const claim = await beginSync(ctx, "linear", opts.manual);
  if (!claim.ok) return Response.json({ error: "too_soon", retry_at: claim.retryAt }, { status: 429 });
  try {
    const page = await issuePage(ctx, claim);
    // The first live pass (no watermark yet) deletes the rows a mock run left ("mock-" ids),
    // after the fetch worked, so a wrong token never empties the page.
    if (ctx.secrets.LINEAR_SOURCE === "live" && claim.watermark === null && claim.cursor === null) {
      must(await ctx.fluid.db.from("issues").delete().eq("source", "linear").like("source_id", "mock-%"));
    }
    const rows = page.issues
      .filter((issue) => !issue.archivedAt)
      .map((issue) => ({
        source_id: issue.id,
        identifier: issue.identifier,
        title: issue.title,
        status: issue.state?.name ?? null,
        assignee_name: issue.assignee?.name ?? null,
        url: issue.url,
      }));
    const archived = page.issues.filter((issue) => issue.archivedAt).map((issue) => issue.id);
    const changed = await reconcile(ctx, "issues", "linear", rows, ["title", "status", "assignee_name", "url"], archived);
    await finishSync(ctx, "linear", { ok: true, items: changed, ...page.next });
    return Response.json({ changed, more: page.next.cursor !== null });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    // Rows written before the error stay; the next run reconciles them again. The page keeps every row it had.
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

The same shape fits a REST API.
- One request a run returns the 20 newest releases. That is a window, not a pass, so it needs no cursor or watermark.
- Map each release to a row with `source_id: String(release.id)`, then call `reconcile(ctx, "releases", "github", rows, ["name", "url"])`.
- Give it a second `sync_runs` row, with `source: "github"`.
- A slow source can run less often than the tick: skip it while its `last_good_at` is under an hour old.

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

/** The schedule's interval, for the stale rule. */
const SCHEDULE_MS = 15 * 60_000;

export interface SyncRun {
  state: "ok" | "running" | "failed";
  last_good_at: string | null;
  lease_until: string | null;
  cursor: string | null;
  error: string | null;
}

/** The source's latest run, or null before the first one. */
export async function readSyncRun(source: string): Promise<SyncRun | null> {
  const { data, error } = await fluid.db
    .from("sync_runs")
    .select("state,last_good_at,lease_until,cursor,error")
    .eq("source", source)
    .eq("scope", "global")
    .limit(1);
  if (error) throw new Error(error.message);
  return (data?.[0] as SyncRun | undefined) ?? null;
}

export type SyncLabel = "never" | "running" | "failed" | "stopped" | "stale" | "catching_up" | "ok";

/**
 * What the pill says. "stopped": a run the platform ended (the 30 s limit)
 * never writes its end, so "running" past its lease means it didn't finish.
 * "catching_up": a pass is part way through its pages.
 */
export function syncLabel(run: SyncRun | null, now = Date.now()): SyncLabel {
  if (!run) return "never";
  if (run.state === "running") {
    return run.lease_until && now < Date.parse(run.lease_until) ? "running" : "stopped";
  }
  if (run.state === "failed") return "failed";
  if (!run.last_good_at) return "never";
  if (now - Date.parse(run.last_good_at) > 3 * SCHEDULE_MS) return "stale";
  return run.cursor ? "catching_up" : "ok";
}

/** Sync now. Re-read the rows after any answer; a 429 means a run is going or someone synced a moment ago. */
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
| `beginSync`: select, then a compare-and-set update or the first insert | 2 |
| Delete leftover mock rows (first live pass only, after the fetch) | 1 |
| One API page | 1 |
| `reconcile`: select, then insert, one update per distinct change and the archived delete together | up to 3 + `PAGE_SIZE` |
| `finishSync` | 1 |
| **Total with `PAGE_SIZE` 25** | **at most 33 of 50** |

If a source needs more requests per row (a detail request for each record), shrink `PAGE_SIZE` until the worst case stays under 50.
