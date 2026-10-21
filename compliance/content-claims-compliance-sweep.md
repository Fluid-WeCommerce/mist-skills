---
name: Content claims compliance sweep
description: Scan every product, page, and post through Fluid's compliance scanner for income/health-claim risk, and rank fixes by enforcement likelihood.
icon: shield-alert
---

# Goal

Sweep `{{company.name}}`'s product copy, storefront pages, and posts for risky income or health claims using Fluid's own compliance scanner, and produce a do-this-first remediation list.

# Steps

1. Pull the content inventory to scan: `fluid_api("/api/company/v1/products?per_page=100", "GET")`, `fluid_api("/api/v202506/pages?limit=100", "GET")` (filter `publish: true`), and, if reachable, posts. Paginate each until exhausted.
2. For every item, call its compliance-scan history: `fluid_api("/api/v202506/products/<id>/compliances?limit=1", "GET")` (and the equivalent `pages/<id>/compliances`, `posts/<id>/compliances`) to get the latest scan. Each returns `score`, `status`, `summary`, and `compliance_issues[]` from the `mlm_compliance` service. Skip items with no scan yet and count them separately — an unscanned page is a gap, not a clean bill of health.
3. Rank every scanned item by risk: `status` other than `"excellent"`/`"good"` first, then by `score` ascending. Read each flagged item's `compliance_issues[]` and `summary` for the actual language flagged — income claims ("guaranteed income," "quit your job"), health/disease claims ("cures," "treats," specific medical conditions), or missing required disclosures.
4. Group findings by severity:
   - **Critical** — explicit income-guarantee or disease-cure language likely to draw FTC/FDA attention.
   - **Should fix** — soft claims, missing disclaimers, or ambiguous language a regulator could still flag.
   - **Unscanned** — content never run through the compliance scanner (a coverage gap, list separately, don't score it).
5. Render a table: item (type + title), status, score, top issue summary, severity tier. Group the table by severity, most urgent first.
6. End with a **Decision**: the single highest-severity, highest-traffic item to fix first (cross-reference page traffic via `fluid_api("/api/v202506/pages/<id>/views", "GET")` if you need a tiebreaker between two Critical items), and whether the unscanned-content gap itself is large enough to be the bigger risk.
7. This is read-only — it reports findings and can draft replacement copy on request, but doesn't publish anything without explicit confirmation.
