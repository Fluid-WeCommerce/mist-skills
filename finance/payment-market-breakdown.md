---
name: Payment market breakdown
description: Analyze approval rates and blocked revenue by market and card type. Surfaces underperforming card-market combos and quantifies the recovery opportunity.
icon: activity
---

# Goal

Show where `{{company.name}}`'s payment performance breaks down by market and card type, quantify the blocked revenue, and give specific recommendations. No database or additional setup required — works from the payments API alone.

# Steps

1. Parse `$ARGUMENTS` for `days=N` (default 30) and `min_txns=N` (minimum transactions per group to suppress noise, default 5).

2. Compute the start timestamp: `{{today}}` minus `days` days at 00:00:00 UTC.

3. Fetch all transactions in the window by paginating `fluid_api("/api/payment/v2026-04/transactions?per_page=100&page=N", "GET")` until no more pages. Only include records where `created_at >= start`.

4. For each transaction, determine the country:
   - Use `metadata.country_code` if present.
   - Otherwise infer from `currency_code` using this map: USD→US, EUR→DE, GBP→GB, AUD→AU, CAD→CA, BRL→BR, MXN→MX, SGD→SG, INR→IN, TWD→TW, JPY→JP, KRW→KR. If the currency doesn't map, mark the country as `—`.

5. Compute overall stats across all transactions where `action` is `purchase` or `authorize`:
   - Total attempts, successful count, declined count, approval rate (%)
   - Total successful revenue in USD-equivalent (use the raw `amount_cents` sum — note this will be inflated for non-USD; flag that in the report)
   - Total blocked revenue (sum of `amount_cents` for declined transactions)
   - Refund count and refund rate (refunds / successful purchases)

6. Group remaining transactions by `currency_code × card_network × country`. For each group with at least `min_txns` attempts, compute:
   - Attempt count
   - Approval rate (%)
   - Successful revenue (sum of amount_cents for successful records, in local currency)
   - Blocked revenue (sum of amount_cents for declined records, in local currency)
   - Refund rate

7. Flag a group if: approval rate < 80% OR it accounts for more than 10% of total blocked revenue.

8. For each flagged group, generate a one-sentence recommendation using this logic:
   - Low approval + EUR/GBP/CAD/AUD: "Consider adding a local payment method (SEPA, PayPal, or regional debit) as an alternative for [country] customers."
   - Low approval + amex: "Amex has elevated decline rates in [country]. Offering Mastercard or Visa as preferred checkout options may recover this revenue."
   - Low approval + USD: "Investigate whether a gateway routing rule or fraud filter is applying incorrectly to [card_network] in the US."
   - Low approval + any: "Review gateway configuration for [card_network] transactions in [country] — decline rates are above baseline."
   - High refund rate (>10%): "High refund rate for [card_network]/[country] may indicate fulfillment or fraud patterns worth investigating."

9. Render the report in this structure:

```
[Company] — Payment Market Breakdown
Window: last [N] days  |  [X] total transactions fetched

OVERALL
  Approval rate    XX%
  Blocked revenue  [currency] X,XXX  (raw sum — non-USD amounts not converted)
  Refund rate      X%

BY MARKET × CARD TYPE  (min [N] transactions)

  Currency  Country  Card    Attempts  Approval  Blocked
  --------  -------  ------  --------  --------  -------
  ...rows sorted by blocked revenue descending...

FLAGGED COMBOS
  For each flagged group: "Currency / Country / Card — XX% approval, X,XXX blocked"
  → [Recommendation]

WHAT THIS REPORT COULD SHOW WITH ORDER + SUBSCRIPTION DATA
  - Which products have the highest payment failure rates (high-value items declining
    more than average suggests a fraud filter problem, not a card problem)
  - Subscription MRR sitting on underperforming card types — quantify churn risk
    before it happens
  - Customer LTV by card type and market — if Amex customers are worth 2x, optimizing
    their approval rate has outsized revenue impact
  - Retry success rate — of declined transactions, which ones were later recovered
    through a retry or dunning flow
```

10. If there are no flagged groups, say so — it means payment performance looks healthy across all markets. If there are fewer transactions than `min_txns` in every group, lower the threshold and re-run, or note that more transaction history is needed.
