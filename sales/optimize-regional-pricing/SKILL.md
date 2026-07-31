---
name: Regional Pricing Strategist
description: Recommend evidence-aware country-specific pricing tests from Fluid catalog and performance data, with break-even contribution scenarios and a reversible experiment plan.
icon: badge-dollar-sign
---

# Regional Pricing Strategist

Turn regional pricing into a documented decision and controlled experiment. Distinguish currency presentation from a deliberate change in willingness-to-pay, show the conversion lift required to offset every discount, and keep live pricing unchanged until the user explicitly approves implementation.

## Keep the run safe

- Default to local analysis and local output.
- Treat store inspection as read-only. A recommendation run may fetch catalog and performance data, but must not call product, price, theme, or asset write operations.
- Never publish prices, call a billing write API, edit a live theme, or migrate existing subscribers without explicit authorization.
- Treat all recommended prices as proposals. Prefer experiments with new customers or clearly defined eligible cohorts.
- Never promise that a lower price will increase revenue.
- Never hide taxes, payment fees, refunds, commissions, variable costs, foreign-exchange assumptions, or uncertainty.
- Do not use VPN location, ethnicity, or other sensitive personal attributes for individual pricing. Work at an approved market or storefront level.

## Classify the request

Choose one mode:

1. **Presentment:** display the same economic price in local currency.
2. **Regional strategy:** change the economic price by country or storefront.
3. **Experiment design:** compare a control and candidate price for eligible new customers.
4. **Performance review:** measure a completed pricing experiment.

Do not call currency conversion “pricing optimization.” If the user has no country-level performance data, produce hypotheses, break-even thresholds, and an experiment plan—not a revenue forecast.

## Inspect a Fluid store

When the skill runs for a Fluid merchant or inside Mist, read [references/fluid-store-adapter.md](references/fluid-store-adapter.md).

- Use `fluid_api("/api/v202604/company/products?page[limit]=100", "GET")` for the first catalog page. Follow every `meta.pagination.next_cursor` with `page[cursor]` until it is `null`; do not infer completeness from row count or expect `total_count`.
- Use `fluid_api("/api/v202604/company/products/{id}", "GET")` for product detail when the list response does not carry the variants, images, or country prices needed for the audit.
- Use the catalog's real product titles, image URLs, variants, currencies, and country prices.
- If `fluid_api` is unavailable or either documented read endpoint fails, ask for a read-only export or saved API response. Do not probe legacy product endpoints.
- Never substitute generated or arbitrary images for a missing catalog image.
- State whether the result is a catalog-only audit or a performance-backed recommendation.

Before invoking a bundled helper, call
`run_skill("sales/optimize-regional-pricing")`. Use the exact content-addressed,
project-relative paths it prints under `.mist-desktop/skill-assets/` for:

- `scripts/import_fluid_catalog.py` as `<IMPORT_FLUID_CATALOG_PATH>`;
- `scripts/analyze_regional_pricing.py` as `<ANALYZE_PRICING_PATH>`;
- `assets/regional-pricing-report.html` as `<REPORT_TEMPLATE_PATH>`.

Never assume these assets exist at source-relative paths in the active project.
Do not copy or edit the materialized files. The supported local handoff is a
saved Product API response:

```bash
python3 <IMPORT_FLUID_CATALOG_PATH> \
  --catalog <absolute-saved-products-json> \
  --output <absolute-normalized-catalog-json>
```

This importer has no network or production write path. It can also enrich an
analysis CSV with exact catalog images and country prices; see the adapter
reference for the command.

## Establish the input contract

Read [references/input-contract.md](references/input-contract.md). Collect:

- product or portfolio scope, plan, billing period, and eligible customer cohort;
- supplied image or official product-page URL for every product, plus honest alt text and source;
- current and proposed local prices by country;
- dated foreign-exchange rate used for normalization;
- visitors or eligible checkout exposures, orders, and refunds;
- taxes included in displayed prices;
- percentage and fixed payment fees, commissions, and variable cost;
- low, base, and high conversion-lift assumptions;
- source and evidence grade for each assumption;
- price floor, maximum discount, excluded markets, and brand constraints.

Preserve the source data. Never fill a missing metric with a plausible-looking value without labeling it as a synthetic assumption.

## Acquire product images

For every distinct product, prefer, in order:

1. a user-supplied local product image;
2. the image URL returned by an authenticated read-only Fluid catalog response;
3. an explicit official catalog or storefront image URL;
4. preview metadata from the official `product_url`;
5. no image.

