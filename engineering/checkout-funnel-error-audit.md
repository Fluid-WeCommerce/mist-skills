---
name: Storefront & checkout-funnel error audit
description: Correlate Lighthouse performance regressions and payment error-rate spikes with lost conversions, and rank the fix with the biggest payoff.
icon: activity
---

# Goal

Find the technical issue costing `{{company.name}}` the most conversions right now — whether that's a slow page or a payment-processing regression — and give a single, prioritized fix.

# Steps

1. Call `fluid_api("/api/v202506/pages?limit=100", "GET")`, paginating until exhausted, filter to `publish: true`. For each published page, call `fluid_api("/api/v202506/pages/<id>/lighthouses?limit=1", "GET")` to get its latest scan. Skip a page if it has never been scanned and note the count skipped.
2. Rank pages by `core_metrics.performance_score` ascending (worst first). For the bottom 5, pull `category_scores` (seo/performance/accessibility/best-practices) and the specific failing `core_metrics` (`largest_contentful_paint`, `total_blocking_time`, `cumulative_layout_shift`) with their `_rating` fields — call out any `"poor"` rating by name.
3. Separately, call `fluid_api("/api/v202506/payments/reports/kpis?period=last_7_days", "GET")` and the same with `period=last_30_days`. Compare `error_rate.current` against `error_rate.previous` in both windows — a rising error rate on top of a slow storefront compounds: shoppers who make it through a slow page then hit a payment failure are the most expensive kind of lost order.
4. Estimate lost-conversion impact: pull `fluid_api("/api/v202506/orders/stats", "GET")` for `average_amount_base` and multiply by the estimated order-volume drop implied by the error-rate delta (`transaction_count.growth` from the same `kpis` call) — be explicit that this is a rough order-of-magnitude estimate, not an attributed A/B result.
5. Render two sections: **Slowest pages** (table: page title, performance score, worst metric + rating, last scanned) and **Payment error trend** (7-day vs. 30-day error rate, direction, estimated $ impact if the trend continues).
6. End with a **Decision**: name the single highest-payoff fix — the worst-performing high-traffic page, or the payment error trend if it's actively worsening — and state why it beats the runner-up.
7. If no page has ever been scanned, say Lighthouse data doesn't exist yet and suggest running a scan before this audit can rank anything.
