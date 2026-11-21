---
name: Retire a product
description: Discontinue a product without stranding anyone — find every autoship, enrollment kit, bundle, plan and collection that holds it, move autoship customers to a replacement, swap it out of kits, and archive it last, applying only what you approve.
icon: archive
---

# Goal

Retire one product from {{company.name}}'s catalog as of {{today}} without leaving anything pointing at it. Archiving takes a product off the storefront, but it does not touch the autoships, enrollment kits, bundles or subscription plans that still hold it: those customers keep renewing on a product that is gone, and new reps keep buying a kit with a hole in it. This skill maps everything that holds the product, agrees a replacement and a plan with the user, makes the changes in the safe order, and archives the product **last**.

# Rules

- **Read first, write only with approval.** Steps 1 to 4 change nothing. Each write stage in step 5 starts with one `human_in_the_loop` card for that stage, and you END YOUR TURN until the user clicks Approve.
- **Order matters.** Autoships first, then kits, then subscription plans, then archive. Never archive while an active or paused autoship or a kit still holds the product, unless the user explicitly chose to end those autoships instead.
- **Don't message customers or reps.** This skill changes records only. Hand the user the list of customers moved and a short draft notice; they send it their own way.
- **Talk in plain words.** Name products, kits and markets. Refer to customers by first name and subscription number. No ids, paths or JSON in the chat.
- If a write is refused because the user turned on *Ask before making changes*, propose the exact title it returns with `human_in_the_loop`, END YOUR TURN, then retry the same call with `approval_id`. Never retry a refused write another way.

# Steps

## 1. Pick the product and its replacement

1. Ask the user which product to retire (use a `steps` panel when there are several close matches). Find it with `fluid_api("/api/v202604/company/products?filter[status]=active&sort=title", "GET")`, following the pagination, then read it with `fluid_api("/api/v202604/company/products/<id>", "GET")`. Keep its title, variants (id, SKU, options), price in each market, `bundle` flag and whether it has subscription plans.
2. Ask what replaces it: a named product (and, if it has several, which variant matches each old variant), or **no replacement**. Read the replacement the same way and check that it is active, priced in every market where the old product has autoship customers, and has subscription plans when autoships will move to it. List any gap; a gap in a market means those customers can't move there yet.

## 2. Map everything that holds the product

1. **Autoships.** `fluid_api("/api/subscriptions?search=<product title>&per_page=100&page=1", "GET")`, then the next `page` until the pagination in `meta` shows no next page (`next_page` empty, or `page` reaching `total_pages`). The search also matches customer and plan names, so keep only subscriptions whose `variant.product` is this product and whose `status` is `active`, `paused`, `past_due` or `pending`. For each keep subscription number and token, customer first name, status, variant, quantity, `price`, `next_bill_date`, currency and plan name.
2. **Enrollment kits.** `fluid_api("/api/v202604/company/enrollment-packs", "GET")`, then `fluid_api("/api/v202604/company/enrollment-packs/<id>", "GET")` for each. A kit holds the product when any row in `member_enrollable_products` or `subscription_enrollable_products` has its `product_id`. Keep the kit title, status, which list the row is in, and the row `id`.
3. **Bundles.** `fluid_api("/api/v202604/company/products?filter[bundle]=true&filter[status]=active", "GET")`, then read each bundle and look for the product in its `bundle_groups` items.
4. **Subscription plans.** `fluid_api("/api/subscription_plans", "GET")` and keep the plans the product is attached to (the product read from step 1 lists them).
5. **Collections.** `fluid_api("/api/v202604/company/collections", "GET")`, then `/api/v202604/company/collections/<id>/products` for each, and note the collections that list it.
6. **Stock and recent demand.** `fluid_api("/api/inventory_levels?variant_ids=<comma-separated variant ids>", "GET")` for available units per warehouse. For the last 90 days, `fluid_api("/api/v202506/orders?status=completed&start_date=<90 days before {{today}}>&end_date={{today}}&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`, and `fluid_api("/api/v202506/orders/<id>", "GET")` for line items when the list doesn't carry them. Count the product's units and buyers. Stop reading after 2,000 orders and say the figure is a sample.

## 3. Work out the price change for each autoship

For each autoship that will move, compare its current `price` with the replacement variant's price in the subscription's currency. Group the customers as **same or lower price**, **higher price** (show the difference) and **can't move** (no replacement price in their market, or no replacement at all).

## 4. Present the plan

Lead with one line: the product, how many autoship customers, kits, bundles and plans hold it, and the stock left. Then:

| Area | What holds it | Proposed change |
|---|---|---|

with one row per area (autoships by price group, each kit, each bundle, each plan, collections, stock). Then a sell-down estimate: units left divided by the last 90 days' average daily units, in days. Recommend a stop-selling date after the last autoship move and, when there is stock, after the sell-down.

Ask the user to confirm the replacement, what to do with **higher price** customers (move them, or leave them for the user to contact first) and with **can't move** customers (leave them for the user, or cancel those autoships), and whether to archive today or on the stop-selling date.

## 5. Apply, stage by stage

For each stage, propose one `human_in_the_loop` card (source `"agent"`, a title such as `Move 14 autoships from Travel Lotion to Body Lotion`, suggestion_id `retire-product:<product id>:<stage>`, and the list in plain words as `description`). END YOUR TURN. After Approve, run the stage, then read back.

1. **Move autoships.** For each approved subscription: `fluid_api("/api/subscriptions/<token>", "PATCH", { "subscription": { "variant_id": <replacement variant id> } })`. Read it back with `fluid_api("/api/subscriptions/<token>", "GET")` and confirm the variant, `price` and `next_bill_date`. A refusal returns its reason (for example the replacement isn't sold in that market): leave that subscription as it is and list it. Only if the user chose to end the **can't move** autoships: `fluid_api("/api/subscriptions/<token>/cancel", "POST")` for each, as its own approved stage.
2. **Swap kits.** For each approved kit: `fluid_api("/api/v202604/company/enrollment-packs/<id>", "PATCH", { "enrollment_pack": { "<member_enrollable_products_attributes or subscription_enrollable_products_attributes>": [ { "id": <row id>, "_destroy": true }, { "variant_id": <replacement variant id> } ] } })`, leaving out the second item when there is no replacement. Read the kit back.
3. **Plans.** For each plan: `fluid_api("/api/subscription_plans/<plan id>/remove_product", "POST", { "product_id": <product id> })`.
4. **Bundles and collections.** Bundle contents can't be changed safely from here. List each bundle that still holds the product, with the suggested swap, for the user to change in the admin. Collections drop the product on their own once it is archived.
5. **Archive.** Re-run step 2.1. Archive only when no active, paused, past-due or pending autoship and no kit still holds the product, or the user explicitly accepted the ones left: `fluid_api("/api/v202604/company/products/<id>", "PATCH", { "product": { "status": "archived" } })`, then read it back and confirm `status`. If the user picked a later stop-selling date, don't archive: tell them the date and that running this skill again then will finish the job.

## 6. Hand over

Finish with:

- What changed: autoships moved (with any price change), autoships left and why, kits swapped, plans updated, and whether the product is archived.
- What the user still has to do: bundles to edit, customers to contact (a CSV-ready list of subscription number, first name, old and new product, old and new price, next bill date), and a three-sentence draft notice to those customers in plain words, with no health or results claims.
- A reminder to tell the field before the stop-selling date, so no rep keeps sharing a product that is about to go.