Never use arbitrary image-search results or generate a substitute product image. Record each image source. Let the report continue without an image when official-page discovery fails, but treat an invalid explicit image as an input error. Package the images locally and attach them to the product-market rows; do not hide the only image in a hero.

## Research the market

Use current primary sources for platform capabilities, storefront tiers, taxes, fees, and implementation constraints. Record the access date and direct URL.
Read [references/research-and-positioning.md](references/research-and-positioning.md) when evaluating comparable products, choosing external benchmarks, or positioning the output.

For purchasing-power or income signals, use a cited public dataset or a user-provided internal source. Treat purchasing power as one input, not an automatic price formula. Also evaluate:

- observed conversion and refund behavior;
- local competitors or credible category benchmarks;
- local price conventions and price endings;
- app-store or payment-platform price-point constraints;
- VAT, GST, sales tax, commissions, and currency conversion;
- geo-arbitrage risk and brand perception.

Do not infer willingness-to-pay from currency exchange rates alone.

## Create the proposal

Choose the honest evidence tier first:

- **Catalog-only audit:** identify price gaps, localization issues, candidate markets, break-even thresholds, and experiments. Do not project gains.
- **Performance-backed recommendation:** calculate low, base, and high contribution scenarios only after country-level visitors, orders, refunds, taxes, fees, and costs are available.

For every market, record:

- control price and proposed local price;
- normalized control and proposed price;
- percentage price change;
- price effect at unchanged order volume;
- break-even conversion lift;
- incremental orders required to break even;
- low, base, and high lift assumptions;
- volume recovery and margin of safety for each scenario;
- evidence grade and source note;
- a risk-aware recommendation: `Needs more evidence`, `Small test only`, or `Strong test candidate`.

Never recommend an immediate rollout solely because the base scenario is positive. A modeled result is not experimental evidence.
Use `Strong test candidate` only when the conservative scenario clears
break-even. Use `Small test only` when the base scenario clears but the
conservative scenario loses contribution.

Read [references/model-and-guardrails.md](references/model-and-guardrails.md) before calculating projections. Use contribution revenue after modeled taxes, fees, refunds, and variable cost. Keep lifetime value separate unless retention and churn assumptions are supplied.

## Run the deterministic analysis

Prepare the market CSV described in the input contract, then run:

```bash
python3 <ANALYZE_PRICING_PATH> \
  --input <absolute-market-csv> \
  --config <absolute-project-json> \
  --output-dir <absolute-local-output-directory> \
  --template <REPORT_TEMPLATE_PATH>
```

The script produces:

- `regional-pricing-analysis.json`
- `regional-pricing-analysis.csv`
- `regional-pricing-summary.md`
- `index.html`

The HTML report is self-contained and reads no remote data. The calculations are deterministic; the scenario assumptions are not.
When configured, the report also contains a locally copied product image under `assets/`; it does not hotlink the source image.
When the current agent surface can safely open a local HTML artifact, open the
generated `index.html` after validation so the user lands directly on the
recommendations. Otherwise return the local file or URL. Never imply that the
page opened when the surface could not open it.

## Design the decision view

Read [references/chart-contract.md](references/chart-contract.md). Always show:

1. current versus proposed price for every recommended product-market test;
2. weak-response downside and base-case outcome together for every recommendation;
3. a cumulative quarterly contribution projection versus keeping current prices;
4. customer-response, eligible-traffic, and time-horizon controls that update every related number;
5. the selected contribution outcome, conservative exposure, and additional first orders at the chosen test size;
6. break-even lift versus low, base, and high conversion assumptions in supporting analysis;
7. price effect versus volume recovery for each scenario in supporting analysis;
8. an accessible assumptions and evidence table.

Lead with a plain-language recommendation statement and immediately show the
ranked product-country tests that clear break-even in the base scenario. Do not
make rejected candidates compete with the recommendations in the primary view.
For every included test, show a large uncropped catalog image first, then the
product name, market, exact local price change, low-assumption downside,
base-case outcome, risk-aware recommendation, and one-quarter conservative
exposure at the default test reach. Never reduce the label to `worth testing`. Keep rejected
candidates in the saved analysis data, not in the primary recommendation list.
Place the scenario control, project metadata, charts, evidence table, and sources
behind one clearly labeled supporting-analysis disclosure.

