---
name: Install Wisp session replay
description: Install and configure Wisp session replay on a Fluid company from zero — droplet install, write key, Global Embed pixel, and proof that a real session recorded.
icon: monitor-play
category: mist
---

# Install Wisp session replay on {{company.name}}

Wisp is a Mist-hosted droplet that records storefront sessions — an invisible pixel captures the
DOM and interactions on every storefront page, and the merchant watches any session back inside a
Droplet panel in the Fluid admin.

This skill takes a company from **nothing** to **a session the merchant can watch**. Five things
have to be true, in this order, and none of them are optional:

1. The **Wisp droplet is installed** on {{company.name}}.
2. The droplet's **`embed_url` path contains `/integrations/`**. Load-bearing and non-obvious — see Step 2.
3. A **`wisp_settings` row exists and a write key has been revealed** (`wk_…`).
4. A **Global Embed** carries the pixel snippet, so every storefront page loads it.
5. **Verification**: the snippet is in the live storefront HTML, and a test visit produced a session row.

Today is {{today}}.

## Before you touch anything

**Skim [references/verify-and-troubleshoot.md](references/verify-and-troubleshoot.md) first.** Every
step below can fail in a way that looks like nothing happening at all — a panel that silently never
authenticates, a CDN-cached page that keeps serving the pre-embed HTML, a loader that declines to
record on purpose. That reference maps each symptom to its one specific remedy. Knowing the shape of
them up front is what keeps a stalled install from becoming an afternoon of guessing.

This whole path is proven end to end in production, not theoretical: the API install described below
created Global Embed **52360** on Prose and the pixel went live on the storefront, verified in the
served HTML with a cache-buster. Where a step says "this works", it has.

Two more references, load them when the step tells you to:

| Reference | Read it when |
| --- | --- |
| [references/global-embed-api.md](references/global-embed-api.md) | Step 4 — the verified `/api/global_embeds` contract, permissions, caching, idempotency |
| [references/dev-install-and-privacy.md](references/dev-install-and-privacy.md) | You want to test without touching the live storefront, or the merchant asks about privacy |

**This skill is idempotent.** Every write step checks for the existing artifact first. Re-running it
on a fully-installed company should change nothing and report "already installed."

**Three steps pause for a human.** Installing the droplet, rotating the write key, and activating
the Global Embed are merchant-visible or destructive. Each one stops, states the blast radius in
one line, and waits for an explicit yes. Do not batch them into one question.

**This skill is Mist Desktop only.** It runs on `fluid_api` and `db_query`, which are Mist Desktop
tools; there is no Claude Code equivalent, so do not try to translate it into `curl` and a Fluid
token — the write-key step (Step 3) is unreachable that way regardless.

> ### Safe Mode must be OFF before Step 1
>
> Mist blocks `fluid_api` for **any method other than `GET`** while Safe Mode is on
> (`fluid-mono/apps/mist-desktop/src/main/tools/safe-mode-policy.ts`, the `fluid_api` case). This
> install does `POST /api/droplet_installations`, `POST /api/global_embeds`, and `PUT` for both the
> activation and any `embed_url` fix. All of them are refused.
>
> **The failure mode is the nasty kind: a clean half-success.** Step 0's permission probes are GETs,
> so they pass. Step 1's "is it installed?" check is a GET, so it passes. Then the very first write
> is refused and you are standing in the middle of an install with a green preflight behind you.
>
> So check it first, not when it bites: if the user has Safe Mode on, say *"Safe Mode blocks every
> write this install needs — turn it off in the titlebar and I'll start"* and wait. Read-only
> reconnaissance (Steps 0–2's checks, and Step 5a's verification fetch) is genuinely safe to run
> either way, and saying which half works keeps the diagnosis honest.

---

## Step 0: Preflight

Establish who you are and what you're allowed to do **before** you start writing.

