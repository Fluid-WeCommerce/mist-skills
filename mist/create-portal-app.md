---
name: Create Portal App
description: Create a new Fluid portal using the same default screens, navigation, theme, and profile as fluid-admin.
icon: panels-top-left
---

# Goal

Create a new Fluid portal definition using Fluid's canonical starter template,
then make it available in Mist's portal workspace. Use this skill only when the
user explicitly asks to create a new portal app.

# Steps

1. Ask for the portal's display name if the user did not provide one. Preserve
   that display name exactly. Derive a lowercase kebab-case local slug and show
   both values.
2. Check for an existing portal with the same display name:
   `fluid_api("/api/company/fluid_os/definitions", "GET")`, matching names
   case-insensitively.

   If a match exists, stop and offer to open the existing portal. Do not
   create a duplicate.
3. Explain that the operation will create a remote Fluid OS definition and seed
   it with the same Home screen, desktop and mobile navigation, company-branded
   theme, and default profile that fluid-admin creates. It will not publish or
   activate a version.
4. Ask for confirmation immediately before the write: propose it with
   `human_in_the_loop` (source `agent`, title exactly the display name,
   a fresh `suggestion_id` of `portal-create:<display name>:<short random
   suffix>`), then end your turn.
5. After the user approves, call Mist's `create_portal_app` tool with
   `display_name`, `approval_id` set to that exact `suggestion_id`, and
   `confirm_create: true`. Each approval is single-use, so a retry needs a new
   proposal. Do not reproduce the template through individual `fluid_api`
   calls; `create_portal_app` is the canonical, transactional implementation
   (it rolls back a partly seeded definition).
6. Parse the JSON result. On `status: "created"`, confirm that `created`
   reports:

   - a Home screen
   - Main (web) and Mobile navigations
   - the Company Theme
   - the Default Profile

   On `duplicate`, offer to open the existing portal. On `rolled_back` or
   `rollback_failed`, surface the exact errors and do not retry
   automatically.
7. Tell the user the portal is ready and give its display name and definition
   ID. Explain that it will appear in Mist's portal list after refresh; opening
   it lets Mist clone the connected repository or use the local fallback
   scaffold when GitHub is not connected.

# Guardrails

- Never create a portal without explicit user invocation and confirmation.
- Never publish a portal version as part of this skill.
- Never create GitHub repositories, install a GitHub App, or change company Git
  integration settings.
- Never fall back to a hand-built sequence of API writes. If
  `create_portal_app` is unavailable (for example, outside Mist), say that
  creating a seeded portal needs Mist. `fluid portal create` only scaffolds a
  local project and does not create the remote definition.
- Treat the display name as data. Pass it unchanged as `display_name` and
  never interpolate it into a shell command.
