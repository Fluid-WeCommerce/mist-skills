---
name: Open a Country
description: Guided company-launch flow powered by Fluid's Country Atlas. Detects "open <country>" intent, asks the operating mode, then branches into mode-specific setup (OTG operations status + entity + business id + warehouse; NFR warehouse; USD digital), plus payment methods, missing languages, agreements, and enrollment fields — then runs a workflow that does the writes with QA and chains the mode finalizer.
---

<!--
  Publish location: this file ships in-repo for review. To use it,
  install it as a Local skill (~/Fluid/skills/open-a-country.md) or
  publish it to the Fluid-WeCommerce/mist-skills community repo —
  mist-desktop mirrors that repo into its Community skills list.
-->

# Goal

Help {{company.name}} launch a new country the slick way: an interactive `steps` panel that ADAPTS its questions to the operating mode, live data from the Fluid API, and Fluid's **Country Atlas** — the official per-market pre-setup profile. On confirmation, hand off to the `open-country` workflow (which does the writes with per-step QA and bounded rework) and then chain the mode's finalizer. The user should feel taken care of, not interrogated — never ask a question the atlas or API already answers.

**Trigger** whenever the user expresses intent to sell in / launch / expand into a country: "Open France", "Expand to China", "let's launch in Japan", "start selling in Germany", "add Canada". Resolve the country name to its ISO 3166-1 alpha-2 code and begin Step 0.

# Step 0 — Gather data BEFORE asking anything

Run these in parallel:

1. `country_atlas` with the country's ISO code (e.g. `DE`). The backbone of the flow. Returns per-mode (`nfr` / `otg` / `usd`) market overviews + launch checklists, `marketNotes`, `agreements` (titles + metadata; full legal bodies come later via `agreement_local_id`), `taxSettings`, `legalSettings`, `addressFields`, `paymentMethods` (ranked; `integration_type` matches `integration_class` in `/api/payment_integrations`), `enrollmentFormFields`, `majorLanguages`, `defaultCurrency`, `requires3ds`. If `covered: false`, tell the user Fluid has no atlas for this market yet, offer conservative generic defaults, and skip the atlas-derived enrichment below.
2. `fluid_api` → `GET /api/countries` — the country's record (id, iso, currency_code). The atlas `defaultCurrency` should match; if not, trust the atlas and note it.
3. `fluid_api` → `GET /api/settings/company_countries` — is the country ALREADY open? If so, offer to review its settings instead of re-opening.
4. `fluid_api` → `GET /api/agreements` — existing company agreements (to avoid duplicating atlas agreements by title, case-insensitively).
5. `fluid_api` → `GET /api/settings/languages` — installed languages (`iso`, `active_in_company`), to diff against the atlas `majorLanguages`.
6. `fluid_api` → `GET /api/payment_integrations` — which integrations are already configured, to annotate the payment step.
7. `fluid_api` → `GET /api/settings/warehouses` — the company's existing warehouses (`id`, `name`, `country`). These become the options in the warehouse step for OTG/NFR modes.

Give the user a 2-3 sentence market brief distilled from `marketNotes` before opening the panel — the "Fluid knows this market" moment. Keep it tight.

# Step 1 — The adaptive steps (one call; several steps are conditional)

Compute FIRST:

- `themeLanguages` = `country_atlas.majorLanguages` verbatim (e.g. `['es']` for Mexico). The storefront must be available in these to sell in the market; the workflow translates themes into ALL of them regardless of whether they're already enabled company languages. This is separate from enabling a language.
- `missingLanguages` = every ISO in `themeLanguages` MINUS every `/api/settings/languages` ISO with `active_in_company === true`. Drives the `languages` step (which ENABLES a language company-wide). If empty, DROP the `languages` step — but translation still happens for `themeLanguages`, so never conclude "nothing to do about language".
- `fx_rate` for USD → `defaultCurrency` via a reliable public rate (`web_fetch` an FX endpoint). Round to 3 sig figs for display.

**Conditional visibility works by chaining `show_if` on single_select answers.** A step's `show_if` can reference exactly ONE earlier single_select step (`equals` or `any_of`). There is no compound AND — but gating transitively works: a step hidden because its gate is unanswered can never be answered, so anything depending on ITS answer also stays hidden. Order the steps so each `show_if` points at the nearest gate.

Call `steps` with title like `Open Germany 🇩🇪` and these steps IN THIS ORDER, then END YOUR TURN and wait for the answers message:

