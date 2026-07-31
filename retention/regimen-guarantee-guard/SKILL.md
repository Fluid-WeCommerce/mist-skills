---
name: Regimen Guarantee Guard
description: Find subscription customers at risk of churning or breaking a regimen guarantee, then produce evidence-backed actions, compliant outreach drafts, and a CEO summary without changing production data.
icon: shield-check
---

# Regimen Guarantee Guard

Run this checklist verbatim. Stay read-only. Never send outreach, change a
subscription, or write customer data.

Read `references/cohort-rules.md` before classifying anyone. Read
`references/copy-templates.md` before drafting the deliverable.

## 1. Start an auditable run

Call `steps` exactly once with one live reveal step:

```json
{
  "title": "Regimen guarantee risk scan",
  "intro": "Read-only analysis for {{company.name}} as of {{today}}.",
  "steps": [
    {
      "id": "guard-progress",
      "title": "Building the retention action pack",
      "kind": "reveal",
      "mode": "live",
      "items": [
        {"id": "subscriptions", "label": "Load every subscription and delivery"},
        {"id": "engagement", "label": "Cross-check optional engagement data"},
        {"id": "cohorts", "label": "Classify evidence-backed risk cohorts"},
        {"id": "deliverable", "label": "Reconcile and render the action pack"}
      ]
    }
  ]
}
```

Keep the returned `steps_id`. Call `steps_mark_item` only after the real work
for that item succeeds. If a source is unavailable, recording the exact failed
read and its downstream limitation counts as completing that read-only check.

State the active company as `{{company.name}}`, the API context as
`{{company.api_base}}`, and the analysis date as `{{today}}`. Do not hardcode a
company ID or hostname.

Collect or infer only from company-authored sources:

- guarantee rules, including delivery count and eligibility window
- app-download, check-in, dosage, and progress-photo requirements
- core-formula to root-cause-booster mappings
- brand voice and prohibited claims
- recovery-rate assumption, if the company has approved one

If a policy input is unavailable, write `Unknown — policy not supplied`. Do not
substitute a plausible industry default.

## 2. Pull subscription evidence

Call
`fluid_api("/api/subscriptions?per_page=100&page=1&sort_by=created_at&sort_direction=desc", "GET")`.
Follow `meta.pagination.total_pages`, repeating the same call with `page=2`,
`page=3`, and so on until every page is loaded. Do not use the
customer-scoped `/api/checkout/v2026-04/subscriptions` endpoint. Preserve:

- subscription token and status
- customer ID, name, and email
- created date
- last successful and failed billing dates
- next billing date and decline count
- price, quantity, currency, plan, and variant

For every subscription token, call:

`fluid_api("/api/subscriptions/{subscription_token}/orders?sort_by=created_at&sort_direction=desc", "GET")`

Keep only successful, non-refunded deliveries when counting bottles. Record
returns and refunds separately. Do not assume one order equals one bottle; use
line quantity and the catalog's unit definition.

Use `fluid_catalog_index` or a read-only `fluid_api` catalog endpoint to map each
subscribed variant to a core formula, booster, or other product. Never classify
from a product title alone when structured tags, collections, or variant data
contradict it.

Reconcile subscriptions fetched against `meta.pagination.total_count`, then
call `steps_mark_item` with the saved `steps_id`, `step_id:
"guard-progress"`, and `item_id: "subscriptions"`.

## 3. Inspect optional engagement evidence

Call `db_schema` before any `db_query`. Begin with
`db_schema({"mode":"search","keyword":"subscription"})`, then make at most three
more searches for `app`, `check_in`, and `photo`. Look for app
download/activation, check-in, dosage/adherence, progress-photo,
recovery-attempt, root-cause, or quiz fields.

If relevant tables exist, call `db_schema` in `tables` mode for those exact
table names. Only then call `db_query` with a read-only, parameterized `SELECT`
using confirmed column names, scoped to the customer IDs from step 2, and
capped at 1,000 rows. Include the exact query and params in the final evidence
appendix. Never guess a table or column.

If the reporting database is unavailable, a field is absent, or a customer has
no row, set that condition to `Unknown — data unavailable`. Missing evidence is
never `met`, `missed`, `false`, or zero.

After either the verified query or the documented unavailable result, call
`steps_mark_item` for `item_id: "engagement"`.

## 4. Compute one evidence record per customer

Use the formulas in `references/cohort-rules.md`. At minimum compute:

- months on regimen
- successful bottles delivered in the trailing 180 days
- bottles required by today to remain on pace
- days since last successful charge
- app downloaded within the required window: `Met`, `Missed`, or `Unknown`
- check-ins, dosage, and progress photos: `Met`, `Missed`, or `Unknown`
- recovery attempt after the latest failure: `Yes`, `No`, or `Unknown`
- subscribed core formula and expected booster
- dollar value at risk

Prefix every calculated, projected, estimated, or inferred value with
`Assumption:`. Dates, statuses, counts, and prices returned directly by a source
are verified facts; arithmetic and business projections are assumptions.

## 5. Assign and prioritize cohorts

Apply the exact rules and precedence in `references/cohort-rules.md`. A customer
appears once in the action table, under the highest-priority qualifying cohort.
Keep all secondary flags in the reason/evidence field.

Exclude staff, test, refunded-only, and non-subscription accounts when the data
proves that status. If it does not, mark eligibility unknown rather than
excluding them.

Reconcile cohort counts against unique evaluated customers, then call
`steps_mark_item` for `item_id: "cohorts"`.

## 6. Emit the exact deliverable

Use the templates in `references/copy-templates.md` without changing their
section order:

1. More-for-Less header
2. Data coverage and policy inputs
3. Prioritized customer-level action table
4. Cohort outreach drafts
5. One-screen CEO summary
6. Evidence appendix

Every table row must contain customer, cohort, specific reason, dollar at risk,
and exactly one next action. Draft one outreach message for each non-empty
cohort, but do not send it.

When no subscribers qualify, still render every section, show zero verified
rows, and explain which source or policy input would change the answer. Never
fill an empty demo with synthetic customers.

## 7. Reconcile before finishing

Prove:

- subscriptions fetched = subscriptions evaluated + evidenced exclusions
- customers evaluated = action-table customers + non-qualifying customers
- action-table customers are unique
- every cohort row cites its triggering evidence
- every unknown field remains unknown downstream
- every inferred number begins with `Assumption:`
- no production mutation or message-send tool was used

Call `steps_mark_item` for `item_id: "deliverable"` only after these checks
pass. End with the exact sentence:
`No production data or customer communications were changed.`
