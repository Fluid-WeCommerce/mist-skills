---
name: Genealogy change queue
description: Work the genealogy queue — new members waiting in a holding tank and pending sponsor or placement move requests — check each against your sponsor-change policy, recommend place, approve or reject, and apply only what you approve.
icon: git-fork
---

# Goal

Clear {{company.name}}'s genealogy queue as of {{today}}. Two kinds of item wait on a person here:

- **Held seats.** New members parked in a tree's holding tank, waiting for someone to choose where they sit. Until they are placed, their volume does not build anyone's leg, and when the hold runs out Fluid either places them by the tree's default rule or leaves them waiting forever.
- **Move requests.** A member asking to change sponsor or placement. These are where crossline poaching and upline disputes show up, so each one needs the same rules applied every time, with the reason written down.

For each item, gather the evidence, recommend **place**, **approve**, **reject** or **needs a human**, and apply only the decisions the user approves.

# Rules

- **Read first, write only with approval.** Nothing changes until the user approves a card. Every placement and every decision is one `fluid_api` POST gated by `human_in_the_loop`.
- **At most 3 decision cards per turn**, then END your turn and wait for the clicks.
- **The company's policy decides, not you.** Apply the policy from step 1. When the policy doesn't cover a case, the item is "needs a human".
- **Never approve a move that moves a downline** unless the policy explicitly allows it. Most companies keep the downline with the original line.
- **Talk in plain words.** Refer to people by name and to trees by name ("Placement tree"). Don't show ids, paths or JSON in the chat.
- Reading needs member view access. Placing needs member management, and deciding a move request needs the move-approval permission. If a write is refused, say in plain words that the user's role can't make that change and leave the item as it is. Never retry another way.

# Steps

## 1. Load the policy

1. Look for `genealogy-policy.md` in the active project with `read_file`. If it exists, use it and show the user a one-line summary.
2. If not, ask the user once, with these defaults they can accept as they are:
   - **Sponsor changes:** allowed only after the member has been inactive (no order) for **6 months**, or within **7 days** of enrolling to fix an enrollment mistake.
   - **Upline release:** required from the current sponsor for any other change. Fluid doesn't store releases, so a change that needs one is "needs a human" unless the request's reason says the release is on file.
   - **Limit:** one sponsor change per member, ever.
   - **Downline:** stays with the original line.
   - **Holding tank:** place every held seat before its hold runs out, under the enroller, in the first open spot (or the leg the user names).
3. Save the answers to `genealogy-policy.md` with `write_file` so the next run doesn't ask again.

## 2. Build the queue

1. `fluid_api("/api/company/v2026-10/genealogy/tree-keys", "GET")`. Keep each tree's `id`, `key` and `name`.
2. For each tree:
   - **Held seats:** `fluid_api("/api/company/v2026-10/genealogy/trees/<tree_id>/holding-tank?limit=100", "GET")`, following `meta.pagination.next_cursor` as `cursor` until it is null. Keep each seat's `id`, `member_id` and `held_until`.
   - **Move requests:** `fluid_api("/api/company/v2026-10/genealogy/trees/<tree_id>/move-requests?status=pending&limit=100", "GET")`, following `next_cursor` the same way. Keep `id`, `node_id` (the seat that would move), `parent_node_id` (the proposed new parent), `leg`, `reason`, `requested_by_type`, `requested_by_id`, `created_at` and `expires_at`.
   - A 404 for one tree means it has no holding tank or moves; skip it quietly.
3. If both lists are empty everywhere, say so in one line and stop.

## 3. Evidence for each held seat

Soonest `held_until` first:

1. **Who.** `fluid_api("/api/v2025-06/members/<member_id>", "GET")`: `name`, `created_at`, `country_code`, `rank`, `orders_count`, `activity_status`.
2. **Their enroller.** `fluid_api("/api/company/v2026-10/genealogy/nodes/<seat id>/enroller", "GET")`. A null node means no enroller is recorded. When there is one, find the enroller's own seat in this tree: `fluid_api("/api/company/v2026-10/genealogy/trees/<tree_id>/nodes?member_id=<enroller's member_id>", "GET")`, and the enroller's name from the members endpoint above.
3. **Room under the enroller.** `fluid_api("/api/company/v2026-10/genealogy/nodes/<enroller seat id>/children?limit=100", "GET")` shows which legs are taken.
4. **Time left.** Hours until `held_until`. Flag any seat already past it: Fluid places an expired seat on its own only when the tree's default rule allows it, so an expired seat still listed is stuck and needs placing now.

## 4. Evidence for each move request

