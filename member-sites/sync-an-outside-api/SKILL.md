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
   - If there is no `db/schema.json` yet, ask the user before you add one. Adding it creates the site's database on the next publish. Its usage (rows read, rows written, storage) is billed to the company's credits by day, with no free allowance, and the schedule writes on every tick. Go on only after they agree.

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
6. **The sync** (the full code is in the reference). Both Sync now and the schedule call the same `syncIssues(ctx, { manual })`, which runs:
   - **`beginSync`** claims the run in `sync_runs` with a compare-and-set update, so only one run syncs at a time.
     - It refuses with `429 {retry_at}` while another run holds the row: state `running` for under 60 s, the lease.
     - It also refuses a person's second run within 60 seconds.
     - The schedule passes `manual: false` and never writes `last_manual_at`: **the schedule must not take the Sync now slot**.
     - A run the platform stopped (the 30 s limit) never writes its end. Its lease runs out, and the page shows it as stopped.
   - **One page from the API**, mock or live.
   - **`reconcile`** stands in for upsert, which `fluid.db` doesn't have.
     - It makes one select by `source_id`, one insert for new rows, one update per distinct change and one delete for records the API reports archived or deleted.
     - It writes only the columns the API owns, and compares `json` columns by value.
   - **`finishSync`** records how the run ended.
     - On success: `ok`, with `last_good_at`, `items` and the paging position.
     - On failure: `failed`, with the error. It also drops the page cursor, so a cursor the API stopped accepting can't fail every later run.
     - Rows already written stay, and the next run reconciles again. The page keeps every row it had, so it shows the last good data.
   - **Mock rows.** Their ids start with `mock-`. Once the source is live, each pass deletes them, so a site that ran in mock mode doesn't keep sample rows.
7. **Stay inside the limits.** Each call gets 30 s of wall time, 1 s of CPU and 50 outgoing requests; the whole site gets 600 calls a minute.
   - Count every `fetch`, and to be safe every `ctx.fluid.db` call.
   - Sync one page per call: 25 rows cost at most 33 requests. Never loop pages until done in one call.
   - **Sync incrementally**, by the API's "updated after" filter.
     - A pass pages through records updated after the stored `watermark`, keeping the API's cursor in `sync_runs.cursor` between runs.
     - When the pass ends, the newest update it saw becomes the new watermark.
     - So only the first fill takes many runs; after that each run reads only what changed, and Sync now picks up an edit made a moment ago.
     - A source with no "updated after" filter re-reads a fixed window (the newest N) on each run instead.
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
10. **Check it locally.**
    - `start_preview` (Mist runs `fluid sites dev`).
    - Press Sync now: the rows appear from the fixtures, and `db_query` `side: "local"` `SELECT * FROM sync_runs` shows `state = ok`.
    - Press it again at once: you should get a 429.
    - Note `last_manual_at`, fire the schedule with `curl -X POST http://127.0.0.1:<port>/_fluid/fn/_dev/fire/work-tick`, and read `sync_runs` again. The tick's run must leave `last_manual_at` unchanged. A Sync now pressed 60 s after the first press must succeed. A press inside those 60 s is refused by design, not by the tick.
    - Set a wrong token with `LINEAR_SOURCE=live` in `.fluid/secrets.env`: the run fails, the page shows Failed, and the old rows stay.
11. `npm run build` and `fluid sites lint` through `run_cli`; fix every error. `functions/` and `config/functions.json` must agree.
12. Report:
    - the tables and rules;
    - the area function and its routes;
    - the schedule;
    - which secrets are still missing for live mode;
    - that publishing is the `member-sites/publish-and-check` skill.

    After publishing, read `fluid sites logs --since 1h`. Each line has the function, caller and status, but no `console.log` output, so the response status is your only signal; return a real one.

# Production gotchas

- **Webhooks into a private site.** If an outside service pushes to a `key` function instead of the site pulling, note that production answered **503** to API keys on a **private** site until the gateway deployed on 2026-11-12. A 503 there now has another cause.
- **Schedules.** They are the newest part of Sites, so confirm in `fluid sites logs` that ticks arrive before you promise "updates every 15 minutes".
- **Live logs.** They carry no `console.log` output. Return the error in the JSON body and a non-2xx status.
- **Racing first runs.** Two first runs can race on inserting the `sync_runs` row; the loser gets `unique_violation` and backs off. After that, the compare-and-set claim keeps runs apart.

# Guardrails

- Read-only tokens. A sync that also writes back to the outside tool needs an allowlist of records it may change, checked in the function.
- No secret in the page, `dist/`, a response body or a commit. Only functions read `ctx.secrets`.
- Never make synced rows guest-readable unless the user asked.
- Don't publish in this skill.
