---
name: Portal Widget or Mist App
description: Decide whether a requested feature should be a company portal widget or a Mist app with a droplet, and surface it correctly on a portal screen.
icon: git-fork
---

# Goal

Route a "build me X for the portal" request to the right system before any code
is written. This is the most expensive decision to get wrong in portal work: a
portal widget cannot be converted into a Mist app, or the reverse, without
starting over.

The deciding question is:

> Is any of this data from outside Fluid?

If yes, it is a Mist app. If every field comes from Fluid — orders, products,
account, shares, subscriptions, content, points, todos, calendar — it is a
portal widget. There is no third option, and the reasons are in "Why there is no
third case" below.

# The two systems

## Company portal widget

A portal widget is a Remote DOM package that runs inside a **locked-down Web
Worker** in the portal. `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`,
`localStorage`, `indexedDB` and a dozen more globals are removed before widget
code runs, and no capability re-grants them. **A portal widget cannot make a
network request.**

Its data comes from exactly three places:

- props written into the screen JSON
- built-in host capabilities — `account`, `store`, `products`, `content`,
  `mySite`, `todos`, `calendar`, `points`, `localization`, and similar
- data sources the host resolves and passes in as props: `api` with a **Fluid
  preset**, `custom` for hand-picked Fluid resources, `static` for literal data.
  A preset resolves to a Fluid path against the portal's own base URL. Writing an
  absolute third-party URL into a data source is not a supported way to reach an
  outside API — see below.

Cheap to build, nothing to host, no secrets, no install lifecycle.

## Mist app

A Mist app is a hosted application with its own backend and a `public_url`. It
can hold secrets, call any external API, receive webhooks, and do server-side
work.

Fluid surfaces it through integration records that **all point at that same
`public_url`**:

| Record           | What it is                                                                                                                        | Per mist |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------- | -------- |
| **Droplet**      | Identity and credentials — `FLUID_DROPLET_UUID` / `FLUID_DROPLET_SECRET` / `FLUID_DROPLET_WEBHOOK_AUTH_TOKEN`, OAuth scopes, install lifecycle and webhooks | one      |
| **Mobile embed** | A placement in the mobile app: `embed_url` plus a required cover image and height                                                 | many     |
| **Drop zone**    | A placement in an admin page/zone slot                                                                                            | many     |

**The droplet is not the app.** It is the app's identity and permission record.
The Mist app is what runs, and it is what every embed points at. A droplet must
also be *installed*, not just created and linked, or install-scoped features
(token exchange, admin embeds, install webhooks) will not work.

# Steps

1. **Classify the request** into one of two cases:

   1. **Mist app** — any data or action from outside Fluid. A third-party API,
      an API key, OAuth, webhooks, background jobs, server-side processing.
      "Free", "public", "no API key" and "CORS-enabled" do NOT move a request
      out of this case; see "Why there is no third case".
   2. **Portal widget** — every field comes from Fluid: orders, products,
      account, shares, subscriptions, content, points, todos, calendar.

   The test is the source of the data, not the difficulty of reaching it.

2. **When the request is ambiguous, ask.** Say which two systems you are
   choosing between and what the tradeoff is (hosting and credentials versus a
   presentation-only widget). Do not guess — the rework cost is the whole
   feature.

   A request is not ambiguous merely because the outside API is easy to call.
   "Build me a widget that shows the weather" is a Mist app: the noun the user
   reached for is not the architecture decision, and they have no way to know a
   portal widget runs in a worker with `fetch` removed.

3. **Check whether it already exists before building.** An installed droplet may
   already publish registered widget types. Confirm with
   `GET /api/company/mobile_widgets` for mobile-embed placements, and by
   inspecting a builder-authored screen for registered widget types. Prefer what
   exists over rebuilding it.

4. **For case 1**, build the Mist app first, then attach its surfaces: a droplet
   for identity and credentials, plus a mobile embed or drop zone for placement.
   Every `embed_url` is the Mist's `public_url`.

5. **For case 2**, build a company portal widget in the portal project and
   publish it with `fluid portal deploy`.

