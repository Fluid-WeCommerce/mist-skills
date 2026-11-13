---
name: Late shipment notices
description: Find paid orders that haven't shipped and are nearing or past the ship-by date you promised (or the 30-day default), draft the delay notice with a new date and the option to cancel, send only what the user approves, and save a dated record of every notice for the FTC's Mail Order Rule.
icon: truck
---

# Goal

Keep {{company.name}} on the right side of the FTC's Mail, Internet, or Telephone Order Merchandise Rule as of {{today}}. The rule is simple and easy to miss in a busy week. If you can't ship when you said you would, or within 30 days when you didn't say, you must tell the buyer before that date, give a new date, and offer to cancel with a prompt refund. Social-selling companies hit this most during launches, sell-outs, preorders and warehouse moves, and a late order shipped with no notice is exactly what turns into a chargeback.

At the end the user has:

1. Every paid, unshipped order sorted into **past due**, **due within 3 days** or **on track**.
2. A delay notice for each order that needs one, approved by the user and sent, or a reason it wasn't.
3. A list of buyers who asked to cancel, for the user's team to refund.
4. A dated record in the project of what was found and what was sent.

This skill is not legal advice. It applies the rule as the FTC's business guide explains it. Point the user to their counsel for anything unusual: credit-financed orders, preorders sold without a date, or buyers outside the US.

# Rules

- **Read first, send only with approval.** Nothing goes to a buyer until the user approves a `human_in_the_loop` card. One card can cover one batch of orders that share the same new date and wording.
- **At most 3 approval cards per turn**, then END your turn and wait for the clicks.
- **One notice per order per delay.** Before you draft, check the message history for that buyer and order (step 4.1). Never send a second notice for the same new date.
- **Notices are transactional.** Send them as `message_type: "transactional"`: they are required by law, not marketing, and must not include offers or upsells.
- **Never cancel or refund in this skill.** List buyers who ask to cancel for the user's team, who cancel and refund in Fluid's admin. The rule expects a prompt refund: within 7 working days for cash or check payments, and within one billing cycle for card payments.
- **Talk in plain words.** Name orders by their order number, people by name, and warehouses and products by name. Don't show ids, paths or JSON in the chat.
- If a read is refused, say in plain words which part you couldn't check and carry on with the rest. If a send is refused, tell the user Fluid's reason (for example, email isn't set up) and leave those orders in the record as "not sent".

# Steps

## 1. Load the last run and the promise

1. Look for files under `shipping-notices/` in the active project with `list_dir`. If there is an earlier run, read the newest with `read_file` and keep the orders already notified, their new dates and any buyer who asked to cancel.
2. Ask the user in a `steps` panel, prefilled from the last run if there is one:
   - **What ship time do you promise?** Their stated handling time ("ships in 2 business days"), or "we don't state one". With no stated time the rule's 30 days applies. If they're unsure, `web_fetch` the storefront's shipping policy page and quote what it says.
   - **Any products with their own promise?** Preorders, made-to-order items or launches with a stated ship date. Record each product and its date.
   - **Who signs the notices?** A name or team, and the reply address buyers should use.
3. Keep the result as the **ship-by rule**: for each order, ship-by = order date + promised time, or the product's own date when it is later and was stated at sale.

## 2. Find paid, unshipped orders

1. `fluid_api("/api/v202506/orders?status=awaiting_shipment&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]` until it is empty. Keep only orders whose `financial_status` is `paid` and whose `fulfillment_status` isn't `fulfilled`.
2. For each order keep `order_number`, `sale_date` (or `created_at` when it's missing), `amount`, `currency_code`, `country`, `warehouse_id`, `fulfillment_status`, the `customer` id, name and email, and `type`.
3. For orders marked partly fulfilled, `fluid_api("/api/order_fulfillments?order_id=<id>", "GET")` to see what already shipped. Only the unshipped items need a notice.
4. Leave out orders shipping outside the US unless the user says to treat them the same (most other countries have their own rules), and say how many you left out.
5. If there are none, say so in one line, save the record (step 6) and stop.

## 3. Sort by risk

For each order, compute days until its ship-by date and sort it:

- **Past due:** ship-by date has passed. A notice is overdue; send it now with an honest new date.
- **Due within 3 days:** the notice must go before the ship-by date.
- **On track:** more than 3 days left. List the count only.

For each past-due and due-soon order, find out why it's stuck in one line: the warehouse it's routed to, the items still waiting (`fluid_api("/api/v202506/orders/<id>", "GET")` for its items), and whether those items are out of stock. Group orders by cause: same product, same warehouse, or no clear cause.

Show the user a short summary first: how many orders, total value, how many past due and due soon, and the biggest cause (for example, "41 of the 52 late orders are waiting on the Glow Serum at the Dallas warehouse").

## 4. Draft the notices

1. **Check what was already sent.** For each order, `fluid_api("/api/company/v2026-10/messages?customer_id=<customer id>&query=<order number>&created_after=<order date>", "GET")`. If a delay notice for this order is already there, keep its new date and skip the order unless that date has also passed.
2. **Get a new ship date from the user** for each cause group in one `steps` panel: a definite date they can keep, or "unknown". Don't guess one.
3. **Pick the notice type** for each order, following the rule:
   - **First delay, definite new date of 30 days or less past the original:** tell the buyer the new date and that they can cancel for a full refund. If they don't answer, they agree to the delay.
   - **New date more than 30 days out, or unknown:** tell the buyer the new date (or that you don't know it), and that the order **will be cancelled and refunded unless they reply to agree** to wait. Unknown dates must say so plainly.
   - **A second delay** (the order already had a notice and that date passed): the buyer must reply to agree to wait, or the order is cancelled and refunded by the earlier date.
4. **Write each notice** in the buyer's language when the order shows one, and short and plain: the order number, what hasn't shipped, the new date (or that it's unknown), the buyer's choice and how to make it (reply to the email), when the refund will arrive if they cancel, and who it's from. Include no promotion. Show one example of each type to the user.

## 5. Send what the user approves

For each group of orders with the same notice type and new date, one card at a time, at most 3 per turn:

- Card title `Send delay notices for <n> orders`, body listing order numbers, buyers, the new date and the full notice text.
- After Approve, for each order: `fluid_api("/api/company/v2026-10/messages/email", "POST", { "customer_id": <customer id>, "subject": "Update on your order <order number>", "text": "<notice>", "message_type": "transactional", "reply_to": "<reply address>", "idempotency_key": "ship-delay-<order number>-<new date>" })`. The idempotency key makes a repeat run safe.
- Then read each one back with `fluid_api("/api/company/v2026-10/messages?customer_id=<customer id>&query=<order number>", "GET")` and report how many were accepted, and any Fluid refused with its reason in plain words.

When the user asks for text messages too, send the same notice through `/api/company/v2026-10/messages/sms` with `customer_id`, `text` and `message_type: "transactional"`, also only after approval.

## 6. Save the record

Write `shipping-notices/{{today}}.md` with `write_file`:

- Date, company, who ran it ({{user.name}}, {{user.email}}), and the ship-by rule used.
- Every past-due and due-soon order: order number, order date, ship-by date, cause, notice type, new date, and whether the notice was sent (with the time) or why not.
- The count and value of on-track orders.
- Open items: orders past due with no notice, buyers who asked to cancel (fill in from replies the user forwards), and the date of the next run, which is the earliest ship-by date among on-track orders minus 3 days.

End with the path to the record and one line per cause group on what would stop it happening again, such as moving a launch's ship date or switching a market to another warehouse.
