---
name: Publish and check a Site
description: Build, lint and publish a Site with fluid sites publish, confirm destructive database changes only with the owner's yes, then open the live page and report its link.
icon: rocket
---

# Goal

Make the Site in this folder live: build it, check it with `fluid sites lint`, publish it with `fluid sites publish`, then read the live site back and give the user its link. Running this skill is the user asking to publish; still get their yes on each card below.

# Steps

1. Confirm the active folder is a Site: `read_file("package.json")` and check that `dependencies` or `devDependencies` names `@fluid-app/sites`. If not, stop and say: "This folder isn't a Site (its package.json doesn't depend on @fluid-app/sites), so I didn't publish anything." An old Liquid site publishes with its own Publish (`fluid member-site push --publish`), never with this skill.
2. Confirm the folder is bound to a site: `read_file(".member-site.json")` and note `handle` and `site_id`. If it is missing, stop: the site has not been created yet (run **New Site**, which binds it with `fluid sites create`). Never edit this file.
3. Build. If `node_modules/` is missing, install with `install_project_dependencies` (`action: "install"`, with its own approval card) first. Then `npm run build` through `run_cli`. It typechecks and writes `dist/`; publish refuses a folder with no `dist/index.html`. On a build error, fix it or stop and show it.
4. `fluid sites lint` through `run_cli`. It checks `dist/`, `db/schema.json` and `config/*.json` against the contracts and makes no request. A clean folder prints nothing; exit 1 means an error. Fix every error before going on.
5. Look for destructive database changes. If `db/schema.json` has a `migrations` array, list each migration's id and its steps in plain words (for example "Delete the column `note` of `rsvps`, and what every row holds in it"). The first publish of a database skips migrations; on a later publish each new one must be confirmed by the owner, or the publish is refused with nothing changed.
6. Publish. Two ways:
   - **In Mist, the Publish button** in the site's preview is the normal path. It runs `npm run build` and `fluid sites publish --json`, and when the schema has unconfirmed destructive migrations it lists their steps and asks the owner to confirm each one.
   - **From chat**, `run_cli` `fluid sites publish --json`. It writes to Fluid, so call it once without `approval_id` to get the card title, propose it with `human_in_the_loop`, end your turn, and after Approve run the same command with that `approval_id`. Do not add `--as`: the folder's binding names the site and its owner.

   It first commits the folder and pushes it to the site's own source repository (`site-<id>` on Fluid's GitHub), then uploads the build. It leaves out only `.env`, `.env.<name>`, `.envrc`, `.npmrc`, `.member-site.json`, `node_modules` and `dist/`: a file such as `.env-secret` would be committed, so never keep a secret in the folder. When Fluid cannot set the repository up, it says so and publishes without the source (`--no-source` skips it on purpose), so git usually, not always, holds every publish.

   Read the one JSON line it prints, and do not assume:
   - `{"ok":true,"site":…,"bundle":…,"manifestSha256":…}`: published. It uploads only the files the site does not store yet, and the new build serves only once the last step succeeds.
   - `destructive_change_unconfirmed` with `unconfirmed` ids: nothing was published. Show the user each id's steps from step 5 and ask for an explicit yes on each. For the ones they confirm, publish again with `--confirm <id>` once per id (a new approval card). Never confirm an id the user did not say yes to.
   - `schema_change_pending`: an earlier publish's database change has to be finished first. `--finish-pending` publishes that pending bundle again to finish it, and does not publish this build; run the normal publish again after it. If finishing it is refused for its own destructive migrations, those ids need the owner's yes and go with `--confirm-pending <id>`; `--confirm` is never sent with the pending bundle.
   - A 404 when it starts: sites are not turned on for this company. Say so and do not retry; the company asks Fluid support to turn them on.
   - `publish_timeout`: the CLI has already sent it three times and the current version is still serving. It is safe to run the same command again: the files are stored, so nothing is uploaded twice.
   - A 409 after a retry: an earlier attempt may have finished. Check the live site (step 8) before you publish again.
   - A 422 names the check that failed and where. A site a company admin took down cannot be published.
7. Visibility. A new site is private: only its owner, the company's admins and the members it is shared with can open it. Change it only if the user asks: `fluid sites visibility public` (anyone can open it) or `fluid sites visibility private`, through `run_cli` with its own approval card. Never make a site public on your own.
8. Check the live site:
   - `fluid_api("/api/company/v2026-10/member-sites/<site_id>", "GET")` with the `site_id` from `.member-site.json`. Confirm `member_site.status` is `published`, and read `visibility`, `share_url` (the link to share; it credits the company) and `site_url` (where members open it). A null `share_url` means the sites gateway cannot serve the site yet: say so.
   - `web_fetch` the `share_url` and confirm it answers with the storefront page, not an error or a not-found page. The site's own content runs in a frame inside that page, so also ask the user to open the preview's **Prod** tab, or the link, and look at it. A private site shows a sign-in or refusal page to a signed-out fetch: that is expected, not a failure.
9. If the new version is wrong, roll back rather than rebuilding blind: `fluid sites deployments` lists them (newest first, `*` is current) and `fluid sites rollback [<id>]` makes one current again at once (its own approval card). With no id it goes to the newest kept deployment that is not current.
10. Report: the site's handle, the link (`share_url`, else `site_url`; the storefront address is `https://<store>/home/sites/<handle>`, and a member's share link is `https://<store>/<username>/sites/<handle>`), the bundle id, the visibility, and any migration that was confirmed. If the site has a database, say that the live tables start with only what was published (local rows from `fluid sites dev` never reach it) and that database usage is billed to the company's credits.

# Guardrails

- Publish only when the user asked, and only with `fluid sites publish` (or Mist's Publish button) for a static site.
- Never confirm a destructive migration without the owner's explicit yes for that id.
- Never change visibility unless asked.
- Never retry after a 404, and never create a new site to get past a publish error.
