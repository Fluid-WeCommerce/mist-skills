---
name: Admin access review
description: Run a periodic access review of everyone who can sign in to Fluid's admin — who has which role, which roles grant the riskiest permissions, which installed apps hold broad scopes — get each person confirmed by the user, remove or narrow only what they approve, and save a dated review record for auditors.
icon: shield-check
---

# Goal

Review who can work in {{company.name}}'s Fluid admin as of {{today}}, and leave it tighter than you found it. Card networks and auditors expect this. PCI DSS asks for a review of user accounts and their access at least every six months and for inactive accounts to be disabled within 90 days. SOC 2 auditors ask for a dated review with proof that flagged access was removed. It also matters day to day: in direct sales, admins can change genealogy, refunds, payouts data and member records, and staff, agencies and contractors come and go.

At the end the user has:

1. Every active admin confirmed as "keep", "narrow" or "remove", by a person.
2. The approved removals and role changes made in Fluid and read back.
3. A dated review record in the project that an auditor can read.

# Rules

- **Read first, write only with approval.** Nothing changes until the user approves a card. Every removal and every role change is one `fluid_api` call gated by `human_in_the_loop`.
- **At most 3 approval cards per turn**, then END your turn and wait for the clicks.
- **The user decides who should have access, not you.** Fluid doesn't know who still works for the company. Recommend, then ask.
- **Never remove the user running this skill, and never leave the company without a full admin.** Before you propose removing or narrowing an admin who has full access, count the full admins who will remain. If it would be fewer than two, say so and don't propose it.
- **Remove means deactivate.** Fluid's admin removal deactivates the person's admin access and revokes their reporting and Mist database access; it doesn't delete their history. Say that on the card.
- **Talk in plain words.** Name people, roles and apps. Don't show ids, paths, permission keys or JSON in the chat; describe a permission as what it lets someone do ("issue refunds", "change who sponsors whom").
- Reading needs permission to view admins and roles. If a read is refused, say in plain words which part of the review you couldn't do and carry on with the rest. If a write is refused, say the user's role can't make that change and leave it as it is. Never retry another way.

# Steps

## 1. Load the last review

1. Look for files under `access-reviews/` in the active project with `list_dir`. If there is an earlier review, read the newest with `read_file` and keep its date, the people confirmed then, and anything left open.
2. Tell the user in one line when the last review was, or that this is the first one.

## 2. Build the access list

1. **Admins.** `fluid_api("/api/v2/admins?active=true&per_page=100&page=1", "GET")`, then the next page until a page comes back with fewer than 100. For each admin keep `id`, `computed_full_name`, `computed_email`, `roles`, `created_at` and `country`. An admin whose `roles` is `["admin"]` has full access.
2. **Recently deactivated.** `fluid_api("/api/v2/admins?active=false&per_page=100&page=1", "GET")`. Keep only names and count; they are already removed, and the record just notes them.
3. **Roles.** `fluid_api("/api/company/roles?per_page=100", "GET")`. For each role keep `id`, `name`, `user_count` and `permission_keys`.
4. **What the permissions mean.** `fluid_api("/api/company/roles/structure", "GET")` gives each permission's plain description. Use it to describe roles in the chat.
5. **Who holds each role.** For each role with users, `fluid_api("/api/company/roles/<role id>/members?page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`. Match members to admins by email.
6. **Installed apps.** `fluid_api("/api/company/v2026-10/droplet-installations", "GET")`, then for each active installation `fluid_api("/api/company/v2026-10/droplet-installations/<uuid>", "GET")` for `effective_scopes`, `role` and `installed_by`.
7. **Bots.** `fluid_api("/api/company/v2026-10/bots", "GET")`, following `next_cursor`. Keep each bot's `name`, `status` and `owner`. A bot acts with its owner's permissions, so it inherits whatever the review decides about that person.

## 3. Find what needs a decision

Mark each admin with every flag that applies:

- **Full access.** Holds full admin. Every one needs an explicit "keep" with a reason, and there should be as few as the business can run with.
- **Sensitive permissions.** Holds a role that can issue refunds, change payment or payout settings, change genealogy or approve moves, manage admins or roles, change API or app access, or export customer or member data. Use the permission descriptions from step 2.4 to decide which roles these are.
- **Stacked roles.** Holds three or more roles, or a role that duplicates part of another.
- **Outside email.** Email domain differs from the company's main domain: agency, contractor or personal address.
- **New since the last review.** Added after the previous review's date.
- **Unconfirmed last time.** Left open in the previous review.

Mark each role:

- **Unused.** `user_count` is 0. Recommend deleting it only if the user wants; an unused role is harmless but clutters reviews.
- **Too broad.** Grants sensitive permissions alongside unrelated everyday ones, so everyone who needs the everyday part also gets the sensitive part.

Mark each installed app:

- **Broad scopes.** Can write orders, members, payments or settings, or acts with a role that has sensitive permissions.
- **Installed by someone leaving.** `installed_by` is a person the user is about to remove.

Fluid doesn't record when each admin last signed in, so you can't find dormant accounts by date. Ask instead (step 4).

## 4. Confirm with the user

1. Show a short summary: how many admins, how many with full access, how many flagged, and the apps and bots that need a look. Lead with the riskiest.
2. Open a `steps` panel that lists each flagged admin with their roles in plain words and the flags, and asks for each: **Keep**, **Narrow** (pick which role to drop), or **Remove**. Include a free-text "reason" for every Keep on someone with full access or sensitive permissions. Unflagged admins go in one group the user can confirm together, with the option to pull anyone out.
3. Ask one extra question in the same panel: "Has anyone on this list left the company, changed jobs, or not used Fluid in the last 90 days?" Treat every name they give as Remove or Narrow.
4. For each app with broad scopes, ask whether it is still in use. Removing an app is out of scope here: list unused ones for the user's developer.

## 5. Apply what the user approved

For each change, one card at a time, at most 3 per turn:

- **Remove an admin.** Card title `Remove <name>'s admin access`, body naming their roles, the bots they own (which will stop acting for them), and that history is kept. After Approve: `fluid_api("/api/v2/admins/<id>", "DELETE")`.
- **Narrow an admin.** Card title `Change <name>'s roles`, body listing roles before and after. After Approve: `fluid_api("/api/v2/admins/<id>", "PATCH", { "admin": { "admin_roles": [<role ids to keep>] } })`. Sending the full list of roles to keep is what removes the others.
- **Delete an unused role**, only when the user asked: card title `Delete the <role name> role`. After Approve: `fluid_api("/api/company/roles/<role id>", "DELETE")`.

After each write, read it back with `fluid_api("/api/v2/admins/<id>", "GET")` (or the role list) and confirm the change in one line. If Fluid refuses a change, tell the user its reason in plain words and move on.

## 6. Save the review record

Write `access-reviews/{{today}}.md` with `write_file`:

- Date, company, and who ran the review ({{user.name}}, {{user.email}}).
- Every active admin at the start, with roles, flags, the decision, and the reason the user gave for keeping full or sensitive access.
- Every change made, with the time it was read back as done.
- Roles reviewed, with user counts and any marked too broad.
- Installed apps with broad scopes and whether the user said each is still in use.
- Open items: anything the user deferred, with who owns it.
- The next review date: three months out for full and sensitive access, six months out at the latest.

Show the user the path to the record and the three most important things that changed. If nothing was flagged and nothing changed, say so in one line and still save the record: auditors need proof the review happened.
