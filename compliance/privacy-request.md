---
name: Privacy request
description: Work one person's request to see, correct or delete their data, or to stop all marketing — confirm it's really them, find every record Fluid holds on them, check what must be kept, make only the changes you approve, and draft the reply before the legal deadline.
icon: user-lock
---

# Goal

Handle one privacy request for {{company.name}} from start to finish, today ({{today}}). A customer, rep or prospect has asked to **see** the data the company holds on them, **correct** it, **delete** it, or **stop marketing**. Privacy laws set a deadline: one month under GDPR (EU and UK), extendable by two more months with notice; 45 days under California's CCPA, extendable once by 45 days with notice, and California also expects you to confirm receipt within 10 business days. In direct sales the same person can be a customer, a rep with a downline and a contact in a rep's list at once, so their data sits in several places.

At the end the user has:

1. The person's identity confirmed, or a drafted message asking them to confirm it.
2. A list of everything Fluid holds on them, and the outside places it was sent.
3. The approved changes made in Fluid and read back.
4. A drafted reply to the person, sent only if the user approves.
5. A dated record in the project, without copying the person's data into it.

# Rules

- **Read first, write only with approval.** Nothing changes until the user approves a card. Every write is one `fluid_api` call gated by `human_in_the_loop` (source `"agent"`, a fresh `suggestion_id` of the form `"fluid-api:<random>"`). At most 3 cards per turn, then END YOUR TURN.
- **Confirm it's them before sharing or removing anything.** The request must come from an email or phone number already on their record (step 3). A rep or sponsor asking for someone else is not enough.
- **Stop-marketing requests are done at once.** They need no identity check beyond a matching address, and no deadline waits.
- **Never turn marketing consent on,** and never clear an address someone unsubscribed from.
- **Deletion removes less than people expect.** Removing a customer cancels their active autoships, removing a member soft-deletes it, and orders stay in Fluid for tax and accounting. Say this on every deletion card. Stop and hand to the user, don't delete, if anything in step 5 says hold.
- **Not legal advice.** Quote the deadlines above as a guide. When a hold or exception is a judgement call, say the company's legal contact should decide.
- **Keep personal data out of the chat and the record.** Name the person by first name and country. Mask addresses (`j•••@gmail.com`, `•••• 4821`). Never show full payment details: a card is its brand and last four digits at most. Don't show ids, paths or JSON.
- If a read is refused, say in plain words which part you couldn't check and carry on. If a write is refused, say the user's role can't make that change and leave it.

# Steps

## 1. Take the request

Open a `steps` panel titled `Privacy request` and ask:

- The person's name, and the email and/or phone they wrote from.
- What they asked for: **See my data**, **Correct my data** (and what to change), **Delete my data**, **Stop marketing** (email, texts, or all). More than one is fine.
- Where they live: country, and state if in the US.
- When the request arrived (date), and how (email, form, customer care, a rep).

END YOUR TURN and wait for the answers.

## 2. Set the deadline

From the country and date, compute the due date: one month for the EU, EEA and UK; 45 days for California; for anywhere else, say which law you think applies, use 30 days as a cautious working date, and tell the user to confirm it with their legal contact. Tell the user in one line: what was asked, the due date, and how many days remain. For California, also show the date by which receipt must be confirmed.

Look for an earlier record with `list_dir("privacy-requests")`. If one exists for the same person (same first name, country and masked address), read it with `read_file` and continue from it.

## 3. Find the person and confirm it's them

Search every place they can be, with each email and phone they gave:

1. **Customer:** `fluid_api("/api/v2025-06/customers?filter[email]=<email>&page[limit]=20", "GET")`. Keep only exact email matches.
2. **Member (rep):** `fluid_api("/api/v2025-06/members/find?email=<email>", "GET")`. A 404 means none.
3. **Contact:** `fluid_api("/api/company/contacts/find_by_email?email=<email>", "GET")`. A 404 means none.
4. **Messages to their phone:** `fluid_api("/api/company/v2026-10/messages?phone=<phone>&limit=25", "GET")` shows whether Fluid knows the number and whose it is.

Then read their contact methods: `fluid_api("/api/company/v2026-10/customers/<customer_id>/contact-methods", "GET")`, `/members/<member_id>/contact-methods`, or `/contacts/<contact_id>/contact-methods`.

- **Confirmed:** the address or number they wrote from is one of their contact methods. Say so and continue.
- **Not confirmed:** they wrote from an address Fluid doesn't have for them, or a rep asked on their behalf. Draft a short message to the email on their record asking them to confirm the request from it, show it to the user, and send it only on an approved card (step 7). Save the record (step 8) as "waiting for confirmation" and stop. Stop-marketing requests can still go ahead for the address they wrote from.
- **Not found anywhere:** tell the user Fluid holds nothing under those details, draft a reply saying so, and skip to step 7.

## 4. List everything Fluid holds

For each record found, read and summarize. Don't paste records into the chat.

- **Profile:** `fluid_api("/api/customers/<customer_id>", "GET")` and/or `fluid_api("/api/v2025-06/members/<member_id>", "GET")`: name, addresses, phone, birthday if stored, language, credited rep, and custom fields.
- **Orders:** `fluid_api("/api/v202506/customers/<customer_id>/orders?page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`; for a rep also `/api/v202506/members/<member_id>/orders`. Count them and note the first and last dates.
- **Autoships:** `fluid_api("/api/v2025-06/subscriptions?filter[customer_id]=<customer_id>", "GET")`.
- **Payment methods on file:** `fluid_api("/api/customers/<customer_id>/payment_methods", "GET")`: count and card brand only.
- **Reward points:** `fluid_api("/api/v202506/customers/<customer_id>/points_ledgers", "GET")`: current balance.
- **Team notes:** `fluid_api("/api/customer_notes?customer_id=<customer_id>", "GET")`: count, and whether any hold sensitive details such as health.
- **Contact details and consent:** from step 3: each address, whether marketing consent is on, and whether it's blocked.
- **Messages sent to them:** `fluid_api("/api/company/v2026-10/messages?customer_id=<customer_id>&limit=100", "GET")` (or `member_id=` for a rep): count by channel and type for the last 12 months.
- **For a rep:** `fluid_api("/api/v2025-06/members/<member_id>/genealogy?levels=1", "GET")`: how many people they personally sponsor.

