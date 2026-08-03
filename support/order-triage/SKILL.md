---
name: Diagnose an order
description: Find out what actually went wrong with one specific order — a declined payment, a back-office sync that failed silently, wrong totals, stuck fulfillment, the wrong rep credited, a fraud hold, or a refund that won't go through. Opens a pick-one support menu, then reads the transaction logs and pipeline states the admin order page cannot show you. Use when a customer or rep complains about a single order, when an order looks stuck or wrong, when someone asks "what happened to order #1043", or when the admin Status/Logs card is all green but something is clearly broken.
icon: stethoscope
category: Support
---

# Diagnose an order

Triage **one** order for {{company.name}}, name the root cause, and show the
evidence. Today is {{today}}.

This is a support skill. Read first, explain in the merchant's words, and never
change anything without explicit sign-off.

For fleet-wide questions, use a different skill: `sales/stalled-order-recovery`
ranks every stalled order, and `sales/checkout-funnel-diagnosis` finds where the
funnel leaks. This one goes deep on a single order.

## Why this skill exists

The admin order page **cannot show you a failure**. Its Status/Logs card renders
every log entry in green with `response_status || "200"`, and the section dot is
lit whenever *any* log exists — success or not. Four consequences:

1. A failed back-office sync displays as a green `200`.
2. "Last sync" is the timestamp of the newest integration attempt **whether or
   not it worked** — so "Last sync 07/30" can mean "last *failed* on 07/30".
3. `cart`-type logs are returned by the API but the admin UI never renders them,
   so gateway attempts made *before* the order existed are invisible there.
4. A back-office rejection is usually **HTTP 200 with `success: false`** in the
   body. The status code tells you nothing.

Read `status` (the boolean) and the response body. Never trust a rendered dot,
and never report "the log looks fine because it returned 200".

## Ground rules

- **Read-only by default.** Everything in the playbooks below is a GET. The
  mutations are listed separately and every one needs sign-off.
- **Never guess an API path.** The paths in this skill are exact. If one 404s,
  say so and stop — do not probe variants. In particular the version segment is
  not interchangeable: orders live under `/api/v202506/...` (no dashes) while
  some other Fluid APIs use `/api/v2025-06/...` (with dashes). Copy the paths
  here verbatim.
- **`transaction_logs` is not in the public OpenAPI docs.** Don't try to look it
  up; it's documented here and nowhere else.
- **Quote real values.** Every conclusion cites a field, a log name, or a
  timestamp. If the data doesn't say, say it doesn't say.
- **Don't paste secrets.** Logs contain auth headers, gateway tokens, and full
  customer addresses. Quote the decline reason and the message, not the payload.

## 0. Identify the order

Take an order number, an order id, or a customer email/name. Resolve it and show
the user what you're looking at:

- `order_card` with `order_id`, or `order_number` (e.g. `"1043"`), or `query`
  (customer name / email).
- Then `fluid_api("/api/v202506/orders/{id}", "GET")` for the full record.

If the identifier matches more than one order, list the candidates with dates and
totals and ask which one — don't pick for them.

## 1. Baseline read — always, before the menu

Two calls, every time, regardless of which path they choose. They frequently
reveal the answer before the user finishes picking.

```
fluid_api("/api/v202506/orders/{id}", "GET")
fluid_api("/api/v2/orders/{id}/transaction_logs", "GET")
```

### An order has four independent status fields

Support tickets conflate these constantly. Read all four — they disagree by
design, and the disagreement is the diagnosis.

| Field               | Values                                                                                                        | What it means                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `order_status`      | `draft` `pending` `pending_review` `processing` `completed` `cancelled` `archived`                             | Where it is in the pipeline      |
| `financial_status`  | `pending` `authorized` `partially_paid` `paid` `partially_refunded` `refunded` `voided` `marked_free` `marked_paid` | The money                        |
| `fulfillment_status`| `unfulfilled` `in_progress` `on_hold` `partially_fulfilled` `scheduled` `fulfilled`                           | The shipment                     |
| `status`            | `awaiting_payment` `awaiting_shipment` `shipped` `delivered` `archived` `cancelled` `failed_payment` `draft`   | Legacy single field — still set  |

`order_status` defaults to `completed`, `financial_status` to `pending`, and
`fulfillment_status` to `unfulfilled`. So **"completed" does not mean paid**, and
an order can read `completed` + `pending` + `unfulfilled` all at once. Say which
field you're quoting whenever you use the word "status".

Also worth reading: `order_type` (`requested` `purchased` `imported`
`abandoned`), `order_class` (`sample_order` `customer_order` `member_order`
`enrollment_order` `autoship_order`), and `source` (`mobile` `web` `admin`
`backoffice` `subscription` `enrollment`). An `imported` or `backoffice` order
follows different rules than a `web` one — check this before blaming checkout.

