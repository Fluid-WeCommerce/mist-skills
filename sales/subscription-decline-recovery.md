---
name: Subscription decline recovery
description: Win back past-due subscriptions without double-messaging customers, retrying cards that must not be retried, or charging anyone without a person.
icon: credit-card
---

# Goal

Recover subscriptions whose renewal payment failed, on top of what Fluid already does on its own, and never against it.

Fluid already handles part of a declined renewal. Read its state before you act, and do not assume it:

- Fluid retries automatically only some declines: insufficient funds and spending or frequency limits, gateway or integration errors, and blank reasons. The gaps depend on the plan and the company's settings, and some companies retry insufficient funds up to five times over about 21 days, so read `next_retry_at` instead of predicting it. Other declines, recurring-payment stops and finished retry chains park the subscription as `past_due`.
- Fluid may email the customer a payment-failed notice with an "Update Payment Method" link on the first eligible decline of a failure streak, and a past-due email when it parks the subscription. It skips the first-decline notice for sandbox companies, for integration or blank-reason failures, and when the company turned the email off. The past-due email follows its own rules and can still go out. A booked retry does not prove an email went out. Both emails go out, when they do, at a failed attempt, and no API returns whether or when they were sent.
- If the company offers backup-card renewals and the shopper opted in, Fluid may charge another eligible saved card after a card-specific decline. It never does this for fraud, lost or stolen cards, recurring stops or integration failures.

Your job is the gap: a parked subscription, a message by SMS, WhatsApp or push, and a report the owner can act on.

# Rules

- Never charge a card yourself. Retrying a subscription (`retry`, `bulk_retry`, `scheduled_retries`, `reprocess`) charges the customer. Ask a person through an approval card, one subscription at a time, and only after the payment method changed or the customer asked for a retry.
- Apply the stop rule before any other action. If the decline names fraud, a lost, stolen or picked-up card, "do not retry", or a revoked authorization, never retry that card, and never charge or switch to another saved card. Refer it to the owner. The owner may ask the customer to add a different payment method, which is what Fluid itself requires after a recurring stop. Revocation wording can appear under `bank_decline`, so check the reason text, not only the category. A recurring stop recorded by NMI arrives with an empty `failure_reason` and `decline_category`, so an empty category is never a reason to retry.
- Never choose, charge or switch on a backup card for the customer, and never turn on their backup-card consent.
- Never show `failure_reason` to a customer. It is the gateway's raw text.
- A card-update notice is a transactional message. A win-back discount is marketing. Never send a promotion as transactional.
- Fluid's quiet hours and frequency caps apply only to marketing. For transactional messages, enforce the limits yourself: one message per failure streak, at least 24 hours after the latest `last_failed_at` (Fluid's emails go out at a failed attempt, so this clears both), at least 24 hours after any email you asked Fluid to send in step 6, and inside the owner's contact hours.

# Steps

1. Start from events when your bot can use triggers. `subscription.declined` fires on every failed renewal attempt, and `subscription.resumed_after_payment_fix` fires when one recovers. Do not use `subscriptions.exhausted` for this: it fires when a subscription reaches its plan's last billing cycle and is cancelled, not when retries run out. Then sweep the full list once a day for anything an event missed.

   To read the list, call `GET /api/subscriptions?status=past_due&per_page=100&sort_by=id&sort_direction=asc`. This endpoint is page-numbered: keep incrementing `page` until you reach `meta.pagination.total_pages`. Read every page before you act on any row, because rows that leave `past_due` shift the later pages. A row missed this way shows up in the next sweep. For each one, keep `decline_category`, `failure_reason`, `decline_count`, `last_failed_at`, `next_retry_at`, `next_bill_date`, `timezone` and `disabled`.

2. If `next_retry_at` is set and still ahead, a retry is booked. It may be automatic, or one an operator scheduled. Do not ask for another retry. Check the subscription again after that time.

   A set `next_retry_at` does not prove Fluid will run it. Fluid checks for due retries every few minutes, and skips automatic retries for failures more than 7 days old, for disabled subscriptions and while the company's billing is paused. Treat the subscription as stuck when `next_retry_at` is more than an hour in the past, when `disabled` is true, or when `last_failed_at` is more than 7 days old and `next_retry_at` has passed. Report a stuck subscription to the owner and do not message the customer, because the API cannot tell you whether billing was paused on purpose.

