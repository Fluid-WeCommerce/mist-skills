# Commission ledger: build spec

A small Mist app that turns credited orders into commission lines for a one- or two-level creator plan, and produces a payout statement. It is a ledger. It does not decide who gets credit and it does not move money.

## What it must never become

- No third level, ranks, team volume, qualification rules, or pay for signing people up. If the plan needs any of those, stop and say this app does not do that.
- No second opinion on credit. Fair Share already decided which creator earns the order. Read that answer and use it.

## Plan settings (one row per company)

| Setting | Meaning |
| --- | --- |
| `level1_rate` | Percent of the base the selling creator earns. |
| `level2_rate` | Percent the inviting creator earns. `0` turns the second level off. Must be below `level1_rate`. |
| `level2_source` | Where "who brought this creator in" is read from: `genealogy` or `app`. Chosen once at setup. The two are never mixed. |
| `creator_overrides` | Optional per-creator `level1_rate`. An override must stay above `level2_rate`. |
| `earn_on` | `all_orders`, `first_order_only`, or `first_order_plus_renewals` with `renewal_months`. |
| `own_orders_earn` | Whether a creator's own purchase earns. Default false. |
| `hold_days` | Days from the order date until a line can be paid. Set it to the return window. |
| `payout_schedule` | `monthly` (the calendar month) or `twice_monthly` (the 1st to the 15th, and the 16th to month end). |
| `payout_minimum` | The smallest balance that pays out, set per currency. |
| `payout_method` | `export` or `store_credit`. |

Rates are stored as a percent with up to two decimals. Every change to these settings is saved with who changed it and when, and applies only to orders placed after it.

## Who earns

- **Level one** is the order's `volume_rep` from GET `/api/v202506/orders/:id/journey`. `attribution_rep` is who the shopper came through; `volume_rep` is who earns. They can differ, and `volume_rep` can be empty. An order with no `volume_rep` writes no lines.
- **Level two** is whoever brought the level-one creator in.
  - `level2_source: genealogy` is allowed only when GET `/api/company/v2026-10/genealogy/trees` reports `authority` as `authoritative` or `replica`. Read the creator's `enroller` (who signed them up) from the genealogy node routes. If the company's tree also uses a different `sponsor`, ask the admin once which of the two the plan pays and save the answer.
  - `level2_source: app` keeps an `invited_by` column in this app, set once when a creator joins and changed only by an admin, with the change logged. Reject a creator inviting themselves, and reject an inviter who joined after the creator they claim to have invited, so no loop can form.
- **Own orders.** An order is the creator's own when the buyer's member id is the level-one creator's. If `own_orders_earn` is false, that order writes no lines at either level. If true, it writes them as usual.
- Nobody earns on orders credited to a creator who has been removed from the program.

## The base and the arithmetic

The base is the product subtotal after discounts, before tax and shipping, in the order's currency. Read one real order with GET `/api/v202506/orders/:id` and confirm which fields carry the subtotal, discounts, tax, shipping and refunds before writing the calculation. Do not guess field names.

- Amount = base x rate, rounded half-up to the currency's smallest unit, per line. A statement is the sum of its rounded lines.
- Every line stores the rate it was written at. Reversals and adjustments reuse the rate on the original sale line, never the plan's current rate.
- Keep each currency separate everywhere: lines, balances, minimums, statements. Never add two currencies together.
- Use the date the order was placed. For orders imported from another system, check which field holds the original sale date before trusting the created date.

## Tables

- `plans` - the settings above, per company.
- `creators` - member id, username, `invited_by`, status, optional rate override.
- `commission_lines` - company, order id and number, `kind` (`sale`, `reversal`, `adjustment`), `level` (1 or 2), earner, source creator (for level two), base, rate, amount, currency, `status` (`pending`, `payable`, `paid`), order date, `available_on`, `payout_id`, and a required `event_key`.
- `payouts` - period, earner, currency, total, `status` (`draft`, `approved`, `paid`, `void`), who approved it and when. Unique on company, earner, currency and period.
- `webhook_deliveries` - the delivery id of every event handled, so a repeat is dropped before any work.
- `audit_log` - every settings change, manual adjustment and payout approval.

`event_key` is never empty and is unique per company: `sale:<order id>:<level>`, `reversal:<refund id>:<level>`, `cancel:<order id>:<level>`, `adjustment:<edit id>:<level>`. Do not build the uniqueness on a nullable column; a database treats empty values as different from each other, and the same sale would be written twice.

Lines are never deleted or edited after they are written. A mistake is corrected with a new line.

Scope every read and write to the installation's company. Never fall back to a company id from the request, an env token or "the only row in the table".

## Events

1. List the webhook events this company can subscribe to with GET `/api/webhooks/schemas` and pick the ones for an order being placed or paid, edited, refunded and cancelled. Read each schema before handling it.
2. **Order placed.** Credit lands after the order. Wait, then read the journey. When `volume_state` has settled, write the level-one line and, if on, the level-two line, both `pending` with `available_on` = order date + `hold_days`.
3. **Refund or cancel.** Write `reversal` lines for the same earners, in proportion to the product amount refunded, at the stored rate. A full refund nets the order to zero.
4. **Order edited.** Recompute at the stored rate and write the difference as an `adjustment`.
5. **Nightly sweep.** Re-read orders changed in the last few days and repair anything a missed webhook left behind. Move `pending` lines to `payable` when `available_on` has passed.

## Payout run

At period close, in one database transaction per creator and currency: select `payable` lines whose `payout_id` is empty, create one `draft` payout for the period, and stamp those lines with its id. A line belongs to at most one payout. Running the close twice creates nothing new.

- A payout moves `draft` to `approved` to `paid`, in that order. `paid` is refused unless the payout is `approved`. Approval is an admin action in the app and is logged.
- Voiding a `draft` or `approved` payout releases its lines (their `payout_id` is cleared) and keeps the voided row.
- A balance under `payout_minimum` gets no payout and carries forward.
- A reversal that lands after a payout was paid leaves that creator with a negative balance in that currency. It carries forward and comes off later earnings. Never create a payout for a negative amount; show the balance to the admin.

Then, by `payout_method`:

- `export` - a CSV with creator, email, amount, currency, period and line count. The brand pays through its own rail and marks the payout paid.
- `store_credit` - only if reward points are on for the company (Settings > Commerce > Points) and a points rate exists for that currency. Convert at the company's rate, round down to whole points, and show the admin the conversion before approval. Grant through POST `/api/v2026-10/customers/:id/points-ledgers` with a `reason` naming the payout. Record the payout id before the call and never grant twice for one payout.

Lines become `paid` only when their payout is marked paid.

## Screens

- **Admin:** plan settings; creators with pending, payable and paid totals per currency; the ledger with filters by creator, status and period; payout runs; a per-order view that shows the journey answer next to the lines it produced.
- **Creator:** after the admin side is proven, a simple earnings view (pending, payable, paid, recent orders without the buyer's personal details). Use `run_skill("mist/portal-widget-vs-mist-app")` to choose where it lives.

## Done when

The checks in the skill's Step 5 pass on this store. A payout run on test data produces a statement that matches the ledger to the smallest currency unit, a second run of the same close creates nothing, and a redelivered webhook writes no second line. `npm run typecheck`, `npm run lint` and `npm test` are clean.