### Three pipeline states — silent commission failures

`attribution_state`, `volume_state`, and `journey_state` each hold
`not_applicable` / `pending` / `processing` / `processed` / `processing_failed`
(and `manual` for the first two). **Any of them at `processing_failed` means rep
credit broke and nothing in the UI says so.** Flag it even when the user asked
about something else. Anything stuck at `processing` long after the sale date is
also worth calling out.

### The transaction logs

`GET /api/v2/orders/{id}/transaction_logs` returns:

```
{ "data": { "integration": [...], "payment": [...], "tax": [...], "cart": [...] },
  "integration_logs_metadata": { "latest_retryable_log_id": 123, "last_sync_at": "..." } }
```

Four buckets, keyed by log type:

| Bucket        | Who it talks to                                     |
| ------------- | --------------------------------------------------- |
| `payment`     | The payment gateway                                 |
| `tax`         | The tax provider (Avalara etc.)                     |
| `integration` | The back office / commission system                 |
| `cart`        | Calls made against the cart **before the order existed** — only present when the order still has a cart, and never shown in the admin UI |

Per entry, the fields that matter: `status` (the success flag),
`name` (which provider — `Avalara`, `Paypal`, …), `response_status`,
`response` / `request`, `created_at`, `repeatable`, and `external_reference`.

**`status` has three states, not two.** `true` succeeded, `false` failed, and
**`null` means the outcome was never recorded** — the log was written but nothing
resolved it. Report a null as *indeterminate*, never as success. Payment logs are
where nulls turn up.

**Triage rule:** list every log where `status` is `false` **or null**, oldest
first, and read its `response.message` / `response.displayMessage`. Also treat
`response.success === false` as a failure even when `response_status` is `200`.
The earliest failure is usually the cause and the later ones the symptoms.

**What a real failure looks like.** The most common live failure is the tax
provider rejecting the order — an `Avalara` log with `status: false` and
`response_status: "400"` (sometimes `503`) — on an order that reads
`order_status: completed` and `financial_status: paid`. The customer was charged;
the tax call failed. Nothing on the admin page communicates this: the card prints
that `400` in the same green as a success. When you see this pattern, say plainly
that the order is fine as far as the money went and the **tax record** is what
failed, and check whether `repeatable` is `false` — most tax logs can't be
retried, so this needs the tax provider looked at rather than a retry click.

Then open the menu.

## 2. Ask which kind of problem

Call `steps` with one required single-select. Keep the baseline findings in hand
— if they already point somewhere, say so in the `intro` and still let the user
choose.

```
steps({
  title: "What's wrong with order #1043?",
  intro: "Pick the symptom the customer or rep reported and I'll trace it.",
  steps: [{
    id: "symptom",
    kind: "single_select",
    title: "What went wrong?",
    skippable: false,
    options: [
      { id: "payment",     label: "Payment failed or was declined",   description: "Card declined, charged twice, or never charged at all" },
      { id: "sync",        label: "Never reached the back office",    description: "Missing from the commission or fulfillment system" },
      { id: "totals",      label: "The totals are wrong",             description: "Tax, shipping, discount, or points look incorrect" },
      { id: "fulfillment", label: "It hasn't shipped",                description: "Stuck unfulfilled, on hold, or no tracking" },
      { id: "credit",      label: "The wrong rep got credit",         description: "Commission or volume went to the wrong person" },
      { id: "review",      label: "It's being held for review",       description: "Stuck in pending_review or flagged as fraud" },
      { id: "refund",      label: "A refund or cancel won't go through", description: "The button is disabled or the refund didn't land" },
      { id: "unsure",      label: "Something else / not sure",        description: "I'll walk the whole order and tell you what looks wrong" }
    ]
  }]
})
```

End your turn after calling `steps` and wait — the answer arrives as the next
user message. If the user just types their symptom instead of clicking, record it
with `steps_answer` so the panel stays in sync, then continue.

On `unsure`, run the baseline conclusions plus playbooks **A**, **B**, and **E** —
payment, sync, and credit are where silent failures hide.

## 3. Playbooks

### A. Payment failed or was declined

1. Read the `payment` bucket **and the `cart` bucket** — a decline during
   checkout often lands in `cart`, which is exactly why the merchant can't find
   it in admin. Quote the gateway's own decline text from `response`.
2. Cross-check `financial_status`:
   - `pending` with no successful payment log → never charged.
   - `authorized` → held, not captured. Money is reserved, not taken.
   - `paid` while the customer claims a decline → an earlier attempt failed and a
     later one succeeded. Count the successful logs before saying "charged twice";
     duplicate *attempts* are not duplicate *charges*.
   - `voided` → the authorization was released.
