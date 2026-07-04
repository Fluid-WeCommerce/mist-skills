---
name: Open a Country
description: Guided country-creation flow — operating mode, agreements, payment methods, enrollment fields, and an animated reveal of everything Fluid configures automatically.
---

<!--
  Publish location: this file ships in-repo for review. To use it,
  install it as a Local skill (~/Fluid/skills/open-a-country.md) or
  publish it to the Fluid-WeCommerce/mist-skills community repo —
  mist-desktop mirrors that repo into its Community skills list.
-->

# Goal

Help {{company.name}} open a new country the slick way: an interactive steps panel for every decision, live data from the Fluid API, Fluid's curated recommendations for the market, and an animated reveal of everything Fluid sets up automatically. The user should feel taken care of, not interrogated.

Trigger examples: "Open Germany", "let's launch in Japan", "expand to France".

# Step 0 — Gather data BEFORE asking anything

Run these in parallel:

1. `country_recommendations` with the country's ISO code (e.g. `DE`). Returns curated payment methods, VAT profile, primary language, `widelySpokenLanguages` (other ISO codes commonly used in-market), address-format notes, and enrollment fields. `curated: false` means an uncurated market — the defaults are conservative; say so when presenting them.
2. `fluid_api` → `GET /api/countries` — find the country's record (id, iso, currency_code, tax_rates) from the global catalog.
3. `fluid_api` → `GET /api/settings/company_countries` — check whether the country is ALREADY open for this company. If it is, tell the user and offer to review its settings instead of re-opening it.
4. `fluid_api` → `GET /api/agreements` — the company's agreements. These populate the agreements step: any agreement is a candidate; note in the option description when one already applies to other countries.
5. `fluid_api` → `GET /api/settings/languages` — the company's installed languages. Each entry has `iso` and `active_in_company`. You'll diff this against the country's languages in step 3; **do NOT create a steps step for language selection.**

# Step 1 — The steps (one call, up to seven steps — some are conditional)

Compute `missingLanguages` FIRST: the country's `languageCode` plus every code in `country_recommendations.widelySpokenLanguages` MINUS every ISO in `/api/settings/languages` where `active_in_company === true`. If it's empty, DROP the `languages` step from the call — never ask about a language the company already has enabled.

Also compute `fx_rate` for USD → the country's `currencyCode` using a reliable public rate (e.g. `web_fetch` on an FX endpoint or `country_recommendations` if a rate is provided). Round to 3 significant figures for display.

Then call `steps` with title like `Open Germany 🇩🇪` and these steps in order, then END YOUR TURN and wait for the answers message:

1. `mode` — single_select "How will you operate in <country>?" — you MUST offer these three options with these EXACT labels and definitions (do not paraphrase, do not add options like "Decide later"):
   - id `nfr`, label `NFR — Not For Resale`, description "Ship cross-border for personal use. No local entity required — the customer imports the product."
   - id `otg`, label `OTG — On The Ground`, description "You have (or are setting up) an entity in-country. Local fulfillment, local pricing, local compliance."
   - id `usd`, label `USD`, description "Sell and settle in USD — mainly digital products. No local currency or entity needed."
