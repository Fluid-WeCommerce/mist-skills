---
name: Storefront Search & Speed Scan
description: Scan the products and categories shoppers will land on this sale season for hidden search and AI-discovery problems (pages blocked from search, missing or inherited titles and descriptions, default share images, slow or low-scoring pages) and rank the fixes by traffic at stake.
icon: search-check
---

# Goal

Before a sale, find the pages at {{company.name}} that search engines and AI shopping assistants will read badly, and say which to fix first. A page that is set to noindex, shows the company-wide default description, or loads slowly on mobile loses the traffic a sale is meant to bring. Read-only: this skill changes nothing in Fluid. Fixes are made by the user, or by running **Suggested Changes** for the Lighthouse findings.

Do not quote traffic, ranking or conversion benchmarks. Report only what the store's own data shows. Today is {{today}}.

# Steps

1. **Pick the pages to scan.**
   - `fluid_api("/api/v202604/company/products?filter[status]=active&page[limit]=100", "GET")` - active products only. Follow `meta.pagination.next_cursor` as `page[cursor]` until you have up to 100 products or the end.
   - `fluid_api("/api/v202604/company/categories?filter[status]=published&page[limit]=100", "GET")` - published categories, same pagination.
   - Rank the pages by what the shopper sees first: categories, then products. If the user names a sale collection or a list of products, scan those first and say so.
2. **Read the search fields.** Every product and category carries a `seo` object with `title`, `description`, `image_url` and `indexable`. The authenticated surface also returns `seo.id` and `seo.stored` (what the merchant set, before any fallback). For each page, flag:
   - **Blocked:** `seo.indexable` is false. Say why when the response shows it (the page's own setting, or the company-wide flag). A blocked page is a P0 if it is a category or an active, in-stock product.
   - **Inherited, not written:** `seo.stored` has no title or no description, so the page shows the product name or the company default. Flag any page whose resolved description is the company default text, since two pages with the same description compete with each other.
   - **Default share image:** `seo.stored` has no image, so link previews on social and in chat show a generic image.
   - **Too long or too short:** a resolved title over about 60 characters or under 15; a resolved description over about 160 or under 50. State the count.
   - **Duplicates:** two or more pages with the same resolved title or description. List them together.
3. **Read the speed and Lighthouse scores for the top 25 pages.** For each, `fluid_api("/api/v202604/company/products/{id}/lighthouse", "GET")` or `/api/v202604/company/categories/{id}/lighthouse`. A 202 response means no scan existed and one was queued: do not wait, list the page as "scan queued" and move on. For each result record `scanned_at`, `core_metrics.performance_score`, `core_metrics.largest_contentful_paint_rating`, `category_scores` (including `seo` when present) and the first three `optimization_opportunities` by `savings_ms`. A scan older than 14 days is stale: say so beside its score rather than treating it as current. Do not call `POST .../lighthouse`; queueing scans is the user's call.
4. **Check the agent-facing files.** Fetch `https://{{company.subdomain}}.fluid.app/llms.txt` and `/.well-known/ucp` (use the store's own domain instead if the user gives one). Record whether each returns real content (not the homepage HTML) and, for llms.txt, whether it names the sale categories. If a fetch fails, say so and carry on.
5. **Rank.** Score each finding by who loses: blocked categories first, then blocked products, then duplicate or default descriptions on categories, then poor mobile speed on the first ten pages, then the rest. Count pages per finding type. Never invent a number the data does not give.
6. **Output** these headings, in this order:
   - **Fix first** - at most 10 rows: page, problem, the field or score that shows it, what to change.
   - **Counts** - pages scanned, blocked, missing title, missing description, default image, duplicates, stale or missing scans.
   - **Speed** - table of the 10 slowest scanned pages with score, largest-paint rating and top opportunity.
   - **Agent files** - llms.txt and UCP profile: present, missing, or wrong.
   - **Not checked** - what this scan cannot see (live search rankings, AI-assistant mentions, pages outside the first 100 of each kind).
   Put the "Fix first" table at the top of the chat reply. End by asking whether the user wants the metadata fixes drafted as a list to paste into the admin, or the Lighthouse fixes taken through **Suggested Changes**. Write nothing to Fluid until they say which.

# What this skill does not do

It does not edit titles, descriptions, images or indexing settings, queue Lighthouse scans, or measure rankings and AI-assistant visibility. It reads the store's own fields; whether a search engine or assistant surfaces a page is outside Fluid's data.
