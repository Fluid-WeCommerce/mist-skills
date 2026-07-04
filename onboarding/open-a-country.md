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

# Step 1 — The steps (one call, five steps)

Call `steps` with title like `Open Germany 🇩🇪` and these steps, then END YOUR TURN and wait for the answers message:

1. `mode` — single_select "How will you operate in <country>?" — you MUST offer these three options with these EXACT labels and definitions (do not paraphrase, do not add options like "Decide later"):
   - id `nfr`, label `NFR — Not For Resale`, description "Ship cross-border for personal use. No local entity required — the customer imports the product."
   - id `otg`, label `OTG — On The Ground`, description "You have (or are setting up) an entity in-country. Local fulfillment, local pricing, local compliance."
   - id `usd`, label `USD`, description "Sell and settle in USD — mainly digital products. No local currency or entity needed."
2. `entity_name` — text_input "What's your legal entity name in <country>?", `show_if: { step_id: "mode", equals: "otg" }`, `skippable: true`, skip label "Skip for now". Only OTG needs an entity (that's the whole point of On The Ground).
3. `agreements` — multi_select (mode `opt_out`, everything pre-checked) "Fluid's agreements for <country>" listing the company's agreements from the API (option id = agreement id as a string). If the company has none yet, offer Fluid's standard baseline instead: `terms_of_service`, `privacy_policy`, `rep_agreement`, `refund_policy`.
4. `payment_methods` — multi_select (mode `opt_out`) "Recommended payment methods for <country>" from `country_recommendations`. Set `pre_checked: true` only for entries with `recommended: true`; include the non-recommended ones unchecked so the user can opt in.
5. `enrollment_fields` — multi_select (mode `opt_out`) "Enrollment fields for <country>" from `country_recommendations.enrollmentFields`, same pre_checked treatment — the user adds/removes freely.

**Do NOT ask about VAT and do NOT ask about default language.** Both are handled for the user automatically:

- **VAT**: use `country_recommendations.vat` (name + standardRatePct) as-is — you just tell them what's being set up during the reveal.
- **Language**: never ask "what language?" — the primary language is dictated by the market. Instead, compute `missingLanguages` = the country's `languageCode` plus every code in `widelySpokenLanguages` MINUS the codes already in `/api/settings/languages` where `active_in_company === true`. If `missingLanguages` is non-empty, note them in the reveal (see step 3) as "Language(s) to add: X, Y". If everything is already installed, skip the language reveal item.

If the user answers any step by typing in chat instead of clicking, record it with `steps_answer` right away so the panel stays in sync.

# Step 2 — Confirm before touching anything

Summarize the plan in 3-5 lines (mode, entity, kept agreements, payment methods, enrollment fields + the automatic items below). Then ask ONE yes/no question: whether to create the country now.

- The real write is `fluid_api` → `POST /api/settings/company_countries` with `{ company_country: { country_id: <id from /api/countries>, currency: <currency_code>, ... } }`. Only send it after an explicit yes.
- If the user declines, is just exploring, or the write fails: run everything below in **plan mode** — show what WOULD be configured, write nothing.

# Step 3 — The animated reveal

Call `steps` again with a single `reveal` step titled "Setting up <country>" (or "What Fluid will set up" in plan mode). Items — pull the specifics from `country_recommendations` and the `/api/countries` record:

- `currency` — "Currency: <code>" (detail: symbol / formatting)
- `tax` — "Tax engine" (detail: tax_rates from the catalog record)
- `vat` — "VAT: <name> <rate>%" (skip when vat is null) — informational only, no user input
- `language` — "Add language(s): <missingLanguages joined>" — ONLY include when the diff from step 1.5 produced a non-empty set. If every relevant language is already installed, drop this item.
- `address` — "Address formatting" (detail: first addressFormat note)
- `agreements` — "Agreements linked" (detail: count kept)
- `payments` — "Payment methods" (detail: kept list)

Mode selection:

- **Configured for real** (user confirmed + POST succeeded): `mode: "live"` — fire the reveal steps FIRST, then perform each remaining configuration action and call `steps_mark_item` after each one succeeds so the checkmarks track genuine progress. Anything with no real API behind it gets marked immediately after its sibling completes.
- **Plan mode**: `mode: "plan"` with `item_duration_ms` around 800 — the panel animates on its own. Close by telling the user nothing was written and what it would take to go live.

# Rules

- READ endpoints are always safe; the ONLY write in this flow is `POST /api/settings/company_countries`, and only after explicit confirmation.
- Never invent VAT rates or payment methods — use `country_recommendations` and label uncurated markets honestly.
- Keep chat text short; the panel does the talking.
