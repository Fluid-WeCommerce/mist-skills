# SKIMS Onboard & Launch Validation — 2026-07-25

This is a test-run record, not reusable skill context. SKIMS-specific facts and
URLs belong here and must not be copied into the generic onboarding or theme
skills.

## Run

- Company: SKIMS (Demo), Fluid company ID `980243243`
- Source: <https://skims.com/>
- Mist workflow: `onboard-launch-company`
- Workflow run: `wfr-7aff76d0-b546-49ee-8785-fc2f16416a59`
- Started on workflow revision `2026-07-25.16`
- Scope: complete business/brand data, full product import, existing theme
  `56432`, and home/shop/PDP visual QA
- Production merge: none

## Current verdict

The workflow is not complete. Brand/business context and the source catalog
have passed independent QA. Product import is in progress. Theme discovery
failed on a model image-policy rejection and is awaiting manual workflow
recovery after the independent product-import branch finishes.

## Verified evidence

### Brand and business data — passed after rework

- Source-matched colors include Onyx `#2D2A26` and Sienna `#986B58`.
- The source T-Star families and weights were recorded, but proprietary font
  bytes were not copied without a transferable license. Inter was installed as
  the legal substitute with exact DAM URLs and metadata.
- `brand.md` contains the full canonical section set, source-specific mission,
  audience, voice, naming, visual rules, do/don't guidance, examples, and
  citations.
- Legal entity `126` (Skims Body, Inc.) was linked to live US company-country
  `56620` and re-read successfully.
- BBB identity/rating and same-domain policies were independently re-read.
- Trustpilot remains an explicit human follow-up: the source blocks automated
  verification and the onboarding API rejected attempts to clear the prior
  `N/A` placeholder while required consent fields were absent.
- Earlier reruns created four byte-identical wordmark uploads. References were
  consolidated to one URL, but Mist exposed no discoverable DAM list/delete
  contract for removing the three orphaned copies; manual cleanup remains.

### Source catalog — passed after rework

- Live products: `3,160`
- Evidence-backed exclusions: `15`
- Unresolved: `0`
- Accounted identities: `3,175 / 3,175`
- Gallery image entries: `18,844`
- Distinct source image URLs: `18,194`
- Exact variants: `34,527`
- Collections discovered/completed: `315 / 315`
- Missing title, price, image, variant, or identity fields: `0`
- Storefront product cursor terminated at `hasNextPage=false`.
- Current-vs-manifest identity reconciliation: `0` new, `0` missing, `0` ID
  mismatches.
- Deterministic 12-product fidelity sample: `0` gallery mismatches and `0`
  variant mismatches.
- Repaired manifest:
  `manifest/run-wfr-7aff76d0-b546-49ee-8785-fc2f16416a59/source-catalog.json`
- Current SHA-256:
  `f779ed021326ca1010079af81df4404e869b69d8566221c848a7a17fa601c934`

The first catalog review caught four live collections that the source HTML
crawler had mislabeled as dead after 404 pages: Gift Card, The North Face x
SKIMS Apparel, NikeSKIMS Satin Shine, and Stretch Satin. Rework checked all 18
source-404 collections through Storefront GraphQL, recovered four live
collections, confirmed 14 stale collections, discarded error-page product
links, and increased collection-derived product URLs from `1,208` to `1,285`
without changing the complete `3,160`-product denominator.

### Fresh-build skill assets — passed

After a full Mist Desktop restart and skill refresh, `run_skill` materialized:

```text
.mist-desktop/skill-assets/themes__theme-clone/57f8c1026114ec50/scripts/theme_audit.py
```

The materialized file matched the public source SHA-256
`8d410ecb631273c362c33aa971ecc6b6d40b9855c32c07b994ac832847dbccd7`,
and `python3 <path> --help` exited successfully.

## Failures and decisions

### GPT-5.6 Sol failed SKIMS visual discovery

The discovery worker captured the six required desktop/mobile home, shop, and
PDP baselines, then the model gateway rejected image processing with:

```text
Image processing blocked due to content policy violation.
```

