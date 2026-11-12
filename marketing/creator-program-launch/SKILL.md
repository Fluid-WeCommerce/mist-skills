---
name: Creator Program Launch
description: Set up a creator program on Fluid for a consumer brand with no affiliate app - the plan, creator sign-up, credited links, a one- or two-level commission ledger built as a Mist app, one proven test order and a launch kit.
icon: megaphone
category: marketing
---

# Goal

Help {{company.name}} launch a creator program that runs on Fluid alone: no affiliate app, no spreadsheet of coupon codes. By the end the brand has an approved plan, a way for creators to join, links that carry credit, a commission ledger that follows the plan, one test order proven end to end, and a kit for the first group of creators.

The method and the best practices are in `references/methodology.md`. The build spec for the ledger is in `references/commission-ledger-spec.md`. If those files are not appended below this body, read them from this skill's folder before Step 1.

**Trigger** when the user wants a creator, ambassador, influencer or referral program, asks how to pay people who share their products, or asks to replace an affiliate app.

Today is {{today}}.

# Ground rules

- Say "creator" to the user, or the word they choose in Step 1. The admin and the API call the same person a **rep**. Use the API's word only in API calls.
- Two levels at most. Level one is the creator who sent the order. Level two is the creator who brought that creator in. If the user asks for a third level, ranks, team volume or a bonus for signing people up, stop and say this skill does not build that plan and they should talk to their Fluid team.
- The ledger records what is owed. It never moves money. Never tell the user a creator was paid unless they marked the payout paid themselves.
- Every write waits for approval through `human_in_the_loop`. One change per approval.
- Do not quote conversion rates, creator benchmarks or "typical" commission rates. Use this store's own numbers from Step 0.
- The creator agreement, the disclosure rules and tax forms are the brand's to settle with its own counsel and accountant. Draft, flag, and leave the decision with them.

# Step 0 - Read the store before asking anything

Run these in parallel and keep the results for later steps.

1. `fluid_api` GET `/api/v2025-06/member-types` - each row in `member_types` carries `rep_eligible`, `system_defined` and `pricing_tier`. Is there already a type with `rep_eligible: true` and `system_defined: false` (a creator or ambassador type)? A store normally starts with three system types: `customer`, `preferred` and `rep`.
2. `fluid_api` GET `/api/v2025-06/fairshare/settings` - the four credit rules, under `fairshare_settings`: `attribution_config`, `order_volume_config`, `enrollment_volume_config`, `orphan_sponsor_config`.
3. `fluid_api` GET `/api/droplet_installations` (read `droplet_name` on each row) and GET `/api/droplets` - is an affiliate-app sync or a commission app already installed? If one is, say so and ask whether this program replaces it or sits beside it before going further.
4. `list_projects` - is there already a Mist app for commissions in this workspace?
5. `fluid_api` GET `/api/company/v2026-10/genealogy/trees` - read `authority` on each tree (a store normally has an `enrollment` tree and a `placement` tree). `unconfigured` means nobody is seated, so a second level cannot read its "who brought whom" from genealogy.
6. `fluid_api` GET `/api/v202604/company/enrollment-packs?page[limit]=15` - any sign-up packs.
7. `fluid_api` GET `/api/v202604/orders?filter[start_date]={{thirty_days_ago}}&page[limit]=100`, following `meta.pagination.next_cursor` as `page[cursor]` - order count (`meta.pagination.total_count`) and average order for the last 30 days, worked out separately for each `currency_code` from each order's `amount`. Check `sale_date` on what comes back; if the date filter was ignored, filter on it yourself.
8. `run_cli` `fluid countries list` - the countries and currencies the store sells in.

Then give the user a four-line read: what is already in place, what is missing, the store's average order, and the countries in play. Do not open the panel until that is on screen.

# Step 1 - The plan questions (one `steps` call)

Open one `steps` panel titled `Creator program for {{company.name}}`, then END YOUR TURN and wait for the answers. In each rate option's description, show what that rate pays on this store's average order, in the store's own currency, so the user is choosing an amount of money.

