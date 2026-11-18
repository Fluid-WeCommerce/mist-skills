---
name: Message delivery health
description: Find out why the company's emails, texts and push messages aren't reaching people — split setup problems from bad addresses and opt-outs, show who is unreachable, and fix only what you approve.
icon: mail-warning
---

# Goal

Check how well {{company.name}}'s outbound messages reached people over the 30 days from {{thirty_days_ago}} to {{today}}, find what stopped the rest, and fix what can be fixed. A refused or failed message is a missed order confirmation, a missed autoship warning or a rep who never heard the news. Many failures have one cause (texting not registered, no postal address on marketing email, a bounced address still listed first) that one fix clears for everyone.

# Rules

- **Read first, write only with the user's go-ahead.** The only writes this skill makes are to a person's contact method (mark an address unusable, or change which one is tried first), and only after the user approves the list in chat. If a write is refused because the user turned on Ask before making changes, propose the exact title the refusal gives with `human_in_the_loop` (source `"agent"`, a fresh `suggestion_id` `"fluid-api:<random>"`), END YOUR TURN, and after Approve repeat the same call with `approval_id`.
- **Never turn marketing consent on.** Consent comes from the person, not from this skill. Never set `consent_marketing` to `true`, and never clear an address someone unsubscribed or complained from.
- **Never resend anything.** This skill diagnoses and repairs contact data. Resending is the user's call, made elsewhere.
- **Delivered is not read.** Email delivered means the receiving server accepted it; text delivered is carrier confirmation; push delivered means it was handed to Apple or Google. Say "delivered", never "read" or "opened".
- **Talk in plain words.** Name people by first name and markets by country. Don't show addresses in full (show `j•••@gmail.com`, `•••• 4821`), ids, paths, codes or JSON in the chat.

# Steps

## 1. Read the send rules

`fluid_api("/api/company/v2026-10/messaging/send-rules", "GET")`. Note the quiet hours and the per-person frequency limit for marketing messages, so you can tell a planned hold from a problem.

## 2. Pull the message history

`fluid_api("/api/company/v2026-10/messages?created_after={{thirty_days_ago}}T00:00:00Z&created_before={{today}}T23:59:59Z&limit=100", "GET")`. Follow `page.next_cursor` as `cursor` until `page.has_more` is false, up to 30 pages (3,000 attempts). If you stop at the cap, say the figures are from the most recent 3,000.

For each message keep `channel`, `message_type`, `status`, `refusal_code`, `source` (company messages or bot outreach), `recipient`, `created_at`, and the `detail` of its last `failed` or `refused` event (for example `bounced`, `unsubscribed`).

If `history_complete` is `false`, older bot messages are still being imported: say so once, and don't treat a missing message as proof someone wasn't contacted.

Older mail paths aren't in this history. If the totals look low for the company, say that in one line.

## 3. Score each channel

Per channel (email, text, WhatsApp, push, Flow) and per type (transactional, marketing), count attempts and the share that were delivered, sent and still in flight, failed, and refused. Hold `scheduled` and `accepted` messages younger than 10 minutes out of the failure counts.

## 4. Sort the problems

Group every failed and refused message by cause, in this order:

1. **Company setup (one fix clears all of them):** `sms_not_registered`, `email_sender_not_configured`, `whatsapp_not_configured`, `channel_disabled`, `postal_address_missing`, `promotional_set_not_ready`, `promotional_mail_unavailable`, `app_sender_disabled`. For one example of each, `fluid_api("/api/company/v2026-10/messages/<id>", "GET")` and read the refusal's `setup` status and plain-English message, which says what is left to finish.
2. **Send rules working as intended:** `quiet_hours` and `frequency_capped`. Not a fault. Report the count, and flag it only if the same person was capped three or more times, which means too many senders are aiming at them.
3. **Transactional volume:** `transactional_fanout_exceeded` means the same email went to 100 or more people as transactional in a day. It should have gone as marketing. Name the subject.
4. **The person said no:** `opted_out`, `consent_required`, and failed events with `unsubscribed` or a complaint. Respect these. Report counts only.
5. **Bad or missing address:** `invalid_address`, `contact_method_invalid`, `no_contact_method`, `no_reachable_channel`, `push_no_devices`, and failed events with `bounced` or an invalid number.
6. **Anything else:** list the code and count once.

Note any cause that jumped in the last 7 days against the 23 days before: a sudden rise in bounces or opt-outs usually follows one send.

## 5. Check the people behind group 5

Each message's `recipient` names a `member_id` or a `contact_id`, and the `contact_method_id` it was sent to. Take the people with a bad or missing address, most messages lost first, at most 25. For each, read their contact methods with the matching call:

- `fluid_api("/api/company/v2026-10/members/<member_id>/contact-methods", "GET")`
- `fluid_api("/api/company/v2026-10/contacts/<contact_id>/contact-methods", "GET")`

A message sent to a bare address with neither id can't be traced to a person: count those once and move on.

From `contact_methods`, keep `kind`, `usable`, `verified`, `preferred_rank`, `last_outcome` and `last_outcome_at`, `consent_marketing`, `invalidated_reason`, and `devices` for push. Sort each person into one of these:

- **Fix: a dead address still marked usable.** Two or more hard failures (`bounced`, invalid number) since its last delivery, but `usable` is still true. Proposed fix: mark it unusable.
- **Fix: the wrong address is tried first.** The first-ranked method keeps failing while another usable, verified method of the same person has delivered. Proposed fix: rank the working one first.
- **Unreachable.** No usable method left, or push only with no devices. Nothing to fix in Fluid: the person or their sponsor must update the profile. List them for outreach by another route.
- **Fine now.** A newer delivery since the failure. Leave it alone.

## 6. Report

Lead with one line: messages attempted, the share delivered, and the single biggest cause of loss. Then:

1. **Setup fixes,** biggest first, each with how many messages it stopped and what is left to finish, in the refusal's own words.
2. **A channel table:** attempts, delivered %, failed %, refused % for each channel and type.
3. **Opt-outs and complaints:** counts, and the date of any jump with the subject of the message just before it.
4. **People:** how many in each group from step 5, with the top names for "Unreachable" so the user can ask their sponsors or support team to reach them.
5. **One recommendation** that would recover the most messages next month.

## 7. Apply the contact fixes the user approves

Offer the "dead address" and "wrong address first" fixes as one numbered list. Apply only the items the user approves, one call each:

- Mark an address unusable: `fluid_api("/api/company/v2026-10/contact-methods/<id>", "PUT", { "contact_method": { "invalidated": true } })`.
- Rank a working address first: `fluid_api("/api/company/v2026-10/contact-methods/<id>", "PUT", { "contact_method": { "preferred_rank": 1 } })` on the working one.

Read the returned `contact_method` and confirm `usable` or `preferred_rank` changed. If a call is refused, say in plain words that it couldn't be changed and move on; never try a different method. Finish with what changed, what is waiting on company setup, and how many people still can't be reached.
