---
name: Open a Country
description: Guided country-creation flow — operating mode, agreements, payment methods, enrollment fields, and a workflow that runs the writes (country, pricing, language translations) with QA + rework.
---

<!--
  Publish location: this file ships in-repo for review. To use it,
  install it as a Local skill (~/Fluid/skills/open-a-country.md) or
  publish it to the Fluid-WeCommerce/mist-skills community repo —
  mist-desktop mirrors that repo into its Community skills list.
-->

# Goal

Help {{company.name}} open a new country the slick way: an interactive steps panel for every decision, live data from the Fluid API, Fluid's curated recommendations for the market, and — on confirmation — hand off to the `open-country` workflow, which does the writes (country creation, pricing conversion, language enablement, theme translation) with per-step QA and bounded rework. The user should feel taken care of, not interrogated.

Trigger examples: "Open Germany", "let's launch in Japan", "expand to France".

# Step 0 — Gather data BEFORE asking anything

Run these in parallel:

1. `country_recommendations` with the country's ISO code (e.g. `DE`). Returns curated payment methods, VAT profile, primary language, `widelySpokenLanguages` (other ISO codes commonly used in-market), address-format notes, and enrollment fields. `curated: false` means an uncurated market — the defaults are conservative; say so when presenting them.
2. `fluid_api` → `GET /api/countries` — find the country's record (id, iso, currency_code, tax_rates) from the global catalog.
3. `fluid_api` → `GET /api/settings/company_countries` — check whether the country is ALREADY open for this company. If it is, tell the user and offer to review its settings instead of re-opening it.
4. `fluid_api` → `GET /api/agreements` — the company's agreements. These populate the agreements step: any agreement is a candidate; note in the option description when one already applies to other countries.
5. `fluid_api` → `GET /api/settings/languages` — the company's installed languages. Each entry has `iso` and `active_in_company`. You'll diff this against the country's languages in step 3; **do NOT create a steps step for language selection.**

# Step 1 — The steps (one call, up to eight steps — some are conditional)

Compute `missingLanguages` FIRST: the country's `languageCode` plus every code in `country_recommendations.widelySpokenLanguages` MINUS every ISO in `/api/settings/languages` where `active_in_company === true`. If it's empty, DROP the `languages` step from the call — never ask about a language the company already has enabled.

Also compute `fx_rate` for USD → the country's `currencyCode` using a reliable public rate (e.g. `web_fetch` on an FX endpoint or `country_recommendations` if a rate is provided). Round to 3 significant figures for display.

Then call `steps` with title like `Open Germany 🇩🇪` and these steps in order, then END YOUR TURN and wait for the answers message:

1. `mode` — single_select "How will you operate in <country>?" — you MUST offer these three options with these EXACT labels and definitions (do not paraphrase, do not add options like "Decide later"):
   - id `nfr`, label `NFR — Not For Resale`, description "Ship cross-border for personal use. No local entity required — the customer imports the product."
   - id `otg`, label `OTG — On The Ground`, description "You have (or are setting up) an entity in-country. Local fulfillment, local pricing, local compliance."
   - id `usd`, label `USD`, description "Sell and settle in USD — mainly digital products. No local currency or entity needed."
