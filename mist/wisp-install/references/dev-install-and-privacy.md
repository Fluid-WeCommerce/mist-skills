# Dev/test installs, durable URLs, and privacy posture

> Part of the `mist/wisp-install` skill. See [`../SKILL.md`](../SKILL.md) for the install runbook.

## Contents

- Record without touching the live theme
- Never write a literal `$`-then-quote into a Liquid file
- Never bake a per-deployment host into a snippet
- The snippet's `data-*` attributes
- Privacy posture — what to tell the merchant
- Local ≠ prod, twice over

## Record without touching the live theme

A Global Embed is **company-wide** — every theme, including the live one. When the merchant isn't
ready for that, or you just want to prove the pipeline end to end before going live, put the snippet
in a **draft theme** and browse it with a preview param. Nothing a real shopper sees changes.

1. Duplicate the live theme, or pick an existing draft. Note its id.
2. Add the snippet to that theme's `layout/theme.liquid`, inside `<head>`, immediately after
   `{{ content_for_header }}`.
3. Push only that theme: `fluid theme push --theme <id> --nodelete`. `--nodelete` matters — without
   it you can strip files the draft theme still needs.
4. Browse the storefront with `?preview_theme_id=<id>`. The recorder runs, sessions land, and the
   live theme is untouched.

Prefer this for any exploratory work. Promote to a Global Embed only when the merchant has said yes
to recording real traffic.

The same trick is the cleanest way to A/B a sampling rate or a masking mode before committing it
company-wide.

## Never write a literal `$`-then-quote into a Liquid file

If a dev-theme install needs the character `$` inside a `<script>` in a `.liquid` file, **do not
write it literally.** Something in the theme toolchain mangles a `$` immediately followed by a quote
into a raw newline, which kills the whole script at parse time — no error, the script just stops
existing. Learned in production on a real company's theme.

Use `String.fromCharCode(36)` instead. This only bites the Liquid-file path; Global Embed `content`
goes through the JSON API and is stored verbatim, so it is not affected.

## Never bake a per-deployment host into a snippet

Wisp's `getAppBaseUrl()` (`lib/app-url.ts`) resolves in this order:

```
APP_URL  ||  FLUID_DROPLET_URL  ||  https://$VERCEL_URL  ||  http://localhost:3000
```

`VERCEL_URL` is a **new host on every deploy** — e.g. `prose-8de108-3ir4ipndg.wecommerce.dev`. A
snippet built from that host keeps working until the next deploy and then silently stops: the old
host still resolves, so nothing errors and nothing records. This has already happened once in
production during Wisp's scaffolding, and it is invisible from the merchant's side.

Before you copy a snippet out of the panel, look at the host. If it has a random-looking suffix,
`APP_URL` is not set on that Mist. Fix the env var, `fluid mist push` (env changes need a redeploy —
otherwise the running deployment keeps the old value and you debug a ghost), re-read the snippet,
and only then create the Global Embed.

Rule of thumb: **never put a `getAppBaseUrl()` output into anything durable** — a snippet, a stored
webhook URL, a DB row — without first confirming `APP_URL` is set in that environment.

## The snippet's `data-*` attributes

The loader at `GET /pixel/v1` reads exactly three attributes off its own `<script>` tag:

| Attribute | Required | Values | Notes |
| --- | --- | --- | --- |
| `data-wisp-key` | yes | `wk_<hex>_<base64url>` | Missing → the loader bails silently. This is the only tenancy signal ingest trusts. |
| `data-wisp-sampling` | no | float `0`–`1` | Defaults to the company's configured sampling rate, baked in server-side. `1` records everyone. |
| `data-wisp-mask` | no | `inputs` \| `all_text` | Defaults to `inputs`. Anything unrecognized falls back to `inputs`. |

There is **no endpoint attribute.** The ingest URL (`<base>/api/ingest`) and the stage-2 recorder
URL (`<base>/pixel/recorder-v1.js`) are both baked into the loader server-side — which is exactly
why the `APP_URL` warning above matters.

`async` is required in the tag. Head-placement embeds are prepended to `content_for_header`, so the
Wisp script is the first executable thing in the document; without `async` it blocks first paint on
every storefront page. **Degrade the recording, never the page.**

## Privacy posture — what to tell the merchant

Activating the embed starts recording real shoppers. Say so out loud, in the same breath as the
confirmation. The merchant needs to know, and in most jurisdictions their privacy policy needs to
say it too. Wisp's own privacy doc is `docs/05-privacy.md` in the Wisp repo; the short version an
installer should be able to state confidently:

- **Masking happens in the shopper's browser, at capture time, configured before `record()` is
  called.** Real keystrokes never reach the server.
- **There is no unmask.** No privileged reveal, no support escalation, no "record raw for debugging"
  flag. That is the product's safety property, not a missing feature. One leaked frame is permanent
  — it's in a chunk, in a backup, and possibly in a replay someone already watched.
- **Input values are always masked**, every type including `hidden` and `file` (storefronts stash
  customer ids and emails in hidden inputs). The replacement preserves **length only**, so the
  replay shows a field filling up without the content.
- **Keystrokes are counted, not read.** One `*` per press. Navigational and modifier keys (`Tab`,
  `Enter`, `Escape`, `Backspace`, arrows) are recorded by name because they carry interaction
  meaning, not content.
- **The recorder respects the shopper's signals**: Global Privacy Control and DNT stop it before it
  loads anything.

`data-wisp-mask="all_text"` is available for merchants who want the strictest posture — it masks all
text, not just inputs, at some cost to replay legibility. Offer it when the storefront shows
personal data as rendered text (order confirmations, account pages).

If the merchant asks for a specific recording to be deleted, say plainly that retention/deletion
tooling is not built yet and it is a manual job against the Wisp database.

## Local ≠ prod, twice over

A working localhost droplet proves nothing about production. The two differ in **both** the database
(PGlite locally vs Neon in prod) **and** the auth path (the `/integrations/wisp` → `GET /api/me`
handshake only happens inside a real Fluid admin iframe). Anything you verify locally has to be
re-verified against the live company before you call the install done.

Related: `db_query` on a Mist project **defaults to production**. When you're checking for a session
row that's what you want — but pass `side` deliberately rather than relying on the default, and
never assume a query you ran locally reflects prod.
