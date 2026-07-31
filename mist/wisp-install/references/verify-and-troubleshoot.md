# Failure modes and how to verify

> Part of the `mist/wisp-install` skill. See [`../SKILL.md`](../SKILL.md) for the install runbook.

## Contents

- Panel says "not installed" on a company that *does* have Wisp installed
- Droplet not installed
- Token lacks `developer`
- `embed_url` missing `/integrations/`
- Write key was never revealed
- Snippet not found in live HTML after cache-bust
- Snippet is there but nothing records
- Sessions appear, then stop after a deploy
- What "verified" actually means

---

## Panel says "not installed" on a company that *does* have Wisp installed

**This was a real Wisp bug. Fixed and deployed 2026-07-31 (commit `2d8bf0f`). If you still see it,
the deployment is stale — `fluid mist push`, then retry.** The diagnosis below is kept because it is
exactly how you recognise a stale deploy.

**Symptom.** Step 1 confirms an active `droplet_installation`. The user opens Droplets → Wisp in the
Fluid admin and gets Wisp's own error page: **"Wisp is not installed on this company — Install Wisp
from the Fluid droplet marketplace, then reopen this panel."** (HTTP 403.) Reinstalling does not
help. It happens on the **first** panel load for a company, i.e. exactly during a fresh install, and
only on companies other than the droplet's owner.

**What it was.** Wisp gates tenant self-heal on a second factor — it asks Fluid whether the caller's
company really has the droplet installed (`app/integrations/wisp/route.ts` → `isDropletInstalled()`
in `lib/fluid/admin-identity.ts`). It used to ask the wrong endpoint:

```ts
const body = await fluidGet("/api/droplets/company_droplets", token);  // ← wrong endpoint
const droplets = (body as Record<string, unknown>).droplets;
```

`GET /api/droplets/company_droplets` returns `current_company.owned_droplets` —
`has_many :owned_droplets, class_name: "Droplet::Application", inverse_of: :owner_company`
(`~/fluid/app/models/concerns/company/associations.rb:143`,
`~/fluid/app/services/api/droplets/company_droplets_action.rb:12`). Those are the droplets a company
**publishes**, not the ones it has **installed**. For the owner company the two coincide, which is
why it went unnoticed. For every other company the array was empty, `isDropletInstalled` returned
`false`, and the panel failed closed.

**The fix now in production** queries `GET /api/droplet_installations?per_page=100&page=N`, matches
on `droplet_uuid`, treats `active === false` as not-installed, pages through the full list (that
endpoint defaults to 10 per page, so a merchant with a long droplet list would otherwise read as
"not installed"), and still returns `null` when Fluid doesn't answer so callers keep failing closed.
Ten tests pin it, including a negative assertion that `company_droplets` is never called again.

**If the symptom appears anyway**, in order:

1. **Stale deployment.** Confirm the running Wisp deployment includes `2d8bf0f`. `fluid mist push`,
   then reload the panel. This is by far the most likely cause.
2. **Token lacks `droplets:view`.** Fluid returns 403, `fluidGet` returns `null`, and Wisp shows
   **"Could not confirm the installation with Fluid"** (503) rather than the 403 page — a different
   message pointing at the same area. Grant `droplets:view` and retry.
3. **Genuinely not installed.** Re-check `GET /api/droplet_installations` and confirm the entry's
   `active` is `true`. An installation with `active: false` correctly reads as not installed.

---

## Droplet not installed

**Symptom.** No matching entry in `GET /api/droplet_installations`, or Wisp's panel says it isn't installed.

**Remediation.** `POST /api/droplet_installations` with `{"droplet_uuid": "<droplet uuid/slug>"}`.
Note the param is *named* `droplet_uuid` but is matched against `droplets.slug`
(`Droplet::Application.available(company).find_by(slug: …)`) — Fluid aliases `uuid` to `slug` on that
model, so the `uuid` you read from `GET /api/droplets` is the right value.

- `409 already installed` → benign race, treat as success.
- `404 not found` → the droplet is neither publicly available nor owned by this company. Only the
  droplet owner can fix that (publish it, or add the company). Say so; do not retry.

---

## Token lacks `developer`

**Symptom.** `GET /api/global_embeds` → `403`, or index works and `POST /api/global_embeds` → `403`.

