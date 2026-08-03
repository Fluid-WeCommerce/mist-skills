---
name: Import Fidelity Auditor
description: Audit a completed Fluid onboarding import against its source storefront when product identity, variants, prices, subscriptions, inventory, images, or regional availability may not have carried over faithfully.
icon: scan-search
---

# Import Fidelity Auditor

Verify that a Fluid onboarding import preserved the source storefront's commerce data. This is a read-only post-import audit: do not modify source or Fluid records.

This differs from a catalog health check, which evaluates Fluid records internally, and from a claim-fidelity audit, which checks marketing substantiation. This skill compares source commerce evidence with the imported Fluid catalog.

## Evidence contract

Record the source storefront URL, active Fluid company, country/locale, active theme, audit time, and every endpoint or artifact used. Label unavailable fields and inferences as assumptions; never invent source values.

Use Fluid's documented API contract. Call `query_docs` before querying an unfamiliar resource. Use `fluid_api` for Fluid data and `crawl` for public source pages. The audit must remain read-only.

Do not claim completion unless:

- source and Fluid inventories are attached or linked;
- `matched + source-only = source total` and `matched + Fluid-only = Fluid total`;
- every Critical or High finding has reproducible source and Fluid evidence;
- Home, Shop or collection, and representative PDP evidence was manually spot-checked;
- confirmed findings, source ambiguities, assumptions, and discarded hypotheses are separate;
- both requested output files were reread and their IDs and counts reconcile.

## 1. Build independent inventories

Discover the source product universe from the union of sitemaps, structured catalog data, collections, Shop links, and PDPs. A missing sitemap entry is not proof that a product does not exist. A URL returning HTTP 200 is not proof it is a PDP; verify the rendered content and canonical identity.

Extract visible source products and variants with raw values for:

- title, handle, source ID, canonical URL, status, and regional availability;
- SKU, options, and variant cardinality;
- regular price, sale price, currency, and subscription cadence or trial;
- stock state and limited-unit messaging;
- image count and primary-image identity;
- memberships, subscriptions, add-ons, and relationships between products.

Query all corresponding Fluid products and variants, including draft, archived, delisted, and duplicate records. Fetch detail records when list endpoints omit variants or return aggregate fields.

Preserve raw values beside comparison-normalized values. Normalize only whitespace, currency formatting, URL parameters, and explicit option aliases.

## 2. Match conservatively

Match in this order:

1. SKU or source variant ID.
2. Source product ID or canonical URL/handle.
3. Exact normalized title plus exact option set.

Never silently merge uncertain candidates. Put them in **Needs Review** with all candidate records and evidence.

## 3. Compare field by field

Classify each difference as `Missing`, `Extra`, `Wrong value`, `Wrong state`, `Duplicate`, or `Source ambiguous`.

For every price comparison, report source regular and sale prices, Fluid variant ID, Fluid market row, list and sale prices, currency, and arithmetic. Compare source subscription cadence and trial terms to Fluid subscription plans; a numerically correct one-time price does not prove a recurring membership imported correctly.

Check image counts and primary images, options and variant cardinality, SKU placement, stock and publication state, regional rows, memberships, subscriptions, and add-ons.

## 4. Guard against false findings

- Treat product-list pricing as potentially aggregated across variants. Confirm any price defect on the product detail's exact variant and country row.
- Do not treat decorative scarcity counters as canonical inventory unless corroborated.
- Distinguish a Shop-card template label from a PDP's real stock and purchase state.
- Verify redirects, canonical URLs, page identity, and add-to-cart availability; HTTP status alone is insufficient.
- Reopen source evidence for every Critical and High finding and seek two evidence forms when possible: source page or structured data plus a Fluid API result.
- Keep a discarded-hypotheses ledger explaining why plausible findings were withdrawn.

## Severity

| Severity | Meaning |
| --- | --- |
| Critical | Wrong product identity, missing sellable product, wrong currency, materially wrong variant price, or unsafe publication state |
| High | Missing or duplicate variant, incorrect stock state, subscription mismatch, or broken primary image |
| Medium | Secondary image, metadata, option-label, or regional-row mismatch |
| Low | Cosmetic normalization that does not change purchasing behavior |

## 5. Produce and reconcile outputs

Write these files in the current project:

1. `import-fidelity-report.md`
2. `import-fidelity-discrepancies.csv`

The report must contain:

- executive summary with coverage, matched and unmatched counts, severity totals, confidence, and a CEO-ready More-for-Less statement;
- discrepancy table with ID, severity, product and variant, field, source value, Fluid value, evidence, and recommended fix;
- clean checks;
- Needs Review items;
- assumptions and unavailable evidence;
- discarded hypotheses;
- remediation checklist ordered by revenue and customer impact.

The CSV must carry the same finding IDs and counts as the report, with one addressable row per finding or explicitly grouped finding. Include variant IDs where applicable. Discarded hypotheses must not appear as active findings.

Before finishing, reread both files and calculate reconciliation explicitly. If the files disagree, fix them without rerunning settled evidence collection. Return exact paths plus a concise summary of confirmed Critical and High problems.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Trusting import receipt counts | Build source and Fluid inventories independently and reconcile both equations |
| Comparing a product rollup to a source default price | Compare the exact Fluid variant and market row |
| Calling a 200 response a live PDP | Verify canonical identity, product content, and purchase controls |
| Treating card badges as inventory truth | Corroborate with PDP and structured commerce state |
| Reporting recurring memberships as correct because prices match | Verify subscription plans, cadence, trial, and variant placement |
| Updating only one output after correcting a finding | Reread report and CSV, then align IDs, counts, and discarded items |
