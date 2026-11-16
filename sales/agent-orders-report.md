---
name: Agent orders report
description: Show how many orders AI shopping agents placed in the last 30 days, which agents they were, how sure Fluid is, and how those orders compare with the rest on order value and cancellations.
icon: bot
---

# Goal

AI shopping agents (ChatGPT, Gemini, Muse and others) now complete purchases on merchants' own checkouts. Fluid records which agent placed an order and how it knows. Use that record to tell {{company.name}} how much revenue arrives through agents, which agents send it, and whether those orders behave differently from the rest, so the merchant can decide where to invest (agent-readable catalog, UCP, product data) and whether anything is going wrong.

This skill only reads orders. It never changes an order, a setting or the catalog.

Today is {{today}}.

# Steps

1. **Pull the orders.** Page through `fluid_api("/api/v202604/orders?filter[start_date]={{thirty_days_ago}}&filter[end_date]={{today}}&page[limit]=100", "GET")`, passing `meta.pagination.next_cursor` back as `page[cursor]` until it is null. This list has no total count and no stats block, so count rows yourself. Stop at 20 pages (2,000 orders) and say so if you hit the cap; the report then covers the newest 2,000 orders only.
2. **Check you can see the agent field.** Each order has an `agent` object or `null`. The field is returned only to a company admin; a rep's response leaves it out. If no order on the first page has an `agent` key at all (not even `null`), stop and tell the user this sign-in cannot see agent data, and that an admin must run the skill.
3. **Split the orders.** From each order take `agent.name`, `agent.classification` (`verified`, `declared` or `inferred`), `agent.signals`, `status`, `financial_status`, `amount` (fall back to `amount_in_base` when `amount` is blank or zero), `currency_code`, `items_count`, `source` and `created_at`. Put each order in one of four groups:
   - **Verified agent**: `classification` is `verified` (a signature checked against the agent's published key).
   - **Declared agent**: `declared` (the agent named itself, for example in a UCP header or a known agent user agent).
   - **Possible agent**: `inferred` (circumstantial signals only, such as an agent payment card or a headless browser). Treat these as a guess.
   - **No agent signal**: `agent` is `null`.
4. **Compare the groups.** For each group compute: order count and share of all orders; total and average order value in `amount_in_base`; share of orders in `cancelled` status; average `items_count`. Use `amount_in_base` for every cross-order total so currencies are not mixed; show `currency_code` only when naming a single order. Leave out a figure when its group has fewer than 5 orders and say "too few to compare" instead.
5. **Break down the agent orders.** Group verified and declared orders by `agent.name`: orders, revenue, average order value, cancelled share. List the `signals` seen for each name. Show possible-agent orders as one line each group, not per name.
6. **Look at the trend.** Count agent orders (verified plus declared) per week across the 30 days, and say whether the count is rising, flat or falling. With fewer than 10 agent orders, skip the trend and say the volume is too small to read.
7. **Look for trouble.** Flag, with order numbers (at most 10 each):
   - any agent name whose cancelled share is clearly above the no-agent group's;
   - orders in `pending_review` that have an agent, since those may be held by fraud screening: list them and point the user to the Fraud review queue skill rather than deciding here.
8. **Report.** Open with one sentence: of N orders in the window, how many came from verified or declared agents and what share of revenue that is. Then the comparison table (group, orders, share, revenue, average order value, cancelled share), the per-agent table, the trend line and the flags. Close with ONE recommendation grounded in the numbers, for example: "agents placed X orders worth Y; run Agent Checkout Dry Run to find where they get stuck", or "no agent orders yet; nothing to change, re-run next month".

# What this report does not show

- Only orders that were completed or at least created. An agent that was blocked at checkout or abandoned before payment leaves no order and does not appear here, so low numbers do not prove agents are not trying.
- "No agent signal" does not mean a human. It means Fluid saw nothing that identified an agent.
- `inferred` is a guess. Do not add it to the agent totals or quote it as agent revenue.
- Fluid records and never blocks or scores an order on this signal, so nothing here says an order was risky.
