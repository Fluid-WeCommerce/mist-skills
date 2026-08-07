---
name: Agent Commerce Publisher
description: Publish a store as a zero-configuration agent-commerce surface — one URL a merchant pastes into ChatGPT, Claude Desktop, or Cursor, after which any assistant can shop the catalog, quote a real landed total, and hand checkout to a human.
icon: bot
---

# Goal

Build the storefront's agent interface as a Mist app. The deliverable is **one
URL**. A merchant pastes it into a GPT builder or an MCP client and the assistant
can shop the store with no API key, no shop name, and no setup.

The hard constraint that shapes every decision: **the agent assembles, the human
pays.** There is no order-placing tool and no payment tool. Adding one later is a
product decision, not a follow-up task.

**Run this skill when the merchant wants their store reachable from AI
assistants** — "make my store work in ChatGPT", "an MCP server for our catalog",
"let Claude order our filters", "agentic commerce".

Do **not** use it to build a chat widget for the merchant's own site. This is the
outbound direction: the merchant's store exposed to agents the merchant does not
control.

**Why a Mist app and not a theme feature.** The tools must be reachable by a
server with no browser, no cookies, and no session. That is an HTTP surface, not
a Liquid template. The theme's job is to *advertise* the surface (step 8); the
Mist app *is* the surface.

---

## What "broken" means here

Every one of these was hit live during the build this skill is derived from. None
trips a type check or a lint. Each surfaces as an agent confidently telling a
customer something false.

| # | Failure | What it costs |
|---|---------|---------------|
| 1 | **`source` sent as free text** — it is an ENUM (`web`, `mobile`, `external`, `admin`) | Every cart create 422s. The first integration attempt fails with no obvious cause. |
| 2 | **Address sent as PATCH**, or sent and then followed by a "recalculate" call that does not exist | No tax, no shipping. The agent quotes a subtotal as if it were the landed total. |
| 3 | **Caller metadata written at the top level** — it merges into the same object as Fluid's system keys | A caller writing `metadata.shipping` clobbers the cart's selected shipping method. Silent, and it breaks a real order. |
| 4 | **Metafields read from the wrong accessor** — populated on `metafields` from the storefront API, on `metafields_collection` from the cart payload | Compatibility data reads as absent. The matcher returns nothing and the agent guesses. |
| 5 | **Checkout URL composed from a slug or token** instead of quoted from `meta.checkout_url` | A link that 404s handed to a buyer at the moment of purchase. |
| 6 | **Compliance handled in prompt text** rather than code | An agent that ignores the instruction makes a regulated claim in the merchant's name. |
| 7 | **Compatibility ids matched as substrings** | `86814` matches `868140`. Ships a part that does not fit: a return, a support ticket, a lost customer. |
| 8 | **Raw cart tokens in logs** | The token *is* the capability. A log reader can mutate any cart in it. |
| 9 | **MCP envelope written against a stale spec revision** | `tools/list` succeeds and `tools/call` fails, or the client refuses to connect at all. |

---

## Step 1 — Verify the cart surface is token-only before writing anything

The whole design depends on this. Check it live; do not assume:

```
cat /openapi/api-reference/checkout-v2026-04.yaml | jq '.paths["/api/checkout/v2026-04/carts"].post.security'
```

`security: []` on cart create/read/items/address/metadata means the cart token is
the entire capability — no bearer, no cookie. That is what makes zero-config
possible: the app holds no merchant credential an agent could borrow.

Then create one real cart against the live store **before writing a line of app
code**. You are looking for the response's `meta.checkout_url` and the exact
`source` enum. Both bite later if assumed.

## Step 2 — Bake the shop identity in server-side

`fluid_shop` comes from config, **never from the caller**. An agent that has to be
told the shop name is not zero-config, and a caller-supplied shop is an open proxy
to every store on the platform.

Two hosts, both public. Do not confuse them:

- carts → `https://api.fluid.app`
- catalog → `https://<fluid_shop>.fluid.app` (company resolved by subdomain)

