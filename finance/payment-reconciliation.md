---
name: Payment Reconciliation
description: Compare Fluid's payment ledger against each connected PSP/gateway/APM for a given company and timeframe. Surfaces discrepancies in count, amount, and status between what Fluid recorded and what each provider recorded.
icon: shield-check
---

# Goal

Reconcile `{{company.name}}`'s Fluid payment records against every connected PSP, gateway, and APM for a specified time window. Surface any transactions that are in Fluid but not the provider, in the provider but not Fluid, or where amounts or statuses disagree. Produce a terminal report and save a copy to disk.

# Steps

## 1 — Get parameters

Ask the user for:
- **Company name** (e.g. "Neumi", "Kyani") — skip if already set in `{{company.name}}`
- **Timeframe** — e.g. "last 24 hours", "last 7 days", or an explicit start/end date
- **Environment** — **Sandbox/test** or **Production/live**? This determines which payment accounts are included and which PSP API credentials/endpoints are used. Ask explicitly — do not default to either.

Parse the timeframe into UTC start and end timestamps. Confirm all three before proceeding.

---

## 2 — Pull Fluid's transaction ledger + PSP credentials

Run the following script via Rails runner from the fluid repo. It queries the DB directly (the API has no date-range filter and credentials are obfuscated over the API).

```bash
COMPANY="<COMPANY_NAME>" \
START_AT="<YYYY-MM-DD HH:MM:SS UTC>" \
END_AT="<YYYY-MM-DD HH:MM:SS UTC>" \
SANDBOX="<true|false>" \
bundle exec rails runner - <<'RUBY'
require 'json'

company    = Company.find_by!(name: ENV.fetch('COMPANY'))
start_at   = Time.parse(ENV.fetch('START_AT') + ' UTC')
end_at     = Time.parse(ENV.fetch('END_AT') + ' UTC')

# Fluid transaction ledger — only money-moving actions with a terminal status
payments = Payments::Payment
  .where(company_id: company.id)
  .where(created_at: start_at..end_at)
  .where(action: %w[capture purchase settle charge agreement])
  .where(status: %w[success declined error])
  .includes(:payment_account)

fluid_txns = payments.map do |p|
  {
    fluid_id:          p.slug,
    psp_transaction_id: p.transaction_id,
    payment_account_id: p.payment_account_id,
    action:            p.action,
    status:            p.status,
    amount_cents:      p.amount ? (p.amount * 100).round : nil,
    currency_code:     p.currency_code,
    created_at:        p.created_at.utc.iso8601,
  }
end

# Payment accounts — filtered by environment
sandbox_mode = ENV.fetch('SANDBOX', 'false') == 'true'
account_scope = Payments::PaymentAccount
  .where(company_id: company.id, active: true)
  .kept
account_scope = sandbox_mode ? account_scope.select(&:sandbox?) : account_scope.reject(&:sandbox?)

accounts = account_scope.map do |pa|
    {
      id:                pa.id,
      display_name:      pa.display_name.presence || pa.name,
      integration_class: pa.integration_class,
      adapter_class:     pa.adapter_class,
      credentials:       pa.credentials,
    }
  end

puts JSON.pretty_generate({
  company:           company.name,
  start_at:          start_at.iso8601,
  end_at:            end_at.iso8601,
  fluid_total_txns:  fluid_txns.size,
  fluid_txns:        fluid_txns,
  payment_accounts:  accounts,
})
RUBY
```

Run this from `/Users/bendaley/Desktop/code/work/fluid`. Store the full JSON output — you'll use it for every comparison below.

---

## 3 — Fetch PSP transaction data

For each entry in `payment_accounts`, call that provider's transaction listing API for the same date window. Use the instructions per integration class below.

**Match key:** Fluid's `psp_transaction_id` (stored as `payments.transaction_id`) must match the PSP's transaction ID exactly. If `psp_transaction_id` is blank for a Fluid record, flag it separately — it likely means the payment was recorded before the gateway responded.

**Scope:** only fetch settled/charged transactions (not pending or voided) so the comparison is apples-to-apples.

---

### CreditCard — Stripe (`StripePaymentIntentsGateway`)

Credential key: `credentials[:gateway_token]` (the `sk_live_...` secret key)

