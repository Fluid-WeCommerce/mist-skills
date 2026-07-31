---
name: Non-Renewed Subscriptions Summary
description: It provides a summary of subscriptions that were not renewed for various reasons
icon: credit-card
---

# Goal

Give a clear picture of the subscriptions that stopped renewing: how many there are, how much recurring revenue they represent, why they lapsed, and which ones are worth trying to win back.

Fluid subscriptions have three states: active, expired, and failed. Non-renewed means expired plus failed, and the two are different stories — a failed subscription is a charge that did not go through and is often recoverable, while an expired one reached the end of its term. Keep them separate throughout; never merge them into a single "lost" number.

This skill is read-only. It never cancels a subscription, never retries a charge, and never modifies any record.

# Steps

1. Fetch the subscriptions with `GET /api/subscriptions`. Do not assume which filter or pagination parameters exist — make one plain, unfiltered call first, inspect the actual response shape and any pagination envelope, then adapt to it. If the account is large enough that listing is slow, switch to `GET /api/subscriptions/export_csv`, which returns the same data as CSV.

2. Split the records by status into active, expired, and failed. Everything that is not active is non-renewed.

3. Report the headline: the count of failed subscriptions and the sum of their amount, and separately the count of expired subscriptions and the sum of their amount. The failed total is the recoverable figure — label it as such.

4. Group the failed subscriptions by `failure_reason` and rank the groups by total dollars at risk. `failure_reason` is a free-text string written by whatever failed the charge, not a fixed code set, so bucket similar wordings together — expired card, insufficient funds, declined, gateway error — and keep an explicit "other" bucket instead of inventing a taxonomy. Show the raw strings you folded into each bucket.

5. Split both groups by recency using `renewed_at` and `expiry_date`: lapsed within the last 30 days versus older. Something that failed last week is worth a phone call; something that failed eight months ago is churn. Report both, clearly labeled, and do not let old records inflate the recoverable headline.

6. Resolve plan names by calling `GET /api/subscription_plans` and mapping `plan_id`, so the output shows plan names rather than raw ids.

7. Build the call list: the top 20 non-renewed subscriptions by amount, as a table with customer, plan name, amount, status (failed or expired), failure-reason bucket, the date it lapsed, and how many days it has been lapsed. This table is the deliverable.

8. Close with one recommendation: the single failure cause worth fixing first, and the dollar figure behind it.

9. Be honest about the data. Never report a percentage without the counts underneath it. If a field is null or empty across the whole account, say so plainly instead of inferring a value. If there are no non-renewed subscriptions at all, say that in one line rather than padding the output.
