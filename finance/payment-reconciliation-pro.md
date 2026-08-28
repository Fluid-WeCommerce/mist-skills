---
name: Payment Reconciliation Pro
description: Deep reconciliation of Fluid's payment ledger against every connected PSP/gateway/APM. Covers all accounts, classifies each discrepancy by root cause, and produces prioritized action items with severity ratings. Outputs a self-contained HTML report saved to the Desktop.
icon: shield-check
---

# Goal

Reconcile `{{company.name}}`'s Fluid payment records against every connected PSP, gateway, and APM for a specified time window. Go beyond simple count matching — classify every discrepancy by root cause, assign severity, and produce a prioritized action item list. Produce an HTML report saved to `~/Desktop`.

---

# Steps

## 1 — Get parameters

Ask the user for:
- **Company name** (e.g. "Neumi", "TUSHY") — skip if already set in `{{company.name}}`
- **Timeframe** — e.g. "last 6 hours", "last 7 days", or an explicit start/end date
- **Environment** — **Sandbox/test** or **Production/live**? Ask explicitly — do not default to either.

Parse the timeframe into UTC start and end timestamps. Confirm all three before proceeding.

---

## 2 — Pull Fluid's transaction ledger + PSP credentials

### Path A — Rails runner (preferred; gives decrypted credentials)

Run from `/Users/bendaley/Desktop/code/work/fluid`:

```bash
COMPANY="<COMPANY_NAME>" \
START_AT="<YYYY-MM-DD HH:MM:SS>" \
END_AT="<YYYY-MM-DD HH:MM:SS>" \
SANDBOX="<true|false>" \
bundle exec rails runner - <<'RUBY'
require 'json'

company    = Company.find_by!(name: ENV.fetch('COMPANY'))
start_at   = Time.parse(ENV.fetch('START_AT') + ' UTC')
end_at     = Time.parse(ENV.fetch('END_AT') + ' UTC')
sandbox_mode = ENV.fetch('SANDBOX', 'false') == 'true'

payments = Payments::Payment
  .where(company_id: company.id)
  .where(created_at: start_at..end_at)
  .where(action: %w[capture purchase settle charge agreement])
  .where(status: %w[success declined error])
  .includes(:payment_account)

fluid_txns = payments.map do |p|
  {
    fluid_id:           p.slug,
    psp_transaction_id: p.transaction_id,
    payment_account_id: p.payment_account_id,
    action:             p.action,
    status:             p.status,
    amount_cents:       p.amount ? (p.amount * 100).round : nil,
    currency_code:      p.currency_code,
    response_message:   p.response_message,
    response_status:    p.response_status,
    created_at:         p.created_at.utc.iso8601,
  }
end

sandbox_mode_val = sandbox_mode
account_scope = Payments::PaymentAccount
  .where(company_id: company.id, active: true)
  .kept
accounts = (sandbox_mode_val ? account_scope.select(&:sandbox?) : account_scope.reject(&:sandbox?)).map do |pa|
  {
    id:                pa.id,
    display_name:      pa.display_name.presence || pa.name,
    integration_class: pa.integration_class,
    adapter_class:     pa.adapter_class,
    credentials:       pa.credentials,
    sandbox:           pa.sandbox?,
  }
end

puts JSON.pretty_generate({
  company:          company.name,
  start_at:         start_at.iso8601,
  end_at:           end_at.iso8601,
  fluid_total_txns: fluid_txns.size,
  fluid_txns:       fluid_txns,
  payment_accounts: accounts,
})
RUBY
```

### Path B — Fluid API (fallback; credentials must be provided manually)

If Rails runner is unavailable, use the Fluid API. Requires a valid `fluid-token`:

```bash
TOKEN=$(fluid-token)
# Paginate all transactions in window using cursor pagination
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.fluid.app/api/v202506/company_transactions?page[limit]=100&filter[type]=<test|live>&sorted_by=created_at_desc"
```

Continue paginating with `page[cursor]=<next_cursor>` until `next_cursor` is null or `created_at` falls before the window start. Filter results to the window client-side.

**Note when using Path B:** PSP credentials are obfuscated in the API response. You must ask the user to provide each active PSP's API key manually before proceeding to Step 3.

Also fetch payment accounts:
```bash
curl -s -H "Authorization: Bearer $TOKEN" "https://api.fluid.app/api/payment_accounts"
```

---

## 3 — Fetch PSP transaction data

For each entry in `payment_accounts`, call that provider's API for the same date window. Fetch **all** pages before reconciling.