Paginate all payment intents in the window:

```bash
# Repeat with starting_after=<last_id> while has_more=true
curl "https://api.stripe.com/v1/payment_intents?created[gte]=<UNIX_START>&created[lte]=<UNIX_END>&limit=100" \
  -H "Authorization: Bearer <gateway_token>"
```

Extract per item: `id`, `amount` (already cents), `currency`, `status`, `created`.

Stripe status mapping: `succeeded` → success, `requires_payment_method` / `canceled` / `requires_action` → declined/error.

Also fetch charges separately if the account uses legacy charge IDs:

```bash
curl "https://api.stripe.com/v1/charges?created[gte]=<UNIX_START>&created[lte]=<UNIX_END>&limit=100&expand[]=data.payment_intent" \
  -H "Authorization: Bearer <gateway_token>"
```

---

### CreditCard — Braintree (`BraintreeGateway`)

Credentials: `merchant_id`, `public_key`, `private_key`

Base URL: `https://api.braintreegateway.com` (production)

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
  <status>
    <is type="array">
      <item>settled</item>
      <item>submitted_for_settlement</item>
      <item>processor_declined</item>
      <item>gateway_rejected</item>
    </is>
  </status>
</search>'
```

Parse response XML: `<transaction>` elements with `<id>`, `<amount>`, `<currency-iso-code>`, `<status>`, `<created-at>`.

Braintree status mapping: `settled` / `submitted_for_settlement` → success, `processor_declined` / `gateway_rejected` / `failed` → declined.

---

### Dlocal

Credentials: `dlocal_login`, `dlocal_trans_key`, `dlocal_secret_key`

dLocal uses HMAC-SHA256 auth. Compute the Authorization header:

```python
import hmac, hashlib, datetime

x_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
request_body = ""  # empty for GET
signature = hmac.new(
    dlocal_secret_key.encode(),
    (dlocal_login + x_date + request_body).encode(),
    hashlib.sha256
).hexdigest()
auth_header = f"V2-HMAC-SHA256, Signature: {signature}"
```

Or compute via bash:

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

Filter response items by `created_date` within the window. Paginate with `page` until no more results.

dLocal status mapping: `PAID` / `AUTHORIZED` → success, `REJECTED` / `CANCELLED` → declined.

---

### Ppro (European APMs)

Credentials: `ppro_api_key`, `merchant_id`

PPRO's reporting API is not a standard transaction list — they provide reconciliation files and a reporting portal. If a direct API is not available:
- Note in the report: "PPRO — no direct transaction listing API; reconcile via PPRO merchant portal or reconciliation file download."
- Record Fluid's count and total for PPRO-routed payments and flag it as "manual reconciliation required."

If PPRO has provisioned API access, try:

```bash
curl "https://op.ppro.com/v1/merchant/<merchant_id>/transactions?from=<ISO_DATE>&to=<ISO_DATE>" \
  -H "Authorization: Bearer <ppro_api_key>"
```

---

### CitconUPI (APAC APMs)

Credential: `upi_api_key`

Attempt:

```bash
curl "https://api.citconpay.com/v2/payments?start_time=<UNIX_TS>&end_time=<UNIX_TS>&limit=100" \
  -H "Authorization: <upi_api_key>"
```

If the endpoint returns 404 or is not documented, note in the report: "Citcon — direct API reconciliation not available; check Citcon merchant dashboard."

---

### Paypal

Credentials: look for `client_id` and `client_secret` in the credentials hash.

First, get an access token:

```bash
curl -X POST "https://api-m.paypal.com/v1/oauth2/token" \
  -u "<client_id>:<client_secret>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials"
