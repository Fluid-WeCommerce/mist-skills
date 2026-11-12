---
name: Sync an outside API into a Site
description: Pull data from an outside API (Linear, GitHub or any HTTPS API) into a Site's database with a secret token, a Sync now button and a schedule, inside the function limits.
icon: refresh-cw
---

# Goal

Show data from another tool on a Site: Linear issues, GitHub releases, CRM deals, tickets. A server function calls the API with a secret token and writes rows into `fluid.db`. The page reads those rows, shows "last synced 2 min ago", and has a **Sync now** button. A schedule keeps the data fresh. The code in the reference is the pattern a production internal Site runs, made generic.

# Steps

1. Confirm the active folder is a Site: `read_file("package.json")` and check that it depends on `@fluid-app/sites`. If not, stop and say: "This folder isn't a Site (its package.json doesn't depend on @fluid-app/sites), so I didn't change anything." Read `db/schema.json`, `config/functions.json`, `functions/` and `src/` first, and extend what is there: a second sync joins the existing area function, `sync_runs` table and helpers rather than copying them.
2. Ask the user:
   - Which API, and which records become rows (fields, and the record's stable id).
   - Who may see the rows (usually `signed_in`; staff-only data needs a staff check in the function and a narrower `read` rule).
   - How fresh they need to be. A schedule runs at most every 5 minutes; 15 is plenty for most dashboards.
   - Whether they have a **read-only** token. Until they do, build in mock mode; nothing waits on the token.
3. **Tables** (the `member-sites/add-database-table` skill has the column types and limits).
   - If there is no `db/schema.json` yet, ask the user first, exactly as `member-sites/add-database-table` step 3 says (a new database is billed to the company's credits). Add that the schedule writes on every tick.

   Add:
   - The data table: the record's own columns plus `source`, `source_id` and `synced_at`, with `"unique": [["source", "source_id"]]`.
   - `sync_runs`: one row per source, unique on `source` and `scope`.

   Rules for both: `read: signed_in` (or narrower), and `insert`, `update`, `delete` all `nobody`. Only the function writes, as the site; the browser only reads. A column people edit (a note, a pin) needs its own write path, and the sync must never overwrite it.
4. **Secrets and the mock switch.**
   - The token: `run_cli` `fluid sites env set LINEAR_API_KEY <value> --secret`, with the value the user gave you as the argument. Never ask them to paste it in a terminal, and never write it into code, `dist/` or a response.
   - The switch: a plain env var `LINEAR_SOURCE` set to `live`. Anything else means mock.
   - Mock data lives in `functions/lib/fixtures/` **in the API's own response shape**, so mock and live run the same mapping code.
   - Locally, both go in `.fluid/secrets.env` as `NAME=value` lines (never committed).
   - Names match `^(?!FLUID_)[A-Z][A-Z0-9_]{0,63}$`; a site holds at most 64.
5. **One function per area, routed by sub-path.** A site has at most 20 functions, so don't make one per action.
   - Make the area's function once: `run_cli` `fluid sites functions new work --access signed_in`.
   - Route inside it: `fluid.fn.fetch("work/sync")` reaches `/api/work/sync`.
   - Put shared code in `functions/lib/` (plain modules, not functions).
   - The function writes as the site, so **no table rule protects these rows**. Check the caller before any write: a page viewer from the site's company, plus your own staff check if the data is staff-only.
6. **The sync.** Copy the reference's `functions/lib/sync.ts` as is, and write the source's own two files (`lib/linear.ts`, `lib/work-sync.ts`). Both Sync now and the schedule call the same `syncIssues(ctx, { manual })`. The rules that matter when you adapt it:
   - The schedule passes `manual: false`, so it never takes the Sync now slot. Only a person's run is held to the 60 s gap.
   - `beginSync` claims the run with a compare-and-set and a lease, so two runs never sync at once. A run the platform stops (30 s) never writes its end; the lease runs out and the page shows "stopped".
   - `reconcile` stands in for the upsert `fluid.db` lacks. Pass only the columns the API owns, so columns people set survive. Pass the ids the API reports archived or deleted as `removed`.
   - A failed run keeps every row and drops its page cursor; the next run starts the pass again.
   - Mock rows carry `mock-` ids, and the first live pass deletes them.
7. **Stay inside the limits.** Each call gets 30 s of wall time, 1 s of CPU and 50 outgoing requests; the whole site gets 600 calls a minute.
   - Count every `fetch`, and to be safe every `ctx.fluid.db` call. One page of 25 rows costs at most 33 (the budget table is in the reference). Never loop pages until done in one call.
   - Sync incrementally with the API's "updated after" filter: `advance()` keeps the cursor and the watermark in `sync_runs`, so only the first fill takes many runs. A source without that filter re-reads a fixed window (the newest N) each run.
   - Compute dates inside the handler, never at module scope: a Worker's clock reads 0 at module load. That includes seed data (store markers like "3 days ago" and resolve them when the seed runs).
8. **The schedule.**
   - Create it with `run_cli` `fluid sites functions new work-tick --access key --schedule "*/15 * * * *"`. Cron is in UTC, at most every 5 minutes.
   - `access: key` keeps pages and the public out. Any site API key can still call it, so the handler refuses every caller whose `ctx.caller.kind` isn't `"schedule"`.
   - A scheduled call has no viewer, so `ctx.fluid.api` answers 401 `fn_api_needs_viewer`. Reach outside tools with `fetch` and secrets only.
   - A failed scheduled run isn't retried; the next tick is the retry.
   - Treat the schedule as the bonus: Sync now must work on its own.
9. **The page.** Read `sync_runs` for the source and show:
   - "Last synced <time ago>";
   - **Catching up** while a pass is part way through its pages (the cursor is set);
   - **Stale** when `last_good_at` is older than three schedule intervals;
   - **Failed** with the error and "showing data from <last_good_at>";
   - **Stopped** when the state has been `running` for longer than the lease.

   **Sync now** POSTs to `work/sync`. On 429 (a run is going, or someone synced a moment ago) it says "try again at <retry_at>". After any answer it re-reads the rows.
10. **Check it locally**, with `start_preview` and `db_query` `side: "local"` as in `member-sites/add-database-table` step 9:
    - Sync now fills the rows from the fixtures, and `sync_runs` shows `state = ok`. A second press at once gets 429.
    - Fire the schedule (`curl -X POST http://127.0.0.1:<port>/_fluid/fn/_dev/fire/work-tick`): `last_manual_at` must not change. A press 60 s after the first must succeed.
    - A wrong token with `LINEAR_SOURCE=live` in `.fluid/secrets.env`: the run fails, the page shows Failed, and the rows stay.
11. `npm run build` and `fluid sites lint` through `run_cli`; fix every error. `functions/` and `config/functions.json` must agree.
12. Report:
    - the tables and rules;
    - the area function and its routes;
    - the schedule;
    - which secrets are still missing for live mode;
    - that publishing is the `member-sites/publish-and-check` skill.

    After publishing, read `fluid sites logs --since 1h`: one line per call with its status, and no `console.log` output, so return a real status and the error in the body.

# Production gotchas

- **Webhooks into a private site.** If an outside service pushes to a `key` function instead of the site pulling, note that production answered **503** to API keys on a **private** site until the gateway deployed on 2026-11-12. A 503 there now has another cause.
- **Schedules.** They are the newest part of Sites, so confirm in `fluid sites logs` that ticks arrive before you promise "updates every 15 minutes".

# Guardrails

- Read-only tokens. A sync that also writes back to the outside tool needs an allowlist of records it may change, checked in the function.
- Never make synced rows guest-readable unless the user asked.
- No secret in the page, `dist/` or a response, and no publishing in this skill.
