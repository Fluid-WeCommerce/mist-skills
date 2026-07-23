---
name: UGC product gap analysis
description: Cross-reference best-selling products against the existing media/UGC library to find best-sellers with no social proof — the highest-leverage gaps to fill next.
icon: puzzle
---

# Goal

Cross-reference {{company.name}}'s best-selling products against its existing shareable media library to find best-sellers with no social proof — a prioritized gap list, instead of running a blind content search for everything.

# Steps

1. Pull the last 30 days of completed orders: `fluid_api("/api/v202506/orders?status=completed&start_date={{thirty_days_ago}}&end_date={{today}}&limit=100", "GET")`, following `meta.pagination.next_cursor` until exhausted. Tally revenue (`amount`, falling back to `amount_in_base`) and unit count by `first_item.title` — the best product signal available directly on the order payload — to build a top-15 best-sellers list.
2. Pull the media library: `fluid_api("/api/users/v2025-06/media?limit=100", "GET")`, paginating fully, filtered to `active: true` and `kind` in `video`/`image`. Build a lowercased keyword index from each item's `label`/`description` (strip common filler words).
3. For each of the top-15 best-sellers, check whether any media item's indexed text contains the product name (fuzzy-match: strip trailing sizes/flavors/units like "55ml", "30-count" before comparing). Mark **COVERED** (with matching asset count) or **GAP**.
4. Render a table: product, 30-day revenue, unit count, coverage status.
5. For the top 5 GAP products by revenue, list them explicitly and ask the user which ones to kick off UGC discovery for — do NOT auto-run anything. If they pick one or more, hand off with `run_skill("marketing/tiktok-ugc-discovery")` scoped to that specific product (the discovery skill will ask its own scoping question — you don't need to pre-answer it).
6. Close with the prioritized gap list ordered by revenue at stake — the products losing the most social-proof-driven conversion upside right now.

This is a fuzzy keyword match against Fluid's own media library, not a live scrape of storefront product pages — say so if the user expects page-level coverage detection.