**Match key:** Fluid's `psp_transaction_id` must match the PSP's transaction ID exactly. Blank `psp_transaction_id` → pre-classify as `GATEWAY_TIMEOUT` (see Step 4).

---

### Stripe (`StripePaymentIntentsGateway`)

Credential: `credentials[:gateway_token]` (the `sk_live_...` or `sk_test_...` secret key)

Paginate payment intents. Use `expand[]=data.charges` to get nested charge data in one call:

```bash
curl "https://api.stripe.com/v1/payment_intents?created[gte]=<UNIX_START>&created[lte]=<UNIX_END>&limit=100&expand[]=data.charges" \
  -H "Authorization: Bearer <gateway_token>"
# Paginate: repeat with starting_after=<last_id> while has_more=true
```

Extract per intent: `id`, `amount` (cents), `currency`, `status`, `created`,
`last_payment_error.code`, `last_payment_error.message`, `metadata`,
`charges.data[0].disputed`, `charges.data[0].refunds.total_count`.

Stripe status mapping: `succeeded` → success; `requires_payment_method` / `canceled` / `requires_action` → declined.

---

### Braintree (`BraintreeGateway`)

Credentials: `merchant_id`, `public_key`, `private_key`

```bash
curl -s -X POST \
  "https://api.braintreegateway.com/merchants/<merchant_id>/transactions/advanced_search" \
  -u "<public_key>:<private_key>" \
  -H "Content-Type: application/xml" \
  -H "X-ApiVersion: 6" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<search>
  <created-at>
    <min type="datetime"><START_ISO8601_UTC></min>
    <max type="datetime"><END_ISO8601_UTC></max>
  </created-at>
</search>'
```

Extract per `<transaction>`: `<id>`, `<amount>`, `<currency-iso-code>`, `<status>`,
`<created-at>`, `<processor-response-code>`, `<gateway-rejection-reason>`.

Status mapping: `settled` / `submitted_for_settlement` → success; `processor_declined` / `gateway_rejected` / `failed` → declined.

---

### dLocal

Credentials: `dlocal_login`, `dlocal_trans_key`, `dlocal_secret_key`

```bash
X_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
SIGNATURE=$(echo -n "${DLOCAL_LOGIN}${X_DATE}" | openssl dgst -sha256 -hmac "${DLOCAL_SECRET_KEY}" | cut -d' ' -f2)
AUTH="V2-HMAC-SHA256, Signature: ${SIGNATURE}"

curl "https://api.dlocal.com/payments?page=1&page_size=100" \
  -H "X-Login: ${DLOCAL_LOGIN}" \
  -H "X-Trans-Key: ${DLOCAL_TRANS_KEY}" \
  -H "X-Date: ${X_DATE}" \
  -H "Authorization: ${AUTH}"
```

Filter by `created_date` within window. Paginate with `page` until no more results.

Extract: `id`, `amount`, `currency`, `status`, `status_code`, `status_detail`, `created_date`.

Status mapping: `PAID` / `AUTHORIZED` → success; `REJECTED` / `CANCELLED` → declined.

---

### PayPal

Credentials: `client_id`, `client_secret`

```bash
# Get access token
curl -X POST "https://api-m.paypal.com/v1/oauth2/token" \
  -u "<client_id>:<client_secret>" \
  -d "grant_type=client_credentials"

# Fetch all statuses (not just settled)
curl "https://api-m.paypal.com/v1/reporting/transactions?start_date=<ISO8601>&end_date=<ISO8601>&fields=all&page_size=100&page=1" \
  -H "Authorization: Bearer <access_token>"
```

Paginate via `total_pages`. Extract: `transaction_id`, `transaction_amount`, `transaction_status`, `transaction_initiation_date`, `reason_code`.

Status mapping: `S` (success) → success; `D` (denied) / `V` (voided) → declined; `P` (pending) → note separately.

---

### PPRO (European APMs)

No direct transaction listing API available.

- Record Fluid's count and total for PPRO-routed transactions.
- Output in report: "Manual reconciliation required — log into PPRO merchant portal."
- Pre-classify all Fluid PPRO transactions as `MANUAL_VERIFICATION_REQUIRED`.

---

### Citcon UPI (APAC APMs)

```bash
curl "https://api.citconpay.com/v2/payments?start_time=<UNIX_TS>&end_time=<UNIX_TS>&limit=100" \
  -H "Authorization: <upi_api_key>"
```

If endpoint returns 404 or is undocumented: record Fluid's count/total and mark as `MANUAL_VERIFICATION_REQUIRED`. Note in report: "Citcon — direct API unavailable; check Citcon merchant dashboard."

---

### Other / unknown adapter classes

