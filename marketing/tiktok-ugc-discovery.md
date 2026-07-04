---
name: TikTok UGC Discovery
description: Find the 20-30 most engaging, FTC/FDA-compliant TikTok UGC videos about a brand or product, let the user pick, and pull the picks into the DAM.
icon: video
category: marketing
---

# TikTok UGC Discovery

Find the best user-generated TikTok content about a brand or product for {{company.name}}, screen it for engagement and FTC/FDA compliance, present a ranked shortlist, and import only the videos the user picks into the DAM.

Ask the user for the brand/product name if they haven't given one. Today is {{today}} — use it for the recency bonus weighting below.

## 1. Search

Build 4-6 query variants covering how real people talk about the brand:

- the brand name alone
- brand + product name
- brand + "review"
- the brand hashtag (mode `hashtag`)
- 1-2 common misspellings or spaced/joined variants

Call `tiktok_search` for each variant with `mode: "keyword"` (or `"hashtag"` for the hashtag variant) and `count: 30`. If any response has `degraded: true`, tell the user which source was actually used (`source_used`) before continuing. Merge all results and dedupe by `id` — TikTok returns duplicates across queries.

## 2. Enrich

Compute engagement rate for every unique video: `ER = (likes + comments + shares) / views`. Take the top ~50 by ER.

For each of those, call the `video_metadata` tool (one URL per call) to confirm stats and pull the caption + transcript — it uses the app's bundled yt-dlp with no download, so it's fast.

If an individual video fails (private, deleted, region-locked), **skip that video and continue — never abort the run**. Videos without enrichment keep their `tiktok_search` stats and are judged on caption alone.

## 3. Score and gate

Prefilter — drop videos failing any of:

- ER < 3%
- more than 2 videos from the same creator (keep their 2 best)
- shorter than 8 seconds or longer than 3 minutes

Views and age are NOT filters — a small creator's perfect-fit video or an evergreen banger from two years ago can still be great UGC. Apply both as **bonus weights** when ranking instead: higher view counts boost a video's rank, and recency adds a meaningful boost inside 90 days, a small one inside 12 months, and no boost (no penalty) beyond that.

Then judge each survivor on relevance to the brand, message quality, and compliance.

**DISQUALIFY** (exclude, with reason) any video whose caption or transcript contains:

- disease claims — cures, treats, prevents, or heals a named condition or symptom
- income or earnings claims
- guarantees, or "no side effects" claims
- "doctor recommended" (or similar authority claims) without substantiation
- apparently brand-affiliated creator — discount code, "partner"/"ambassador" language, or affiliate link — **without** #ad or #sponsored in the caption itself

**Mark "review"** (include, flagged) for structure/function claims — "supports", "helps maintain", "promotes" and similar. These are often permissible but need a human look.

## 4. Present

Show a numbered markdown list, best first, aiming for 20-30 entries:

```
N. [thumb](thumbnail_url) — @handle (Xk followers) — Xk views / X.X% ER — "one-line hook from the caption" — compliance: ok
N. [thumb](thumbnail_url) — @handle (Xk followers) — Xk views / X.X% ER — "one-line hook" — compliance: review: structure/function claim ("supports immunity")
```

Add an **Excluded** section listing disqualified videos with a one-line reason each (e.g. `@handle — income claim in caption`).

Then ask which numbers to add to the DAM and **END YOUR TURN immediately** — the question must be the very last thing you output. Finish ALL searching, enrichment, and scoring BEFORE presenting the list; never run a tool call after asking (the user's answer stays queued until your turn ends). **Do NOT rip anything yet** — wait for the user's selection.

## 5. Import on selection

For each picked video, call `video_ripper` with the video URL and tags `ugc,tiktok,<brand>` (lowercased brand). Report the DAM/Media links as each rip completes. If an individual rip fails, note it and continue with the rest; summarize successes and failures at the end.
