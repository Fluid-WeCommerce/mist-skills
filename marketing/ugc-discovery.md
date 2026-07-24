---
name: UGC Discovery
description: Find the 20-30 most engaging, FTC/FDA-compliant UGC posts about a brand or product across TikTok, Instagram, YouTube, and Pinterest, let the user pick, and pull the picks into the DAM.
icon: video
category: marketing
---

# UGC Discovery

Find the best user-generated content about a brand or product for {{company.name}} across TikTok, Instagram, YouTube, and (optionally) Pinterest, screen it for engagement and FTC/FDA compliance, present a ranked shortlist, and import only the posts the user picks into the DAM.

Today is {{today}} — use it for the recency bonus weighting below.

## 0. Scope the search (ask FIRST, wait for the answer)

Before running ANY searches, ask the user (as ONE short question):

1. **Brand search** or **specific product search**? (ask which product if they haven't named it)
2. **Which platforms?** Default to **TikTok + Instagram + YouTube**. Offer Pinterest as an opt-in — pins are mostly images that link out, useful for visual/inspiration boards but they carry no engagement stats and usually can't be ripped as video.

Also ask for the brand/product name if they haven't given one, and let them know up front that **this can take some time — every candidate gets reviewed individually for compliance** before the shortlist is presented. Ask this as one short question, then **END YOUR TURN and wait for their answer — do not search, enrich, or run any tool until they've responded.** If the user already made the scope unambiguous in their request (e.g. "find TikTok and IG UGC about our collagen gummies"), confirm it in one line (including the heads-up that the review takes a while) and proceed without re-asking.

## 1. Search

Build 4-6 query variants covering how real people talk about the target.

For a **brand search**:

- the brand name alone
- brand + flagship product name
- brand + "review"
- the brand hashtag (mode `hashtag` — TikTok and YouTube only)
- 1-2 common misspellings or spaced/joined variants

For a **specific product search**:

- product name alone, and brand + product name
- product + "review" / "before and after"
- the product hashtag if one exists (mode `hashtag` — TikTok and YouTube only)
- 1-2 common nicknames, misspellings, or spaced/joined variants of the product name

Run each variant through `social_search` on **each selected platform** with `count: 30`:

- `platform: "tiktok"` — `mode: "keyword"` (or `"hashtag"` for the hashtag variant)
- `platform: "instagram"` — `mode: "keyword"` only (no hashtag mode; search the tag text as a keyword instead)
- `platform: "youtube"` — `mode: "keyword"` (or `"hashtag"`); results include Shorts
- `platform: "pinterest"` — `mode: "keyword"` only, and only if the user opted in

If any response has `degraded: true`, tell the user which source was actually used (`source_used`) before continuing. Merge all results and dedupe by `id` **within each platform** (ids are only unique per platform) — every platform returns duplicates across queries.

## 2. Enrich

Platform stats differ at search time — normalize before ranking:

- **TikTok / Instagram** — full engagement stats arrive with search results. Compute `ER = (likes + comments + shares) / views` (shares are 0 on Instagram; that's fine). Take the top ~50 by ER across both platforms.
- **YouTube** — search results carry views only (likes/comments come back 0). Take the top ~20 by views, then let enrichment fill in real engagement before ranking.
- **Pinterest** — pins carry no engagement stats at all. Skip enrichment and ranking math entirely: judge pins on relevance and visual fit from title/description/thumbnail, cap at ~10, and present them in their own section.

For each surviving TikTok / Instagram / YouTube candidate, call the `video_metadata` tool (one URL per call) to confirm stats and pull the caption + transcript — it uses the app's bundled yt-dlp with no download, so it's fast. Recompute ER from the enriched numbers where they're more complete (this is what makes YouTube rankable).

If an individual post fails (private, deleted, region-locked), **skip it and continue — never abort the run**. Posts without enrichment keep their `social_search` stats and are judged on caption alone.

## 3. Score and gate

Prefilter — drop posts failing any of (Pinterest exempt — it goes through the relevance-only path above):

- ER < 3% (TikTok / Instagram; apply to YouTube only when enrichment produced real like/comment counts — never gate YouTube on the zeros search returned)
- more than 2 posts from the same creator (keep their 2 best)
- videos shorter than 8 seconds or longer than 3 minutes (YouTube long-form up to 10 minutes is fine when the transcript is on-topic)

Views and age are NOT filters — a small creator's perfect-fit post or an evergreen banger from two years ago can still be great UGC. Apply both as **bonus weights** when ranking instead: higher view counts boost a post's rank, and recency adds a meaningful boost inside 90 days, a small one inside 12 months, and no boost (no penalty) beyond that.

Then judge each survivor on relevance to the brand, message quality, and compliance.

**DISQUALIFY** (exclude, with reason) any post whose caption or transcript contains:

- disease claims — cures, treats, prevents, or heals a named condition or symptom
- income or earnings claims
- guarantees, or "no side effects" claims
- "doctor recommended" (or similar authority claims) without substantiation

**Mark "review"** (include, flagged) for structure/function claims — "supports", "helps maintain", "promotes" and similar. These are often permissible but need a human look.

## 4. Present

Show a numbered markdown list, best first, aiming for 20-30 entries across the selected platforms (group by platform, video platforms first). **The post URL is the MOST IMPORTANT part of each entry — the reviewer can't evaluate a post they can't open.** Show the full URL plainly on its own line under each entry (never bury it behind link text or omit it):

```
N. [tiktok] @handle (Xk followers) — Xk views / X.X% ER — "one-line hook from the caption" — compliance: ok
   https://www.tiktok.com/@handle/video/1234567890123456789
N. [youtube] Channel Name — Xk views / X.X% ER — "one-line hook" — compliance: review: structure/function claim ("supports immunity")
   https://www.youtube.com/watch?v=abcdefghijk
N. [pinterest] @pinner — relevance pick (no stats) — "pin title"
   https://www.pinterest.com/pin/1234567890/
```

Add an **Excluded** section listing disqualified posts with a one-line reason each, also with their URLs (e.g. `@handle — income claim in caption — https://…`) so the reviewer can spot-check the disqualification.

Then ask which numbers to add to the DAM and **END YOUR TURN immediately** — the question must be the very last thing you output. Finish ALL searching, enrichment, and scoring BEFORE presenting the list; never run a tool call after asking (the user's answer stays queued until your turn ends). **Do NOT rip anything yet** — wait for the user's selection.

## 5. Import on selection

For each picked video (TikTok / Instagram / YouTube), call `video_ripper` with the post URL and tags `ugc,<platform>,<brand>` (lowercased brand, e.g. `ugc,tiktok,acme`). Report the DAM/Media links as each rip completes. For picked Pinterest pins, rip the pin's image into the DAM via `dam_upload` from its thumbnail/original URL with the same tag shape (`ugc,pinterest,<brand>`), and include the pin's outbound `link` in the DAM description for attribution. If an individual import fails, note it and continue with the rest; summarize successes and failures at the end.
