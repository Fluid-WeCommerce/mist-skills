---
name: Audit env vars across all live Mists
description: Check every live Mist for missing or inconsistent env vars (Stripe keys, webhook secrets, etc.).
icon: shield-check
---

# Goal

Sweep every live Mist on `{{company.name}}` and report on env-var hygiene: missing required keys, duplicates with different values, dev-mode keys leaked to production.

# Steps

1. List live Mists: `fluid_api("/api/v202604/mists?filter[state]=live&page[limit]=100", "GET")`. While `meta.pagination.next_cursor` is set, fetch the next page with `page[cursor]=<next_cursor>`.
2. Keep each Mist's `id` (a UUID — the env-var endpoint takes it, not the slug) and `slug` (for the report).
3. For each live Mist, fetch env vars: `fluid_api("/api/v202604/mists/<id>/env_vars", "GET")`. Each var has `managed_by`: `mist` vars (`DATABASE_URL`, the `FLUID_*` connection vars) are provisioned by Mist, read-only, and some return `[REDACTED]` — report them, but never propose changing them. Ignore `[REDACTED]` values when comparing.
4. Build a matrix: row = env var key, column = mist slug, cell = value (mask everything after the first 4 chars, e.g. `sk_li...`).
5. Flag:
   - **Missing required** — any production-targeted Mist lacking keys its code reads (check `process.env.*` uses and `.env.example` when the project is local), such as `STRIPE_SECRET_KEY`.
   - **Test-mode keys in prod** — values starting with `sk_test_`, `pk_test_`, `whsec_test_` on a Mist with `state === "live"`.
   - **Inconsistent values** — the same key set to different masked prefixes across Mists (suggests environment drift).
6. Render as a Markdown table per category, prioritized by severity. Include the mist slug + key + suggested action for each row.
7. Don't write or modify any env vars without explicit user confirmation per finding. Fix a `user` var with `fluid mist env set <slug> KEY=value`, then `fluid mist push` to redeploy.