2. `entity_name` — text_input "What's your legal entity name in <country>?", `show_if: { step_id: "mode", equals: "otg" }`, `skippable: true`, skip label "Skip for now". Only OTG needs an entity (that's the whole point of On The Ground).
3. `otg_posture` — single_select "In <country>, will you sell mainly B2B, B2C, or both?", `show_if: { step_id: "mode", equals: "otg" }`. Only OTG needs this — it shapes the finalizer's compliance review (B2C sellers pick up Impressum / Mentions Légales / 特定商取引法 disclosure duties that pure B2B relaxes). Three options with these EXACT ids and labels:
   - id `b2c`, label `B2C — end consumers`, description "Selling to end consumers. Consumer-protection disclosure pages are statutorily required for this posture."
   - id `b2b`, label `B2B — business builders / distributors`, description "Selling to business builders and distributors. Consumer-protection pages are recommended but not statutorily required."
   - id `both`, label `Both`, description "A mix — the compliance review applies the B2C bar to be safe."
4. `languages` — multi_select (mode `opt_in`, all pre-checked) "Add languages spoken in <country>?" — ONLY include this step when `missingLanguages` is non-empty. Each option: id = ISO code (e.g. `fr`), label = display name (e.g. "French"), description = short "primary language of France" / "widely spoken in France" note. Skip the whole step when nothing is missing.
5. `agreements` — multi_select (mode `opt_out`, everything pre-checked) "Fluid's agreements for <country>" listing the company's agreements from the API (option id = agreement id as a string). If the company has none yet, offer Fluid's standard baseline instead: `terms_of_service`, `privacy_policy`, `rep_agreement`, `refund_policy`.
6. `payment_methods` — multi_select (mode `opt_out`) "Recommended payment methods for <country>" from `country_recommendations`. Set `pre_checked: true` only for entries with `recommended: true`; include the non-recommended ones unchecked so the user can opt in.
7. `enrollment_fields` — multi_select (mode `opt_out`) "Enrollment fields for <country>" from `country_recommendations.enrollmentFields`, same pre_checked treatment — the user adds/removes freely.
8. `product_pricing` — single_select "How should existing products be priced in <country>?" — you MUST offer these two options with these EXACT labels (recommend the first; both are reasonable):
   - id `convert`, label `Convert Product Pricing by <fx_rate> from USD` (interpolate the fx_rate you computed — e.g. `Convert Product Pricing by 0.92 from USD`), description "Fluid multiplies every existing USD-priced product by <fx_rate> to create the local <currency> price and activates them in this country. You can override individual prices later."
   - id `leave_inactive`, label `Leave Products Inactive in Country for now`, description "Nothing gets a local price; every existing product stays inactive in <country> until you set prices yourself later."

**Do NOT ask about VAT.** VAT is not a decision — it's the country's fixed consumption-tax rate; use `country_recommendations.vat` (name + standardRatePct) as-is and mention it in the confirmation summary so the user knows it will be set automatically.

If the user answers any step by typing in chat instead of clicking, record it with `steps_answer` right away so the panel stays in sync.

# Step 2 — Confirm, then hand off to the `open-country` workflow

Summarize the plan in 3-5 lines (mode, entity, languages being added if any, kept agreements, payment methods, enrollment fields, product-pricing choice, plus a one-line note that currency, tax engine, VAT, and address formatting are configured automatically). Add ONE more line naming the mode-specific finalizer that will run after the base setup:

- `mode === "otg"` → "After the base setup, I'll run the OTG finalizer to draft VAT-registration guidance, configure local invoicing, surface local payment gateways, and run a full compliance review."
- `mode === "nfr"` → "After the base setup, I'll run the NFR finalizer to verify the international shipping profile, confirm import-duty disclosure, spot-check product country-of-origin labeling, and run a light compliance review."
- `mode === "usd"` → "After the base setup, I'll run the USD finalizer to check digital-services-tax registration for foreign sellers, guardrail USD-only pricing, verify cross-border digital ToS coverage, and run a compliance review."

Then ask ONE yes/no question: whether to open the country now.

**On yes** — do NOT call `fluid_api` yourself. Hand off to the workflows in order — the base `open-country` first, then the mode-specific finalizer after it completes. Kick off the base workflow immediately:

```
run_workflow({
  workflow_slug: "open-country",
  context: {
    country_id: <country id from /api/countries>,
    country_iso: <iso from /api/countries — useful downstream for country_settings lookups>,
    currency_code: <currency_code from /api/countries>,
    agreement_ids: <array of kept agreement ids from the agreements step>,
    payment_method_ids: <array of kept payment method ids from the payment_methods step>,
    enrollment_field_ids: <array of kept enrollment field ids from the enrollment_fields step>,
    entity_name: <entity_name answer or null when mode != "otg" or the step was skipped>,
    languages_to_add: <array of ISO codes the user kept in the languages step; [] when the step was dropped or all opt-outs>,
    pricing_choice: <"convert" or "leave_inactive" from the product_pricing step>,
    fx_rate: <the numeric fx_rate you computed; still send it when pricing_choice is "leave_inactive" for the record>,
    mode: <"otg" | "nfr" | "usd" — the mode answer, verbatim>,
    otg_posture: <"b2b" | "b2c" | "both" from the otg_posture step; null when mode != "otg">
  }
})
```

Once the base `open-country` run reaches `completed` (watch the run card; workflow_status also reports it), fire the mode-specific finalizer with the SAME `context` payload:

- `mode === "otg"` → `run_workflow({ workflow_slug: "finalize-otg-country", context: <same payload> })`
- `mode === "nfr"` → `run_workflow({ workflow_slug: "finalize-nfr-country", context: <same payload> })`
- `mode === "usd"` → `run_workflow({ workflow_slug: "finalize-usd-country", context: <same payload> })`

Never fire the finalizer when the base workflow's terminal status is `failed`, `cancelled`, or `interrupted` — surface the failure and stop.

Then END YOUR TURN with a one-line confirmation like "Kicking off the setup — watch the card below." The workflow-run card renders in this same chat and takes over: it POSTs the company_country, enables the added languages, converts pricing (or skips when the user chose leave_inactive), translates themes for each added language, and runs a final QA sweep. Each step gets QA-reviewed and reworked automatically on failure.

Do NOT poll `workflow_status` in a tight loop — one check when the base run's card shows `completed` (to decide whether to fire the finalizer) is enough. The user can watch both cards live and can ask for progress later.

**On no / decline / "just exploring"** — do NOT run the workflow. Tell the user nothing was written and give a short text summary (3-6 bullets) of what the setup WOULD have configured, including the automatic items (currency, tax, VAT, address formatting) and the automated tail (language enablement, product pricing, theme translation, final QA). Offer to run it whenever they're ready.

# Rules

- READ endpoints during data-gathering are always safe. The ONLY writes in this flow are performed by the `open-country` workflow, and only after the user's explicit yes.
- Never invent VAT rates or payment methods — use `country_recommendations` and label uncurated markets honestly.
- Keep chat text short; the panel and the workflow-run card do the talking.
