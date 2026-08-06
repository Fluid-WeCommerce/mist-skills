# 06 — Greenfield: a company with no bundles

Zero bundles, zero infrastructure. The deliverable is **not** one bundle — it is the platform,
proven by one real bundle.

**Prerequisite.** Greenfield here means *no bundles*. It does **not** mean no store. This
playbook assumes an existing active theme and a populated catalog — that is onboarding's
output. If the catalog is empty or there is no theme, stop and say the onboarding workflow
should run first.

## Order of work

1. **Generate the theme implementation first** (`03-theme-generation.md`). It is independent
   of any bundle and is the reusable asset.
2. **Create the host template** and record its id.
3. **Build one proving fixture from the live catalog** — never a toy. Choose or construct a
   bundle that exercises as many dimensions as the catalog honestly supports:

   | Dimension | Why it must be in the fixture |
   |---|---|
   | an `included` group | proves server-side reconstitution and the explicit-price rule |
   | an `exact` group | the most common rule |
   | a `max_only` group | proves zero-submit (P14) and the nil-bound guard (P16) |
   | a `dynamic_price` group | the only mode where CV/QV flows |
   | a per-item `max_quantity` | proves unit counting, not line counting |
   | a default selection | proves the clamp-to-max fix (P19) |
   | an exclusive pair | proves the `bundle_config` read (P2) — the highest-value defect |

4. **Route it, then run G3–G7.**
5. **Prove reusability (G7)** with a second, differently-shaped bundle, then remove it.

## Choosing the fixture for THIS company

Pick the shape the company would plausibly sell, from its own catalog. In descending order of
how often it is the right answer:

**A. Fixed kit** — the default choice for most companies. Three to five existing products that
belong together, one `included` group each (or one group holding all of them), bundle-level
flat price below the sum. Exercises: reconstitution, the explicit-price rule, flat pricing.
*Good for: home goods, gift sets, apparel sets, anything with a natural "buy these together".*

**B. Pick-N** — "choose any 3". One `customizable` group, `exact 3`, `dynamic_price` so CV/QV
flows. Exercises: selection gating, unit counting, per-item pricing.
*Good for: coffee, pet food, supplements, beauty shades, beverages.*

**C. Base + options** — an `included` core plus `exact 1` and `max_only` groups. Exercises
nearly everything, and is the honest test if the company's real product needs configuration.
*Good for: electronics kits, meal builders, supplement stacks, "build your routine".*

Whichever you choose, stretch it to cover the dimension table above — add one per-item
`max_quantity`, one default, and one exclusive pair even if the minimal version wouldn't need
them. The point is the platform, not the bundle.

If the catalog genuinely has no products that belong together, say so and ask rather than
inventing a nonsense bundle.

---

## Worked example — food/QSR (the test company)

Chipotle is greenfield (`GET /api/v2025-06/bundles` → `[]`) with an unusually good catalog for
this: 47 build components already exist as individual products — 7 proteins, 2 rices, 2 beans,
11 toppings, chips & dips, sides, high-protein cups. That makes it a shape-C fixture. **Read
this as one instance of the recipe above, not as the recipe.**

Map `chipotle.com/order/build/burrito` (Archetype F, `01-discovery.md` §6) onto:

| Group | Type | Rule | Pricing | Notes |
|---|---|---|---|---|
| Tortilla / base | `included` | — | explicit `fixed_price` | the $0 decision must be deliberate |
| Protein | customizable | `exact 1` | `dynamic_price` | prices differ per protein; `max_quantity: 2` for double |
| Rice | customizable | `max_only 1` | `fixed_price "0.0"` | the "No Rice" card is a negative selection, **not** an item |
| Beans | customizable | `max_only 1` | `fixed_price "0.0"` | same |
| Toppings | customizable | `max_only N` | `fixed_price "0.0"` | many-select, included at no charge |
| Extras (guac, queso) | customizable | `max_only N` | `dynamic_price` | real per-item deltas |

Bowl vs burrito is the natural **exclusive pair** if both are modelled in one product;
otherwise they are two bundles sharing the same groups' worth of items.

Two catalog rules already established for this company and still binding: prices for build
components come from the meal-builder HTML, not the in-store photo; and creating a product
whose slug already exists silently yields a UUID-suffixed slug, so always read `slug` /
`canonical_url` back from the response.

The equivalents in other verticals, for orientation: an electronics "configure your laptop"
page is the same shape (included chassis + `exact 1` RAM + `exact 1` storage + `max_only`
accessories, with RAM tiers as an exclusive set); a supplement "build your stack" is the same
shape with subscription forcing on the base; a beauty "build your routine" is the same shape
with `dynamic_price` throughout. None of them need a code change.

Create the fixture as **draft** while iterating; publish only after G6 passes.

## Handing over

Say plainly:
- what was built, and that it renders every future bundle with no code change
- how to add the next bundle (admin Bundle Builder → set the Theme Template field)
- that a theme switch or clone **un-routes every bundle**, and the manifest is the replay list
- which judgement calls were made on their behalf and what each one costs
