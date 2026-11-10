---
name: Fraud review queue
description: Work the orders held for fraud review — weigh each one's screening result, customer history and payment attempts, recommend approve or cancel, and apply only the decisions you approve.
icon: shield-alert
---

# Goal

Clear {{company.name}}'s fraud review queue as of {{today}}. Every order in it is a sale that is neither shipping nor cancelled: good customers are waiting, and a bad order that ships is lost product plus a chargeback. For each held order, gather the evidence, recommend **approve**, **cancel** or **needs a human**, and apply only the decisions the user approves.

# Rules

- **Read first, write only with approval.** Nothing changes until the user approves a card. Every decision is one `fluid_api` PUT gated by `human_in_the_loop`.
- **At most 3 decision cards per turn**, then END your turn and wait for the clicks.
- **Never decide a "needs a human" order yourself.** Give the user the one check that would settle it (for example, "call the customer to confirm the shipping address").
- **Talk in plain words.** Refer to orders by order number and customers by first name. Don't show card numbers, ids, paths or JSON in the chat.
- Held orders are not abandoned carts. Don't offer recovery outreach for them until they are approved.

# Steps

## 1. Build the queue

1. `fluid_api("/api/v202506/orders?status=pending_review&sort=-created_at&page[limit]=100", "GET")`. Follow `meta.pagination.next_cursor` as `page[cursor]` until it is null.
2. If the queue is empty, say so in one line and stop.
3. For each order keep `id`, `order_number`, `created_at` (hours waiting), `amount` and `currency_code`, `email`, `customer.id` and `customer.orders_count`.

## 2. Pull card-testing context once

`fluid_api("/api/v202604/analytics/payments/overview?from=<14 days before {{today}}>&to={{today}}&flow=checkout", "GET")`. Keep `multi_card_checkouts` (email, cards tried, declines, last attempt) and `summary.card_approval_rate` against `previous_summary.card_approval_rate`. If it answers 422, try a 7-day range. A sharp drop in card approval, or many multi-card checkouts, means a stolen-card run is under way: say so at the top of the report.

## 3. Gather evidence per order

For each held order, oldest first:

1. **Screening.** `fluid_api("/api/orders/<id>/fraud_check_details", "GET")`. Read `stored.pre_auth.decision` (APPROVE, REVIEW, DECLINE) and `risk_score`, and `live` when it isn't null, since the provider may have rescored since checkout. An empty `stored` means the order was held without a screen.
2. **The order.** `fluid_api("/api/v202506/orders/<id>", "GET")`. Compare `billing_address` with `shipping_address` (country, then postal code, then name). Note `items` and `quantity_count` (several units of one item is a resale pattern), `discount_codes`, and whether it `starts_subscription`.
3. **Payment attempts.** `fluid_api("/api/v202506/transactions?order_id=<id>&sorted_by=created_at_asc", "GET")`. Count distinct `card_id` values, declines, and declines whose `decline_class` is `never_retry` or `card_gone` (bad card data or a lost or stolen card). Also check whether the order's `email` appears in step 2's `multi_card_checkouts`.
4. **History.** When `customer.orders_count` is above 1: `fluid_api("/api/v202506/customers/<customer_id>/orders?page[limit]=25", "GET")`. Count earlier orders that completed and were not refunded or cancelled.

## 4. Recommend

- **Cancel:** the screen says DECLINE; or 3 or more cards were tried on this checkout; or a `card_gone`/`never_retry` decline comes on a first order whose billing and shipping countries differ.
- **Approve:** the screen says APPROVE, or REVIEW with no other signal against it, **and** the customer has at least one earlier good order **and** the addresses match **and** one card paid cleanly.
- **Needs a human:** everything else. Name the single check that would settle it.

Within each group, sort by amount, largest first. Flag any order waiting more than 48 hours: card authorizations can expire, and the customer is waiting.

## 5. Report

Lead with one line: how many orders are held, their total value, and the oldest wait. Then one table per group (order number, amount, hours waiting, a one-line reason in plain words). If step 2 found a card-testing run, put it first and suggest the user ask their payment provider to add protection on that account.

## 6. Apply approved decisions

Offer to apply the Approve and Cancel recommendations. For each order the user wants decided, up to 3 per turn:

1. Call `fluid_api("/api/orders/<id>/review_order", "PUT", { "review_action": "approve" | "cancel", "reason": "<one-line reason from step 4>" })` **without** `approval_id` to get the exact approval title.
2. Propose it with `human_in_the_loop` (source `"agent"`, that title exactly, a fresh `suggestion_id` of the form `"fluid-api:<random>"`, and the reason as `description`). END YOUR TURN.
3. After the user approves, call the same PUT again with the same body plus `approval_id`. Confirm the returned `order_status` (`cancelled` after a cancel; the order moves on to processing after an approve).
4. If the call is refused, say in plain words that the decision couldn't be saved and leave the order held. Never retry with a different method.

After a cancel, check the order's payment with the step 3 transactions read. If money was captured, tell the user it may need a refund, and refund only if they ask.

Finish with what was approved, cancelled and left for a human, and the value released to ship.
