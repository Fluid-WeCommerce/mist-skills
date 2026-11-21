---
name: Orphaned customer handoff
description: Find customers still credited to reps who have left or gone inactive, rank them by what they spend and their active autoships, pick an active rep to look after each group under your policy, and reassign only what you approve.
icon: user-round-check
---

# Goal

Find {{company.name}}'s orphaned customers as of {{today}}: customers whose credited rep has been deactivated or gone inactive. Nobody follows up with them, and their future orders credit someone who will never help them. For each departed rep, list the customers still credited to them, choose an active rep to adopt them under the company's policy, and change the credited rep only for the groups the user approves.

Why it matters. Customers who aren't reps themselves are the healthiest volume a direct-selling company has. A customer with an active autoship and no rep is the easiest customer to lose. Giving a customer to a newer rep can also help that rep stay.

# Rules

- **Read first, write only with approval.** Nothing changes until the user approves a card. Every reassignment is one `fluid_api` PATCH, and every group of reassignments is proposed with `human_in_the_loop` first.
- **At most 3 approval cards per turn**, then END your turn and wait for the clicks.
- **The policy decides, not you.** Choose adopters with the policy from step 1. When the policy doesn't settle a case, the group is "needs a human".
- **This changes credit for future orders only.** It never moves past orders, commissions or anyone's place in the genealogy tree, and it never changes the customer's sponsor. Say so on every card.
- **Never message a customer or rep from this skill.** Offer the "tell the new rep" draft in step 7 as text the user can send.
- **Talk in plain words.** Refer to people by name. Don't show ids, paths or JSON in the chat.
- Reading needs member, customer and order view access. Changing a credited rep needs member management. If a write is refused because the user's role can't make it, say so in plain words and leave that customer as they are. Never retry another way.

# Steps

## 1. Load the policy

1. Look for `customer-handoff-policy.md` in the active project with `read_file`. If it exists, use it and show the user a one-line summary.
2. If it doesn't, read the company's attribution setting for context: `fluid_api("/api/v2025-06/fairshare/settings", "GET")`. Note `orphan_sponsor_config` and `orphan_sponsor_rep_id`. It decides who gets credit when an order has no rep at all, not what happens to customers whose rep has left. Mention it only when it suggests a default: `select_rep` names a rep the company already uses as a catch-all.
3. Ask the user once, offering these defaults they can accept as they are:
   - **Who counts as departed:** a rep who is deactivated, or whose `activity_status` isn't active. Leave out reps updated in the last **14 days** in case they come back.
   - **Which customers:** customers with an order credited to that rep in the last **365 days**, or an active autoship.
   - **Who adopts:** the departed rep's sponsor, if active. If not, the nearest active rep above them. If nobody active is found, the catch-all rep from the attribution setting, or "needs a human".
   - **Load limit:** no rep adopts more than **25** customers in one run. Overflow goes to the next active rep above.
   - **Leave alone:** customers who are reps themselves, and customers who ordered through a different active rep in the last 90 days. They already chose someone.
4. Save the answers to `customer-handoff-policy.md` with `write_file` so the next run doesn't ask again.

## 2. Find departed reps