Where a question offers `other`, the next step is a `text_input` with `show_if` on that answer. Each `show_if` points at one earlier single_select.

1. `creator_word` - single_select: `creators`, `ambassadors`, `partners`, `other`. What the brand calls them.
2. `creator_word_other` - text_input, `show_if: { step_id: "creator_word", equals: "other" }`.
3. `level1_rate` - single_select: three preset rates and `other`. The share of each sale the selling creator earns.
4. `level1_rate_other` - text_input, `show_if: { step_id: "level1_rate", equals: "other" }`.
5. `level2` - single_select, `skippable: false`: id `one_level`, "One level. Creators earn on their own sales." (list it first); id `two_levels`, "Two levels. A creator who brings in another creator also earns a smaller share of that creator's sales."
6. `level2_rate` - text_input, `show_if: { step_id: "level2", equals: "two_levels" }`: the share the inviting creator earns. Reject an answer that is not below the level-one rate and ask again.
7. `earn_on` - single_select: id `all_orders`, every order; id `first_order_only`, a customer's first order only; id `first_order_plus_renewals`, the first order plus subscription renewals for a set number of months.
8. `renewal_months` - text_input, `show_if: { step_id: "earn_on", equals: "first_order_plus_renewals" }`.
9. `hold_days` - text_input: how many days a commission waits before it can be paid. Ask for the store's return window and say the hold should match it.
10. `payout_schedule` - single_select: `monthly` or `twice_monthly`.
11. `payout_minimum` - text_input, `skippable: true`: the smallest balance that pays out.
12. `payout_method` - single_select: id `export`, "We pay creators ourselves from a statement"; id `store_credit`, "Store credit", description "Works only if reward points are on at Settings > Commerce > Points". If the user asks about bank payouts through Fluid, say this skill does not set them up and their Fluid team can tell them what exists for their account.
13. `join_mode` - single_select: `invite_only`, or `open_application` with approval.
14. `own_orders` - single_select: id `no_commission` (list it first), "Creators get a discount on their own orders and no commission on them"; id `earns_commission`.
15. `follower_offer` - single_select: `no_code`, or `promo_code` creators can give followers.

# Step 2 - Play the plan back

Write the plan on one screen in plain words, with one worked example on the store's average order: what the selling creator earns, what the inviting creator earns if there are two levels, when it becomes payable and when it is paid. State what happens on a refund (the commission is reversed), what the base is (product subtotal after discounts, before tax and shipping), and what a creator's own order earns.

Propose it with `human_in_the_loop` (source `agent`, title `Creator program plan: {{company.name}}`, a fresh `suggestion_id` of `creator-plan:{{company.subdomain}}:<short random suffix>`), then end your turn. Nothing is built until the plan is approved. If the user changes an answer, show the whole plan again.

# Step 3 - Set up the store side

One approval per item. Skip anything Step 0 found already in place.