Never attach an `Authorization` header. If Fluid ever starts requiring one on
these paths, the call must fail loudly rather than silently escalate to a
credentialed request.

## Step 3 — Build the seven tools from one registry

One registry drives both transports so they cannot drift.

| Tool | Contract |
|------|----------|
| `find_products` | Search; optionally resolve what fits a device the customer owns |
| `start_cart` | Create with `source: "external"`; return token + checkout_url + totals |
| `view_cart` | Fresh GET every time |
| `update_cart` | add / set_quantity / change_variant / remove (quantity 0 removes) |
| `set_destination` | POST address → real tax + shipping, broken out |
| `save_context` | Merge agent notes under ONE reserved namespace |
| `handoff` | Fresh read → checkout_url + one-line summary |

### Hard exclusions

Not implemented, not described in the OpenAPI, and not added without an explicit
product decision:

- `POST /carts/{token}/complete`
- anything under `/api/payments/*` or `/api/payment/*`
- customer JWT / MFA / `customers/me`

**Write a test that greps the whole tool surface for these verbs and fails if one
appears.** A prose promise is not an exclusion; a failing test is.

### API facts that silently break a naive implementation

- **`source` is an ENUM**: `web | mobile | external | admin`. Anything else 422s.
  Use `external` — agent traffic becomes a clean analytics segment for free.
- **Address is POST, not PATCH**, at `/carts/{token}/address`. The body needs
  `type: "both"` and `use_shipping_address_for_billing: true`.
- **Setting the address computes tax and shipping.** There is no separate
  recalculate call.
- **`state` is not enforced on a US address.** Verified live: the API accepts an
  address without it and still returns correct postal-code-derived tax, storing
  `state: null`. But `province_required: true` on the country means the human's
  checkout page still asks for it. Tell the agent to send it — do **not** claim
  the API rejects it, because that is the intuitive assumption and it is wrong.
- **`meta.checkout_url` must be quoted from the response.** Never compose a
  checkout URL from a slug or token you hold. If it is missing, error — do not
  synthesize one.
- **Metafields invert by surface.** On `/api/v202604/products` the populated
  accessor is `metafields`; on the CART payload it is `metafields_collection`
  while `metafields` is `[]`. Read whichever is non-empty.

## Step 4 — Namespace cart metadata, because it is a correctness requirement

`PATCH /carts/{token}/metadata` merges into the **same object** as Fluid's system
keys: `shipping`, `timezone`, `available_shipping_methods`,
`total_creditable_points`, `routed_credit_card_pa_id`.

A caller writing `metadata.shipping` **clobbers the cart's selected shipping
method**. Nest every caller key under one reserved namespace (`agent_session`),
enforce that server-side, and read-modify-write so a save does not replace the
namespace wholesale.

Test it adversarially: send `context.shipping = "CLOBBER"` and assert it lands
*inside* the namespace with the system keys intact. Return that proof in the
response rather than claiming it in a comment.

## Step 5 — Match deterministically, never by model inference

If the catalog has a compatibility relationship — device→consumable,
garment→size chart, printer→cartridge — resolve it **in code from structured
data** and return the field that proved it.

Compare ids **delimiter-wrapped**: build `",86814,"` and test against `",{id},"`,
so `86814` cannot match `868140`. A substring match here ships a part that does
not fit, which costs a return, a support ticket, and the customer.

When a device cannot be resolved, return `resolved: false` plus candidates and
let the agent ask. Guessing is worse than asking.

Skip this step entirely for catalogs with no compatibility relationship. It is
not a universal requirement.

## Step 6 — Make the compliance gate code, not a prompt

If the vertical is regulated — supplements, medical devices, financial products,
alcohol — prompt instructions are not a control. An agent can ignore an
instruction; it cannot ignore a filter.

Run every outbound prose string through a deterministic filter, and **report**
rewrites in `meta.compliance_rewrites` rather than applying them silently. Never
scrub URL or identifier fields (`url`, `slug`, `sku`, `checkout_url`) — rewriting
those breaks links.

