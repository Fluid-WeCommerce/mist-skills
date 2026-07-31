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
2. Check for an existing portal with the same display name by running:

   `fluid portal scaffold --name "<display name>" --check`

   If an exact match exists, stop and offer to open the existing portal. Do not
   create a duplicate.
3. Explain that the operation will create a remote Fluid OS definition and seed
   it with the same Home screen, desktop and mobile navigation, company-branded
   theme, and default profile that fluid-admin creates. It will not publish or
   activate a version.
4. Ask for confirmation immediately before the write.
5. Run:

   `fluid portal scaffold --name "<display name>" --json`

   Use `run_cli` with `command` set to `fluid` and each argument passed
   separately. Do not reproduce the template through individual `fluid_api`
   calls; the CLI command is the canonical, transactional implementation.
6. Parse the JSON result. Confirm that it reports:

   - one definition
   - a Home screen
   - web and mobile navigations
   - an active company theme
   - a default profile

   If the command reports a partial or rolled-back creation, surface the exact
   error and do not retry automatically.
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
  `fluid portal scaffold` is unavailable, say that the installed Fluid CLI must
  be updated.
- Treat the display name as data. Pass it as a single CLI argument and never
  interpolate it into a shell command.
