# Copy templates and output contract

## 1. More-for-Less header

Start with:

> **Regimen Guarantee Guard — More for Less**
> Replaces a retention analyst, lifecycle marketer, and BI dashboard: an
> estimated 2–3 week recurring cycle for three people becomes one read-only run
> button, executable daily.

Prefix the time estimate with `Assumption:` unless the company supplied and
verified it. Follow with:

> Custom retention flows like this are normally hand-built during launch week.
> Shipping the method to the Skill Library makes it reusable for the next
> subscription company on day one.

## 2. Data coverage and policy inputs

Render:

| Input | Coverage | Source |
|---|---|---|
| Subscriptions | {fetched}/{reported total} | `{exact endpoint}` |
| Order history | {customers covered}/{customers evaluated} | `{exact endpoint}` |
| App download | {covered}/{evaluated} or Unknown | `{table/query or unavailable}` |
| Check-ins | {covered}/{evaluated} or Unknown | `{table/query or unavailable}` |
| Progress photos | {covered}/{evaluated} or Unknown | `{table/query or unavailable}` |
| Root cause | {covered}/{evaluated} or Unknown | `{table/query or unavailable}` |

List the guarantee and regimen policy inputs beneath the table. Use
`Unknown — policy not supplied` where necessary.

## 3. Prioritized customer action table

Render exactly:

| Priority | Customer | Cohort | Specific reason and evidence | Dollar at risk | One next action |
|---:|---|---|---|---:|---|

Use one row per customer and one imperative next action. Do not expose email,
phone, or health/quiz details beyond what the operator needs.

## 4. Cohort outreach drafts

Draft only for non-empty cohorts. Never send.

### Silent Lapse

Subject: `A quick check on your regimen`

> We noticed an interruption in your subscription. Keeping deliveries on track
> can matter for regimen continuity. Review your billing details or reply if
> you would like help with the next step.

### Guarantee Breakage

Subject: `Keep your guarantee requirements on track`

> One of your guarantee requirements may need attention: {verified reason}.
> Review the requirement by {verified deadline}, or reply and our team can help
> you confirm what is still needed.

If the issue is missing evidence, say `We could not verify` rather than `You
missed`.

### Cliff Risk

Subject: `You are approaching the next regimen stage`

> You are around month {verified or Assumption: calculated month} of your
> regimen. {Company-cited results timeline}. Consistency matters, and our team
> is here if you have questions about staying on track.

Never promise that results will occur.

### Regimen Gap

Subject: `Review your regimen pairing`

> Your current regimen includes {verified core formula}. Based on the root cause
> you previously shared, {verified booster} is the matching option in the
> company's regimen guide. Review the pairing or speak with the appropriate
> company professional before changing your regimen.

Never infer a medical condition or claim to diagnose, cure, or treat.

Use the active company's brand voice. For a clinical-warm voice: sentence-case
headings, no exclamation marks, and never use `miracle`, `cure`, or `instant`.

## 5. One-screen CEO summary

Keep this section under 180 words:

- **Verified population:** subscriptions and unique customers evaluated
- **Revenue at risk:** sum of table values, prefixed `Assumption:`
- **Revenue recoverable:** `Assumption: revenue at risk × approved recovery
  rate`; otherwise `Unknown — recovery-rate assumption not supplied`
- **Guarantee-liability exposure:** verified affected customers plus an
  `Assumption:` monetary estimate only when the formula is disclosed
- **Coverage warning:** the single most decision-relevant missing source
- **Top three actions this week:** owner-ready actions in priority order

For an empty company, say the live cohort count is zero and that the analysis is
a readiness proof, not a retention finding.

## 6. Evidence appendix

Include:

- run date `{{today}}` and comparison date `{{thirty_days_ago}}`
- exact read-only API paths and query text
- raw fetched/evaluated/excluded counts
- cohort count reconciliation
- exclusions with evidence
- unknown fields and their downstream effect
- every calculation and assumption formula
- statement: `No production data or customer communications were changed.`
