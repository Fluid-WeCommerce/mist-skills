# Product Quiz — backend contract

Freeze these shapes before the theme work starts; the Liquid section is built against them
in parallel. Capture **real** responses into `docs/theme-quiz-section-spec.md` in the Mist
project — that file, not this one, is the handoff artifact.

## `GET /api/quiz/config?shop=<shop>`

```jsonc
{
  "questions": [
    { "id": "…", "prompt": "…", "subtitle": null, "kind": "single|multi",
      "optional": false,
      "options": [{ "id": "…", "label": "…", "hint": null }] }
  ],
  "offer": { "promoCode": "…", "discountPct": 15, "label": "…" }
}
```

Question count is **not fixed** — it is AI-generated per catalog snapshot (5–8). The client
must read the length rather than assume it.

## `POST /api/quiz/score?shop=<shop>&country=US`

Body: `{ "answers": { "<questionId>": "<optionId>" | ["<optionId>"] } }`

```jsonc
{
  "shareToken": "…",
  "result": {
    "headline": "…", "blurb": "…",
    "primary": { /* one item */ },
    "items": [{ "productId": 0, "variantId": 0, "title": "…", "url": "…",
                "imageUrl": "…", "price": 0, "subscriptionPlanId": null,
                "reason": "…", "role": "primary|addition|accessory|gift", "score": 0 }],
    "bundle": { "items": [], "subtotal": 0, "discountPct": 15, "savings": 0,
                "total": 0, "promoCode": "…", "currency": "USD" }
  }
}
```

- Unknown answer ids are **ignored, never fatal**.
- `bundle` is `null` when fewer than 2 items.
- Persist the **final result object**, not the prompt, so `GET /api/quiz/result/:token`
  replays identically forever.

## Remaining endpoints

| Endpoint | Notes |
| --- | --- |
| `GET /api/quiz/result/:token` | Returns the stored `result` verbatim. No re-scoring, no model call. |
| `POST /api/quiz/lead` | Optional email capture. **Never a gate** — the result renders without it. |
| `POST /api/quiz/event` | Fire-and-forget analytics. Must never block or fail the UI. |

## Public catalog response shape

```
GET https://<shop>/api/v202604/products?country=US&page[limit]=100
```

No auth — the company is resolved from the subdomain. Returns only live products with an
active variant in that country.

The shape differs from the admin catalog endpoint in ways that silently break a naive
mapper:

| Field | Notes |
| --- | --- |
| `default_variant.{id,sku}` | `default_variant.id` is **the variant id you add to cart**. |
| `pricing.{price,currency_code,compare_at}` | Prices are here, not on the product root. |
| `images.{thumb,medium,large}.url` | There is **no** top-level `image_url`. |
| — | There is **no** `variants[]` array in the list view. |

Do not reach for `/api/v202604/company/products` with the Mist's
`FLUID_COMPANY_PRIVATE_TOKEN` — it returns 403 (authenticated but not authorized).

## AI provider configuration

Plain `fetch` against an OpenAI-compatible chat-completions endpoint with a JSON-schema
`response_format`. No new dependency. Resolve config from env in this order:

1. `AI_GATEWAY_API_KEY` (+ `AI_GATEWAY_BASE_URL`, default `https://ai-gateway.vercel.sh/v1`)
2. `OPENAI_API_KEY` (+ `OPENAI_BASE_URL`)
3. `ANTHROPIC_API_KEY`

Model from `QUIZ_AI_MODEL`. Set with `set_mist_env_var`; a redeploy (`fluid mist push`) is
required for production to pick them up.

### Failure policy

No key, non-200, timeout, or malformed JSON ⇒ **log once and return `null`** so the caller
falls back to the deterministic path. Hard `AbortController` timeouts: ≤8s on config, ≤6s
on score. The quiz must never 500 or hang because of a model.

### Validation the model cannot bypass

- Every returned `variantId` is checked against the deterministic shortlist. Anything else
  is dropped. Fewer than 2 valid items surviving ⇒ use the deterministic result unchanged.
- Prices, URLs, images and titles come from the catalog record — never from the model.
- Bundle math (subtotal / discount / savings / total) is server-side arithmetic — never
  model output.

## Cache keys

Every derived artifact must be keyed by the catalog content hash **and** a `VERSION`
constant bumped whenever the derivation logic changes meaning:

| Artifact | Key | TTL |
| --- | --- | --- |
| Catalog snapshot | company + country | ~15 min |
| Classifications | company + catalog hash + `CLASSIFIER_VERSION` | follows snapshot |
| Generated questions | company + catalog hash + `PROMPT_VERSION` | ~24h |

Without the version component, stale output is served for the whole TTL after a logic
change. On a questions cache miss, serve the deterministic set immediately and warm the
cache in the background.
