---
name: PII exposure & webhook-endpoint hygiene audit
description: Check every registered webhook and installed Droplet for where customer PII actually flows, and flag insecure or overexposed endpoints.
icon: lock
---

# Goal

Map where `{{company.name}}`'s customer PII actually flows to — via webhooks and installed Droplets — and flag anything insecure, over-broad, or pointed at a dead endpoint.

# Steps

1. Call `fluid_api("/api/company/webhooks?limit=100", "GET")`, paginating until exhausted. Keep `url`, `resource`, `event`, `active`, `http_method`.
2. Flag every webhook whose `resource` carries customer PII directly — `customer`, `member`, `member_addresses`, `member_payment_methods`, `user`, `contact` — and check:
   - **Non-HTTPS target** — any `url` not starting with `https://` is sending PII in the clear.
   - **Third-party domain** — a PII-carrying webhook pointed at a domain that isn't the company's own or a recognized Fluid/Droplet integration domain deserves a name-the-vendor call-out, not a silent pass.
   - **Active but unreachable** — spot-check up to 5 PII-carrying webhook URLs with `web_fetch` (HEAD-equivalent expectations only — don't assume a non-2xx means broken, some endpoints reject GET/HEAD by design, note that nuance rather than over-flagging).
3. Call `fluid_api("/api/droplets?per_page=100", "GET")` and `fluid_api("/api/droplet_installations?per_page=100", "GET")`. Cross-reference `requested_scopes` against PII-adjacent scopes (`members`, `prospects`, `users`) — any installed, active Droplet holding one of these scopes is a PII-processing third party and belongs in this report even if it never appears in the webhooks list (Droplets can pull data via API instead of receiving pushed webhooks).
4. Build a single **PII flow map**: for every webhook or Droplet touching customer PII, list the destination (URL or Droplet name/vendor), what data category it receives (order/customer/member/payment), and the specific hygiene flag from steps 2-3 if any.
5. Render the flow map as a table, sorted flagged-items first. Follow with a plain-language summary: how many distinct third parties receive customer PII today, and how many of those have an active hygiene flag.
6. End with a **Decision**: the single riskiest flow (non-HTTPS or unreachable-but-active beats a merely broad-scope Droplet, since data-in-the-clear or silently-failing delivery is the more acute risk) and the concrete next step (rotate/reconfigure the webhook, or review the Droplet vendor's scope need).
7. This is read-only — it never disables a webhook or uninstalls a Droplet. Flag findings for the user to action.
