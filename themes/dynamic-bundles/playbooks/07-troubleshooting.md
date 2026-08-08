# 07 — Troubleshooting

Work top to bottom. Stop at the first failure. **Most "platform bugs" are not.**

## 1. Is the product actually a published, routed bundle?

`GET /api/company/v1/products/{id}` and check, in order:

| Field | Must be | If not |
|---|---|---|
| `status` | `active` | drafts aren't published. Not a bug. |
| `product_bundle_groups.length` | `> 0` | **not a bundle product**, whatever `/bundles` says. Not a bug. |
| `application_theme_template_id` | not `null` | **unrouted** — the most common real fault |

Worked example from the source campaign: three bundles showed "no bundle UI" and only **one**
was a fault (unrouted). The others were a draft and a product with zero groups. Two of three
would have been false bug reports.

## 2. Are you reading the right bundle row?

Match by `product_bundle_groups[].id`, **never slug**. Duplicate/orphan rows share a title and
the later row often owns the uniquified slug.

## 3. Is it an orphan?

Storefront 302s to /404 ⇒ the Product was deleted and the Bundle row survived. `DELETE` on it
then 500s forever. Always delete **Bundle first, then Product**.

## 4. Which implementation is rendering?

Compare all three paths (plain / canonical / picker). If it only misbehaves on one, that
implementation owns the bug. To decide platform-vs-theme with certainty, render the section
with no theme code around it in a throwaway host template.

## 5. Is it a data precondition?

| Symptom | Cause |
|---|---|
| "Out of stock" on a new bundle | the master variant has no active `variant_countries` row for the shopper's country |
| Everything prices at $0.00 | a child has no priced country row. HTTP 200, `items[].errors: []` — **no signal at all** |
| Subscribe toggle missing | the item's `allow_subscription` is false |
| Renewal price is wild | P7, by design — the BGI variant's own country row, not the parent |

## 6. API traps that fake a theme bug

| Trap | Effect |
|---|---|
| `per_page=100` on `/api/company/v1/products` | returns **zero** products, no error. 50 works. |
| `/api/v2025-06/bundles` | no pagination, omits `product_id` |
| Ignored filters | return an unfiltered page |
| `?country=CA` | ignored — use `?country_id=<numeric>` |
| Unknown keys on a write | silently dropped, HTTP 200 |

## 7. Symptom → cause, ours

| Symptom | Look at |
|---|---|
| Section renders nothing | `product_bundle_groups.size > 0` gate — correct behaviour on a non-bundle |
| Renders but no cards | `normalize()` dropped them — hidden groups, or every item filtered as unavailable. Turn on `debug` and read the warnings. |
| CTA never enables | `rules().violations` — most often a `configError` (nil bound) or an unchosen exclusive branch |
| CTA does nothing, no error | SDK never loaded. Our code shows a message; the platform's shows nothing (P17) |
| Add succeeds, cart empty/wrong | read the captured `bundled_items` — included group sent by mistake, or a missing group id |
| Total right on page, wrong in cart | a fixed-price group being summed, or bundle-level flat being ignored. `total()` mode must match the config. |
| Duplicate cart lines | an untagged entry crept in — every entry needs `product_bundle_group_id` |

## 8. Before filing anything

`reference/13-defect-triage.md`. **8 of 21 reported defects were downgraded.** Do not file
P7, P12, P4 (by design, named verbatim in their originating commits) or P11, P13, P16, P18
(fixture artifacts the Bundle Builder cannot produce). Do file P2 (exclusivity) and P19
(defaults over max) — those are reachable by a real merchant and cost real money.