2. `entity_name` — text_input "What's your legal entity name in <country>?", `show_if: { step_id: "mode", equals: "otg" }`, `skippable: true`, skip label "Skip for now". Only OTG needs an entity (that's the whole point of On The Ground).
3. `languages` — multi_select (mode `opt_in`, all pre-checked) "Add languages spoken in <country>?" — ONLY include this step when `missingLanguages` is non-empty. Each option: id = ISO code (e.g. `fr`), label = display name (e.g. "French"), description = short "primary language of France" / "widely spoken in France" note. Skip the whole step when nothing is missing.
4. `agreements` — multi_select (mode `opt_out`, everything pre-checked) "Fluid's agreements for <country>" listing the company's agreements from the API (option id = agreement id as a string). If the company has none yet, offer Fluid's standard baseline instead: `terms_of_service`, `privacy_policy`, `rep_agreement`, `refund_policy`.
5. `payment_methods` — multi_select (mode `opt_out`) "Recommended payment methods for <country>" from `country_recommendations`. Set `pre_checked: true` only for entries with `recommended: true`; include the non-recommended ones unchecked so the user can opt in.
6. `enrollment_fields` — multi_select (mode `opt_out`) "Enrollment fields for <country>" from `country_recommendations.enrollmentFields`, same pre_checked treatment — the user adds/removes freely.
7. `product_pricing` — single_select "How should existing products be priced in <country>?" — you MUST offer these two options with these EXACT labels (recommend the first; both are reasonable):
   - id `convert`, label `Convert Product Pricing by <fx_rate> from USD` (interpolate the fx_rate you computed — e.g. `Convert Product Pricing by 0.92 from USD`), description "Fluid multiplies every existing USD-priced product by <fx_rate> to create the local <currency> price and activates them in this country. You can override individual prices later."
   - id `leave_inactive`, label `Leave Products Inactive in Country for now`, description "Nothing gets a local price; every existing product stays inactive in <country> until you set prices yourself later."

**Do NOT ask about VAT.** VAT is not a decision — it's the country's fixed consumption-tax rate; use `country_recommendations.vat` (name + standardRatePct) as-is and show it in the reveal so the user knows it was set.

If the user answers any step by typing in chat instead of clicking, record it with `steps_answer` right away so the panel stays in sync.

# Step 2 — Confirm before touching anything

Summarize the plan in 3-5 lines (mode, entity, languages being added if any, kept agreements, payment methods, enrollment fields, product-pricing choice + the automatic items below). Then ask ONE yes/no question: whether to create the country now.

- The real write is `fluid_api` → `POST /api/settings/company_countries` with `{ company_country: { country_id: <id from /api/countries>, currency: <currency_code>, ... } }`. Only send it after an explicit yes.
- If they picked `convert` in product_pricing: the follow-up write is the bulk product-pricing update — do this AFTER the country POST succeeds. If they picked `leave_inactive`, skip the pricing write entirely.
- If the user declines, is just exploring, or the write fails: run everything below in **plan mode** — show what WOULD be configured, write nothing.

# Step 3 — The animated reveal

Call `steps` again with a single `reveal` step titled "Setting up <country>" (or "What Fluid will set up" in plan mode). Items — pull the specifics from `country_recommendations` and the `/api/countries` record:

- `currency` — "Currency: <code>" (detail: symbol / formatting)
- `tax` — "Tax engine" (detail: tax_rates from the catalog record)
- `vat` — "VAT: <name> <rate>%" (skip when vat is null) — informational only, no user input
- `languages` — "Add language(s): <chosen joined>" — ONLY include when the user KEPT at least one option in step 1's `languages` step (or when the step was skipped because nothing was missing, and every relevant language is already installed — in that case drop this item too).
- `address` — "Address formatting" (detail: first addressFormat note)
- `agreements` — "Agreements linked" (detail: count kept)
- `payments` — "Payment methods" (detail: kept list)
- `pricing` — depends on the `product_pricing` answer:
  - `convert` → "Product pricing: converted from USD by <fx_rate> ×" (detail: N products activated)
  - `leave_inactive` → "Products: kept inactive in <country>" (detail: user will price them later)

Mode selection:

- **Configured for real** (user confirmed + POST succeeded): `mode: "live"` — fire the reveal steps FIRST, then perform each remaining configuration action and call `steps_mark_item` after each one succeeds so the checkmarks track genuine progress. Anything with no real API behind it gets marked immediately after its sibling completes.
- **Plan mode**: `mode: "plan"` with `item_duration_ms` around 800 — the panel animates on its own. Close by telling the user nothing was written and what it would take to go live.

# Step 4 — Translate themes if the user added a language

AFTER the reveal completes, IF the user kept at least one option in the `languages` step (i.e. added a new language to the company), ask ONE follow-up in plain chat:

> "You added `<language names>`. Want me to run the Translate Theme skill next so your storefronts are ready in <language(s)>?"

Wait for a yes/no. On yes, run the `translate-theme` community skill (`themes/translate-theme` in the mist-skills manifest) with the added language codes as context. On no or skip, close out politely — the languages are enabled and the user can translate later.

If NO language was added, skip this step entirely.

# Rules

- READ endpoints are always safe; the ONLY write in this flow is `POST /api/settings/company_countries`, and only after explicit confirmation.
- Never invent VAT rates or payment methods — use `country_recommendations` and label uncurated markets honestly.
- Keep chat text short; the panel does the talking.