**Cause.** `GlobalEmbedsController` requires company admin plus `developer:view` (read) /
`developer:update` (write). These are two separate grants; having the first does not imply the second.

**Remediation.** Report verbatim: *"This Fluid token lacks the `developer` permission. Global Embeds
require `developer:view` to read and `developer:update` to create, update, or delete. A company
admin has to grant `developer` on this user's role, then re-run."* Do not attempt a workaround
through the admin UI — the same permission gates it.

**Stop before Step 1 when this fires.** Installing the droplet and rotating a key without being able
to create the embed leaves a half-built install: a droplet in the merchant's admin, a live key, and
no pixel.

---

## `embed_url` missing `/integrations/`

**Symptom.** The panel loads but cannot authenticate — no error from Fluid, no `?jwt=` in the iframe
URL, Wisp redirects to its "session expired, reload the panel" page and stays there forever.

**Cause.** `fluid-mono/apps/fluid-admin/components/Droplets/views/DropletsDetailsView.tsx` (~165–188)
only sets `jwt` when `new URL(droplet.embed_url, origin).pathname.includes("/integrations/")`. That
code carries a `// TODO: Temporary fix … integration pages are supposed to be removed` comment —
this mechanism is load-bearing *and* fragile. If a future admin release removes it, every droplet
using the `?jwt=` handshake loses auth at once.

**Remediation.** `PUT /api/droplets/<uuid>` with
`{"droplet": {"embed_url": "https://<mist-host>/integrations/wisp"}}`. Two constraints:

- `embed_url` is on the **droplet**, not the installation — only the owner company or a root admin
  can change it, and the change hits **every** company that has the droplet installed.
- Fluid normalizes and validates on write: the value must be absolute http(s) (a bare host gets
  `https://` prepended) and non-blank. Legacy bad rows only get validated when the attribute changes.

Renaming that path later silently removes all authentication with no error anywhere. Treat
`/integrations/` as part of the contract, not a URL preference.

---

## Write key was never revealed

**Symptom.** The panel snippet still shows the `wk_…` placeholder, or the user has a key that
doesn't match `wk_<hex>_<base64url>`.

**Cause / constraint.** Wisp stores only `write_key_id` plus a SHA-256 of the secret half. Plaintext
is returned exactly once, by `POST /api/droplet/write-key/rotate`, which authenticates with Wisp's
own signed `mist_session` cookie — **not** a Fluid bearer token. It cannot be curled, scripted, or
fetched with `fluid_api`. It comes out of the panel or it doesn't come out.

The keyId half is **hex, not base64url**, deliberately: base64url contains `_`, which made
`wk_<id>_<secret>` ambiguous and rejected roughly one in three valid keys. If you find yourself
"simplifying" that grammar, don't.

**Remediation.** Have the user open the panel and click Reveal/Rotate. Then stop and re-read the
blast-radius warning in Step 3 — if a key already exists, revealing means *rotating*, and every
already-deployed snippet carrying the old key stops ingesting the instant they click, with no error
anywhere. Reuse the key from the existing Global Embed's `content` instead whenever you can.

---

## Snippet not found in live HTML after cache-bust

Work down this list in order:

1. **Was the cache-buster unique?** Storefront HTML is CDN-cached ~30+ minutes. Reusing
   `?wispcheck=1` from a previous attempt returns the previous answer. Use a fresh value every time.
2. **Is the embed `active`?** `GET /api/global_embeds/<id>`. A draft renders nothing —
   `available_embeds` scopes `.active`. This is the most common cause after a paused activation step.
3. **Is `target` `storefront`?** `checkout` saves fine and renders nowhere. See
   [global-embed-api.md](global-embed-api.md) § *`target: "checkout"` is dead*.
4. **Is the page a themed storefront page?** Only template types in `CAN_HAVE_GLOBAL_EMBEDS` render
   embeds. Admin pages, checkout, and the portal do not. Test on the homepage first.
5. **Right domain?** A company can serve several; you may be fetching one the theme doesn't back.
   Confirm the storefront domain from `GET /api/me` / company settings rather than assuming.
6. **Still nothing?** Fetch the whole `<head>` and look for *any* Wisp trace. If some other embed's
   content is present and Wisp's isn't, the create silently targeted a different company — re-check
   the active company in Mist Desktop.

---

## Snippet is there but nothing records

