---
name: Subscription decline recovery
description: Win back past-due subscriptions without double-messaging customers, retrying cards that must not be retried, or charging anyone without a person.
icon: credit-card
---

# Goal

Recover subscriptions whose renewal payment failed, on top of what Fluid already does on its own, and never against it.

Fluid already handles part of a declined renewal. Read its state before you act, and do not assume it:

- Fluid retries automatically only some declines: insufficient funds, gateway or integration errors, and blank reasons. The gaps depend on the plan and the company's settings, so read `next_retry_at` instead of predicting it. Other declines, recurring-payment stops and finished retry chains park the subscription as `past_due`.
- Fluid may email the customer a payment-failed notice with an "Update Payment Method" link on the first eligible decline of a failure streak, and a past-due email when it parks the subscription. It skips the first-decline notice for sandbox companies, for integration or blank-reason failures, and when the company turned the email off. The past-due email follows its own rules and can still go out. A booked retry does not prove an email went out.
- If the company offers backup-card renewals and the shopper opted in, Fluid may charge another eligible saved card after a card-specific decline. It never does this for fraud, lost or stolen cards, recurring stops or integration failures.

Your job is the gap: a parked subscription, a channel Fluid did not use, and a report the owner can act on.

# Rules

- Never charge a card yourself. Retrying a subscription (`retry`, `bulk_retry`, `scheduled_retries`, `reprocess`) charges the customer. Ask a person through an approval card, one subscription at a time, and only after the payment method changed or the customer asked for a retry.
- Apply the stop rule before any other action. If the decline names fraud, a lost, stolen or picked-up card, "do not retry", or a revoked authorization, never retry that card and never steer the payment to another card to get around it. Refer it to the owner. Revocation wording can appear under `bank_decline`, so check the reason text, not only the category.
- Never choose, charge or switch on a backup card for the customer, and never turn on their backup-card consent.
- Never show `failure_reason` to a customer. It is the gateway's raw text.
- A card-update notice is a transactional message. A win-back discount is marketing. Never send a promotion as transactional.
- Fluid's quiet hours and frequency caps apply only to marketing. For transactional messages, enforce the limits yourself: one message per failure streak, at least 24 hours after a Fluid email you have confirmed, and inside the owner's contact hours. If you cannot tell when Fluid last emailed the customer, refer the message to the owner instead of sending it.

# Steps

1. Read the past-due subscriptions with `GET /api/subscriptions?status=past_due&per_page=100`. This endpoint is page-numbered: keep incrementing `page` until you reach `meta.pagination.total_pages`. For each one, keep `decline_category`, `failure_reason`, `decline_count`, `last_failed_at` and `next_retry_at`.

2. If `next_retry_at` is set, a retry is booked. It may be automatic, or one an operator scheduled. Do not ask for another retry. Check the subscription again after that time.

3. If `next_retry_at` is empty, no retry is booked and none will happen unless someone asks for one. Apply the stop rule first, then act on `decline_category`:

   | `decline_category` | What it means | What to do |
   | --- | --- | --- |
   | `card_invalid` | Expired or closed card or account, or wrong number, expiry or security code | Check the card first (step 4). Ask the customer to correct the details or add a card through Fluid's secure payment page. A closed account needs another payment method. |
   | `limit` | Insufficient funds, or a spending or frequency limit | Do not retry early, and do not promise an automatic retry. Refer the parked subscription to the owner, who can decide on one approved retry later. |
   | `bank_decline` | The issuer refused: "do not honor", "refer to issuer", and some revocation wording | Stop rule first. For an ordinary refusal only, ask the customer to call their bank or choose another payment method. |
   | `blocked` | Fraud, lost or stolen card, transaction not permitted | Never retry and never offer a discount. Report it to the owner. |
   | `document_invalid` | The payer's document number was refused | Ask the customer to correct their details on the secure payment page. |
   | `verification` | 3DS or card verification failed, or a PayPal approval expired | Ask the customer to update the payment method and confirm it themselves. |
   | `operational` | A known failure on Fluid's or the gateway's side | Do not ask the customer to change anything. Report it to the owner. |
   | `unknown` or empty | No known pattern matched, or no gateway decline was recorded | Do not guess the cause. Report it to the owner. |

4. Before you tell a customer their card failed, read their payment methods with `GET /api/customers/{customer_id}/payment_methods`. Its `au_status` comes from the card networks' Account Updater:
   - `update_needed`: the issuer says to contact the cardholder. Ask them to update their payment method.
   - `closed`: the issuer reported the account closed. Ask for another payment method.
   - `enrolled`, `pending`, `not_enrolled` or empty: none of these proves the card changed or still works. Check the shown expiry instead, and never use `au_status` as the reason to ask for a retry.
   Another saved card that has not expired may still not qualify for renewals. Ask the customer to review their payment methods on the secure payment page rather than naming a card for them.

5. Message only through a channel Fluid did not use, and only after the checks in the Rules. Use `POST /api/company/v2026-10/messages/{sms,whatsapp,push}` with `message_type` `transactional`.
   - Send an idempotency key (the `Idempotency-Key` header or `idempotency_key`), record the channel and the outcome for this failure streak, and reuse the same key if you repeat the request.
   - SMS needs one recipient and `text`. Push needs the member's UUID as `member_id` and a `body`. WhatsApp needs an approved template unless the customer wrote to you in the last 24 hours.
   - Fluid checks consent and opt-outs per channel. If a send is refused, respect it. Never change channel or key to get around a refusal or an earlier attempt.

6. To ask Fluid to send its own payment-failed email, call `POST /api/subscriptions/payment_failed_emails` with `{"tokens": ["<subscription token>"], "renewal_date": "YYYY-MM-DD", "resend": false}`. `renewal_date` is the local date of the failed billing, not the next renewal. Confirm first that the subscription is still past due and the customer can fix it. Fluid skips a customer it already noticed for this streak, or one an operator emailed in the last day. Never set `resend` to `true` yourself, and read the result for each token. A sent result means Fluid queued the email, not that it was delivered.

7. A win-back offer is marketing. Create it only within the owner's discount limit, and send it as `message_type` `marketing`.

8. When billing moves a subscription from `past_due` back to `active`, Fluid emits `subscription.resumed_after_payment_fix`, unless events were turned off for that billing. If the event never arrives, confirm recovery by re-reading the subscription. Count that failure streak once as recovered and stop following it up. Do not claim the recovery for yourself without separate evidence, and re-check the subscription before any delayed follow-up.

9. Report to the owner:
   - Recovery against the usual rate: read `GET /api/v202604/analytics/dashboard/payment_recovery` and compare `won_back_pct` with `baseline_won_back_pct`, with `recovered_amount` and `recovered_count` underneath.
   - The parked subscriptions by `decline_category`, with the amount at risk in each group.
   - Every subscription you did not message, and why: the stop rule, `blocked`, `operational`, `unknown`, or an email you could not time.
   - Each retry you want, as a request for an approval card.

10. Be honest about the data. Never report a percentage without the counts underneath it. If a field is empty across the whole account, say so instead of guessing. If nothing is past due, say that in one line.
