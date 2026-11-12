---
name: Add a database table to a Site
description: Add a table to a Site's db/schema.json with the narrowest rules, read and write it with fluid.db, and check it locally with fluid sites dev.
icon: database
---

# Goal

Give a Site a table for something visitors write (a guestbook, RSVPs, a sign-up list), declared in `db/schema.json`, read and written from the page with `fluid.db`, and checked against the local database before anything is published.

# Steps

1. Confirm the active folder is a Site: `read_file("package.json")` and check that `dependencies` or `devDependencies` names `@fluid-app/sites`. If not, stop and say: "This folder isn't a Site (its package.json doesn't depend on @fluid-app/sites), so I didn't change anything." An old Liquid site has no `db/schema.json`; never use `fluid member-site` commands here.
2. Read what is there: `db/schema.json` if it exists, and `src/` for code that already uses `fluid.db`. Extend an existing table or page rather than adding a second copy.
3. If there is no `db/schema.json` yet, tell the user before you add one: adding it creates the site's database on the next publish, and its usage (rows read, rows written and storage held) is billed to the company's credits, metered by day per site, with no free allowance. Go on only after they agree.
4. Ask the user:
   - What one row holds: the fields, and which are required.
   - Who may read the rows, who may add one, and who may change or remove one.
5. Pick a rule for each of `read`, `insert`, `update` and `delete`. Explain the five in plain words:

   | Rule | Who |
   | --- | --- |
   | `public` | Anyone who can open the site, guests included. |
   | `signed_in` | Any signed-in member the site lets in. |
   | `creator` | Only the member who wrote the row. Not allowed for `insert`. |
   | `owner` | The site's owner (for a company site, its admins). |
   | `nobody` | No one from the browser. |

   Choose the least permissive rule that does the job. Every row carries `created_by`, the writer's user id, and anyone who can read the table sees it, so never make `read` `public` unless the user asks for guests to see the rows; prefer `signed_in` or narrower. A table that names no rules gets `read: owner`, `insert: signed_in`, `update: creator`, `delete: creator`.
6. Write the table into `db/schema.json`:

   ```json
   {
     "version": 1,
     "tables": {
       "guestbook": {
         "columns": {
           "name": { "type": "text", "required": true },
           "message": { "type": "text", "required": true }
         },
         "rules": { "read": "signed_in", "insert": "signed_in", "update": "creator", "delete": "creator" }
       }
     }
   }
   ```

   - Column types: `text`, `integer`, `number`, `boolean`, `date`, `timestamp`, `uuid`, `json`. A column may set `required` and a literal `default`.
   - Never declare `id`, `created_by`, `created_at` or `updated_at`: every table has them.
   - Names match `[a-z][a-z0-9_]{0,62}` and never start with `_` or `pg_`. At most 32 tables, 64 columns a table, 8 `indexes` and 4 `unique` sets of 1 to 3 columns each. The file is at most 1 MiB.
7. Changing a table that already has rows:
   - Applied on publish with no question: a new table, a new optional column, adding or dropping an index, relaxing `required`, changing a rule or a default.
   - Destructive: dropping or renaming a table or column, changing a type, or making a column required. Each needs a step in a top-level `migrations` array with an `id`, such as `{ "id": "2026-11-20-drop-notes", "steps": [{ "op": "drop_column", "table": "rsvps", "column": "note" }] }`. Ops: `drop_table`, `rename_table`, `drop_column`, `rename_column`, `change_type`, `require` (with a `fill`).
   - Before adding a destructive step, show the user exactly which data it removes or changes, and add it only after an explicit yes. Never confirm one on your own, locally or at publish.
8. Write the code with `fluid.db`, in the page that needs it:

   ```ts
   import { fluid } from "@fluid-app/sites";

   const { data, error } = await fluid.db
     .from("guestbook")
     .select("id,name,message,created_at")
     .order("created_at", { ascending: false })
     .limit(50);

   const { error: insertError } = await fluid.db.from("guestbook").insert({ name, message });
   ```

   Check `error` on every answer; `error.code` is one of `validation`, `rule_denied`, `quota_exceeded`, `unique_violation`, `timeout`, `unavailable`, `no_database`. `rule_denied` usually means a guest who has to sign in: show "Sign in to …". Never retry an insert on its own; let the member send it again. For a new page, add its component, its path in `src/App.tsx`, a `<Link>` to it and its title in `config/meta.json`. `fluid.db` needs no scope in `config/access.json`; never add the `database` family for it.
9. Check it locally:
   - Call `start_preview` (Mist runs `fluid sites dev`). It applies `db/schema.json` to `.fluid/dev.sqlite` on start and on every save. `read_recent_log_tail` for errors. A destructive change is held, not applied: the log has a `schema_held` line with its migration ids and a plan fingerprint, and the local database keeps its old shape. With the user's yes, they can apply it from a terminal with `fluid sites dev --confirm <id> --confirm-plan <fingerprint>`, or start the local database over with `fluid sites dev --reset-db`.
   - Confirm the table exists: `db_query` with `side: "local"` and `SELECT name FROM sqlite_master WHERE type = 'table'` (the `_fluid_*` tables are the database's own bookkeeping).
   - Insert: ask the user to submit one row from the page in the preview pane (Mist's preview tools do not submit forms). Then select it: `db_query` with `side: "local"`, `SELECT * FROM <table> ORDER BY created_at DESC LIMIT 5`, and `screenshot_preview` the page to see the row listed.
   - The local viewer is a stand-in owner, so local rows carry `created_by: "local-owner"`. Local rows never reach the live site: the live table starts empty.
10. Run `npm run build` and `fluid sites lint` through `run_cli`. Lint checks `db/schema.json` against the contract and exits 1 on an error; fix every error.
11. Report the table, its columns, each rule and why, the local check, and that publishing (the **Publish and check** skill) creates or changes the live database and that its usage is billed to the company's credits.

# Guardrails

- Never make data readable by guests unless the user asked for it.
- Never add or confirm a migration that removes or rewrites data without the user's explicit yes.
- No SQL from the browser and no database credential in the site: everything in `dist/` is public.
- Hiding content in the page protects nothing. Members-only data belongs in a table whose `read` is `signed_in` or narrower.
- Do not publish in this skill.
