---
name: Audit env vars across all live Mists
description: Check every live Mist for missing or inconsistent env vars (Stripe keys, webhook secrets, etc.).
icon: shield-check
---

# Goal

Sweep every live Mist on `{{company.name}}` and report on env-var hygiene: missing required keys, duplicates with different values, dev-mode keys leaked to production.

# Steps

1. List all Mists: `fluid_api("/api/v202604/mists?limit=100", "GET")`. Paginate via cursor.
2. Filter to `state === "live"`.
3. For each live Mist, fetch env vars: `fluid_api("/api/v202604/mists/<id>/env_vars", "GET")`.
4. Build a matrix: row = env var key, column = mist slug, cell = value (mask everything after the first 4 chars, e.g. `sk_li...`).
5. Flag:
   - **Missing required** — any production-targeted Mist lacking common keys (`STRIPE_SECRET_KEY`, `WEBHOOK_SECRET`).
   - **Test-mode keys in prod** — values starting with `sk_test_`, `pk_test_`, `whsec_test_` on a Mist with `state === "live"`.
   - **Inconsistent values** — the same key set to different masked prefixes across Mists (suggests environment drift).
6. Render as a Markdown table per category, prioritized by severity. Include the mist slug + key + suggested action for each row.
7. Don't write or modify any env vars without explicit user confirmation per finding.
