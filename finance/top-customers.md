---
name: Top customers by lifetime value
description: Rank customers by lifetime order revenue. Useful for VIP outreach.
icon: trophy
---

# Goal

Identify the top 20 customers at `{{company.name}}` by lifetime order revenue.

# Steps

1. Call `fluid_api("/api/v202604/customers?sort=-total_spent_cents&limit=20", "GET")` to fetch the top 20 by spend.
2. For each customer, optionally call `fluid_api("/api/v202604/customers/<id>/orders?limit=1&sort=-created_at", "GET")` to grab the most recent order date.
3. Render a Markdown table with: rank, name, email, lifetime spend (in dollars), order count, last order date.
4. After the table, add a "Cohort notes" section: longest tenure customer, newest entrant in the top 20, average order count.
5. If the company has fewer than 20 customers, render whatever's there and say so.
