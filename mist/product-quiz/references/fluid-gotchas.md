# Product Quiz — Fluid gotchas that bite this build

Every item here has cost a real build a debugging session. Read before step 1.

## Pages and templates

- **`create_page` ignores the `slug` you pass** (unless `custom_slug` is set) and derives
  one from the *title*. Its returned `preview_route` echoes your *requested* slug, so it
  can point at a 404. Always re-read the real `slug` / `canonical_url` from
  `GET /api/v202604/company/pages` before quoting a URL to anyone.
- **`create_page` can report an error ("Object has been destroyed") *after* it already
  created the Page.** It fails on the preview-navigation step, not the write. **Never
  blind-retry it** — re-list pages first, or you get duplicates with `-1e` / `-2e` slug
  suffixes.
- **Agents cannot delete Pages.** `fluid_api` refuses Page mutations ("Page mutations must
  use create_page") and `create_page` cannot delete. A duplicate has to be removed by a
  human in Fluid admin — so avoid creating one.
- **A `page/<name>/index.liquid` pushed with the theme is not an assigned template.**
  `fluid theme push` creates it with status `draft` and **no Page assignment**; the Page
  keeps whatever template it had (often the theme's generic `default` → `main_page`), so
  with `page.description` null the live route renders an **empty shell** and looks like a
  broken theme. Verify `GET /api/v202604/company/pages/{id}` →
  `application_theme_template_id` matches the intended template id. Iterate the assigned
  template with `update_page_template`, not a theme push.
- The correct local source path is `page/<template-name>/index.liquid` — never
  `page/templates/<name>`.

## Theme dev preview

- **`?theme_template_id=<id>` renders the owning theme's STORED sections, not your local
  files.** Loading a local route with that query param makes the storefront render the
  main theme's saved sections — so local edits that `fluid theme dev` reports as
  "✓ synced" appear to have no effect, and `read_preview_dom` keeps showing old copy even
  with cache-busting params.
  Workaround: `fluid theme push` and verify against the live URL with `crawl` at an exact
  viewport, or view a route the dev theme itself owns.
- A non-current theme's Page assignment is theme-scoped, so its isolated dev copy needs
  the `?theme_template_id=` override to preview at all — which is exactly the trap above.
  Know which one you are in before concluding your section is broken.

## Mist app environment

- **`pnpm install` is blocked for agents** — use `retry_lifecycle({ kind: "install" })`.
- A fresh Mist clone can ship a placeholder `pnpm-workspace.yaml` containing
  `allowBuilds: esbuild/sharp: set this to true or false` — invalid config, so install
  aborts and there is no dev server. Set both to `true`.
- **Local dev uses PGlite, production uses Neon** — different databases. "Empty in prod" is
  usually this, not a bug. Check each side with `db_query`.
- On serverless, concurrent cold lambdas race `CREATE TABLE IF NOT EXISTS`. Treat Postgres
  codes `42P07`, `42710` and `23505` as success in schema bootstrap.
- Anything calling the session helper outside a request scope needs `next/headers` mocked
  in tests — `cookies()` throws rather than returning empty.
- Production env vars set with `set_mist_env_var` require a redeploy (`fluid mist push`)
  before the running app sees them.