1. **Creator member type.** If no rep-eligible creator type exists, create one through POST `/api/v2025-06/member-types` with body `{ "name": "<singular of creator_word>", "permissions": { "rep_eligible": true } }`. Leave the pricing tier at company default unless the plan gives creators their own price. The write answers 201 even when it ignores a field, and a top-level `rep_eligible` is ignored, so read the list back and confirm the new row shows `rep_eligible: true`. If it does not, PATCH `/api/v2025-06/member-types/<slug>` with the same `permissions` body and read it back again. If the write is refused, give the click path instead: Settings > Commerce > Member Types > Create Member Type. Tell the user first that a member type can be archived later but not deleted.
2. **Credit rules.** Show the four Fair Share answers from Step 0 in plain words and say which one matters for this plan (usually what happens when a shopper touched two creators' links). Changes are made by the user at Settings > Company > Fair Share. Do not change them through the API.
3. **How creators join.** Invite only: the user adds each creator in the admin with the creator member type and a username, then uses Send Invite. An existing customer becomes a creator with PUT `/api/v2025-06/members/:id/member-type` and body `{ "member_type_slug": "<slug>" }`, after approval. Every member already has a `username`, so their own page at `/my/<username>` works as soon as the type changes. Open application: build an application page with `fluid pages create` (it needs `--title`, `--theme`, `--content-file` and the `approval_id` from an approved `page-create:` card), and approve each applicant by changing their member type. Suggest a sign-up pack only if the brand wants a starter kit, and tell the user to confirm with their Fluid team what a pack must contain.
4. **Creator terms.** Draft a one-page agreement from the approved plan: rate, base, hold period, payout schedule and method, refunds, disclosure, product claims, content rights, ending the relationship. Mark it DRAFT, tell the user their counsel reviews it, and leave adding it under Agreements to them.
5. **Follower code.** If chosen, tell the user the limits a promo code supports (total uses, one per customer, minimum spend, country, active dates) and have them create it at Promo Codes.
6. **Share kit.** Check that products and media exist for creators to share. List what is thin.

# Step 4 - Build the commission ledger

If Step 0 found a commission app, read its code and settings first and extend it. Do not build a second one.

Otherwise build a Mist app to `references/commission-ledger-spec.md`. With two levels, set `level2_source` from Step 0: `app` when the genealogy `authority` is `unconfigured`; otherwise ask the user whether the plan follows the tree or the app's own record of who invited whom. Follow `run_skill("mist/scaffold-droplet")` for the scaffolding, the installation-scoped routes and the deploy. Confirm every payload field against a real order from this store before relying on it; the spec says which ones.

# Step 5 - Prove it with one order

Do this on a test gateway. If the only active payment account is real, stop and ask the user how they want to test.

1. Create or pick a test creator. With two levels, also a second test creator who brought in the first, recorded wherever the plan's `level2_source` reads it from. A member cannot be deleted afterwards, so give test creators an obvious name and an address at `example.com`, and tell the user before creating them.
2. Place one order through the test creator's MySite link (`https://{{company.subdomain}}.fluid.app/my/<username>`). Open it first: that route returns a 404 for a username that does not exist, so a typo cannot pass as a credited visit. Do not test with a bare `/<username>` path; it returns the home page for any text at all.
3. Credit lands after the order, not with it. Poll GET `/api/v202506/orders/:id/journey` for up to five minutes and read `order_journey`. **Pass:** `volume_rep` is the test creator. If `attribution_state` and `volume_state` both read `not_applicable`, the visit was never credited: stop and check the link before testing anything else.
4. **Pass:** the ledger holds a level-one line for that order whose amount equals base times `level1_rate`, status `pending`, with the right `available_on`.
5. With two levels, **pass:** a level-two line for the inviting creator at `level2_rate`.
6. Refund the order. **Pass:** reversal lines bring the order's net commission to zero.
7. Send the same order event again. **Pass:** no second line is written.

Report each pass or fail with the order number and the ledger rows. If any check fails, fix it and rerun them all. Do not move on with a failed check.

# Step 6 - Launch kit

1. **First creators.** Rank customers by orders and spend (`run_skill("finance/top-customers")`) and hand the user a shortlist to invite. The user decides who gets asked.
2. **Invite note.** Draft a short invitation in the brand's voice: what they earn, how they get paid, how to share. The user sends it.
3. **One-page guide for creators.** Where their link is, how to share from the app's Share tab, what to say and what not to claim, the disclosure line, when payouts land.
4. **Where the team looks.** Traffic > Reps ranks creators by visitors sent, with orders, revenue and top asset. The ledger shows what is pending, payable and paid.

# Step 7 - Hand back

Finish with a short status the user can forward:

- Live and proven: each piece, with the test order number.
- Waiting on the brand: counsel's review of the terms, tax forms, the payout method.
- Questions for the Fluid team: anything the user asked for that this skill does not set up, such as bank payouts or an outside sales channel.
- The weekly rhythm from `references/methodology.md`.
- Next: more countries (`run_skill("compliance/open-a-country")`).
