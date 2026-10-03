# The Global Embed API — verified contract

> Part of the `mist/wisp-install` skill. See [`../SKILL.md`](../SKILL.md) for the install runbook.
> Everything here was read out of the Fluid Rails source, not inferred from docs. File paths are in
> the read-only `~/fluid` checkout. **It is proven in production, not just on paper:** a `POST`
> exactly like the one below created Global Embed **52360** on Prose (2026-07-31) and the pixel went
> live, confirmed in the served storefront HTML with a cache-buster.

## Contents

- Why the API and not the admin UI
- Endpoints
- Schema
- Permissions
- What happens to the content
- Caching — why verification needs a cache-buster
- `target: "checkout"` is dead
- Idempotency recipe

## Why the API and not the admin UI

The Global Embeds drawer in Fluid admin is unreliable to automate: its Save button renders outside
the layout viewport at common window sizes, and its disabled state gets stuck. Every minute spent
driving that drawer is wasted. The REST API is the correct automation path and is fully featured —
index, show, create, update, destroy.

Wisp's ADR-5 used to claim Global Embeds have no API and that install therefore could not be
automated. Both were wrong; the ADR was corrected on 2026-07-31. If you meet a copy of that claim
anywhere else, the doc is stale — the API exists, is routed, and has been driven end to end against
a live company.

## Endpoints

Routed as `resources :global_embeds` inside the `api` namespace
(`~/fluid/config/routes/storefront/api_themes.rb:102`), so:

| Method | Path | Action |
| --- | --- | --- |
| `GET` | `/api/global_embeds` | index — paginated, filterable |
| `GET` | `/api/global_embeds/:id` | show |
| `POST` | `/api/global_embeds` | create → `201 {"global_embed": {…}}` |
| `PUT` / `PATCH` | `/api/global_embeds/:id` | update |
| `DELETE` | `/api/global_embeds/:id` | destroy |

Auth is `Authorization: Bearer <token>` — in Mist Desktop, just
`fluid_api({ path, method, body })`. It takes **one object argument**: `path` required, `method`
optional and defaulting to `GET`, `body` a JSON object for `POST`/`PATCH`/`PUT`. The token is
injected and scoped to the active company.

**Every write on this page needs Safe Mode off.** Mist blocks `fluid_api` for any method other than
`GET` while Safe Mode is on, so the reads below work and the `POST`/`PUT`/`DELETE` are refused.

**Index defaults to `per_page: 10`** (`~/fluid/app/services/api/global_embeds/index_action.rb`).
Pass `per_page=100` or paginate, or your "is Wisp already installed?" check will miss an embed that
exists. Index also accepts `status`, `placement`, and `target` filters.

## Schema

`~/fluid/app/services/api/global_embeds/create_action.rb`:

```ruby
required(:global_embed).hash do
  required(:name).value(:string)
  required(:content).value(:string)
  optional(:status).value(:string,    included_in?: %w[draft active])
  optional(:placement).value(:string, included_in?: %w[head body])
  optional(:target).value(:string,    included_in?: %w[storefront checkout])
end
```

Only `name` and `content` are required. Model defaults (`~/fluid/app/models/global_embed.rb`) fill
the rest: `placement: "head"`, `target: "storefront"`. `status` has no default — set it explicitly.

The Wisp body:

```json
{
  "global_embed": {
    "name": "Wisp session replay",
    "content": "<script async src=\"https://<mist-host>.wecommerce.dev/pixel/v1\" data-wisp-key=\"wk_…\" data-wisp-sampling=\"1\"></script>",
    "status": "active",
    "placement": "head",
    "target": "storefront"
  }
}
```

A validation failure returns `422` with `errors` as a per-field hash — read it, don't retry blindly.

## Permissions

`~/fluid/app/controllers/api/global_embeds_controller.rb`:

```ruby
before_action :authorize_company_admin
authorize_permission :developer, :view,   only: %i[index show]
authorize_permission :developer, :update, only: %i[create update destroy]
```

So the caller must be a **company admin** *and* hold the **`developer`** permission — `view` to
read, `update` to write. A token with `developer:view` but not `developer:update` reads the index
fine and then 403s on create, which is exactly the trap the skill's Step 0 probe is designed to
catch early. Surface a 403 as *"this token lacks the `developer` permission"* — not as a generic
API error.

## What happens to the content

Content is inserted **verbatim**. The model's `before_save :sanitize_content` is a documented no-op:

```ruby
def sanitize_content
  # Basic sanitization to prevent harmful scripts
  self.content = content if content.present?
end
```

Rendering (`~/fluid/app/services/page_builder.rb`, `apply_global_embeds`):

```ruby
all_embeds = fetch_global_embeds(company["id"], theme_template.theme)
variables["content_for_layout"] = [ all_embeds["body"], variables["content_for_layout"] ].compact.join("\n")
variables["content_for_header"] = [ all_embeds["head"], variables["content_for_header"] ].compact.join("\n")
```

Head embeds are **prepended** to `content_for_header` — your script is the first executable thing in
the document, ahead of Fluid's own canonical tags, OG meta, CSRF token, and stylesheets. **This is
why `async` is mandatory.** A synchronous Wisp script would block first paint on every storefront
page of a live store. Degrade the recording, never the page.

Only active embeds render (`GlobalEmbed.available_embeds` scopes `.active`), and only on templates
whose type is in `Themes::Template::CAN_HAVE_GLOBAL_EMBEDS` — which is every storefront template
type, **cart page included**:

```
product · medium · enrollment_pack · shop_page · library · page · category_page ·
collection_page · cart_page · home_page · join_page · collection · post ·
category · post_page · mysite · error_page
```

That settles Wisp's open question about whether the embed fires on cart. It does.

## Caching — why verification needs a cache-buster

Two layers sit between your `POST` and the HTML you fetch:

1. **Rails cache.** `fetch_cached_global_embed_map` keys on
   `global_embeds/storefront/<company_id>/<collection.cache_key_with_version>`, TTL 1 hour. The
   version component changes whenever the collection changes, so a create/update/delete effectively
   misses the old entry immediately. (`GlobalEmbed::CacheInvalidator` deletes the *unversioned* key
   and is therefore vestigial — don't rely on it, and don't be surprised it appears to do nothing.)
2. **CDN cache on storefront HTML, ~30+ minutes.** This is the one that will fool you. A `crawl` or
   a plain `web_fetch` of the bare URL can keep returning the pre-embed page long after the embed is
   live at origin.

**Always verify with a unique query param** (`?wispcheck=<epoch>`) and re-check with a *different*
value before concluding the embed didn't land.

## `target: "checkout"` is dead

The enum accepts it and the record saves happily. Nothing renders it: `apply_global_embeds` only
merges the storefront map, and a checkout-targeted embed's head injection does not reach checkout's
server-rendered HTML at all (Wisp's ADR-5 probed this live against `checkout.fluid.app`). Checkout
coverage is a separate, unsolved integration problem.

**Never set `target: "checkout"`.** It produces a row that looks installed and records nothing.

## Idempotency recipe

```
GET /api/global_embeds?per_page=100          # paginate; default is 10
  → match name ~ /wisp/i  OR  content contains "/pixel/v1"
     ├─ active, key matches   → done, change nothing
     ├─ active, key differs   → surface both keys, ask which is authoritative
     ├─ draft                 → PUT {"global_embed":{"status":"active"}} after confirmation
     └─ none                  → POST as draft → confirm → PUT to active
```

Never create a second Wisp embed. Two active embeds means two `<script>` tags, two recorders, and
duplicate ingest against the same session — the loader does not guard against being loaded twice.