3. If `order_status` is `cancelled`, read `cancel_context`: `void_authorization`
   (auth released), `pending_hold` (cancelled while held), or `no_payment`
   (cancelled because payment never landed).
4. Check `payment_method` for the brand and last four so the merchant can match
   it to what the customer is looking at, and `source` to know where it was paid.

Re-charging is a mutation — see §5.

### B. Never reached the back office

The highest-value path, and the one the UI actively hides.

1. Read `integration_logs_metadata`:
   - `last_sync_at` **is just the newest integration attempt, success or not.**
     Never report it as "synced at" without checking that log's `status`.
   - `latest_retryable_log_id` is non-null only when a retryable attempt exists.
2. Walk the `integration` bucket for `status: false` or `response.success:
   false`. The reason is in `response.message` / `response.displayMessage` —
   quote it. Typical causes are a missing or unknown distributor id, a rejected
   SKU, or a validation error on the address.
3. Check the order's external id two places: the top-level `external_id` field
   and `metadata.external_id`. **No external id + no successful integration log
   = the back office never received this order**, whatever the green dots say.
4. If the integration bucket is *empty* while `order_status` is `completed`, the
   sync was never attempted — a different failure from a rejected sync. Say which.
5. Report whether a retry is possible (`latest_retryable_log_id` non-null) and
   offer it — see §5.

### C. The totals are wrong

1. Two sets of totals exist. `subtotal` / `tax` / `shipping` / `discount` /
   `amount` are **immutable checkout-time** values; `current_subtotal` /
   `current_tax` / `current_shipping` / `current_discount` / `current_amount`
   reflect the order **after edits**. If they differ, the order was edited after
   purchase — that alone explains most "the total changed" tickets. Show both.
2. Tax: read the `tax` bucket for the provider's response. Then check
   `tax_exempt_at_order_time` and `sales_tax_id_at_order_time` — these are a
   **snapshot** and do not change when the customer's exemption is updated later.
   A customer who became tax-exempt *after* ordering was still correctly taxed.
3. Inclusive-tax markets: `price_inclusive_of_tax`, `price_inclusive_tax_name`,
   and the `totals` breakdown. Tax inside the price isn't a missing line item.
4. Points: `points_applied`, `points_applied_amount`,
   `order_total_after_points_redemption`, `total_points_credited`.
5. Discounts: `discount_codes` and `free_shipping`.
6. Currency: `currency_code` with `amount_in_base` and
   `currency_conversion_rate`. Confirm which currency the complaint is in before
   comparing numbers.

### D. It hasn't shipped

1. `fulfillment_status` first. `on_hold` and `scheduled` are deliberate states —
   don't call them stuck.
2. `fluid_api("/api/order_fulfillments?order_id={id}", "GET")` for the actual
   fulfillment records and tracking.
3. `warehouse_id` / `warehouse_name` — an unassigned warehouse blocks shipment.
4. Check upstream causes before blaming the warehouse: `financial_status` still
   `pending`/`authorized` (nothing is picked until it's paid), `order_status`
   `pending_review` (see **F**), or a failed integration sync (see **B**) when
   fulfillment is driven by the back office. Say which layer is actually stuck.

### E. The wrong rep got credit

```
fluid_api("/api/v202506/orders/{id}/journey", "GET")
fluid_api("/api/v202506/orders/{id}/journey/events", "GET")
```

1. `order_journey` names **six** rep slots: `first_touch_rep`, `last_touch_rep`,
   `most_touch_rep`, `attribution_rep`, `volume_rep`, and `enrollment_rep`. The
   rep who *earned* the touch and the rep who *got* the credit are different
   fields — quote both before agreeing anything is wrong.
2. `fairshare_settings` on the response holds `attribution_config`,
   `order_volume_config`, `enrollment_volume_config`, and
   `orphan_sponsor_config`. These decide who wins. Explain the outcome **as a
   consequence of the configured rule** — e.g. under `last_touch`, the last rep
   whose link was clicked wins even if another rep did all the work. That's the
   setting behaving correctly, not a bug.
3. `attribution_state` / `volume_state`: `processing_failed` is a genuine
   failure; `manual` means someone set it by hand; `not_applicable` means this
   order was never eligible for attribution.
4. `journey/events` is the click trail — `event_type`, `occurred_at`, and the
   `attribution_rep` per event, with page/visit data. Use it to show *why* a rep
   won, in order.
5. To change the company-wide rule rather than this one order, hand off to the
   `fairshare/fairshare-settings` skill. Don't rewrite settings from here.

### F. It's being held for review

1. `order_status: pending_review` is a deliberate hold, not a stuck order.
2. `fluid_api("/api/orders/{id}/fraud_check_details", "GET")` returns `stored`
   (the check as recorded at order time) and `live` (re-run now). They can
   disagree — say which one you're quoting.
3. Explain the signals in plain language, then offer approve or cancel (§5).
   Never approve on your own judgment: releasing a fraud hold is the merchant's
   call and their liability.

### G. A refund or cancel won't go through

1. `is_refundable`, `is_cancellable`, and `item_refunds_allowed` are the API's
   own verdicts — if one is false, that's why the button is disabled. Pair it
   with `financial_status`: you can't refund something never captured (`pending`,
   `authorized`) — that's a void, not a refund.
