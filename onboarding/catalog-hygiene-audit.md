---
name: Catalog Hygiene Audit
description: Sweep a product catalog for data-integrity defects — duplicate SKUs, defective live slugs, inconsistent family naming, reused images, unpriced purchasable products — rank them by customer-visible impact, and apply only the fixes the user approves one at a time.
icon: list-checks
---

# Goal

Sweep the company's product catalog for data-integrity defects, rank them by
customer-visible impact, and apply ONLY the fixes the user approves.

This skill is **read-only until approval**. It never deletes a product, never
bulk-writes, and never changes a live public URL without an explicit Approve
click on that specific product.

# Scope note before you start

- Use `fluid_api` (live) for all catalog data. Before trusting ANY `db_query`
  result, confirm the saved reporting connection actually contains the active
  company — several companies' reporting copies hold a different tenant, or hold
  the right tenant with transactional tables not yet synced. A `0` from the wrong
  environment is not evidence of absence. If in doubt, answer from `fluid_api`.
- Prices come back as strings like `"$179.95 (USD)"` in display fields and
  `"0.0"` in raw fields. Strip the currency suffix; treat `0` as *unpriced*,
  never as *free*.

# Step 1 — Enumerate the catalog (read-only)

Prefer `fluid_catalog_index` — it follows pagination internally, re-reads
first/middle/last through the detail endpoint, and writes
`fluid-catalog-index.json` as evidence.

Fallback: `GET /api/v202604/company/products?page[limit]=100`, following
`meta.pagination.next_cursor` until null. Note that large pages come back as a
`compact_projection` (id, title, default_variant.sku, canonical_url,
image_url) — that projection is enough for rules R1–R4, but R5 needs variant
detail, so fetch `GET /api/v202604/company/products/{id}` for any product whose
price is not present in the projection.

Record the total product count. Every later claim must reconcile against it.

# Step 2 — Run the five detection rules

## R1 — Duplicate SKU across distinct products · CRITICAL
Normalize each default SKU (trim, uppercase). Flag any normalized SKU held by
**2 or more distinct product ids**.

Why critical: a shared SKU breaks inventory decrementing and merges the two
products in every revenue report.

Proposed fix: assign a distinguishing suffix to the *non-canonical* product
(the clone / gated / secondary listing), never to the primary retail SKU.
Ask which is canonical if it is not obvious from the titles.

## R2 — Defective slug shipped live · HIGH
Flag a slug that matches any of:
- `-copy` / `-copy-\d+` / `copy-of-` anywhere in the slug
- a bare trailing counter: `-\d+$`
- `^untitled`
- the slug shares **no** normalized word with the product title

Why high: the slug is the public URL. `…/products/widget-2-copy` is a
customer-visible artifact of an admin duplicate.

**Suppress the bare-counter match when the digit is a model number that appears
in the title** (`widget-2` for "Widget 2" is correct, not an admin counter).
Report the suppressions in one line so the user can see what you chose not to
flag.

Proposed fix: a clean slug derived from the title.
**Blast radius — always state this on the card:** changing a slug changes the
live public URL, and the old URL will 404. Before proposing, check whether the
slug is referenced by a mobile widget (`GET /api/company/mobile_widgets` — read
each `embed_url`), a theme, a post, or an active campaign, and name what you
found either way.

## R3 — Inconsistent naming convention inside a product family · MEDIUM
Group products by family (the model name in the title). Within a family, compare
the slug pattern of every product sharing a qualifier such as `(Refurbished)` or
a membership/tier tag.

Flag the family when **2 or more distinct patterns** express the same
qualifier. Pick the majority pattern in the catalog as the target convention;
if there is no majority, propose `<base>-<qualifier>` (qualifier last) and say
it is a judgment call.

Offer the cheap fix and the complete fix separately: normalizing the single
outlier changes one URL, normalizing the whole family changes several. Let the
user choose the scope.

## R4 — Image reused verbatim across distinct products · MEDIUM (review, not auto-fix)
Flag an identical `image_url` held by 2 or more distinct product ids.

Judgment required — do NOT propose a mechanical fix. A refurbished SKU
legitimately reuses its retail parent's hero image. A *differently-branded*
listing (a co-branded or member-exclusive edition) reusing the standard
image is a real merchandising gap. Report both, labelled, and let the user
decide which need their own photography.

## R5 — Zero or missing price on a purchasable product · CRITICAL
Flag a default variant whose price is `0`, `"0.0"`, null, or absent **while the
product is active/public**.

Distinguish two causes before reporting:
- genuinely free/promo item → not a defect, note and move on
- price simply never entered → CRITICAL, it is purchasable at $0 right now

Never invent a price. Ask the user for the number, or offer deactivation as the
interim fix.

