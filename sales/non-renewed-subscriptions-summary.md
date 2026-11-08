---
name: Non-Renewed Subscriptions Summary
description: It provides a summary of subscriptions that were not renewed for various reasons
icon: credit-card
---

# Goal

Give a clear picture of the subscriptions that stopped renewing: how many there are, how much recurring revenue they represent, why they lapsed, and which ones are worth trying to win back.

Fluid subscription statuses are `pending`, `active`, `paused`, `past_due`, and `cancelled`. Non-renewed means `past_due` plus `cancelled`, and the two are different stories — a `past_due` subscription is a charge that did not go through and is often recoverable, while a `cancelled` one has stopped (`billing_cycle_limit_reached: true` marks the ones that simply reached the end of their term). Keep them separate throughout; never merge them into a single "lost" number. Below, "failed" means `past_due` and "expired" means `cancelled`.

This skill is read-only. It never cancels a subscription, never retries a charge, and never modifies any record.

# Steps

1. Fetch the non-renewed subscriptions with `GET /api/subscriptions?status=past_due&per_page=100` and `GET /api/subscriptions?status=cancelled&per_page=100`. This endpoint is page-numbered: keep incrementing `page` until you reach `meta.pagination.total_pages`.

2. Keep the two sets apart: `past_due` is failed, `cancelled` is expired. `paused` and `pending` subscriptions are not non-renewed — leave them out.

3. Report the headline: the count of failed subscriptions and the sum of their `price` × `quantity`, and separately the count of expired subscriptions and the same sum. The failed total is the recoverable figure — label it as such.

4. Group the failed subscriptions by `failure_reason` (use `decline_category` when it is set) and rank the groups by total dollars at risk. `failure_reason` is a free-text string written by whatever failed the charge, not a fixed code set, so bucket similar wordings together — expired card, insufficient funds, declined, gateway error — and keep an explicit "other" bucket instead of inventing a taxonomy. Show the raw strings you folded into each bucket.

5. Split both groups by recency using `last_failed_at` (failed) and `cancelled_at` (expired): lapsed within the last 30 days versus older. Something that failed last week is worth a phone call; something that failed eight months ago is churn. Report both, clearly labeled, and do not let old records inflate the recoverable headline.

6. Show plan names, not raw ids: read the embedded `subscription_plan`, and fall back to `GET /api/subscription_plans` for any plan it doesn't name.

7. Build the call list: the top 20 non-renewed subscriptions by amount, as a table with customer, plan name, amount, status (failed or expired), failure-reason bucket, the date it lapsed, and how many days it has been lapsed. This table is the deliverable.

8. Close with one recommendation: the single failure cause worth fixing first, and the dollar figure behind it.

9. Be honest about the data. Never report a percentage without the counts underneath it. If a field is null or empty across the whole account, say so plainly instead of inferring a value. If there are no non-renewed subscriptions at all, say that in one line rather than padding the output.