2. `refunds[]` lists what already happened, with `amount` and `refund_type`.
   `financial_status: partially_refunded` plus a customer expecting a full refund
   is an amount dispute, not a failure.
3. `cancel_context` explains an existing cancellation's mechanism.
4. `points_refunded` — points and money refund separately. A customer who paid
   partly in points needs both checked.
5. Look for a failed refund attempt in the `payment` bucket before concluding
   nothing happened.

## 4. How to report

Lead with the answer, not the trail. Then:

1. **What went wrong** — one sentence, in the merchant's words.
2. **Evidence** — the specific fields and log entries, with timestamps. Quote the
   provider's own message verbatim where there is one.
3. **What's still true right now** — the four status fields, so they know the
   order's actual current state.
4. **What to do next** — either an offered action (§5) or a plain statement that
   this needs a human decision, and whose.
5. **Anything else you noticed** — especially a `processing_failed` pipeline
   state, since it's invisible in admin and nobody asked about it.

Re-render `order_card` if the conversation moved to a different order. If the
merchant's premise turns out to be wrong ("the total changed" → the order was
edited by a droplet), say so directly and show the two totals.

## 5. Mutations need sign-off

Present any change through `human_in_the_loop` with a deterministic
`suggestion_id` like `order-triage:{order_id}:retry-sync`, and **wait**. Do not
chain two mutations behind one approval.

| Action                   | Call                                                              |
| ------------------------ | ----------------------------------------------------------------- |
| Retry the back-office sync | `GET /api/v2/orders/{id}/transaction_logs/{log_id}/retry`        |
| Approve / cancel a review  | `PUT /api/orders/{id}/review_order` `{ "review_action": "approve" \| "cancel", "reason": "..." }` |
| Re-charge the order        | `POST /api/v2/orders/{id}/charge`                                |
| Cancel the order           | `PATCH /api/v2/orders/{id}/cancel` `{ "reason": "...", "restock_all_items": true }` |
| Set fulfillment status     | `PATCH /api/orders/{id}/update_fulfillment_status` `{ "fulfillment_status": "...", "reason": "..." }` |
| Fix the external id        | `PATCH /api/v2/orders/{id}/update_external_id`                   |
| Re-send the invoice email  | `POST /api/v2/orders/send_invoice_email` `{ "cart_token": "..." }` (needs the order's `cart_token`) |

**The retry endpoint is a `GET`.** That's genuinely how the route is defined —
don't "correct" it to POST. Three more things about it:

- It only works when `latest_retryable_log_id` is non-null. Retrying a
  non-retryable log fails outright.
- It is **asynchronous**. A `200` with "in progress" means *queued*, not fixed.
  Wait, re-fetch `transaction_logs`, and confirm a new entry with `status: true`
  before telling anyone it worked.
- A retry re-sends the **original** payload. If the sync failed because the data
  was wrong, retrying sends the same wrong data. Fix the cause first.

Permissions: reading logs needs `orders: view`, retrying needs `orders: update`,
and both need company-admin access. On a 403, say the user's role can't do this
rather than reporting the order as broken.

## Endpoint reference

| Purpose                     | Call                                                       |
| --------------------------- | ---------------------------------------------------------- |
| The order                   | `GET /api/v202506/orders/{id}`                             |
| Gateway / tax / sync / cart logs | `GET /api/v2/orders/{id}/transaction_logs`             |
| Attribution summary         | `GET /api/v202506/orders/{id}/journey`                     |
| Attribution click trail     | `GET /api/v202506/orders/{id}/journey/events`              |
| Fraud check                 | `GET /api/orders/{id}/fraud_check_details`                 |
| Fulfillment records         | `GET /api/order_fulfillments?order_id={id}`                |

If a read returns zeros or empties for something the merchant is certain exists,
cross-check with `db_schema` + `db_query` against the reporting database before
relaying the zero — some endpoints silently ignore filters. Note in your report
that the number came from the database rather than the API.
