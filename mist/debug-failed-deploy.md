---
name: Debug a failed Mist deploy
description: Pull deployment logs, identify the failure, and propose a fix.
icon: bug
---

# Goal

A Mist deploy failed and the user wants help diagnosing why.

# Steps

1. Confirm the active project is a Mist (`.mist` marker file at the project root). Read the slug from it.
2. Pull the most recent deployments: `fluid_api("/api/v202604/mists/<slug>/deployments?limit=5", "GET")`.
3. Find the latest one whose `state` is `error` or `canceled`. If none, say so and stop.
4. Pull its build logs: `fluid_api("/api/v202604/mists/<slug>/logs?deployment_id=<dpl>&limit=200", "GET")`.
5. Read the log output. Identify the first error and its likely cause. Categorize:
   - **Build failure** — TypeScript, ESLint, missing dep, bad import
   - **Runtime failure** — env var missing, DB migration not applied, secret not set
   - **Vendor failure** — Vercel rate limit, Neon connection refused, GitHub auth
6. For build failures, `read_file` the suspect source file to confirm.
7. Propose a fix:
   - For missing dep: the exact `pnpm add <package>` command
   - For TypeScript: the line and the corrected snippet
   - For missing env var: the `fluid mist env set <KEY> <value>` invocation
8. Wait for user approval before applying the fix. After it's applied, `fluid mist push --watch` and report on the new deploy.
