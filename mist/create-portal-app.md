---
name: Create Portal App
description: Create a new Fluid portal using the same default screens, navigation, theme, and profile as fluid-admin.
icon: panels-top-left
---

# Goal

Create a new Fluid portal definition using Fluid's canonical starter template,
then make it available in Mist's portal workspace. Use this skill only when the
user explicitly asks to create a new portal app.

Portal creation is implemented by Mist's dedicated `create_portal_app` tool.
It creates the remote Fluid OS definition and seeds it with the same Home
screen and widget tree, desktop and mobile navigations, company-branded theme,
and default profile that fluid-admin's Portal Builder "+ New" creates. Do not
reproduce the template through individual `fluid_api` calls or CLI commands;
the tool is the canonical, transactional implementation.

# Steps

1. Ask for the portal's display name if the user did not provide one. Preserve
   that display name exactly.
2. Explain what the operation will do: create a remote Fluid OS definition and
   seed it with the default Home screen, Main (web) and Mobile navigations, a
   Company Theme generated from the company's brand colors, and a Default
   Profile linking them. It will not publish or activate a version.
3. Ask for confirmation immediately before the write: present the plan via
   `human_in_the_loop` with `source` set to `agent`, the exact display name as
   the `title`, the creation described above as the proposed action, and a
   FRESH `suggestion_id` of the form `portal-create:<display name>:<short
   random suffix>` (new suffix for every attempt) — then end your turn. Only
   proceed after the user approves. Mist verifies this exact approval when the
   tool runs: the `source`, `title`, and `suggestion_id` must match, the
   approval must be less than 15 minutes old, and each approval is single-use.
4. Call the `create_portal_app` tool with `display_name` set to the exact
   display name, `approval_id` set to the exact `suggestion_id` from step 3,
   and `confirm_create: true`. If the user dismissed the approval, stop — do
   not re-propose or retry. If the tool reports the approval as used or stale,
   a retry requires a brand-new proposal (fresh suffix) and a fresh Approve.
5. Read the tool's structured JSON result:

   - `status: "duplicate"` — a portal with the same display name already
     exists (matched case-insensitively). Nothing was created. Tell the user,
     name the existing definition (its id and name from
     `existing_definition`), and offer to open that portal instead. Do not
     retry with the same name.
   - `status: "created"` — report the definition ID and display name, and
     summarize the created resources (`created.screens`,
     `created.navigations`, `created.theme`, `created.profile`). Explain that
     no version was published and the portal will appear in Mist's portal
     list after refresh; opening it lets Mist clone the connected repository
     or use the local fallback scaffold when GitHub is not connected.
   - `status: "rolled_back"` — seeding failed and the incomplete definition
     was deleted. Surface `seed_error` verbatim and do not retry
     automatically.
   - `status: "rollback_failed"` — seeding failed AND the cleanup delete also
     failed. Surface BOTH `seed_error` and `rollback_error` verbatim, along
     with the `definition_id` that remains in an incomplete state, so the
     user can delete it in fluid-admin's Portal Builder.

# Guardrails

- Never create a portal without explicit user invocation and confirmation.
  `confirm_create: true` may only be passed after the user approved via
  `human_in_the_loop` in this conversation; Mist independently checks that
  the `portal-create:…` suggestion passed as `approval_id` was approved for
  this exact portal name, consumes it on use, and refuses reused, stale, or
  mismatched approvals.
- Never publish a portal version as part of this skill.
- Never create GitHub repositories, install a GitHub App, or change company
  Git integration settings.
- Never fall back to a hand-built sequence of API writes or CLI commands. If
  the `create_portal_app` tool is unavailable, say that Mist Desktop must be
  updated.
- Treat the display name as data. Pass it through as the `display_name`
  argument exactly as the user gave it — never derive, embellish, or
  interpolate it into commands.
- Rely on the tool's duplicate check (its structured `duplicate` refusal) —
  do not pre-check with other tools or ask the user to verify uniqueness.
