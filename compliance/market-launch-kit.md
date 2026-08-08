---
name: Market Launch Kit
description: Prove a market is actually purchasable before calling it open — walks the real purchase path as a customer in that country and reports which step failed
icon: shield-check
---

# Market Launch Kit

Open a new market for **{{company.name}}** — country, language, pricing, SKUs, localized
storefront content, and per-market routing — and then verify a real customer in that market
can complete a purchase.

The verification is the point. Opening a market is a handful of API calls. The failure mode
that actually costs money is a market that *looks* open and silently isn't: products that
404 because they were never priced in the new market, or a cart that accepts the home-market
SKU, shows 0.00, and blocks checkout. Both are real and both have shipped before. This skill
is not done when the market exists. It is done when a purchase in that market succeeds.

## Relationship to `compliance/open-a-country`

`compliance/open-a-country` owns the sanctioned *opening* writes — operating mode, entity,
agreements, payment methods, languages, enrollment fields — and chains the mode finalizer. It is
the correct tool for that work and this skill does not duplicate it.

**This skill's contribution is the survey and the proof either side of it.** Phase 0 establishes
whether local-currency pricing is even reachable before anyone writes a price row. Phase 1
measures the gap. Phase 4 walks the purchase path as a customer and reports which of five steps
failed. Phase 5 states what remains outside any of it.

So when `open-a-country` is available, **delegate Phase 2 to it** rather than reverse-engineering
market writes. Run Phases 0 and 1 first — they will often stop the run before it starts, which is
the point — then hand off, then come back and verify.

## Phase 0 — Separate "open a market" from "charge in local currency"

Ask this before anything else, because the answer changes the scope by an order of magnitude:

**Does this market need to charge in local currency, or just be open and selectable?**

Those are different projects.

- **Selectable in the company's existing currency** — enable the country and language, price the
  catalog in the current currency, verify the purchase path. Hours of configuration.
- **Charging in local currency** — needs an operating mode the company may not have: either a
  local legal entity with local tax registration, or the home entity plus a licensed
  merchant-of-record and the relevant digital-services tax registration. Weeks of compliance,
  and it gates on relationships nobody can configure from a chat.

**Check the payment side before writing a single price row.** If no enabled payment integration
can accept the target currency, then local-currency pricing cannot be verified at Phase 4 step
5 no matter how correct the rest of the work is. Establish that first and say so plainly —
"this market can be opened in USD today, and can charge local currency after X" is a useful
answer. Writing prices you know can't be charged is not.

If the requester asked for local currency and it isn't available, **stop and report the gate**.
Do not silently downgrade to the home currency, and do not proceed to write rows. Present the
options with their real timelines and let a human choose.

## What to ask for, once

Ask the operator for the target market in a single question, then stop asking:

- Country (or list of countries)
- Language, if it differs from the country default
- Currency, if it differs from the country default
- Which products should be available in this market — default to the full catalog
- Whether to localize existing content, or launch with home-market copy first

If they name only a country, infer language and currency from it, state the inference, and
continue. Don't stall a market launch on a currency question you can answer yourself.

## How markets actually work here — read before acting

Two layers govern whether something is purchasable in a country. Both matter, and skipping
either is what produces a market that looks open and isn't.

**Geography and assortment.** `Region` (geographic grouping) carries a `Retail::Market`
(a pricing market over that region, holding `default_locale` and `position`), which carries
`Retail::Catalog` records (a product assortment for one market, optionally per pricing tier),
which join products via `catalog_products`.

**Per-variant pricing.** `CompanyCountry` enables a country for the company. `VariantCountry`
holds the actual price, points, and currency for one variant in one country.

Three constraints that dictate the order of operations:

1. **Regions before markets.** `Retail::MarketProvisioner#add` returns `region_not_found` if
   the Regions foundation hasn't been provisioned. Provision regions first, or market creation
   fails with a message that looks unrelated.
2. **A variant is purchasable in a country only if it has an `active` `VariantCountry` row for
   that country.** `VariantCountry` has an `active` scope; no row, or a row with
   `active: false`, means not purchasable — and the storefront's market filter drops it from
   listings rather than erroring. That silent drop is the primary failure this skill exists to
   catch.
3. **`country_id` on a `VariantCountry` is immutable.** The model declares
   `validate :cannot_update_country, on: :update`. To move or fix a country you create a new
   row; you cannot edit an existing one. Attempting the edit fails validation.