1. `fluid_api({ path: "/api/me", method: "GET" })` — confirm the active company is the one the user means. Capture
   `company.id`, `company.name`, and the storefront domain. Say the company name back to the user.
   If it isn't the company they asked for, stop: Mist Desktop's active company is what the token is
   scoped to, and you cannot install onto a different one.
2. **Permission probe — `developer`.** `fluid_api({ path: "/api/global_embeds?per_page=1", method: "GET" })`.
   - `200` → you have `developer:view`. Assume `developer:update` too, but Step 4 confirms it for real.
   - `403` → **stop and report**: "This Fluid token lacks the `developer` permission. Global Embeds
     require it (`view` for read, `update` for create/update/delete). A company admin has to grant
     `developer` on this user's role before Wisp can be installed." Do not continue — Steps 1–3
     would leave a half-built install with no pixel.
3. **Permission probe — `droplets`.** `fluid_api({ path: "/api/droplet_installations?per_page=100", method: "GET" })`.
   A `403` here means the token lacks `droplets:view`; same remedy, different permission.

---

## Step 1: Is the Wisp droplet installed?

**Check first.** From the Step 0 response, look for an entry whose `droplet_name` is Wisp (or whose
`droplet_uuid` matches the slug the user gave you). The shape is:

```json
{ "droplet_installations": [ { "uuid": "…", "droplet_uuid": "<droplet slug>", "droplet_name": "Wisp", "active": true } ] }
```

Paginate — `per_page` defaults to **10** on this endpoint.

- **Found and `active: true`** → say "Wisp is already installed" and go to Step 2. Do not reinstall.
- **Not found** → install it:

