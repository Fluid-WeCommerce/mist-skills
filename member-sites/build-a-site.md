---
name: Build a Site
description: Decide Site vs App vs theme, then build a Fluid Site end to end — create it, run it locally, add pages, the shop, a table or the signed-in member's data through the Member API, publish it with its source saved to git, and check the live link.
icon: globe
---

# Goal

Build what the user asked for as a Fluid **Site** for {{company.name}}, or say plainly that it belongs in an App or the theme. A Site is a static bundle (Vite and React by default) on `@fluid-app/sites`. There is one kind of Site: never Liquid, never `fluid member-site` commands. Call it a "Site".

# Steps

1. **Pick the right thing to build.**

   | The user wants | Build |
   | --- | --- |
   | A quick project: a landing or event page, a sign-up page, a calculator, a team dashboard, a members-only resource page | A **Site**. The default. |
   | A custom domain, server rendering, or server code (secrets, webhooks, long jobs) | A **Mist App** (`create_project` `kind: "mist"`). A published, public company Site can become one later with `fluid sites convert`. |
   | The storefront's own look, product, collection or content pages | The **theme** (`theme` project, Liquid). |

   When it is not clear, `fluid_api("/api/company/v2026-10/project-launch-recommendations", "POST", { "description": "<what the user is building>" })` answers `kind` `site` or `app` with `reasons`, and changes nothing. Tell the user which you chose and why in one line.

2. **Get a Site project.** If the active project's `package.json` depends on `@fluid-app/sites` and `.member-site.json` exists, use it. Otherwise run the **New Site** skill (the **New Site** button, or `create_project` with `kind: "member_site"`), then continue in the new project's chat. Its source starts from the public `Fluid-WeCommerce/member-site-template` and lives in its own repository, `site-<id>`.

3. **Read before you add.** Read `src/`, `config/` and `db/` and extend what is there.

4. **Build what was asked, and only that.**
   - Pages: a component, its path in `src/App.tsx`, a `<Link>` to it (never a bare `<a>` between the site's pages), and its route in `config/meta.json` (`"routes": ["/about"]`, `"routeMeta": { "/about": { "title": "About", "description": "…" } }`).
   - Products: the **Add a shop** skill (real variant ids only, `fluid.cart`, credited links from `fluid.storefront.url`).
   - Something visitors write: the **Add a database table** skill.
   - The signed-in member's own data: the Member API (below).
   - SEO: `config/meta.json` holds `default` (title under 200 characters, description under 500, image), `url`, `twitter`, `routes` and `routeMeta` (with `noindex` for a page to keep out of search). Add `fluidSite()` from `@fluid-app/sites/vite` to `vite.config.ts` (`plugins: [react(), fluidSite()]`) so the build writes head tags, one page per route, `llms.txt` and, with `url`, `sitemap.xml`.
   - Style with the CSS tokens at the top of `src/styles.css`.

5. **Run it.** `start_preview` runs `fluid sites dev`. `screenshot_preview` and `read_preview_console` to see it. Locally `fluid.api` and sign-in answer 503, the cart needs the storefront, and `fluid.db` uses a private `.fluid/dev.sqlite`: those parts are checked after publishing.

6. **Check it.** `npm run build`, then `fluid sites lint` through `run_cli`, and fix every error.

7. **Publish only when the user asks**: the **Publish and check** skill. Publishing commits the folder to the site's repository, uploads the build and makes it live. A new Site is private until the user asks for `fluid sites visibility public`. `fluid sites rollback` goes back to an earlier deployment.

8. **Report**: what you built, the files you changed, the scopes in `config/access.json`, and what can only be checked on the live Site.

# The Member API from a Site

`fluid.api` calls the Member API, `/api/member/v2026-10/...`, as the visitor viewing the Site: `fluid.api.get("/orders")` is `GET /api/member/v2026-10/orders` for them. The company API (`/api/company/v2026-10/...`, `/api/v202604/...`) acts for an admin over the whole company, and a Site never calls it.

- **No token in the Site, ever.** The storefront session reaches the API through the Site's own origin. A guest gets 401: show a button that calls `fluid.auth.signIn()`. An admin who opens the Site acts as the member with the admin's email in that company, and gets 401 without one.
- **Scopes.** Add each family the Site calls to `config/access.json`, read or write by method: `{ "uses": ["orders: read", "profile: read", "tasks: write"] }`. Families: `addresses`, `agreements`, `ai`, `calendar`, `carts`, `contacts`, `media`, `messages`, `mysite`, `notifications`, `orders`, `plan`, `points`, `profile` (`/me`, `/profile`), `search`, `shares`, `stats`, `subscriptions`, `tasks`. An undeclared call is 403 `scope_not_granted`.
- **Shape.** Success is `{ status, data, meta }`. Lists page with `page[limit]` and `page[cursor]`; the next cursor is `meta.pagination.next_cursor`, null on the last page. An error is `{ status, error: { message, details }, meta }`, and its code is `error.details.error`.
- **Out of reach for a Site's page:** sites and the site menu, shares and share targets, payment methods, Exigo data (commissions, payouts), Team and genealogy (downline), notifications, contacts' orders and subscriptions, and writes to subscriptions and addresses. Visitors the Site is shared with also never get contacts, message or share writes, cart writes, agreement acceptance or `PATCH /me`. A project that needs those is an App or a portal screen.
- `fluid.api.get(path, query)` throws `FluidRequestError` (`status`, `code`) on a non-2xx; `fluid.api.fetch(path, init)` returns the `Response` and is how you write.

```ts
import { fluid, FluidRequestError } from "@fluid-app/sites";

// "profile: read"
const { data: me } = await fluid.api.get<{ data: { first_name: string } }>("/me");

// "orders: read": ten newest, then the next page with page[cursor]
const page = await fluid.api.get<{
  data: { id: string; number: string; total: string; currency: string }[];
  meta: { pagination: { next_cursor: string | null } };
}>("/orders", { "page[limit]": "10" });

// "tasks: write"
const res = await fluid.api.fetch("/tasks", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Call Jordan", due_at: "2026-12-01T16:00:00Z" }),
});
if (res.status === 401) fluid.auth.signIn();
```

Name only paths the Member API has: `/me`, `/profile`, `/orders`, `/orders/{id}`, `/subscriptions`, `/subscriptions/{id}`, `/points`, `/points/ledger`, `/plan`, `/carts`, `/contacts`, `/tasks`, `/notes`, `/calendar/events`, `/media`, `/playlists`, `/shares`, `/stats`, `/messaging/conversations`, `/agreements`, `/addresses`, `/search`, `/mysite/settings`. Never invent one; read docs.fluid.app's Member API pages when unsure.

# Where it opens

- `https://<store>/home/sites/<handle>` (canonical) and `https://<store>/sites/<handle>`, inside the storefront's cart, sign-in and account menu.
- A member's share link, `https://<store>/<username>/sites/<handle>`, credits them for what the visitor buys.
- The Site itself runs at `https://<label>.sites.fluid.app`; a public company Site of a company with standalone hosting also opens there directly.
- Visibility is `private` (the default: the owner, the company's admins and whoever it is shared with) or `public`. Only a live, public company Site can ever be indexed by search engines.

# Guardrails

- Never put a token, API key or secret in the Site. Everything in `dist/` is public.
- Never call a Fluid API with the page's own `fetch`; use `fluid.api`, `fluid.db` and `fluid.cart`.
- Never use `fluid member-site …` in a Site, and never write Liquid for it.
- Publish, change visibility, roll back or convert only when the user asks, each with its own approval card.