Mist classified this as unknown/non-transient even though the diagnostic marked
the step recovery-eligible. Workflow revision `2026-07-25.17` routes only the
multimodal discovery worker to `google/gemini-3.6-flash`, keeps
`anthropic/claude-opus-5` as the independent visual reviewer, and leaves
GPT-5.6 Sol on the coding/build stages. This is an evidence-based routing
decision, not a blanket model preference.

### v202604 ProductWrite lifecycle docs were contradicted

The reusable instructions said to write `status:"published"`, but the live
`storefront-v2026-04.yaml` ProductWrite schema accepts only the raw enum
`active | draft | archived`. Revision `2026-07-25.18` corrects the product
skill, workflow import step, lifecycle QA, launch review, examples, and catalog
validator to use `status:"active"` plus `public:true`.

### Product import lacks a scoped bulk capability

Mist's `fluid_api` is request-at-a-time and the CLI has no product-admin import
command. To make a complete import tractable, the worker inspected the active
Fluid CLI profile and generated a resumable local API/DAM client. That works
for this authorized test but is the wrong product boundary: an agent should
receive a company-scoped batch import capability without discovering
`~/.fluid/config.json`.

### Omitted product subscription data is not neutral

Live v202604 creates that omitted
`product_subscription_plans_attributes` inherited SKIMS' company-default
Monthly plan. Product `78353`, for example, returned
`has_subscription_plans:true` with an active/default join despite the source
product having no subscription offer. The delegated create implementation
sets `skip_default_subscription_plan` only when the nested array is non-empty;
an omitted key or empty array therefore means "attach the default."

The verified no-subscription create signal is the non-empty sentinel
`product_subscription_plans_attributes:[{"_destroy":true}]`: it causes the
manager to skip the default while the nested association writer discards the
sentinel. Workflow revision `2026-07-25.19` now requires that payload for every
source-non-subscription product, a complete destination re-read of
`has_subscription_plans`, and repair by returned join ID rather than disabling
the company-wide plan.

The update side has a separate implementation mismatch: v202604 validates
`_destroy`, but the delegated product update contract omits that key for
`product_subscription_plans_attributes`, so the attempted delete was silently
dropped. The live-safe repair is `active:false, default:false` by returned join
ID followed by a re-read proving `has_subscription_plans:false`; an inactive
audit row remains. Revision `2026-07-25.21` documents that truth while the
backend contract fix is developed separately.

The same import found a smaller schema contradiction: SKIMS Gift Box has a
genuinely empty source description. Both `null` and `""` returned
`422 product.description must be a string` because the outer validator
normalizes the empty string to null before delegation. Omitting the key
entirely succeeded: Fluid product `81517` re-read as active, USD `$8`, one real
DAM image, one variant, and `has_subscription_plans:false` with no plan joins.
Revision `2026-07-25.22` records that live behavior instead of trusting the
nullable-looking generated contract.

### Restart and UI recovery

- A deliberate app restart preserved the run, completed steps, diagnostics, and
  run ID.
- The run did not auto-resume. Recovery required a chat call to
  `run_workflow(resume_run_id=...)`.
- Partial read-heavy work restarted from the beginning.
- The visible run header continued to say `Starting chat` while independent QA
  was actively running.

### Performance

During parallel QA/rework the development build used roughly `3.2 GB` RSS:
about `1.35 GB` in the workflow Node process, about `1 GB` in the primary
renderer, plus Electron/GPU/helper processes. CPU was approximately `20–25%`.
This does not meet the lower-end-computer bar.

Repeated discovery attempts also accumulated duplicate full-page baseline PNGs
instead of reusing or pruning content-addressed captures.

## Still required before calling this proof complete

- Finish all `18,194` distinct DAM image mappings and all `3,160` product
  creates/updates through the v202604 API.
- Prove destination pagination to a null cursor, 100% manifest coverage, exact
  images/options/variants/prices, no placeholders, and an idempotent second
  pass.
- Recover theme discovery, then pass all six theme build/refine stages.
- Render and compare actual Fluid home, shop, and PDP routes at desktop and
  mobile viewports.
- Pass route, SEO, content, font, lifecycle, price, cart, responsive, and final
  launch-readiness gates.
