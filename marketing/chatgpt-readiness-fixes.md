---
name: ChatGPT readiness fixes
description: Get the store ready to claim in ChatGPT — read Fluid's readiness report, turn every gap into a fix list ranked by the sales it blocks, check barcodes, link the missing policies, and apply only the fixes you approve.
icon: bot
---

# Goal

ChatGPT's Business Hub lets a verified business add its product feed and publish an agent that answers shoppers and sends them to buy. Fluid already serves {{company.name}}'s feed from the storefront and reports what the feed and the store's policies are missing. This skill turns that report into a short, ranked fix list, fixes what can safely be fixed from data the store already has, and re-checks at the end. Today is {{today}}.

# Rules

- **Read first, write only with approval.** The only write is marking an existing agreement as the store's terms, privacy or refund policy, one `fluid_api` call gated by `human_in_the_loop` each. A price conversion runs only through the `fluid` CLI with a rate the user reviewed. Everything else is a list for the user's team.
- **Never invent data.** Never make up a barcode, a price, a description or a policy. A missing value is the user's to supply.
- **At most 3 approval cards per turn**, then END your turn and wait for the clicks.
- **Talk in plain words.** Name products, variants and policies. Don't show ids, paths, codes or JSON in the chat.
- Fluid builds the feed from the catalog. Fix the catalog, never the feed file.
- Whether OpenAI accepts or lists the business is decided in ChatGPT's Business Hub, not in Fluid. Never say the store is "approved" or "listed".

# Steps

## 1. Read the report

`fluid_api("/api/company/v2026-10/chatgpt/readiness", "GET")`. Keep `ready`, `gaps`, `feed_url`, `row_count`, `rows_without_gtin`, `omitted_count`, `omissions` (the first 100), `policies` and `custom_domain`.

If it answers 403, say in one line that this report needs someone who can view both products and company settings, and stop.

## 2. Blockers first

These `gaps` stop a claim. If any is present, lead with it and say what fixes it:

- `storefront_disabled`: the storefront is turned off, so there is no feed to read. Turning it on is a company setting the owner decides.
- `billing_suspended`: the storefront is paused for billing. Send the user to Fluid billing.
- `not_sold_in_us`: ChatGPT's feed is US-only today. Selling in the US is a country launch; offer the `compliance/open-a-country` skill and stop here.
- `empty_feed`: no product can go in the feed. Step 3 explains why.

## 3. Products left out of the feed

Rank what's left out by the sales it blocks.

1. `fluid_api("/api/v202604/analytics/dashboard/best_sellers", "GET")` for the store's best sellers. If it answers anything but 200, rank by product title instead and say so.
2. Group `omissions` by product. For each product: its title, how many variants are left out, the reason, and for `missing_fields` which fields.
3. Turn each reason into a fix:
   - **No US price** (`no_us_price`): the variant has no active US price. If the store sells mostly in another country, offer to preview a conversion with `run_cli` `fluid countries prices US --from-country <that country>`; without `--overwrite` it fills only the US prices that are missing. Write only if the user gives a reviewed rate (`--rate <rate> --write --yes`), and never pass `--overwrite`. Never set prices with `fluid_api`. Otherwise list them for the team.
   - **Missing fields**: `title` or `description` empty, so the product needs copy; `image_url` empty, so it needs an image; `price` empty, so no US price; `url` empty, so the product isn't on the storefront. List these for the team, product by product. For copy, the `marketing/brand-agent-brief` skill shows what agents ask about.
4. If `omitted_count` is more than 100, say only the first 100 are listed and that the report will show the rest once these are fixed.

## 4. Barcodes

`rows_without_gtin` counts feed rows with no barcode that passes the GS1 check digit. ChatGPT can still list them, but a valid barcode helps it match the product.

1. Read the live catalog: `fluid_api("/api/v202604/products?page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`. For every variant keep the product title, variant title, `sku` and `bar_code`.
2. Check each `bar_code` yourself: digits only, 8, 12, 13 or 14 long, and the last digit equal to the GS1 check digit (from the right, excluding the check digit, weight the digits 3, 1, 3, 1…, sum, and the check digit is `(10 - sum mod 10) mod 10`).
3. Report three groups: no barcode, a barcode that fails the check (often a typo or an internal code), and valid. If your count of the first two differs from `rows_without_gtin`, say so; the report counts only variants in the feed.
4. Ask the user for the real barcodes from their supplier or GS1 account, as a pasted list of SKU and barcode, and check each one the same way. Give back a clean table (product, variant, SKU, barcode, valid or not) for the catalog team to enter on each variant in Fluid admin. Don't save barcodes through the API: a variant update rewrites the variant's country prices along with it.

## 5. Policies

`policies` shows the storefront page for the US terms of service, privacy policy and refund policy, or null when there is none. ChatGPT's agent quotes these to shoppers.

For each null policy:

1. `fluid_api("/api/agreements", "GET")`. Look for an active agreement that covers the US (its `company_country_ids` include the US country) and whose title or text is plainly that policy, with no `kind` set.
2. If you find one, show its title and offer to link it. Call `fluid_api("/api/agreements/<id>", "PUT", { "agreement": { "kind": "terms_of_service" | "privacy_policy" | "refund_policy" } })` without `approval_id`, propose it with `human_in_the_loop` ("Mark <title> as the store's <policy>"), END YOUR TURN, then repeat with `approval_id`.
3. If none exists, say the store needs that policy written and published for the US, and that the policy wording belongs to the user's legal or compliance owner. Never draft one as if it were final.

## 6. Domain

If `custom_domain` is false, say that OpenAI verifies a business through a DNS record on its own domain, so the store needs a custom domain first. `fluid_api("/api/domains", "GET")` shows the domains the store has.

## 7. Report and re-check

1. Lead with one line: ready to claim or not, and the single most important fix.
2. Then a table of fixes, most valuable first: what to fix, which products, who fixes it (this skill, the catalog team, legal, the owner), and whether it blocks the claim or only improves answers.
3. After any fix you applied, call step 1 again and show what changed: rows in the feed, variants left out, rows without a barcode, policies linked.
4. End with the feed address so the user can paste it into ChatGPT's Business Hub, and remind them that claiming the business and publishing the agent happen there.

# What this skill does not do

It does not set prices, write product copy, publish policies or change the feed directly. It does not claim the business in ChatGPT, verify the domain, or publish ChatGPT's agent.