1. `mode` — single_select, `skippable: false` (the flow can't proceed without a mode) "How will you operate in <country>?" — EXACT ids/labels (do not paraphrase, do not add "Decide later"):
   - id `nfr`, label `NFR — Not For Resale`
   - id `otg`, label `OTG — On The Ground`
   - id `usd`, label `USD`
     Each option's description = that mode's atlas `overview` distilled to ≤2 sentences with the concrete setup time/cost when given (e.g. "MoR charges local currency, settles USD — you keep your US entity. ~3–6 weeks, ~$1.5–6K."). Real trade-offs, not generic definitions.
2. `otg_operations` — single_select, `show_if: { step_id: "mode", equals: "otg" }`, "Do you already operate in <country>?":
   - id `have_it`, label `We're already set up`, description "Local entity, tax registration, and fulfillment already in place."
   - id `need_setup`, label `We still need to set that up`, description "Fluid will guide you through entity, tax registration, and invoicing in the OTG finalizer."
3. `entity_name` — text_input, `show_if: { step_id: "otg_operations", equals: "have_it" }`, `skippable: true`, skip label "Skip for now", "What's your legal entity name in <country>?".
4. `business_id` — text_input, `show_if: { step_id: "otg_operations", equals: "have_it" }`, `skippable: true`, skip label "Skip for now", "Business / tax registration number? (e.g. VAT ID, ABN, RFC)".
5. `otg_posture` — single_select, `show_if: { step_id: "mode", equals: "otg" }`, "Who will you sell to in <country>?": id `b2c` "Consumers (B2C)", id `b2b` "Businesses (B2B)", id `both` "Both". Shapes which consumer-disclosure duties the OTG finalizer emphasizes.
   The three modes are mutually exclusive — a company is exactly one of NFR / OTG / USD, never a combination. That's why the warehouse question is split into two mode-specific steps below (6 and 7): each references a single mode, and only one of them can ever be visible in a given run.
6. `warehouse_otg` — single_select, `show_if: { step_id: "mode", equals: "otg" }`, "Which warehouse handles local fulfillment in <country>?". OTG fulfills locally, so this is about an in-country warehouse. Options = one per existing warehouse from `/api/settings/warehouses` (id = the warehouse's numeric id as a string, label = `"<name> — <country iso>"`), PLUS a final option id `new`, label "Set up a new in-country warehouse", description "We'll flag warehouse creation as a follow-up."
7. `warehouse_nfr` — single_select, `show_if: { step_id: "mode", equals: "nfr" }`, "Which warehouse ships cross-border to <country>?". NFR ships from an origin warehouse the customer imports from — this picks that origin. Options = one per existing warehouse from `/api/settings/warehouses` (same id/label shape), PLUS a final option id `new`, label "Set up a new warehouse", description "We'll flag warehouse creation as a follow-up." (USD is digital — neither warehouse step shows for it.)
8. `languages` — multi_select (mode `opt_in`, all pre-checked) "Add languages spoken in <country>?" — INCLUDE ONLY when `missingLanguages` is non-empty. Option id = ISO, label = display name, description = short in-market note.
9. `agreements` — multi_select (mode `opt_out`) "Fluid's recommended agreements for <country>" from `country_atlas.agreements`. Option id = `localId`, label = `title`, description = one line (what it is + flags: required/shown at checkout, languages). Pre-check all EXCEPT titles that case-insensitively match an existing company agreement — leave those unchecked with "you already have one".
10. `payment_methods` — multi_select (mode `opt_out`) "Recommended payment methods for <country>" from `country_atlas.paymentMethods`, in priority order. Option id = `integration_type`, label = `name`. `pre_checked: true` only for `enabled: true`; include the rest unchecked. Note integration status from `/api/payment_integrations`: "already configured" vs "needs onboarding in Payments settings".
11. `enrollment_fields` — multi_select (mode `opt_out`) "Enrollment fields for <country>" from `country_atlas.enrollmentFormFields`, in `order`. Option id = field `id`, label = field `label`, description = field `description` (one line). Pre-check `required: true`.
12. `product_pricing` — single_select "How should existing products be priced in <country>?" — EXACT labels (recommend the first):
    - id `convert`, label `Convert Product Pricing by <fx_rate> from USD` (interpolate fx_rate), description "Fluid multiplies every existing USD-priced product by <fx_rate> to create the local <currency> price and activates them. Override individual prices later."
    - id `leave_inactive`, label `Leave Products Inactive in Country for now`, description "Nothing gets a local price; products stay inactive in <country> until you set prices yourself."

**Do NOT ask about tax, currency, 3DS, address formats, or legal settings.** The atlas fixes them (`taxSettings`, `defaultCurrency`, `requires3ds`, `addressFields`, `legalSettings`); they're configured automatically — just mention them in the summary.

If the user answers any step by typing instead of clicking, record it with `steps_answer` right away so the panel stays in sync.

# Step 2 — Confirm, then hand off to the `open-country` workflow

Summarize the plan in 4-7 lines, tailored to the mode: mode; for OTG, whether they already operate (or that Fluid will help set it up), entity name + business id if given, B2B/B2C posture; warehouse choice (existing name or "new — follow-up") for OTG/NFR; **storefront language** — always state that the site will be translated into the market's language(s) from `themeLanguages` (e.g. "Your storefront will be translated to Spanish"), and separately note any language being newly enabled company-wide; agreements to create; payment methods; enrollment fields; pricing choice — plus a one-line "configured automatically" note (currency, <taxSettings.taxName> inclusive/exclusive, 3DS if `requires3ds`, address format, legal settings) and a trailer that after setup they'll get the <mode> launch checklist as their to-do list. Then ask ONE yes/no: open the country now?

**On yes** — do NOT call `fluid_api` yourself. Hand off:

```
run_workflow({
  workflow_slug: "open-country",
  context: {
    country_id: <country id from /api/countries>,
    country_iso: <ISO alpha-2>,
    currency_code: <defaultCurrency from country_atlas>,
    mode: <"nfr" | "otg" | "usd">,
    otg_operations: <"have_it" | "need_setup" | null when mode != "otg">,
    entity_legally_registered: <true when mode == "otg" && otg_operations == "have_it", else false>,
    entity_name: <entity_name answer, or null when skipped / not OTG>,
    business_id: <business_id answer, or null when skipped / not OTG>,
    otg_posture: <"b2c" | "b2b" | "both"; "both" or omit when not OTG>,
    warehouse_id: <numeric id of the chosen existing warehouse from whichever warehouse step was shown (warehouse_otg for OTG, warehouse_nfr for NFR); null when the user picked "new" or neither step showed (USD)>,
    warehouse_choice: <"existing" | "new" | null>,
    tax_name: <country_atlas.taxSettings.taxName>,
    tax_inclusive: <country_atlas.taxSettings.taxInclusive>,
    requires_3ds: <country_atlas.requires3ds>,
    agreements_to_create: <array of atlas localIds kept in the agreements step>,
    payment_integration_types: <array of integration_type values kept>,
    enrollment_fields: <array of { id, label, component, required } kept>,
    languages_to_add: <array of ISO codes kept in the languages step to ENABLE company-wide; [] when dropped or all opt-outs>,
    theme_languages: <the themeLanguages array (country_atlas.majorLanguages) — the storefront languages the workflow translates themes into, regardless of what's already enabled>,
    pricing_choice: <"convert" | "leave_inactive">,
    fx_rate: <numeric fx_rate; still send it when leave_inactive, for the record>,
    launch_checklist: <the chosen mode's launchChecklist array ({ id, label, description }) from country_atlas — verbatim>
  }
})
```

Then END YOUR TURN with a one-line confirmation like "Kicking off the setup — watch the card below." The workflow-run card takes over: it POSTs the company_country (currency, tax profile, 3DS, warehouse, entity-registered flag, business id where given), creates the kept agreements from the atlas legal templates (all languages), enables added languages, converts pricing (or skips), translates the storefront themes into the market's languages (`theme_languages` — so a Spanish market gets a Spanish storefront even if Spanish was already enabled), and runs a final QA sweep that ends with the mode's launch checklist. Every step is QA-reviewed and reworked on failure.

Do NOT poll `workflow_status` in a loop. The user can watch the card live and ask for progress later.

# Step 3 — Chain the mode finalizer once the base setup lands

`open-country` covers what every mode shares. The mode-specific obligations live in a **finalizer workflow**:

- `otg` → `finalize-otg-country` — VAT/GST registration guidance (esp. when `otg_operations == "need_setup"`), local invoicing, local payment-gateway wiring, B2B/B2C interpretation (reads `otg_posture`), full compliance review.
- `nfr` → `finalize-nfr-country` — international shipping profile (reads `warehouse_id`), import-duty disclosure check, country-of-origin labeling, light compliance review.
- `usd` → `finalize-usd-country` — digital-services-tax registration check, USD-only pricing guardrail, cross-border digital ToS, digital-focused compliance review.

When the base `open-country` run has finished (card shows all steps passed) — or right away if the user says "do everything" — kick off the matching finalizer with the SAME context object, then end your turn:

```
run_workflow({
  workflow_slug: "finalize-<mode>-country",   // finalize-otg-country | finalize-nfr-country | finalize-usd-country
  context: { ...the same context you passed to open-country }
})
```

The finalizer reads the country's compliance rulebook via the `country_settings` tool (the atlas compliance projection). If the user only wanted core setup, tell them the finalizer is available whenever they're ready — don't force it.

**On no / decline / "just exploring"** — do NOT run the workflow. Tell the user nothing was written and give a short summary (3-6 bullets) of what the setup WOULD have configured, including the automatic items and the automated tail (agreement creation, language enablement, pricing, theme translation, QA + launch checklist, mode finalizer). Offer to run it whenever they're ready.

# Rules

- READ endpoints during data-gathering are always safe. The ONLY writes are performed by the `open-country` workflow (and the finalizer), and only after the user's explicit yes.
- Never invent tax rates, agreements, payment methods, warehouses, or legal requirements — everything market-specific comes from `country_atlas` / the API. When `covered: false`, be conservative and label the gap honestly.
- Never ask a question the mode makes irrelevant: no warehouse for USD, no entity/business-id/posture unless OTG, no language step when nothing is missing.
- The atlas mode overviews and launch checklists are real compliance intelligence — use their specifics (weeks, costs, regulators, statutes) instead of paraphrasing them into mush.
- Keep chat text short; the panel and the workflow-run card do the talking.