Record Fluid's count and total, mark all as `MANUAL_VERIFICATION_REQUIRED`.

---

## 4 — Reconcile + classify root causes

For each payment account, match Fluid transactions against PSP transactions by `psp_transaction_id` ↔ PSP transaction ID.

Classify every discrepancy into exactly one root cause:

| Root Cause | Signal | Severity |
|---|---|---|
| `UNRECORDED_SUCCESS` | In PSP (succeeded), not in Fluid | HIGH |
| `STATUS_DISAGREEMENT` | Matched by ID; Fluid=success, PSP=declined (or vice versa) | HIGH |
| `PSP_DISPUTE` | Matched; Stripe `charges.data[0].disputed = true` | HIGH |
| `AMOUNT_DELTA` | Matched by ID; amounts differ by >1 cent | MEDIUM |
| `ORPHANED_REFUND_ID` | Fluid `psp_transaction_id` starts with `re_` | MEDIUM |
| `GATEWAY_TIMEOUT` | Fluid declined/error, `psp_transaction_id` is blank | MEDIUM |
| `PSP_DIRECT_CHARGE` | In PSP (succeeded), not in Fluid; likely created outside Fluid | LOW |
| `UNRESOLVED_DECLINE` | In Fluid (declined), not in PSP | LOW |
| `MANUAL_VERIFICATION_REQUIRED` | PSP has no direct API (PPRO, Citcon, unknown) | INFO |

Distinguish `UNRECORDED_SUCCESS` from `PSP_DIRECT_CHARGE` by checking Stripe metadata: if `metadata` is empty and `description` contains "Testing Blueprints" or similar non-Fluid marker, classify as `PSP_DIRECT_CHARGE`.

Also track:
- **Matched & clean** — matched by ID, amounts agree, statuses agree → no action needed

---

## 5 — Generate action items

After classifying all discrepancies, produce a numbered action item list sorted by severity (HIGH first). Each item:

```
[HIGH]  #1 — UNRECORDED_SUCCESS
        pi_3TzLJoAIZQxuuuFb3Wp7Vz1V · $59.99 USD · 2026-07-31T18:38Z
        Stripe shows this payment succeeded but Fluid has no record.
        → Engineering: Check if a Stripe webhook was dropped for this PI.
          Look in Stripe Dashboard > Developers > Webhooks for failed deliveries.

[MEDIUM] #2 — ORPHANED_REFUND_ID
        fpi_4j5ecbpvrzajezvsd3hc9h · $4,660.00 USD
        Fluid stored a refund ID (re_3Tz...) as the transaction ID — data bug.
        → Engineering: Update payments.transaction_id to the originating PI.

[MEDIUM] #3 — GATEWAY_TIMEOUT (6 records)
        6 × $1.00 USD declined, no Stripe PI ID · 2026-07-31T18:56-18:57Z
        Gateway never responded; Fluid recorded the attempt but Stripe has no record.
        → Support: Confirm customers were not charged. No Stripe-side action needed.
```

---

## 6 — Generate HTML report + save to Desktop

Generate a self-contained HTML file saved to:

```
~/Desktop/recon_<company_slug>_<YYYYMMDD_HHMMSS>.html
```

The report must include:

1. **Header** — company name, subdomain, period, environment, generated timestamp, run by
2. **Status badge** — CLEAN (green) or `N ISSUES` (amber/red based on count)
3. **Per-PSP summary grid** — one row per payment account: name, Fluid count/total, PSP count/total, match rate %, status chip
4. **Action Items section** — the numbered list from Step 5, color-coded by severity (red=HIGH, amber=MEDIUM, blue=LOW, grey=INFO). This appears before the detail tables.
5. **Detail tables** — one collapsible section per root cause category, showing transaction-level rows
6. **Matched & Clean** — count of clean matches as a positive signal at the bottom

Design: white cards on light grey background, inline CSS only, no external dependencies. Color system: green=#16a34a, amber=#d97706, red=#dc2626, blue=#2563eb.

Print the full file path when done.

---

## Notes

- Never default sandbox vs production — always ask explicitly
- Paginate all PSP APIs fully before reconciling
- If a PSP API call fails (auth error, timeout, rate limit), note the failure in that account's section and continue
- For Fluid totals in the summary, sum only `success` status transactions
- All amounts formatted as `$X,XXX.XX <CURRENCY>` — never raw cents, never `$` prefix for non-USD
- Use Path B (Fluid API) when Rails runner is unavailable, noting credential limitations
- `MANUAL_VERIFICATION_REQUIRED` items are informational — don't count them in the discrepancy total unless the user asks