# Step 3 — Report, ranked

Present one table ordered CRITICAL → HIGH → MEDIUM, then within severity by
whether the defect is customer-visible:

| # | Severity | Rule | Product (id) | Evidence | Proposed fix | Changes a live URL? |

Rules:
- Evidence is quoted verbatim from the API response (the actual SKU, the actual
  slug, the actual price string) — never paraphrased.
- Every URL you show is copied verbatim from `canonical_url` in a response.
  Never compose a URL from a slug you chose yourself.
- State the total scanned count and the clean count, so the user knows the
  denominator.
- If a rule found nothing, say so in one line. Silence reads as an omission.

Then stop and let the user react to the report before proposing anything.

# Step 4 — Approval-gated fixes, one issue at a time

For each fix the user wants, call `human_in_the_loop` with a **deterministic**
suggestion id so the same defect never gets re-prompted once decided:

    catalog-hygiene:<rule>:<product_id>        e.g. catalog-hygiene:r1-dup-sku:87907

Include `current_score` only where a real number exists, `before_payload` with
the exact current field value, and name the blast radius in the description.
End the turn after proposing. A dismissal is final — do not re-propose it.

If the user says "remove" or "delete" a product, do NOT delete. Propose
**archive + unpublish** instead, state plainly that it is reversible and that
deletion is not, and make them say "delete permanently" explicitly before you
treat destruction as the request.

## Write calls (only after Approve)

**Slug repair** — `PATCH /api/v202604/company/products/{id}`

    { "product": { "slug": "widget-2-member", "custom_slug": true } }

`custom_slug: true` is mandatory. Without it the API **silently ignores** your
slug and regenerates one from the title, and you will report a success that did
not happen. After the PATCH, re-`GET` the product and quote `canonical_url`
from the response to prove the new URL.

**SKU repair** — same endpoint, `{ "product": { "sku": "…" } }`. Re-GET to
verify. Confirm the new SKU is not itself a duplicate before writing.

**Price repair** — `PUT /api/company/v1/variants/{variant_id}`

    { "variant": { "price": "24.95" } }

Note: `PUT`, not `PATCH`, and hit the variant directly rather than nesting
through the product. Re-GET the variant to verify the value persisted.

**Archive / unpublish** — `PATCH /api/v202604/company/products/{id}` with
`{ "product": { "status": "archived", "public": false } }`. `status` accepts
`draft` | `scheduled` | `published` | `archived`.

**Never** delete a product to resolve a duplicate. Archiving is the reversible
alternative — and still needs approval.

# Step 5 — Verify and record

1. Re-run the failing rule against live data and show it now passes.
2. Call `human_in_the_loop` with `mode: "record_outcome"`, the same
   `suggestion_id`, and `after_payload` holding the verified new value.
3. Report any **residual** the fix did not address — archiving a $0 product
   hides it but leaves `variant_countries.*.price: "0.0"` and
   `buyable: true`, so republishing without a price reintroduces the defect.
   Say so rather than implying the underlying data is now correct.
4. Summarize: fixed / deferred / dismissed counts, and anything still needing a
   human decision (a missing price, a canonical-product choice).

Report a fix as complete only after the re-read confirmed it. A 200 response is
not proof — the slug trap above returns 200 while ignoring your change.

# Gotchas

- **The `custom_slug` trap is the single most dangerous behaviour here.** A slug
  PATCH without it returns `200` with the OLD slug in the response body. Read
  the response, don't assume.
- **`sku` at product level is usually `null`**; the real SKU is
  `default_variant.sku`. Deduplicating on the product field finds nothing on a
  catalog full of duplicates.
- **The public storefront endpoint is not a verification path.**
  `GET /api/v202604/products/{slug}` can return `404 "Storefront not found"`
  because the shop host doesn't resolve for the API token — that says nothing
  about the product. The admin re-read is the proof.
- **A digit at the end of a slug is usually a model number, not a duplicate
  counter.** Check the title before flagging.
- **Refurbished/secondary listings sharing a parent's hero image are normal.**
  Only flag image reuse across *differently branded* listings as a real gap.

# Known exceptions

Some collisions and $0 prices are deliberate — member-gated merch whose pricing
lives behind login, or intentional secondary listings of the same hardware.
These are still worth reporting (a shared SKU is a real reporting defect however
deliberate the duplicate listing is), but they must be labelled *awaiting a
decision* rather than *admin error*, and the duplicate listing itself must never
be proposed for merge or deletion.

At the end of a run, record the exceptions this company confirmed via
`update_memory` so the next run reports them as known rather than re-litigating
them. A test-mode payment gateway or an inactive legal entity on a demo company
is seed data — never surface it as a launch blocker.
