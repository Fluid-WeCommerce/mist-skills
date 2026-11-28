---
name: Meta catalog coverage
description: Check which live products are in the store's Meta catalog and which are stuck, rejected or failed, so Muse and Instagram shoppers can find them, then retry the failed publishes you approve.
icon: store
category: marketing
---

# Goal

Meta's personal shopping agent, Muse, starts a product search in Meta's own catalog before it looks anywhere else. A product that is not in {{company.name}}'s Meta catalog, or that Meta has rejected, is invisible to that first search, and to Instagram and Facebook Shops, WhatsApp catalog messages and catalog ads, which all read the same catalog. Fluid syncs selected products into that catalog. This skill compares the live catalog with what Meta holds, lists the gaps ranked by the sales they block, and retries the publishes that failed. Today is {{today}}.

# Rules

- **Read first, write only with approval.** The only write is retrying a failed publish: one `fluid_api` call per listing, gated by `human_in_the_loop`. Never create, edit or delete a product, and never change which products are synced.
- **Never invent a reason.** Quote each listing's `last_error` as it is. If Meta gave no reason, say so.
- **At most 3 approval cards per turn**, then END your turn and wait for the clicks.
- **Talk in plain words.** Name products. Don't show ids, paths or JSON in the chat.
- Whether Meta approves a product is Meta's decision. Never say a product "will" show on a surface. Say what Meta's review status is.
- This reads the connection and listings Fluid stores. It does not call Meta and cannot see impressions, sales or what Muse recommends. Say that under the results.

# Steps

## 1. Connection

`fluid_api("/api/v202506/meta/connection", "GET")`.

- **404:** the store has never connected Meta. Say so, name the fix ("connect the Meta Business account in Fluid's channel settings, or run `fluid channels connect meta --open`") and stop.
- Otherwise read `status`, `catalog_id`, `catalog_name`, `access_token_expires_at` and `last_error`. If `status` is not `connected`, or `last_error` is set, lead with that: nothing below is reliable until the connection is healthy. Quote `last_error`.
- If `catalog_id` is empty, say the connection has no catalog yet and stop.

## 2. Summary counts

`fluid_api("/api/v202506/meta/ads_readiness", "GET")`. Keep `listing_counts` (listings by rolled-up review status). If it answers 404, carry on without it and say the counts come from step 4 only.

## 3. Live products

List the live catalog the way a shopper sees it: `fluid_api("/api/v202604/products?page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]` until there is none. Keep each product's `id`, `title` and `in_stock`. Tell the user the count before moving on. This endpoint returns live products only.

## 4. Meta listings

`fluid_api("/api/v202506/meta/catalog_listings?page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]` until there is none. For each listing keep `product_id`, `product_title`, `status`, `audit_status`, the four `*_review_status` values, `last_synced_at` and `last_error`.

Listings with `status` `deleted` are not in the catalog; treat them as absent.

## 5. Compare

Match listings to live products by product id. Sort every live product into one group:

- **Not in the catalog:** no listing, or a `deleted` one. Say these were never synced or were removed. Whether a product should be synced is the merchant's choice, so do not call these errors.
- **Failed:** `status` is `publish_failed`. Keep `last_error`.
- **Rejected:** `audit_status` is `audit_failed`, or any surface review status says rejected. Say which surface.
- **Paused or frozen:** `status` is `seller_deactivated`, `platform_deactivated` or `frozen`.
- **Waiting:** `status` is `draft` or `pending`, or `audit_status` is `auditing`. Note any that have been waiting for more than 7 days by `last_synced_at` or `last_published_at`; for the rest, say Meta review usually clears on its own.
- **Stale:** `status` is `active` and `last_synced_at` is more than 14 days ago, or null.
- **Live in the catalog:** everything else.

Also list listings whose product is not in the live catalog (a product that was unpublished or discarded after it was synced) as **Orphaned**. Do not retry or touch these.

Rank each group's products so out-of-stock items come last: an in-stock product that Muse cannot find is a lost sale, a sold-out one is not.

## 6. Report

1. Lead with one line: how many live products are live in the catalog out of how many, and the single biggest gap.
2. A table of the products that need attention, 25 rows at most, in this order: Failed, Rejected, Paused or frozen, Not in the catalog, Stale, Waiting. Columns: product, state, the reason in Meta's or Fluid's words, who can fix it (this skill, the catalog team, Meta review, the owner). If there are more rows, say how many were left off.
3. One recommendation grounded in the counts, for example "31 of 340 live products failed to publish, most with a duplicate SKU, so fix the SKUs first."

## 7. Retry failed publishes

Only for products in **Failed**, and only if the user wants to. A retry re-runs the publish and does not fix a bad product: if `last_error` names a data problem (a duplicate SKU, a missing image or price), say the catalog team has to fix that first and offer the retry only for failures that look temporary (a timeout, a rate limit, an expired or refreshed token). If you cannot tell, ask.

For each approved listing, in batches of 3: call `fluid_api("/api/v202506/meta/catalog_listings/<id>/retry", "POST")` without `approval_id`, propose it with `human_in_the_loop` ("Retry the Meta publish for <product title>"), END YOUR TURN, then repeat the call with `approval_id` after the click. After the batch, read the listing back with `fluid_api("/api/v202506/meta/catalog_listings?filter[product_id]=<product id>", "GET")` and show its new `status` and `last_error`. A retry that answers 200 only means the publish ran again; Meta review can still take time.

# What this skill does not do

It does not decide which products belong in the catalog, edit products, fix SKUs, images or prices, appeal a Meta rejection, or measure what Muse or Instagram shoppers do. Say that plainly at the end.