3. If `next_retry_at` is empty, no retry is booked and none will happen unless someone asks for one. Apply the stop rule first, then act on `decline_category`:

   | `decline_category` | What it means | What to do |
   | --- | --- | --- |
   | `card_invalid` | Expired or closed card or account, or wrong number, expiry or security code | Check the card first (step 4). Ask the customer to correct the details or add a card through Fluid's secure payment page. A closed account needs another payment method. |
   | `limit` | Insufficient funds, or a spending or frequency limit | A parked `limit` subscription has usually used up Fluid's retries, and another retry adds a decline that hurts the merchant's acceptance rate. Ask the customer to use another payment method. Ask for one approved retry only after the customer says the funds are there. Never promise an automatic retry. |
   | `bank_decline` | The issuer refused: "do not honor", "refer to issuer", and some revocation wording | Stop rule first. For an ordinary refusal only, ask the customer to call their bank or choose another payment method. |
   | `blocked` | Fraud, lost or stolen card, high risk or blacklist, or a card the issuer restricted, has not activated, or does not allow for this purchase | Never retry and never offer a discount. If `failure_reason` names fraud, a lost, stolen or picked-up card, high risk, a blacklist, a security violation or an illegal transaction, report it to the owner. Otherwise (a restricted, disabled or not-activated card, a transaction not permitted, or a card not supported for this purchase) ask the customer to contact their bank or use another payment method. |
   | `document_invalid` | The payer's document number was refused | Ask the customer to correct their details on the secure payment page. |
   | `verification` | 3DS or card verification failed, or a PayPal approval expired | Ask the customer to update the payment method and confirm it themselves. |
   | `operational` | A known failure on Fluid's or the gateway's side | Do not ask the customer to change anything. Report it to the owner. |
   | `unknown` or empty | No known pattern matched, or no gateway decline was recorded. NMI recurring stops look like this. | Do not guess the cause and never retry. Report it to the owner. |

4. Before you tell a customer their card failed, read their payment methods with `GET /api/customers/{customer_id}/payment_methods`. Its `au_status` comes from the card networks' Account Updater:
   - `update_needed`: the issuer says to contact the cardholder. Ask them to update their payment method.
   - `closed`: the issuer reported the account closed. Ask for another payment method.
   - `enrolled`, `pending`, `not_enrolled` or empty: none of these proves the card changed or still works. Check the shown expiry instead, and never use `au_status` as the reason to ask for a retry.
   Another saved card that has not expired may still not qualify for renewals. Ask the customer to review their payment methods on the secure payment page rather than naming a card for them.

5. Message by SMS, WhatsApp or push, not email, because Fluid's own notices are emails. Send only after the checks in the Rules. Use `POST /api/company/v2026-10/messages/{sms,whatsapp,push}` with `message_type` `transactional`.
   - Send an idempotency key (the `Idempotency-Key` header or `idempotency_key`), record the channel and the outcome for this failure streak, and reuse the same key if you repeat the request.
   - SMS needs one recipient and `text`. Push needs the member's UUID as `member_id` and a `body`. WhatsApp needs an approved template unless the customer wrote to you in the last 24 hours.
   - Fluid checks consent and opt-outs per channel. If a send is refused, respect it. Never change channel or key to get around a refusal or an earlier attempt.

6. To ask Fluid to send its own payment-failed email, call `POST /api/subscriptions/payment_failed_emails` with `{"tokens": ["<subscription token>"], "renewal_date": "YYYY-MM-DD", "resend": false}`. `renewal_date` is the date Fluid billed, in the subscription's `timezone`: take `next_bill_date`, which a failed renewal does not move, and convert it to that timezone. Never use the UTC date of `last_failed_at`. For a subscription in America/Los_Angeles, a renewal for 2026-11-04 that fails at 2026-11-05T03:00Z still has the billed date 2026-11-04, and sending 2026-11-05 returns `no_failure`, so no email goes out. Confirm first that the subscription is still past due and the customer can fix it. Fluid skips a customer it already noticed for this streak, or one an operator emailed in the last day. Never set `resend` to `true` yourself, and read the result for each token. A sent result means Fluid queued the email, not that it was delivered.

7. A win-back offer is marketing. Create it only within the owner's discount limit, and send it as `message_type` `marketing`.

8. When billing moves a subscription from `past_due` back to `active`, Fluid emits `subscription.resumed_after_payment_fix`, unless events were turned off for that billing. If the event never arrives, confirm recovery by re-reading the subscription. Count that failure streak once as recovered and stop following it up. Do not claim the recovery for yourself without separate evidence, and re-check the subscription before any delayed follow-up.

9. Report to the owner:
   - Recovery against the usual rate: read `GET /api/v202604/analytics/dashboard/payment_recovery`. `won_back_pct` is recovered amount over failed amount for the month so far, and `baseline_won_back_pct` covers the previous 6 months. Show `failed_count` and `failed_amount`, `recovered_count` and `recovered_amount`, and `retrying_count` underneath. Early in the month most failures are still retrying, so say the comparison is not settled while `retrying_count` is a large share of `failed_count`.
   - The parked subscriptions by `decline_category`, with the amount at risk in each group.
   - Every subscription you did not message, and why: the stop rule, fraud-type `blocked`, `operational`, `unknown` or empty, stuck, or too soon after a failed attempt.
   - Each retry you want, as a request for an approval card.

10. Be honest about the data. Never report a percentage without the counts underneath it. If a field is empty across the whole account, say so instead of guessing. If nothing is past due, say that in one line.