**Outside places their data went.** List what receives customer, member or order data, so the user can pass the request on:

- `fluid_api("/api/company/webhooks?query[active]=true&query[per_page]=100", "GET")`: each active webhook's resource (customers, members, orders) and its destination host.
- `fluid_api("/api/company/v2026-10/droplet-installations", "GET")`: installed apps, then `/droplet-installations/<uuid>` for their scopes; keep those that can read customers, members or orders.
- `fluid_api("/api/company/v2026-10/connect/integrations", "GET")`: outside systems synced through Fluid Connect.

Show the user a short summary: where the person appears (customer, rep, contact), what's held in each, and the outside places that likely have a copy.

## 5. Check what must be kept (deletion only)

Before proposing any deletion, mark each of these that applies:

- **Open order:** any order not yet paid, shipped or delivered, or refunded in the last 30 days. **Hold** until it's settled.
- **Active autoship:** removing the customer cancels it. Say so; the person should know their next shipment stops.
- **Rep with a downline:** they sponsor anyone (step 4). **Hold**: removing a rep with a downline changes the tree and may affect commissions. Hand this to the user and their compensation team; don't delete.
- **Commissions or payouts not yet settled:** ask the user. Fluid's API doesn't show payouts.
- **Open dispute, chargeback or legal matter:** ask the user.
- **Orders and payments themselves stay** for tax and accounting either way. Tell the person that in the reply.

If anything says hold, tell the user what and why, and offer to do the parts that can go ahead now (stop marketing, correct data, delete the contact record).

## 6. Make the changes the user approves

One card per change, at most 3 per turn. After each approval, make the call, then read the record back and confirm in one line.

- **Stop marketing:** card `Stop marketing to <first name>`. Then `fluid_api("/api/customers/<customer_id>/update_marketing_preferences", "PATCH", { "customer": { "email_marketing": false, "sms_marketing": false } })` (only the channels they asked about), and for each of their contact methods `fluid_api("/api/company/v2026-10/contact-methods/<id>", "PUT", { "contact_method": { "consent_marketing": false } })`. If they asked never to be contacted at an address at all, use `{ "contact_method": { "invalidated": true } }` on that one. Read back with the contact-methods list.
- **Correct:** card `Correct <first name>'s <field>` showing before and after. Then `fluid_api("/api/v2025-06/customers/<id>", "PATCH", { ... })` or `fluid_api("/api/v2025-06/members/<member_id>", "PATCH", { ... })` with only the changed fields; an email change for a rep or customer goes through `fluid_api("/api/v2025-06/members/<member_id>/change-email", "PATCH", { "email": "<new>", "reason": "Privacy request: correction asked by the member", "verification_method": "<how you confirmed it in step 3>" })`, which also updates the linked customer.
- **Delete:** one card per record, title `Delete <first name>'s <customer|member|contact> record`, body listing what goes, what stays (orders), and any autoship that will be cancelled. Then:
  - Contact: `fluid_api("/api/company/contacts/<id>", "DELETE")`.
  - Customer: `fluid_api("/api/v2025-06/customers/<id>", "DELETE")`.
  - Member: `fluid_api("/api/v2025-06/members/<member_id>", "DELETE")`.
  Read back: the same GET should now return 404 (or the member as removed).
- **See my data:** no change. Write the summary for the person to `privacy-requests/<file>-summary.md` (step 8 names the file) in plain language: each kind of data held, why the company holds it, where it came from, who it's shared with (the outside places by type: payment, shipping, email, the apps), and how long it's kept. List figures (number of orders, points balance), not full records. Tell the user to review it before it goes anywhere.

## 7. Reply to the person

Draft a short, plain reply in the person's language: what they asked, what was done, what was kept and why, and who to contact with questions. For a "see my data" request, attach nothing; say the summary is ready and how it will reach them, as the user decides.

Show the draft. On an approved card `Reply to <first name>'s privacy request`, send it with `fluid_api("/api/company/v2026-10/messages/email", "POST", { "customer_id": <customer_id>, "subject": "...", "body": "...", "message_type": "transactional", "idempotency_key": "privacy-request:<random>" })`, or with `"to": "<email on record>"` when they are a contact only. A reply to a privacy request is transactional; never send marketing in it. Confirm it was accepted.

## 8. Save the record

Write `privacy-requests/{{today}}-<first name initial><last name initial>-<country>.md` with `write_file`:

- Date received, how it arrived, what was asked, the law and due date you used.
- Identity: confirmed or not, and how (which kind of contact method matched, masked).
- Where the person was found (customer, rep, contact), and counts of what was held.
- The holds from step 5 and who decided them.
- Every change made, with the time it was read back.
- The outside places listed for the user to contact, each marked "to contact".
- Whether the reply was sent, and when.
- Status: closed, waiting for confirmation, or open with what's left and its due date.

Don't write the person's full email, phone, address, order contents or payment details into the record.

Finish with three lines: the status, the due date and days left (or that it's closed), and the one thing the user still has to do, such as asking an outside app to delete its copy.
