---
name: Summary Mist apps on company
description: Audit every Mist app a company owns across all states and flag where creating a new one would be redundant.
icon: layers
---

# Goal

Give a single, scannable picture of every Mist app the active company owns and, crucially, surface where
creating a *new* one would be redundant: same name/purpose, an existing app already plugged into the target
surface, a `failed` app that may still hold billable cloud resources, or a `live` app that was never wired to
anything.

Read-only. This skill only calls GET endpoints — it never provisions, edits, restores, or tears down a Mist.
When it finds a problem it *recommends* the fix and lets the user run it.

# Steps

1. **Scope.** The `fluid_api` connector is already authenticated for the active company, so there is no
company to ask for — every call below is implicitly scoped to it.

2. **List every Mist.** `fluid_api → GET /api/v202604/mists` with `page[limit]=100`. The response is
cursor-paginated under `meta.pagination` — keep following the next cursor (`page[cursor]=<next>`) until it's
exhausted, accumulating every row. Each Mist returns: `id`, `name`, `kind`, `state`, `slug`, `public_url`,
`provisioned_at`, `scheduled_destroy_at`, `created_at`, `updated_at`. (The list already spans all visible
states — no `filter[state]` needed.)

3. **Fetch each Mist's surfaces.** For every Mist id from Step 2, `fluid_api → GET
/api/v202604/mists/:id/integration_points`. Each point returns `kind` (droplet / drop-zone / mobile-embed)
and `integratable_uuid` — the surface it plugs into. A Mist with an empty list is wired to nothing.

4. **Group and describe.** Present the apps grouped by `state`, live first (live → provisioning → failed →
pending_destroy → archived). For each: `name`, `kind`, `public_url`, and the surfaces it plugs into (or "not
wired to any surface").

5. **Run the redundancy checks** — this is the point of the skill. Flag:
   - **Name collisions:** two or more apps whose `name` matches case-insensitively (trimmed) — the create
endpoint only guards a 10-minute window, so older twins slip through undetected.
   - **Surface already covered:** an existing `live` app already has an integration point of the
`kind`/surface you're about to build (e.g. a droplet-linked Mist already exists for that droplet).
   - **Failed leftovers:** any `failed` app. A failed provisioning run can leave cloud resources (repo /
database / project) still attached and billable. Recommend `DELETE /api/v202604/mists/:id` to reclaim them
rather than creating a fresh one.
   - **Unused apps:** `live` apps with zero integration points — created but never plugged into anything;
reuse one of these before creating new.
   - **Pending destruction:** `pending_destroy` apps whose `scheduled_destroy_at` is still in the future are
inside the 15-day grace window — restorable via `POST /api/v202604/mists/:id/restore` instead of recreating.

6. **Emit a verdict.** End with a short "Before you create a new Mist" section: either "no existing app
covers this — safe to create", or "reuse / restore / clean up <named app> first", naming the specific app and
the exact action.

7. **(Optional) Live deployment health.** Only if asked, enrich `live` apps with their latest deployment via
`fluid_api → GET /api/v202604/mists/:id/deployments?limit=1` and report the deployment `state` (ready /
building / error / canceled / queued). Skip by default — it's one extra call per app.

# Notes

- Read-only. Never call POST / PATCH / DELETE. Deletes and restores are recommendations for the user to run.
- The list endpoint returns only kept rows, so fully torn-down Mists are intentionally absent — the summary
is about apps that still exist.
- The API does not expose vendor identifiers (Vercel / Neon / GitHub), so "may still hold cloud resources" is
inferred from `state: failed`, not from reading vendor IDs.
