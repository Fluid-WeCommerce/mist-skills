---
name: Scaffold a new Droplet for a Mist
description: Set up the Droplet UI scaffolding (embed page, route, droplet config) for a fresh Mist app.
icon: hammer
---

# Goal

The user has a freshly-cloned Mist app and wants the Droplet UI scaffolding — an embed page, an installation-scoped API route, and the registration in `lib/config/droplet.config.ts`.

# Steps

1. Confirm the active project is a Mist by checking for `.mist` (the workspace marker file) at the project root.
2. Ask the user what the Droplet does in one sentence (e.g. "a quiz that recommends a root beer flavor").
3. Read the Mist starter's existing structure: `app/embed/` (the `checkout-banner` example), `app/api/webhooks/`, `lib/config/droplet.config.ts`, `lib/fluid/`, `lib/handlers/`, `lib/schema.ts`. Use the project's existing patterns (Next.js App Router conventions).
4. Generate the following:
   - `app/embed/<name>/page.tsx` — the page Fluid loads in the iframe. Fluid adds `?dri=dri_...` to the URL: capture it with `readFluidInstallationReference` and call your own API routes through `fluidInstallationFetch` (`lib/fluid/installation-reference.ts`). The `dri` selects the installation; it does not authenticate the viewer.
   - `app/api/<name>/route.ts` — the handler for any form submission. Call `resolveFluidInstallation(request)` first, then `createFluidClientForInstallation(context.installation)` for Fluid calls, and scope every database read and write to `context.companyId`. Never fall back to a client-supplied company id, a shared env token, or the only row in the database.
   - An entry in `lib/config/droplet.config.ts` — a drop zone whose `embedPath` is the new page, plus any webhooks or callbacks it needs. Set `enabled: true` only once the backing route exists; enabled entries are registered on install. A new webhook handler goes in `lib/handlers/` and is registered in `lib/handlers/index.ts`.
   - Any new tables in `lib/schema.ts` and the idempotent DDL in `lib/ensure-schema.ts`, which runs on PGlite locally and Neon in production.
   - Secrets the feature needs as user-managed env vars (`fluid mist env set KEY=value`). Never edit the Mist-managed `DATABASE_URL` or `FLUID_*` variables.
5. Update `package.json` if there's a missing dep (validate against `package-lock.json` first — the starter uses npm), then run `npm run typecheck`, `npm run lint` and `npm test`.
6. Run `fluid mist push` and watch the deployment via the `--watch` flag.
7. When the deploy finishes, give the user the Mist's `public_url` + suggested next steps: attach a droplet if there isn't one (`fluid mist attach-droplet`), fix its embed and lifecycle URLs with `fluid mist droplet repair --dry-run`, and contact Fluid to start the Marketplace review.
