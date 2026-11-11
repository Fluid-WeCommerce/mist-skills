---
name: New Site
description: Create a Site on @fluid-app/sites for the active company, install it, and start it locally with fluid sites dev.
icon: globe
---

# Goal

Create a Site for {{company.name}}: a Vite and React app on `@fluid-app/sites`, bound to a new company-owned site, with its packages installed and running locally under `fluid sites dev`. Nothing goes live in this skill: a new site is a private draft until it is published.

This skill is for Sites only. Never use `fluid member-site pull`, `push` or `dev` here: those are for the old Liquid sites, and `pull` would write Liquid files into the folder.

# Steps

1. Look at the active folder and decide which case it is. `read_file("package.json")` and check whether `dependencies` or `devDependencies` names `@fluid-app/sites`, then check for `.member-site.json`.
   - **A Site with `.member-site.json`.** It is already bound to a site. Read `handle` and `site_id` from `.member-site.json`, tell the user, and go to step 5. Do not create another site.
   - **A Site with no `.member-site.json`.** The template is here but no site exists yet. Go to step 2, then bind it in step 4.
   - **Anything else** (no `package.json`, a theme, a Mist app, an old Liquid site). Do not change this folder. Go to step 2, then create the site as a new project in step 3.
2. Ask the user for the site's name, such as "Diamond Leaders". Derive the handle from it: lowercase letters, digits and single hyphens, at most 40 characters (`Diamond Leaders` becomes `diamond-leaders`). Show both and get a yes. A name with no letters or digits cannot make a handle: ask for another.
3. **New project** (the "anything else" case). The normal path is the **New Site** button in Mist's Sites sidebar section: ask the user to click it and enter the name. To do it from chat instead, call `create_project` with `kind: "member_site"` and the name; it refuses the first call and returns the exact `human_in_the_loop` proposal to make. Propose it, end your turn, and after Approve call it again with that `approval_id`, `confirm_create: true` and the same arguments. Mist unpacks the blank template, runs `fluid sites create <handle> <folder> --company --name <name>`, and adds the project to the sidebar, without installing its packages.

   Open the new project's `package.json`. If it does not depend on `@fluid-app/sites`, the company is not on the sites gateway and Mist made a Liquid site: say so and stop. Otherwise tell the user to open the new site and run this skill again there, which picks up at step 5. Stop here: do not edit the new project's files from this chat.
4. **Bind this folder** (the static, unbound case). First check the handle is free: `run_cli` `fluid sites list`, and stop if a site already has it. Then run `fluid sites create <handle> --company --name "<Name>" .` through `run_cli`. It writes to Fluid, so call it once without `approval_id` to get the card title, propose it with `human_in_the_loop`, end your turn, and after Approve run the same command with that `approval_id`. It prints `Created company site <handle> (<id>) as a draft.` and `Bound <folder> to <handle>.`, and writes `.member-site.json`; it leaves the template's files alone. A company site needs an admin login, which Mist's company sign-in is.
   - Run again in a folder already bound to this site, it creates nothing. It refuses a folder bound to a different site: never work around that.
   - If it failed after printing `Created company site …`, the site exists. Do not create it again; check `fluid sites list`.
5. Install the packages if `node_modules/` is missing: call `install_project_dependencies` with `action: "install"`. It needs its own approval: call once without `approval_id`, propose the card it names, end your turn, and repeat with the `approval_id` after Approve. Never run `npm install` through `run_cli` and never edit `package.json` to get around the approval.
6. Start the site: call `start_preview`. For a Site Mist runs `fluid sites dev`, which starts the site's dev script at `http://127.0.0.1:<port>` and answers `fluid.db` from `.fluid/dev.sqlite` in the folder. (Outside Mist, the same thing is `fluid sites dev` in the folder; the default port is 9500.)
7. Confirm it works:
   - `read_recent_log_tail`: find `Serving <folder> at http://127.0.0.1:<port>` and no errors.
   - `screenshot_preview` at `/`: the home page renders, not a blank page or an error. `read_preview_console` shows no errors.
   - If `db/schema.json` exists, the log says `/_fluid/db reads and writes .fluid/dev.sqlite only`. Check the tables were made: `db_query` with `side: "local"` and `SELECT name FROM sqlite_master WHERE type = 'table'` (the `_fluid_*` tables are the database's own bookkeeping). A new blank site has no `db/` folder and no database, which is expected.
8. Report: the site's name, handle and `site_id`, the local URL, and that it is a private draft that nobody can open until it is published. Next steps: grow it (the **Add a database table** and **Add a shop** skills), then **Publish and check**.

# What works locally

`fluid sites dev` runs the site outside the storefront. The viewer is a local stand-in owner (`local-owner`), so rows written locally carry `created_by: "local-owner"` and never reach the live site. The Fluid API (`fluid.api`) answers 503 locally, `fluid.cart` rejects because there is no storefront shell, and `fluid.storefront.url` has no storefront address. The cart, checkout, sign-in and credited storefront links work only once the site is published and opened at its storefront address.

# Guardrails

- Never edit `.member-site.json`, and never copy it into another folder: it names the site the folder publishes to.
- Never create a second site to get past an error. Check `fluid sites list` first.
- Do not publish in this skill.
- Do not add a shop, a table or sign-in content the user did not ask for.