**The trap:** the rules, stated plainly, trip their own filter. "Never say it
treats a condition" contains the blocked token. Carry separate gate-clean phrasing
for anything published, and assert with a test that scrubbing your own OpenAPI and
`llms.txt` is a **no-op**. If your own documentation needs rewriting, the filter is
mis-scoped.

Publish the same rules at `/llms.txt` so well-behaved agents self-limit too. Belt
and braces, not either/or.

## Step 7 — Serve both transports, and validate the schema honestly

- **`GET /openapi.json`** — OpenAPI 3.1, `security: []`, absolute server URL
  derived from the request. Keep it boring: no vendor extensions, no external
  `$ref`, one operation per path, unique identifier-safe `operationId`s, every
  response described, every body property typed and described, operation
  descriptions ≤300 characters.
- **`GET|POST /mcp`** — Streamable HTTP. **Check the current spec before writing;
  the envelope changes between revisions.** As of 2025-06-18: batching is removed
  (reject arrays), session ids are OPTIONAL (be stateless on serverless — there is
  no shared process memory), decline the SSE stream with 405 if you have no
  server-initiated messages, and return TOOL failures as a result with
  `isError: true`, not as a JSON-RPC error.
- **`GET /llms.txt`** — what the store is, what the agent can do, the compliance
  rules, and pointers to the other two.
- **`GET /`** — a genuinely useful human landing page with copy buttons and
  per-client setup steps. This is what the merchant pastes from.

**You cannot run ChatGPT's importer.** Do not claim the schema passes it. Test the
constraints Actions enforces, and say exactly that.

## Step 8 — Emit discovery for everyone; do not try to detect agents

Merchants ask for "show something different when an AI hits the page." Verified
against the docs, it cannot be built in a Fluid theme:

1. The Liquid `request` object exposes only `path`, `host`, `full_url`,
   `page_type`, `query_parameters`. There is no `request.headers` and no
   user-agent, so a server-side `{% if ... GPTBot %}` branch is not expressible.
2. Storefront HTML is cached. Fluid's own affiliate hydration exists *because* of
   this, and the docs warn against treating `affiliate.name` as a reliable
   server-rendered sign-in check. Per-visitor server-rendered variation is not
   something the storefront layer promises.

Client-side user-agent sniffing is self-defeating: the crawlers worth catching
(GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot) largely do not execute
JavaScript, so the branch fires for humans and misses the agents.

Instead emit discovery for everyone, always — cache-safe, JS-free, and it works
for crawlers that do not exist yet. In `layouts/theme.liquid`, inside `<head>`:

```liquid
<link rel="alternate" type="text/plain" title="LLM instructions" href="{APP}/llms.txt">
<link rel="alternate" type="application/json" title="Agent shopping tools (OpenAPI 3.1)" href="{APP}/openapi.json">
<meta name="agent-tools-openapi" content="{APP}/openapi.json">
<meta name="agent-tools-mcp" content="{APP}/mcp">
```

`request.query_parameters` **is** available and **is** cache-safe (different URL →
different cache key), so a link handed to an agent can carry `?ai=1` and vary the
template. Verify dot-access (`request.query_parameters.ai`) against bracket syntax
in a rendered storefront before relying on it — that has not been confirmed. This
is a nice-to-have on top of the always-on tags, never a replacement for them.

## Step 9 — Build a separate embed surface and measure it

Build a compact `/embed` route separate from `/` — no hero, no long prose — and
frame that from the theme page and the portal Embed widget.

**Measure the height at both breakpoints and put the real numbers in the
handoff.** An estimate produces either a scrollbar or a dead band. Have `/embed`
fill its own viewport height on a light surface so an over-tall iframe shows
padding rather than a mismatched colour block.

CSP `frame-ancestors` must allow `*.fluid.app`, which covers storefront, admin and
portal. **A custom domain is not covered** — expose an env var for extra origins.

Scaffold trap: the starter `globals.css` sets a near-black `--background` under
`prefers-color-scheme: dark`. A light-only page whose `<main>` does not fill the
viewport shows a black band below the content for dark-mode viewers — very visible
inside an iframe. Pin `color-scheme: light` rather than patching it per page.

