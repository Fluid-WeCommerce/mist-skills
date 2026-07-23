---
name: Dead link & 404 sweep
description: Crawl the live sitemap and fetch every URL to find broken links before customers do, ranked by how prominent the page is.
icon: link-2
---

# Goal

Find every dead or broken link on `{{company.name}}`'s live storefront before it costs a sale, starting from the site's own sitemap rather than guessing at pages.

# Steps

1. Call `fluid_api("/api/v2025-06/sitemap", "GET")` to get every public URL the storefront declares (`urls[]`, each with `url` and `active`). This is the authoritative crawl seed — don't invent URLs.
2. For each `active: true` URL, call `web_fetch(url)` and record the resulting status. Treat anything that isn't a normal 200 page response (404, 500, a redirect loop, or an empty/error body) as a finding. Batch this in reasonable chunks so a single slow page doesn't stall the whole sweep.
3. For the homepage and any category/collection pages found, also note internal links reachable from `crawl(url)`'s extracted content — links that don't appear anywhere in the sitemap but do appear in on-page navigation are worth a second pass, since they're customer-visible but not sitemap-tracked.
4. Cross-reference broken URLs against `fluid_api("/api/v202506/pages?limit=100", "GET")` — if a broken URL maps to a Page that's `active: false` or `publish: false`, that's an intentional unpublish, not a bug; say so and drop it from the findings instead of flagging it as broken.
5. Rank genuine breaks by how prominent the URL looks (homepage and top-level category/collection pages first, deep individual product/blog pages last) — a broken category landing page is a bigger deal than one broken post.
6. Render a table: URL, status/error observed, prominence tier, and whether it maps to a known unpublished Page (context, not a fix). End with a **Decision**: the single highest-prominence break to fix first and, if it's a redirect or unpublish that should have redirected instead of 404ing, say so explicitly.
7. If the sitemap itself is empty or unreachable, say that plainly — this sweep depends on it and can't fall back to guessing URLs.