The loader is deliberately quiet. Check, in the browser console on a real storefront page:

| Observation | Meaning |
| --- | --- |
| `window.__wisp` undefined | Loader bailed before stage 2, or the script never executed |
| `window.__wisp.err === "worker"` | CSP blocked `worker-src blob:`; recorder refuses to compress on the main thread |
| `window.__wisp` present, no network to `/api/ingest` | Sampling roll failed, or the page hasn't flushed yet (flush is deferred past `load`) |

The loader **declines to record** — silently, by design — when any of these hold: `navigator.globalPrivacyControl`
or DNT is set; the page is not the top-level window (`window.top !== window.self`);
`navigator.webdriver` is true; or the sampling roll fails. **`navigator.webdriver` means headless
browser automation will never produce a session** — verify with a real browser, not Playwright.

**On CSP:** Fluid's storefront CSP is **report-only** today
(`config.content_security_policy_report_only = true`), and themed pages relax `script_src`,
`style_src`, and `connect_src` to `https:` (`~/fluid/app/models/concerns/themeable.rb`) precisely
because merchants inject arbitrary scripts. `worker_src :self, :blob` is allowed in the base policy
and the themed override doesn't narrow it. So **no CSP work is needed for Wisp today** — but the
initializer's comment ("switch to false after monitoring") signals intent to enforce later. When
that happens, the `blob:` worker and the `wecommerce.dev` script/connect origins are the three
things to re-check. Admin pages keep the strict allowlist and are not relevant here.

Also check the ingest response if you can see it: `204` is success; anything else returns
`{error, code}` with a fixed code enum (bad key, quota, origin not allowed).

---

## Sessions appear, then stop after a deploy

**Cause.** The snippet was built from a per-deployment host. `getAppBaseUrl()`
(`lib/app-url.ts` in the Wisp repo) returns `APP_URL` (or `FLUID_DROPLET_URL`) if set, otherwise
falls back to `https://$VERCEL_URL` — which is a **new, immutable host on every deploy**. A snippet
carrying `https://<slug>-3ir4ipndg.wecommerce.dev/pixel/v1` keeps resolving against the old
deployment until it doesn't, and the failure looks like "sessions just stopped appearing."

**Remediation.** Set `APP_URL=https://<slug>.wecommerce.dev` on the Mist, `fluid mist push` (env
changes need a redeploy or the running deployment keeps the old value), then re-read the snippet
from the panel and update the Global Embed's `content` via `PUT`. **Never emit a URL from
`getAppBaseUrl()` into anything durable — a snippet, a stored webhook URL, a DB row — without
confirming `APP_URL` is set in that environment.**

---

## What "verified" actually means

An install is verified when **all three** are true. One or two is not a green light.

1. A cache-busted fetch of the live storefront returns the pixel URL, with the key you expect, on
   more than the homepage.
2. A real browser visit leaves `window.__wisp` on the page and posts to `/api/ingest`.
3. A `wisp_sessions` row exists for this `company_id`, with at least one matching `wisp_chunks` row
   — a session with `chunk_count: 0` means ingest accepted a session shell and persisted no payload.
   `wisp_ingest_counters` (daily `chunks`/`sessions`/`bytes`/`rejected`) is a good coarse check for
   "did anything reach ingest at all", and its `rejected` column is where a bad key shows up.

   **Give (3) a second read before you judge it.** Chunks arrive out of order — `sendBeacon` on
   `pagehide` races the normal in-page flushes — so a freshly-recorded session can briefly show a
   null entry path, an "unknown" device, or a `page_count` below what you actually browsed while
   later chunks are still landing. Wait ~15–30s and re-read. Only a row still holding zero chunks
   after the retry is a genuine failure. (A metadata-backfill bug behind the transient display is
   being fixed separately; it does not affect whether the session recorded.)

**Do not over-promise.** Wisp's post-processing cron (`/api/jobs/tick/cron`) is a stub today: every
phase — close-idle-sessions, motion-track distillation, signal detection, daily rollups, AI
summaries, retention reaper — is listed as pending and does nothing. Sessions therefore stay
`status: "open"`, and `wisp_signals` / `wisp_summaries` / `wisp_daily_rollups` stay empty even on a
perfect install. That is expected, not a defect. Report replay as working and everything downstream
of it as not yet built.
