---
name: Droplet & integration deploy health
description: Audit every installed Droplet for stale/broken state and over-broad requested scopes, and flag the riskiest integration first.
icon: puzzle
---

# Goal

Sweep every Droplet installed on `{{company.name}}` for deploy health and access risk: which ones are inactive or unreachable, and which are asking for more permission than a reasonable integration needs.

# Steps

1. Call `fluid_api("/api/droplets?per_page=100", "GET")`, paginating until exhausted. Keep `uuid`, `name`, `active`, `publicly_available`, `requested_scopes`, `categories`, `embed_url`.
2. Call `fluid_api("/api/droplet_installations?per_page=100", "GET")`, paginating until exhausted, and match installations to the Droplets from step 1 by `droplet_uuid`.
3. Flag deploy-health issues:
   - **Installed but inactive** — an installation exists but the matched Droplet's `active` is `false` — likely broken or deprecated, silently doing nothing.
   - **No `embed_url`** — a Droplet with app extensions but no reachable embed target is misconfigured.
4. Flag access risk by scope. Treat `payments`, `settings`, `users`, and `header_menus` as high-sensitivity scopes. For each installed Droplet, list its `requested_scopes` and flag any combining 3+ scopes or any high-sensitivity scope, especially on a Droplet whose `categories` don't obviously need it (e.g. a "content" or "social" category Droplet asking for `payments`).
5. Render: a table of installed Droplets (name, active, scope count, high-sensitivity scopes held, flag), followed by **Deploy-health issues** and **Over-broad access** call-out sections.
6. End with a **Decision**: name the single Droplet posing the most risk — broken-and-installed beats over-scoped-but-working, since a silently-broken integration can be losing data right now — and the concrete next step (reinstall vs. scope review with the vendor).
7. This is read-only. Don't call `repair_and_reinstall_droplet` or touch installations from this skill — hand the finding to the user to action.