# Why there is no third case

An earlier version of this skill offered one: a portal widget whose `api` data
source names an absolute third-party URL, for "public, unauthenticated,
CORS-enabled JSON and nothing more." A free weather API fits that description
exactly, which is the problem — it reads as the more specific match and wins over
"Mist app" every time.

It should not, for four reasons, none of which are visible to the agent choosing
it:

1. **It does not work in Mist's preview.** The renderer's CSP `connect-src`
   allows `api.fluid.app`, `auth.fluid.app`, `*.fluid.app`, `*.wecommerce.dev`
   and a few Fluid-owned hosts. A third-party origin is refused before the
   request leaves. The tool the portal is built in is the one place this path
   cannot run.
2. **It does not work on a Fluid-hosted portal.** That nginx policy allows three
   origins.
3. **It appears to work on a scaffolded portal**, which ships no CSP at all. So
   the one environment where it succeeds is the one nobody tests in, and the two
   where it fails are preview and production. A widget built this way looks
   broken locally and ships broken.
4. **It sends the member's Fluid credentials to the third party.** The `api`
   fetcher spreads `context.getApiHeaders()` into every request including one
   with an absolute endpoint. In Mist's preview that returns an
   `Authorization: Bearer <jwt>` header. Whatever host the endpoint names
   receives it.

The failure mode when this is attempted is also worth naming, because it is
seductive: the fetch is refused, and the obvious next move is to bake a static
snapshot of the response into the screen JSON so the widget renders. Do not do
that. A widget showing frozen data reads as success in every screenshot and is a
lie. Report the boundary instead.

If the data is not Fluid's, build the Mist app. It survives an API key being
added later, it holds its own secrets, and it works in preview, on a scaffolded
portal, and on a hosted one.

# Surfacing a Mist app on a portal screen

Point the embed at the **Mist's public URL**, or at a purpose-built widget route
the Mist app serves. Those routes are built to be iframed and need no
installation parameter.

**Never point an embed at the droplet's `/embed` route.** That is the admin
dashboard surface and requires a `?dri=` installation parameter. Without one it
renders "Missing installation" or a blank frame. This mistake looks reasonable
and fails quietly.

If the Mist app publishes **registered widget types**, prefer those over an
iframe embed — they compose properly with the screen and with the admin builder.
They are addressed like any other widget:

```json
{
  "id": "…",
  "type": "droplet.<scope>.<dropletId>.<WidgetName>",
  "props": { "headline": "…", "ctaLabel": "…" }
}
```

# Do not infer absence from an empty API response

Widget-related endpoints are scoped differently and will each legitimately come
back empty or 404 for a droplet widget that is installed and working:

| Endpoint                           | Why it looks empty                                    |
| ---------------------------------- | ----------------------------------------------------- |
| `/api/droplets` (`app_extensions`) | Does not list contributed widget types                |
| `/__widget-packages__`             | Dev-server route for unpublished *company* packages   |
| `/api/app/widget-packages`         | Portal-session scoped; 404s for an ordinary API token |
| `/api/company/mobile_widgets`      | **Lists installed mobile-embed placements**           |

When you cannot confirm a widget's type or prop shape from an API, **ask the
user to drag it onto a scratch screen in the admin builder, then pull the
definition**. The pulled JSON is ground truth for both the `type` string and the
exact props. Do this early — it costs one message and replaces a chain of
confident guesses.

# Screens you author need a container root

Any screen you create or modify must have exactly one container node
(`ContainerWidget`, `LayoutWidget`, or `CardWidget`) at the top of its
`component_tree`, with every other widget inside its `props.children`.

A screen with bare top-level widgets renders correctly in preview and in the
live portal, so nothing you can observe reveals the problem — but the admin
builder shows **no drop zones** on it, and the user cannot drag anything onto
the page.

# Report

State which of the two cases you chose and why, in one sentence. If you built
a Mist app, report the `public_url`, the droplet uuid, and which placement
surfaces were attached. If you built a portal widget, report the widget type and
whether it was published.
