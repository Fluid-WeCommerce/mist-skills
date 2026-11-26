---
name: Autoship billing days
description: Map which days of the month autoship renewals bill on, find the days that hurt (month-end dates that slip past the commission close, overloaded peaks, days that decline more), then design, preview and save blackout rules that move them, with your approval.
icon: calendar-clock
---

# Goal

Show {{company.name}}, as of {{today}}, how its autoship renewals are spread across the days of the month, which days cause trouble, and which blackout rules would fix it. Then preview exactly how many subscriptions each rule would move, and save the rules only when the user approves.

In direct sales and social selling, the day an autoship bills is not neutral:

- **Month-end dates slip.** A renewal due on the 29th, 30th or 31st has no date in a short month, and a renewal that bills on the last day and fails is retried in the next month. When the company pays commissions on calendar-month volume, that order counts for the wrong month, and the customer's rep can miss a rank they had earned. Many payment systems and direct sellers keep recurring dates to the 1st to the 28th for this reason.
- **Peaks overload the operation.** When one day carries two or three times the normal number of renewals, the warehouse, the payment processor and customer care all feel it, and a single bad day (a processor outage, a stockout) hits a large share of the month.
- **Some days decline more.** Fluid's own billing records show whether renewals early, mid or late in the month succeed less often.

Fluid's Subscription Pro has a blackout calendar for this: rules that say "a bill date on these days of the month moves to this day". A daily sweep moves subscriptions once their date falls outside the reminder window, and a shopper choosing a blocked day at checkout is saved on the next open day with the note the rule gives.

At the end the user has:

1. A day-of-month map: renewals and revenue per day, each day's share of the month, and how often each part of the month declines.
2. The problem days, each with a reason in one sentence.
3. A proposed blackout calendar with the number of subscriptions each rule moves, previewed by Fluid without saving.
4. If approved, the rules saved and the blackout feature switched on, read back to confirm.
5. A dated record in the project so the next run shows what changed.

# Rules

- **Read first, write only with approval.** Steps 1 to 5 change nothing; the preview in step 5 saves nothing. The only write is the settings save in step 6, gated by one `human_in_the_loop` card. END YOUR TURN until the user clicks Approve.
- If a write is refused because the user turned on *Ask before making changes*, propose the exact title it returns with `human_in_the_loop`, END YOUR TURN, then retry the same call with `approval_id`. Never retry a refused write another way.
- **Never touch a subscription directly.** This skill never edits a bill date, skips, pauses or cancels a subscription. Fluid's sweep moves them under the saved rules.
- **Keep the user's other settings.** A save replaces the whole blackout list, so always send the existing rules you intend to keep, and send only the keys you change.
- **Talk in plain words.** Say "the 30th" and "Canada", not ids, paths or JSON.
- **Never add across currencies.** Revenue is shown per currency.
- **Say what is an estimate.** Counts read from the billing calendar are facts; reasons for a decline pattern and the effect on rank qualification are judgments, labelled that way.
- If a read is refused or a feature is off, say in plain words which part you couldn't check and carry on with the rest.

# Steps

## 1. Load the last run and the policy

1. Look for `autoship-billing-days/` in the active project with `list_dir`. If there is an earlier run, read the newest file with `read_file` and keep its policy answers and the rules it proposed.
2. Ask the user in a `steps` panel, prefilled from the last run if there is one:
   - **Commission period:** does the company pay on calendar months (the usual case), and if not, on which day does the period close?
   - **Days to keep clear:** any days the team already avoids (warehouse closed on the 1st, payday-driven declines, a monthly processing day for the back office). Default: none.
   - **Peak line:** how many times the average day counts as a peak. Default 2.
   - **Markets:** all markets together (default) or one country at a time.
3. Save the answers to `autoship-billing-days/policy.md` with `write_file` so the next run doesn't ask again.

## 2. Read the current settings