## Step 10 — Own the audit trail, because Fluid does not

Fluid keeps no agent-side audit trail for cart-token traffic. This app is it.

Log every call with the tool, its arguments, and the Fluid `meta.request_id`s it
produced, so a cart's history is reconstructable. Two things must never land in
the log:

- **the raw cart token** — it *is* the capability. Key on a SHA-256 prefix so
  history still joins up without storing a live credential.
- **shipping PII** — reduce it to presence flags.

Make the write non-throwing (a logging failure must never fail a sale) and emit the
same record to stdout, so it survives a database outage.

## Step 11 — Relay upstream errors verbatim

Return Fluid's exact body under `error.fluid.body` with its `request_id`. The
`source`-enum 422 is what makes a first integration fixable in one attempt instead
of ten. A swallowed 500 tells the agent nothing, and it will retry the same broken
call.

---

## Verification before declaring done

Local, then production, against the real store — not mocks:

1. **Full lifecycle through your own routes**: `find_products` → `start_cart` →
   `update_cart` → `set_destination` → `save_context` → `handoff`.
2. **A deliberate 422** (bad country code) — confirm the upstream body is relayed
   with its `request_id`.
3. **The metadata clobber attempt** — confirm the system keys are intact.
4. **MCP `initialize` / `tools/list` / `tools/call`** against the current spec
   revision.
5. **`/llms.txt` and `/.well-known/*` on the deployed host.** Next's app router
   ignores dot-prefixed directories, so `/.well-known/*` needs a `next.config`
   rewrite onto a normal route. Both serve correctly on Fluid hosting — verified.
6. `pnpm typecheck && pnpm lint && pnpm build` before push.

**Report what you observed, including anything that turned out wrong.** A cart is
a shared mutable object: `state_revision` moves on its own when the human opens the
checkout page. Fire two mutations at one cart concurrently and you get two
contradictory totals back. That is not a bug to fix — it is the reason `handoff`
re-reads, and it is worth demonstrating rather than asserting.

---

## Reporting the value

Frame the result in the merchant's model of their business, not in tool terms:

> The store is now reachable from any AI assistant with one pasted URL. An
> assistant can find the right part for a device the customer already owns, build
> a cart, and quote a real landed total including tax and shipping — then hand a
> live checkout link to the human, who is still the only one who can pay.

If there is agent traffic to measure, quantify it: carts created with
`source: "external"`, the share reaching handoff, and the share of those completed
by a human. The `external` enum makes that a free segment.

If the surface is new and has no traffic yet, **say so plainly and report the
structural work instead.** A fabricated adoption projection is worse than an
honest statement of what now exists — the merchant will test the number.

---

## Notes and traps

- **The agent assembles, the human pays.** There is no order tool and no payment
  tool. The greps in step 3 are what keep it that way after the next contributor.
- **`source` is an enum, and `external` is the right value.** It is also free
  analytics segmentation, so there is no reason to reach for another.
- **Setting the address is the recalculation.** Do not look for a totals endpoint;
  there isn't one.
- **Metadata is a shared object, not your object.** One reserved namespace,
  enforced server-side, read-modify-write.
- **Metafields invert by surface.** Read whichever accessor is non-empty rather
  than picking one and trusting it.
- **Never compose a checkout URL.** Quote `meta.checkout_url` or error.
- **A prompt is not a control, and a comment is not a test.** Compliance is a
  filter over outbound payloads; exclusions are a failing grep.
- **The compliance rules trip their own filter.** Keep gate-clean phrasing for
  published copy and test that scrubbing your own docs is a no-op.
- **Delimiter-wrap id comparisons.** `86814` must not match `868140`.
- **The cart token is the capability.** SHA-256 prefix in logs, never the raw
  value, and never in an error message or rendered markup.
- **Check the MCP spec revision before writing the envelope.** It has changed
  between revisions and will change again.
- **You cannot run the ChatGPT Actions importer.** Test the constraints it
  enforces and report exactly that, rather than claiming a pass you did not
  observe.