Soonest `expires_at` first:

1. **The moving member.** `fluid_api("/api/company/v2026-10/genealogy/nodes/<node_id>", "GET")` gives `member_id`, the current `parent_node_id` and `downline_count`. Then the members endpoint for `name`, `created_at` (days since enrolling), `activity_status`, `orders_count` and `rank`.
2. **Last order.** `fluid_api("/api/v202506/members/<member_id>/orders?page[limit]=1&sort=-created_at", "GET")`. Months since the latest order is the inactivity the policy measures.
3. **Earlier changes.** `fluid_api("/api/company/v2026-10/genealogy/nodes/<node_id>/placements", "GET")`. More than one recorded placement means the member has moved before.
4. **Current and proposed parents.** Read both parent seats with the nodes endpoint and their members' names.
5. **Crossline check.** `fluid_api("/api/company/v2026-10/genealogy/nodes/<proposed parent seat>/relation?other=<node_id>&kind=ancestor_of", "GET")`. A move to someone who is not already above the member in the tree is a crossline move: the new sponsor gains a member from another team. Say so plainly.
6. **Who asked.** Whether `requested_by_id` is the moving member, and what `reason` says.
7. **Will Fluid accept it?** For a request you would approve, preview it: `fluid_api("/api/company/v2026-10/genealogy/nodes/<node_id>/move/validate", "POST", { "move": { "parent_node_id": "<proposed parent seat>", "reason": "<request reason>" } })`. It writes nothing; still propose it through `human_in_the_loop` like any POST. Any `violations` mean recommend reject, with the violation in plain words. A 503 means moves aren't switched on for this company yet: approvals will fail, but rejections still work.

## 5. Recommend

**Held seats**
- **Place:** an enroller seat exists in this tree. Recommend the first open spot under the enroller (`rule: "first_empty"` starting from the enroller's seat), or a named leg when the policy or the user gives one.
- **Needs a human:** no enroller is recorded, or the enroller isn't seated in this tree. Name the check: "who should Maria sit under?"

**Move requests**
- **Reject:** the policy forbids it (not inactive long enough, past the enrollment fix window, already moved once, or it would move a downline the policy keeps), or the preview found violations. Write the reason the member will read, citing the policy in one sentence.
- **Approve:** the policy clearly allows it, the preview passed, and nothing below applies.
- **Needs a human:** a release is required and not mentioned, it is a crossline move to an active member's team, the moving member has a downline, or the policy is silent. Name the single check that settles it.

Flag anything expiring in the next 48 hours: an expired request can't be decided, and the member has to ask again.

## 6. Report

Lead with one line: held seats and move requests waiting, and the soonest deadline. Then one table per recommendation group (name, tree, deadline, a one-line reason in plain words). Put stuck held seats and crossline moves first.

## 7. Apply approved decisions

Offer to apply the Place, Approve and Reject recommendations, up to 3 per turn. For each:

1. Call the write **without** `approval_id` to get the exact approval title:
   - Place a held seat: `fluid_api("/api/company/v2026-10/genealogy/nodes/<seat id>/place", "POST", { "placement": { "parent_node_id": "<enroller seat id>", "rule": "first_empty", "reason": "<one-line reason>" } })`, or `{ "parent_node_id": …, "leg": "<leg>" }` for a named leg.
   - Approve a move: `fluid_api("/api/company/v2026-10/genealogy/move-requests/<id>/approve", "POST", { "decision": { "reason": "<one-line reason>" } })`.
   - Reject a move: `fluid_api("/api/company/v2026-10/genealogy/move-requests/<id>/reject", "POST", { "decision": { "reason": "<the reason the member will read>" } })`. A reason is required.
2. Propose it with `human_in_the_loop` (source `"agent"`, that title exactly, a fresh `suggestion_id` of the form `"fluid-api:<random>"`, and the reason as `description`). END YOUR TURN.
3. After the user approves, call the same POST again with the same body plus `approval_id`, and confirm the result:
   - A placed seat returns with a `parent_node_id` and `held_until` empty. A 409 `leg_full` or `placement_busy` means someone took the spot: read the enroller's children again and propose the next open spot.
   - An approved move returns the request as `approved`. A 202 with a `move_job` means a large move is running: check it once with `fluid_api("/api/company/v2026-10/genealogy/move-jobs/<move_job id>", "GET")` and tell the user it's in progress.
   - A rejected move returns the request as `rejected` with your reason.
4. On a 422 (the request expired or the member is no longer eligible), say so in plain words and move on.

Finish with what was placed, approved, rejected and left for a human, and the next deadline still in the queue.