1. `fluid_api("/api/v2025-06/member-types", "GET")` to find which member type slugs are reps. Confirm with the user if more than one looks like a rep.
2. `fluid_api("/api/v2025-06/members?filter[member_type_slug]=<rep slug>&filter[active]=false&page[limit]=100", "GET")`, following `page[cursor]` until there are no more pages. Use `filter[member_type_slug][]` for several slugs.
3. Reps who are still marked active but have stopped working (their `activity_status` on `fluid_api("/api/v2025-06/members/<id>", "GET")` isn't active) count only if the policy says so. Checking them means reading every rep one at a time, so offer it as a second pass after the first report rather than running it by default.
4. For each departed rep, keep `id`, `legacy_user_company_id`, name, `country_code`, `updated_at` and `sponsor` (with whether the sponsor is active). Drop reps inside the policy's grace period.
5. If none are found, say so in one line and stop.

## 3. Find their customers

For each departed rep:

1. `fluid_api("/api/v202506/orders?user_company_id=<legacy_user_company_id>&start_date=<window start>&end_date={{today}}&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`. These are orders credited to that rep. Collect the distinct `customer.id` values, with each customer's latest order date and the total of their orders in the window.
2. For each customer, `fluid_api("/api/customers/<customer id>", "GET")`. Keep the customer only if `attributable_rep.id` is still the departed rep's `legacy_user_company_id`: someone may already have reassigned them. Note `member_type_slug` (leave out reps), `active_subscriptions_count`, country and language.
3. For customers with an active autoship, `fluid_api("/api/v2025-06/subscriptions?filter[customer_id]=<customer id>&filter[status]=active", "GET")` for each autoship's amount and next bill date.
4. Apply the "leave alone" rule. For customers whose latest order in the window was credited to a different, active rep, leave them out and list them under "already moved on".

## 4. Choose an adopter for each group

For each departed rep, in the order the policy gives:

1. **Sponsor.** If `sponsor` is active, they are the candidate. Read them with `fluid_api("/api/v2025-06/members/<sponsor id>", "GET")` for name, country and `legacy_user_company_id`.
2. **Nearest active rep above.** If the sponsor isn't active, walk up one sponsor at a time with the same members endpoint, at most 10 levels. Skip anyone who isn't an active rep.
3. **Catch-all.** If nobody qualifies, use the policy's catch-all rep. Otherwise mark the group "needs a human".
4. **Load and fit.** Count customers already planned for each adopter in this run, and apply the load limit. Flag an adopter in a different country from most of the group's customers, or one who doesn't speak the customers' language. Recommend anyway, but say so.

## 5. Report

Lead with one line: how many orphaned customers, how many with an active autoship, and their monthly autoship value. Then show one table per departed rep, largest monthly autoship value first. Each table gives the departed rep, when they left, the proposed adopter and why (sponsor, nearest active rep or catch-all), then the customers (name, country, last order date, orders in the window, active autoship amount and next bill date). Put "needs a human" groups and any adopter flags first. End with the "already moved on" count.

## 6. Apply approved groups

Offer to reassign the groups with an adopter, up to 3 cards per turn, highest value first:

1. Propose each group with `human_in_the_loop`:
   - `source` `"agent"`
   - `suggestion_id` `"customer-handoff:<departed rep id>:<adopter id>:<random>"`
   - title `Credit <N> customers of <departed rep> to <adopter>`
   - in `description`, the customers' names, plus a note that this changes credit for future orders only, not past orders, commissions or the tree
   - in `proposed_action`, the exact change

   END YOUR TURN.
2. After the user approves a group, reassign each customer in it: `fluid_api("/api/customers/<customer id>/update_attributable_rep", "PATCH", { "customer": { "user_company_id": <adopter legacy_user_company_id> } })`. If the user has "Ask before making changes" turned on, Mist refuses the write and names a card title. Propose that card, end your turn, and retry the same call with `approval_id` after the click, one customer at a time.
3. Confirm each change from the response: `attributable_rep.id` is the adopter. A 404 means the adopter isn't a member of the company any more: stop that group and report it. Any other refusal: report it in plain words for that customer and carry on with the rest.
4. Record each change with `human_in_the_loop` in mode `record_outcome`, using the same `suggestion_id`. Save a line per group to `customer-handoff-log.md` with `write_file`: the date, departed rep, adopter and customer count. That way the next run can show what changed and spot repeats.

## 7. Wrap up

Finish with what was reassigned, what was left for a human and why, and the monthly autoship value now looked after by an active rep. For each adopter, offer a short note the user can send, in the adopter's language, naming their new customers and their next autoship dates. It must make no income or product claims. This skill sends nothing itself.
