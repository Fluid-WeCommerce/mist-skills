---
name: Brand Social Content Import
description: >-
  Import a company's OWN social video content (YouTube + TikTok) into Fluid.
  Finds the company's official accounts, registers them in the Fluid social-media
  settings, then pulls their videos into the DAM + Media library. This is the
  brand's own content — NOT user-generated content about the brand.
icon: video
---

# Brand Social Content Import

Pull a company's **own** published social video content into Fluid: find their official
YouTube + TikTok accounts, register those handles in Fluid's social-media settings, and
rip each account's videos into the DAM + Media library.

> **This is NOT `marketing/ugc-discovery`.** UGC discovery searches all of TikTok
> for *other people's* content about the brand and lets the user pick a handful. THIS skill
> ingests the *brand's own* channel content — the company is the creator. Tag accordingly
> (`brand-content`, never `ugc`) so the two libraries stay distinct.

The active Fluid company is already selected in Mist. All Fluid API calls go through
`fluid_api(path, method, body)` (token injected). Never ask for credentials.

## Step 1 — Resolve the company's official accounts

Do NOT guess handles — a wrong account imports someone else's videos. Resolve in order:

1. **From context.** If invoked by the onboarding workflow, the `gather-context` step
   already extracted the site's social links (footer/header) — use the TikTok + YouTube
   URLs it found. The `onboarding/onboarding-prefill` skill captures these.
2. **From the site.** Otherwise `crawl` the company's homepage and read the social links in
   the header/footer. Official accounts are linked from the brand's own site — trust those
   over search.
3. **Confirm ambiguous ones.** Only if a platform has no link on the site AND you must find
   it: for TikTok, `social_search` (platform `tiktok`) mode `user` / `keyword` on the brand name and match on a
   verified handle + follower count + bio that clearly belongs to the brand. For YouTube,
   resolve the channel from the brand's linked handle. If you can't confirm an account is
   the brand's own with high confidence, SKIP it and report — do not import a maybe.

Record, per platform: canonical account URL, handle, and (YouTube) channel id.

## Step 2 — Register accounts in Fluid social-media settings

`PATCH /api/settings/social_media` with the confirmed handles/URLs (fields include
`facebook`, `instagram`, `tiktok`, `twitter`, `linkedin`; include `youtube` if the schema
supports it — GET the endpoint first to see the current shape, and only set fields you
confirmed). GET-before-PATCH; don't clobber an existing correct value with a worse one.
Report which fields you set.

## Step 3 — Enumerate each account's videos

- **TikTok:** `social_search` platform `tiktok` mode `user` with the handle → the account's video list (id,
  canonical URL, caption, stats, created_at). Paginate with the returned `cursor` up to a
  sensible `count` (default the most recent 20–30; the caller may raise it). Dedupe by `id`.
- **YouTube:** fetch the channel's uploads feed
  `https://www.youtube.com/feeds/videos.xml?channel_id=<id>` (via `crawl`/web fetch) → the
  most recent video URLs. For the full back-catalog beyond the ~15 the RSS returns, page the
  channel's videos listing. Collect canonical `watch?v=` URLs.

State the count found per platform and how many you'll import (log any cap — no silent
truncation).

## Step 4 — Rip into DAM + Media (idempotent)

For each video URL, call **`video_ripper`** with tags `brand-content,<platform>,<brand>`
(lowercased brand). `video_ripper` downloads and uploads to the DAM AND creates a Media
record in one call — do not call `dam_upload` separately. Caption/title/uploader are pulled
from the source automatically.

- **Idempotent:** before ripping, check whether a Media/DAM asset for that source already
  exists (match on source URL/caption or a stable tag) and skip it — re-running must not
  duplicate. GET the Media library and compare.
- **Never abort on one failure.** A private/deleted/region-locked/too-large video: note it
  and continue. For oversized clips, `compress_media` is not applicable to a remote rip —
  just skip and report.
- Run rips in parallel (one `video_ripper` call per video) where the platform allows, but
  respect failures individually.

Report every created DAM/Media URL as rips complete.

## Step 5 — Report

Summarize: accounts registered (with URLs), videos found per platform, ripped
(DAM/Media links), skipped (with reason), failed. If an account couldn't be confirmed as
the brand's own, say so explicitly rather than importing a guess.

## Rules

- **Brand's own content only.** If you're searching for *other people's* videos about the
  brand, you're in the wrong skill — that's `marketing/ugc-discovery`.
- Tag every asset `brand-content` (+ platform + brand). Never tag these `ugc`.
- Confirm an account belongs to the brand before importing from it; a wrong account is worse
  than a missing one.
- Idempotent: skip already-imported videos; re-runs must not duplicate.
- Best-effort: a company with no discoverable official social presence is a valid outcome —
  report it, don't invent accounts.
