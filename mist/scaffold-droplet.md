---
name: Scaffold a new Droplet for a Mist
description: Set up the Droplet UI scaffolding (page, route, schema) for a fresh Mist app.
icon: hammer
---

# Goal

The user has a freshly-cloned Mist app and wants the Droplet UI scaffolding — page route, server action, and Fluid widget registration.

# Steps

1. Confirm the active project is a Mist by checking for `.mist` (the workspace marker file) at the project root.
2. Ask the user what the Droplet does in one sentence (e.g. "a quiz that recommends a root beer flavor").
3. Read the Mist starter's existing structure: `app/page.tsx`, `app/api/`, `lib/`. Use the project's existing patterns (Next.js App Router conventions).
4. Generate the following:
   - `app/droplet/page.tsx` — the embed-rendered page. Use the existing layout primitive if there is one.
   - `app/api/droplet/route.ts` — POST handler for any form submission.
   - `droplet.schema.json` — the Droplet's settings schema. Wire to the API via the existing Mist secrets pattern.
5. Update `package.json` if there's a missing dep (validate against the lockfile first).
6. Run `fluid mist push` and watch the deployment via the `--watch` flag.
7. When the deploy finishes, give the user the public URL + suggested next steps (set up the Droplet's marketplace listing, etc.).