Preserve every product image with `object-fit: contain`; do not turn it into
decorative hero art. Use a clear green root for modeled opportunity and positive
financial outcomes, and a clear red root for downside and negative financial
outcomes. Keep price-cut percentages and other non-outcome figures neutral.
Back every financial color with signs, labels, and structural direction so color
is never the only signal. Do not add standalone illustrations, hero
diagrams, metaphor graphics, oversized slogans, or social-post compositions. Use
conventional charts only: in particular, show price effect, volume recovery, and
net change as signed horizontal bars with a zero axis, never as a stepped line or
connected-node illustration. Use a light interface with soft borders and
restrained rounded surfaces. Prefer literal chart names, sentence-case labels,
and moderate typography. Reuse one compact five-role type scale—caption, body,
card title, section heading, and display value—instead of inventing sizes per
component. Do not add uppercase monospace eyebrows or numbered kickers above
headings. Choose familiar chart forms based on the analytical question rather
than preserving a signature visual style.

Use one outer surface per recommendation. Do not wrap the whole recommendation
grid in another card, and do not nest bordered or tinted metric cards inside
each product card. Keep market and recommendation state as direct text with a
small color cue rather than stacking multiple pills. Do not add a utility
topbar or decorative eyebrow copy above the decision. On product cards, use the
market's accessible country flag above the product name instead of a colored
country-name-and-code label; retain the written market name in supporting
analysis for precision. Treat the outcome title and the recommendation grid as
one continuous section. If the title already says how many prices need
controlled testing, do not repeat the hierarchy with a second `Recommended tests` heading
or another explanation immediately above the cards.

When order counts exist for low, base, and high scenarios, add one visible
quarterly cumulative line graph beneath the recommendations. Plot contribution
change versus keeping current prices; the current-price baseline stays at zero.
Show conservative and strong bounds as secondary lines and the selected
response as the primary line. Use three accessible range inputs:

- `Customer response`: piecewise-linear interpolation from conservative to base to strong, defaulting to base;
- `Test reach`: percentage of eligible traffic exposed to the candidate price, defaulting to 10%;
- `Time horizon`: one through four quarters, defaulting to four.

Derive quarter spacing from the configured analysis period. Update the graph,
selected contribution, conservative exposure, and additional first-order orders
together whenever any control changes. Never extrapolate beyond the supplied
response endpoints. Label the graph a constant-run-rate scenario, not a demand
forecast. Say `orders`, not `people` or `customers`, unless the source proves
the metric is unique buyers.

In the aggregate summary, show the selected contribution, conservative
exposure, and additional orders with short descriptions underneath. Do not
place dot-plus-label rows above the values; they read like a chart legend. Keep
the final safety note to one short sentence that states the output is modeled
and no live price changed. Preserve the complete assumptions and disclaimer in
the saved analysis data and supporting detail.

Do not make the reader toggle scenarios to compare risk and reward: keep
low-assumption downside and base-assumption outcome visible together on every
recommendation card. Treat `likely` as plain-language shorthand for the base
assumption, never as a measured probability. Label every projected figure as a
scenario or assumption. Preserve rejected and unfavorable candidates in the
saved analysis, while showing the weak-response downside for every recommendation.
Do not use a world map unless it materially improves a many-market analysis and
uses verified geographic data.

## Design the experiment

Prefer one control and one treatment per market. Define:

- eligible new-customer cohort;
- allocation and country targeting;
- primary metric and guardrail metrics;
- minimum runtime or sample-size method;
- stop conditions;
- refund, retention, support, and abuse checks;
- winner rule and rollback plan.

Do not repeatedly inspect results and stop when a variant happens to look favorable. Ask for a qualified analytics review when statistical design or material revenue risk exceeds the available evidence.

## Prepare implementation without publishing

Read [references/platform-handoff.md](references/platform-handoff.md) when the user requests a platform export or pricing-section implementation.

- Generate a reviewed CSV, API plan, or code diff before any write.
- Keep current subscribers unchanged by default.
- For Fluid, keep pricing, copy, and actions in accessible HTML and make the section editor-compatible.
- Keep internal forecasts and confidence labels out of consumer-facing copy.
- Validate local behavior and clearly state that nothing was published.

## Return

Return:

- the local report URL or file;
- input and output paths;
- the current, proposed, and break-even figures;
- source dates and unresolved assumptions;
- the recommended experiment;
- an explicit statement that no live prices or production systems changed.