```

Then list transactions:

```bash
curl "https://api-m.paypal.com/v1/reporting/transactions?start_date=<ISO8601>&end_date=<ISO8601>&transaction_status=S&fields=all&page_size=100&page=1" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json"
```

Paginate: `total_pages` in the response.

---

### Other / unknown integration classes

For any integration class not listed above, record Fluid's count and total for that account and note: "No direct API reconciliation implemented for `<integration_class>` — verify manually."

---

## 4 — Reconcile

For each payment account, compare Fluid's transaction set against the PSP's:

**Match by `psp_transaction_id` ↔ PSP transaction ID.**

Build three lists:
1. **In Fluid, not in PSP** — Fluid has a non-blank `psp_transaction_id` with no match in the PSP results
2. **In PSP, not in Fluid** — PSP has a transaction ID with no match in `fluid_txns` for that `payment_account_id`
3. **Amount mismatch** — matched by ID but `amount_cents` differs by more than 1 (rounding tolerance)

Also track:
- Fluid records where `psp_transaction_id` is blank — these are "orphaned" records, likely pre-gateway failures
- Status mismatches — Fluid says `success` but PSP says declined, or vice versa

**Amount conversion:** PSP amounts are in the currency's minor unit (cents for USD/EUR, etc.) except for Braintree which returns a decimal string — multiply by 100 and round.

---

## 5 — Generate report

Print this exact format to the terminal:

```
PAYMENT RECONCILIATION REPORT
==============================
Company:    <Name>
Period:     <START UTC> -> <END UTC>
Generated:  <NOW UTC>
Run by:     Ben Daley

SUMMARY
-------
Fluid transactions:   X   ($X,XXX.XX)
PSP total:            X   ($X,XXX.XX)
Discrepancies found:  X

```

Then one block per payment account:

```
----------------------------------------------------------
<DISPLAY_NAME>  [<integration_class>]
----------------------------------------------------------
Fluid:  X txns  $X,XXX.XX <CURRENCY>
PSP:    X txns  $X,XXX.XX <CURRENCY>
Status: CLEAN   OR   WARNING: N issues

[Only if issues:]

  IN FLUID, NOT IN PSP (X)
  <psp_transaction_id>  |  $X.XX <CUR>  |  <created_at>  |  Fluid: <status>

  IN PSP, NOT IN FLUID (X)
  <psp_transaction_id>  |  $X.XX <CUR>  |  <psp_date>    |  PSP: <psp_status>

  AMOUNT MISMATCHES (X)
  <psp_transaction_id>  |  Fluid: $X.XX  |  PSP: $X.XX  |  delta: $X.XX

  ORPHANED FLUID RECORDS (no PSP transaction ID) (X)
  <fluid_id>  |  $X.XX <CUR>  |  <created_at>  |  Fluid: <status>

```

For accounts where no direct API reconciliation is available, use:

```
----------------------------------------------------------
<DISPLAY_NAME>  [<integration_class>]
----------------------------------------------------------
Fluid:  X txns  $X,XXX.XX <CURRENCY>
PSP:    Manual reconciliation required — no direct API
```

Close with:

```
===========================================================
END OF REPORT
===========================================================
```

---

## 6 — Save report as HTML

After printing the terminal summary, generate a styled HTML report and save it to:

```
/tmp/recon_<company_slug>_<YYYYMMDD_HHMMSS>.html
```

Where `company_slug` is the company name lowercased with spaces replaced by underscores, and the timestamp is the moment the report was generated.

The HTML report should:
- Use a clean, modern design with a white card layout on a light grey background
- Show a header with company name, period, environment, generated timestamp, and run-by
- Display summary stats (Fluid count/total, PSP count/total, discrepancy count) as prominent stat cards
- Render each discrepancy section (in Fluid not PSP, in PSP not Fluid, amount mismatches, status mismatches, orphans) as a styled table with alternating row colors
- Use green for clean/success indicators, amber for warnings, red for errors
- Be self-contained (inline CSS only, no external dependencies)

Print the full file path so the user can open it in a browser.

---

## Notes

- The user must explicitly choose **sandbox** or **production** at the start — never default. Sandbox mode reconciles test payment accounts and should use PSP sandbox/test API endpoints and credentials. Production mode reconciles live accounts only.
- Paginate all PSP API calls fully before reconciling — never reconcile on a partial page
- If a PSP API call fails (auth error, timeout, rate limit), note the failure clearly in that account's section and continue with the remaining accounts
- For Fluid totals, sum only `success` status transactions — declined and error records are listed separately
- All dollar amounts in the report are formatted as `$X,XXX.XX` — no raw cents
- If the discrepancy count is zero for all accounts, print a single "ALL CLEAN" banner after the summary