1. `fluid_api("/api/subscription_pro/settings", "GET")`. Keep `active`, `lock_version`, `reminder_lead_days`, `blackout_rules` (each rule's `id`, `name`, `enabled`, `priority`, `blocked_days`, `move_to_day`, `checkout_message`) and `features.blackout_dates` (`available`, `enabled`, `setting`, `precondition_failure`).
2. If `active` is false or the call returns 404, Subscription Pro isn't on for this company. Say so once: the map and the recommendations still work, but rules can't be previewed or saved until it is on. Skip steps 5 and 6.
3. If rules already exist, describe each in one line ("Month end: the 29th to the 31st move to the 28th, on"). If `blackout_dates` has a `precondition_failure`, explain it in plain words.

## 3. Map renewals by day of the month

1. For each of the last three completed months and the current month, call `fluid_api("/api/v202604/analytics/subscription_billing/calendar?month=<YYYY-MM>", "GET")`, adding `&country=<ISO>` when the user picked one market. Work out the month values yourself from {{today}}.
2. From each `days[]` row keep `date`, `renewal_count`, `renewal_amount`, `succeeded_count`, `soft_decline_count`, `hard_decline_count` for days that have run, and `scheduled_count`, `scheduled_amount` and `at_risk_count` for days still to come. Note the response's `currency`.
3. For each day of the month (1 to 31) add up renewals across the completed months and divide by the number of months that have that day. Do the same for revenue. Then work out each day's share of a month and its ratio to the average day.
4. Separately, list the renewals still scheduled this month and next month on each day (call the next month's calendar too). These are the subscriptions a new rule would move first.
5. For each completed month, call `fluid_api("/api/v202604/analytics/subscription_billing/breakdown?month=<YYYY-MM>", "GET")` (same `country`). Keep `month_parts` (success rate for days 1 to 10, 11 to 20 and 21 to 31, with `sufficient_sample`), `failure_rate` and the top `decline_reasons`. A part with `sufficient_sample` false has no rate; say so instead of guessing.
6. If a day looks odd, open it: `fluid_api("/api/v202604/analytics/subscription_billing/day?date=<YYYY-MM-DD>&per_page=25", "GET")` gives that day's renewals with their status and decline reason. Use it to explain, not to list customers in the chat.

## 4. Find the problem days

Mark each day that meets one of these, with the reason:

- **Month end:** any renewals on the 29th, 30th or 31st. Say how many a month and how many fall on a date that doesn't exist in the shortest month ahead.
- **Commission close:** renewals in the last 2 days before the commission period closes (from step 1). A first attempt that fails there is retried in the next period. Count how many of those days' renewals declined at least once in the completed months; that is roughly how many orders a month risk counting in the wrong period. Label it an estimate.
- **Peak:** a day above the peak line.
- **Declines:** a month part whose success rate is clearly below the others in at least two of the three months.
- **Team's own days:** the days the user named in step 1.

If no day qualifies, say so in one line, record the map in step 7 and stop.

## 5. Propose and preview blackout rules

1. Draft the smallest set of rules that fixes the problem days:
   - Month end and commission close: block those days and move them to the last safe day before them (usually the 28th or earlier).
   - Peaks: don't block a peak day on its own, since that only moves the peak. Suggest spreading it instead (for example, block a peak day and move it to the quietest nearby day), and only when the user's team asked to flatten it.
   - Keep every existing rule unless the user agrees to change it.
2. Check each rule before previewing, because Fluid refuses a calendar that breaks these: a rule's move-to day may not be blocked by any rule (even one that is off); a move-to day above the 28th may not have a blocked day from the 28th up to the day before it; a day may not appear twice in one rule; at most 20 rules. Give each rule a short `name` and a `checkout_message` a shopper will understand, such as "We bill on the 28th when your date would fall on the 29th to the 31st."
3. Preview the whole calendar you would save (existing rules you keep plus new ones): `fluid_api("/api/subscription_pro/blackout_preview", "POST", { "blackout_rules": [ { "name": "Month end", "blocked_days": [29, 30, 31], "move_to_day": 28, "checkout_message": "…" } ] })`. Include the `id`, `enabled` and `priority` of existing rules you keep. The preview saves nothing.
4. Read `moves` and `by_day` (for each blocked day, how many subscriptions move and to which day). A 422 names the broken check; fix the rule and preview again. Then work out what the new calendar looks like: each moved day's count added to its move-to day, and whether that creates a new peak.
5. Remind the user what moves: active subscriptions (and paused ones with a bill date) on month or year plans whose bill date lands on a blocked day after the reminder window, which is `reminder_lead_days` but at least 3 days. Renewals inside that window keep their date this cycle.

## 6. Save, with approval

1. Show the proposal: each rule in one line, the subscriptions it moves, and the new busiest day.
2. Build the save: `fluid_api("/api/subscription_pro/settings", "PATCH", { "lock_version": <from step 2>, "blackout_rules": [ …the whole calendar you previewed… ], "features": { "blackout_dates": true } })`. Leave out `features` if the feature is already on.
3. Propose it with `human_in_the_loop` (source `"agent"`, title "Save the autoship blackout calendar", a fresh `suggestion_id` of the form `"fluid-api:<random>"`, and the summary as `description`). END YOUR TURN.
4. After approval, send the PATCH and read the result back:
   - Success returns the settings: confirm each rule is listed and `blackout_dates` shows `enabled` true.
   - 409 means someone changed the settings since step 2: read them again, show the user what changed, and propose again.
   - 422 `precondition_failed` names a feature the company can't turn on yet: explain it in plain words and save the rules with the feature left off, if the user agrees.
5. Tell the user what happens next: the daily sweep moves the subscriptions outside the reminder window, and shoppers who pick a blocked day see the note. Suggest a short heads-up to reps whose customers move, sent by the team that writes to the field.

## 7. Record and report

1. Write `autoship-billing-days/{{today}}.md` with `write_file`: the policy, the day map, problem days with reasons, the rules proposed, the preview counts, and whether they were saved.
2. Report in this order: one line with the decision (for example, "Moving 412 renewals off the 29th to the 31st keeps them inside the commission month"); the problem days table (day, renewals a month, share, reason); the rules with their moves; what was saved; and, from an earlier run, what changed since then.