1. Find it in the catalog: `fluid_api({ path: "/api/droplets?per_page=100", method: "GET" })` and match on `name`.
   Capture its `uuid` (which is the droplet's stable **slug** — Fluid aliases the two) and its
   `embed_url`, you need that in Step 2. Not in the list? The droplet isn't publicly available and
   isn't owned by this company; the droplet owner has to publish it or add this company. Stop and say so.
2. **PAUSE.** Ask: *"Install the Wisp droplet on {{company.name}}? This adds a Wisp panel to their
   Fluid admin and lets it read their admin session — it does not start recording yet."* Wait for a
   clear yes.
3. `fluid_api({ path: "/api/droplet_installations", method: "POST", body: { "droplet_uuid": "<uuid from step 1>" } })`
   - `201` → installed. The response carries `droplet_installation_uuid` — keep it.
   - `409 { "droplet_uuid": ["already installed"] }` → someone installed it between your check and
     your write. Treat as success and continue.
   - `404 { "droplet_uuid": ["not found"] }` → the droplet exists but isn't available to this
     company. Same remedy as above.

---

## Step 2: `embed_url` must contain `/integrations/`

**This is the step everyone skips and then spends a day on.**

Fluid admin only appends the admin's auth token to the droplet iframe as `?jwt=` when the
`embed_url` **path contains the literal substring `/integrations/`**. The check lives in
`fluid-mono/apps/fluid-admin/components/Droplets/views/DropletsDetailsView.tsx` (~lines 165–188):

```ts
const url = new URL(droplet.embed_url, window.location.origin);
if (url.pathname.includes("/integrations/")) {
  url.searchParams.set("inFrame", "true");
  const token = cookies.auth_token || getUserToken();
  if (token) url.searchParams.set("jwt", token);
}
if (droplet.droplet_installation_uuid) url.searchParams.set("dri", droplet.droplet_installation_uuid);
```

Wisp authenticates by spending that `?jwt=` once against `GET /api/me` server-side. **Without
`/integrations/` in the path there is no token, no error, and no way to authenticate** — the panel
just sits there. (Note the `dri=` param is appended regardless; Wisp deliberately ignores it. Tenancy
comes from the verified token, never from a caller-supplied id.)

Check it:

1. `fluid_api({ path: "/api/droplets?per_page=100", method: "GET" })`, find Wisp, read `embed_url`. It must look like
   `https://<mist-host>.wecommerce.dev/integrations/wisp`.
2. **Path contains `/integrations/`** → good, continue.
3. **It does not** → **stop and report loudly.** The fix is
   `fluid_api({ path: "/api/droplets/<uuid>", method: "PUT", body: { "droplet": { "embed_url": "https://<mist-host>/integrations/wisp" } } })`
   — but `embed_url` lives on the **droplet record, not the per-company installation**, so:
   - it can only be changed by the droplet's **owner company** (or a root admin), not by {{company.name}}; and
   - changing it changes the panel URL for **every company that has Wisp installed**.

   Do not issue that PUT from this skill unless the active company owns the droplet **and** the user
   explicitly confirms the cross-company blast radius. Otherwise hand it to whoever owns the droplet.

Confirm the panel actually authenticates before you go further: open Wisp in the Fluid admin
(Droplets → Wisp) and check that the panel renders rather than showing an auth error. If it shows
**"Wisp is not installed on this company"** even though Step 1 says it is, the running Wisp
deployment is stale — that check was fixed on 2026-07-31 and a `fluid mist push` clears it. See
`references/verify-and-troubleshoot.md` § *Panel says "not installed" on a company that does have
Wisp installed* for the other two causes.

---

## Step 3: Mint and capture the write key

The write key (`wk_<keyId>_<secret>`) is what the pixel presents to `/api/ingest`. Wisp stores
**only a SHA-256 hash of the secret half** — the plaintext is returned exactly once, by the rotate
call, and can never be shown again.

**You cannot curl this.** `POST /api/droplet/write-key/rotate` authenticates with Wisp's own signed
`mist_session` cookie, which is minted only by the `/integrations/wisp` handshake inside the Fluid
admin iframe. A Fluid bearer token will not work. The key has to come out of the panel.

1. Open **Fluid admin → Droplets → Wisp**. Loading the panel is what creates the company's
   `wisp_settings` row (Wisp calls `ensureWispSettings` on every panel render) — so a first-ever
   panel load already provisions the tenant and mints the first key.
2. **PAUSE.** Ask: *"Reveal the write key? If a key already exists this **rotates** it — any pixel
   snippet already deployed with the old key stops recording the moment you click, silently."*
   Wait for a clear yes.
   - **First install, no key yet:** the panel shows the snippet with a `wk_…` placeholder. Clicking
     reveal mints the first key; nothing is invalidated. Say that — it's a much cheaper yes.
   - **Key already exists:** rotating is destructive. If the goal is just "install the pixel" and a
     working embed already exists, **do not rotate** — reuse the deployed key from the existing
     Global Embed's `content` (Step 4 reads it anyway).
3. Have the user click **Reveal / Rotate** and copy the whole snippet the panel renders. It looks
   like this and it is the authoritative version — the panel builds it from the deployment's own
   base URL and the company's own sampling rate, so copying it avoids every hand-assembly mistake:

   ```html
   <script async src="https://<mist-host>.wecommerce.dev/pixel/v1"
           data-wisp-key="wk_ab12cd34ef56_…"
           data-wisp-sampling="1"></script>
   ```

4. Sanity-check what you were handed before you deploy it:
   - key matches `wk_<hex>_<base64url>` — if the keyId half isn't hex, it's not a real key
   - `async` is present (see Step 4 — the snippet lands first in `<head>`; without `async` it blocks the page)
   - the host is the **stable** Mist host (`<slug>.wecommerce.dev`), **not** a per-deployment host
     like `<slug>-3ir4ipndg.wecommerce.dev`. A per-deployment host means `APP_URL` isn't set on the
     Mist, and the snippet will silently die on the next deploy. See
     `references/dev-install-and-privacy.md` § *Never bake a per-deployment host into a snippet*.

If the panel never reveals a key — no key in hand, no install. Stop; do not create a Global Embed
with a placeholder.

---

## Step 4: Create the Global Embed

Read [references/global-embed-api.md](references/global-embed-api.md) now. Short version of what
matters here:

- **Use the API, not the admin UI.** The Global Embeds drawer in Fluid admin is unreliable to
  automate — its Save button renders outside the layout viewport at common window sizes and its
  disabled state gets stuck. Don't waste time clicking.
- **Global Embeds are company-wide.** Every theme, including the live one. There is no per-theme scoping.
- `target: "checkout"` is a dead enum value — nothing renders it on either side. **Never use it.**

Steps:

1. **Idempotency check.** `fluid_api({ path: "/api/global_embeds?per_page=100", method: "GET" })` (paginate — default
   `per_page` is 10). Look for an existing Wisp embed: name matching `Wisp`, or `content` containing
   `/pixel/v1`.
   - **Found and `status: "active"`** → report the existing embed's `id`, `status`, `placement`,
     `target`, and the `data-wisp-key` in its content. If the key matches the one you hold, you're
     done here — skip to Step 5. Do **not** create a second one; two embeds means the pixel loads twice.
   - **Found but `status: "draft"`** → go to 4 below and activate that one via `PUT`.
   - **Found with a different key** → surface both keys and ask which is authoritative. Do not guess.
2. **Create as a draft.** A draft is inert — it exists, nothing renders it, nothing is merchant-visible:

   ```
   fluid_api({
     path: "/api/global_embeds",
     method: "POST",
     body: {
       "global_embed": {
         "name": "Wisp session replay",
         "content": "<script async src=\"https://<mist-host>.wecommerce.dev/pixel/v1\" data-wisp-key=\"wk_…\" data-wisp-sampling=\"1\"></script>",
         "status": "draft",
         "placement": "head",
         "target": "storefront"
       }
     }
   })
   ```

   `201` returns `{"global_embed": {…}}` — capture the `id`. A `403` here means the token has
   `developer:view` but not `developer:update`; report that precisely. A `422` returns per-field
   errors; `name` and `content` are the only required fields.
3. Show the user the exact `content` string you're about to make live. Content is inserted
   **verbatim** — Fluid's `sanitize_content` is a documented no-op — at the **top** of
   `content_for_header`, making it the first executable thing in the document. That is why `async`
   is mandatory, not stylistic.
4. **PAUSE.** Ask: *"Activate this embed? It goes live on every storefront page of every theme on
   {{company.name}} — including the live theme — and Wisp starts recording real shoppers within the
   CDN cache window."* Wait for a clear yes. Then:

   ```
   fluid_api({ path: "/api/global_embeds/<id>", method: "PUT", body: { "global_embed": { "status": "active" } } })
   ```

If the merchant isn't ready to record real traffic yet, stop here with the draft in place and point
them at `references/dev-install-and-privacy.md` § *Record without touching the live theme*.

---

## Step 5: Prove it works

An install you haven't verified is a rumor. Do all three.

**5a — the snippet is in the live storefront HTML.** Storefront HTML is CDN-cached ~30+ minutes, so
a plain fetch will happily hand you the pre-embed page. **Always cache-bust** — put a unique query
param on the URL every time you check:

```
web_fetch({ url: "https://<storefront-domain>/?wispcheck=<unix-timestamp>" })
```

Then search the returned body for `pixel/v1`. `web_fetch` is unauthenticated, which is exactly right
here: you want the anonymous shopper's view of the page, not an admin's.

Two things **not** to reach for. `run_cli` will not run that `curl … | grep` one-liner — its
allowlist is `fluid`, `pnpm`, `npm`, `git` only, and it does no shell interpretation, so there are no
pipes either. And `fluid_api({ path: "/api/v202604/util/fetch?url=…", method: "GET" })` fetches
through Fluid rather than directly; keep it as the fallback if `web_fetch` is blocked by egress
rules, not as the first move.

- **Hit** → the embed is live. Check the `data-wisp-key` in the served HTML matches the key you hold.
- **Miss** → do not conclude failure yet. Re-run with a *different* cache-buster after 60s. Still
  missing after two tries → `references/verify-and-troubleshoot.md` § *Snippet not in live HTML*.

Then confirm it fires beyond the homepage. Global Embeds render on every storefront template type —
product, collection, category, cart, post, page, error — so spot-check a product page and the cart
page with the same cache-busted grep.

**5b — the recorder loads.** Open the storefront in a browser and check the console:
- `window.__wisp` present → the loader ran.
- `window.__wisp.err === "worker"` → the recorder refused to start because the page's CSP blocks
  `worker-src blob:`. It records nothing by design rather than compress on the shopper's main
  thread. See the CSP notes in `references/verify-and-troubleshoot.md`.
- Nothing at all → the loader bailed. It silently declines to record on GPC/DNT, inside an iframe,
  under `navigator.webdriver` (so **headless automation will not produce a session** — use a real
  browser for this test), or on a failed sampling roll.

**5c — a session row exists.** Browse two or three storefront pages in a real browser, click a few
things, then wait ~10s for the flush. Confirm from the panel: reload Wisp in the Fluid admin and
check the sessions list, or hit `GET /api/droplet/sessions` from inside the authenticated panel.

If you have DB access to the Wisp deployment, the authoritative check is a row in `wisp_sessions`
for this `company_id` (`id`, `page_count`, `chunk_count`, `started_at`) plus at least one row in
`wisp_chunks` — a session shell with zero chunks means ingest accepted the session but never
persisted payload. `db_query` on a Mist project **defaults to production**; that's what you want
here, but pass `side` deliberately either way.

**Read it twice before you judge it.** Chunks arrive **out of order** — the `sendBeacon` flush on
`pagehide` races the normal in-page flushes — so for the first few seconds after a test visit a
session row can legitimately show a null entry path, an "unknown" device, or a `page_count` lower
than the number of pages you actually browsed, while later chunks are still landing. That is a
transient read, not a broken install. Wait ~15–30s and re-read before concluding anything; only a
row that still has zero chunks after a retry is a real failure. (The underlying metadata-backfill
bug is being fixed separately — don't chase it from here.)

Sessions currently stay `status: "open"` — Wisp's post-processing cron is a stub today, so don't
treat an open session as a failure, and don't promise signals, rollups, or AI summaries.

---

## Step 6: Report

Give the user a short table: droplet installation uuid, `embed_url`, Global Embed id + status,
the write key **masked** (`wk_ab12cd34…`), the storefront URLs you verified, and the session id you
watched. Then state plainly what is now true: **Wisp is recording real shoppers on {{company.name}}.**
Recommend they tell the merchant, and point them at the privacy posture in
`references/dev-install-and-privacy.md`.

---

## Uninstall / rollback

Reverse order of install. Each step is independently useful — stopping recording does not require
uninstalling the droplet.

1. **Stop recording, keep everything.** `fluid_api({ path: "/api/global_embeds/<id>", method: "PUT", body: { "global_embed": { "status": "draft" } } })`.
   Instant at origin; live for up to the CDN window (~30+ min) on already-cached pages. Reversible
   with one `PUT` back to `active` — the key stays valid.
2. **Remove the snippet entirely.** `fluid_api({ path: "/api/global_embeds/<id>", method: "DELETE" })`. Same cache
   caveat. Verify with the cache-busted grep from Step 5a.
3. **Invalidate the key.** Rotate it from the panel and discard the new value — any stale copy of
   the snippet still in a cached page or a theme file stops ingesting.
4. **Uninstall the droplet.** `fluid_api({ path: "/api/droplet_installations/<installation-uuid>", method: "DELETE" })`.
   Fires Wisp's uninstall webhook.

**What happens to recorded data:** nothing automatic. Sessions, chunks, and counters already written
stay in Wisp's database under that `company_id` — uninstalling the droplet does not delete them, and
Wisp's retention reaper is not implemented yet. If the merchant is asking for deletion (not just
"stop recording"), that is a manual job against the Wisp deployment and you should say so rather
than implying the uninstall handled it.