`default_locale` is formatted `<language_code>_<country_code>` — `en_US`, `de_DE`. Match that
exactly; a malformed locale resolves to the home market silently.

## Phase 1 — Survey what already exists

Before creating anything, establish the baseline so you can report a real delta:

1. List the company's enabled countries (`CompanyCountry`) and languages.
2. List existing regions and markets, with each market's `default_locale` and `position`.
3. Record the home market and its currency.
4. Count the catalog: total purchasable variants, and how many carry an `active`
   `VariantCountry` row. The gap between those two numbers is your real work.
5. Note the active theme and any existing per-country template overrides.

Report this as a short table. If the requested market already exists, say so and skip to
Phase 4 — verification is still worth running, because "open" and "working" are different.

## Phase 2 — Open the market

Order matters; do not reorder these.

1. **Confirm the Regions foundation exists.** If not, provision it before anything else.
2. Create or confirm the region covering the target country.
3. Enable the country on the company.
4. Enable the language.
5. Create the market over that region, setting `default_locale` to
   `<language_code>_<country_code>` and a `position` that doesn't collide — `position` is
   unique per store.
6. Create or confirm the catalog for that market, and attach the products that should be
   available. One catalog per market per pricing tier.
7. **Create an `active` `VariantCountry` row for every variant that should be purchasable**,
   with price, points, and currency for this country. This is the step that gets skipped, and
   skipping it is invisible until someone tries to buy.

After each step, state what changed. If a step fails, report the error verbatim and stop — do
not localize content on top of a broken market. Note especially that a `region_not_found` from
market creation means step 1 was skipped, not that the country is invalid.

## Phase 3 — Localize the storefront

1. Translate the storefront's navigation, homepage, and shop copy into the target language.
   Keep the brand's tone: read the company's brand guidelines first and match them. Do not
   invent a new voice per locale.
2. Localize product titles and descriptions. Keep product names that function as trademarks
   in their original form unless the company already localizes them.
3. Set up per-market routing so the locale serves the right templates, and confirm the
   redirect behavior for the market root.
4. Localize prices in display format, not just value — separators, symbol placement, and
   decimal conventions differ by locale.
5. Translate any compliance or claims copy carefully. If the company's category carries
   regulated claims, flag the strings you translated for human review rather than assuming
   the translation is compliant in the new jurisdiction.

## Phase 4 — Prove it works (do not skip)

Open the storefront **as a visitor in the new market** and walk the whole path in a real
browser. Take a screenshot at each step so the evidence exists:

1. Load the market's storefront root. Confirm the locale, currency symbol, and language are
   correct on first paint — not after a manual switch. A home-market locale here usually means
   a malformed `default_locale`.
2. Load the shop page and **count the products**. Compare against the number of variants you
   gave an `active` `VariantCountry` row in Phase 2. If the page shows fewer, the difference is
   exactly your silently-dropped products — the market filter excluded them rather than
   erroring. Name which ones.
3. Open a product detail page. Confirm the price is in the market currency and is not 0.
4. Add to cart. Confirm the cart line shows the **market-specific variant** and a non-zero
   price. A 0.00 line means the cart fell back to the home-market variant, which will block
   checkout with a country availability error.
5. Proceed to checkout. Confirm it loads and does not reject the market.

Then state the result plainly. If any step fails, say which one, what you saw, and what you
think is wrong. **A market that fails step 4 or 5 is not launched, and reporting it as
launched is the single worst outcome of this skill.** Say it failed.

## Phase 5 — Report

Give the operator a short summary they could forward to an executive:

- Market opened: country, language, currency
- Products made purchasable: count, and any excluded with the reason
- Content localized: what was translated, what was left in the home language
- Verification: each of the five checks, pass or fail, with the screenshots
- Anything needing human review — regulated claims, tax, shipping, payment coverage

Then note explicitly what this skill does **not** cover, so nobody assumes it did: payment
provider coverage in the new market, tax configuration, shipping rates and carriers, customs
and duties, and local regulatory review. Those are real gates on selling, and they are
outside this skill.

## Notes for whoever runs this next

- Run one market at a time. Two concurrent market launches on the same company will fight
  over the same catalog pricing writes.
- If the company has a reporting database connected, check post-launch whether the market is
  converting; a market that opens cleanly and then converts at zero usually means a payment
  or shipping gap, not a storefront problem.
- Re-running this skill on an already-open market is safe and is a reasonable way to audit a
  market someone else opened. Phase 4 alone has value.
