# brand.md — the company brand guide

`brand.md` is the single highest-leverage artifact this skill produces. Mist injects it
as a `<brand_voice>` block into **every agent turn for this company, forever** — every
workflow step, every QA reviewer, every later theme/portal/widget/copy request. Nothing
else in the onboarding run has that reach.

`STEP_OUTPUT` does not have that reach. It only reaches steps that declare a `dependsOn`,
it is invisible to every QA reviewer, and it dies with the run. **Brand facts that live
only in `STEP_OUTPUT` are lost.** Write them to `brand.md`.

## What goes wrong when you skip it

A real run: a clone of `cowboy.com` — a Belgian maker of €2,399-3,999 connected e-bikes,
with a near-black/paper palette, Suisse Intl type, and spec-driven headline copy
("Riding reinvented", "Super. Natural.") — shipped with generic apparel-template copy:
*"Built different. Worn forever."*, *"NEW DROP"*, *"Trusted by thousands"*.

Nothing was broken. The theme agent simply had no idea what the brand was, because the
brand data lived in a `STEP_OUTPUT` blob it never saw. Every downstream agent fell back
on template defaults. That is the failure this file exists to prevent.

## How to write it

**Tool:** `update_brand_voice({ content, mode: "replace" })`.

- `mode: "replace"` on the first write (you are supplying the complete document).
- `mode: "append"` with a `section` for a single later correction.
- The tool writes `<workspaceRoot>/<companySlug>/brand.md` **and** pushes the whole
  document to `PATCH /api/settings/brand_guidelines` → `brand_guidelines.brand_md`. It
  returns whether the API push succeeded; the local write stands either way.
- Do not hand-roll the write. `fluid_api` alone skips the local file, which is what
  `<brand_voice>` actually reads.

**Keep the canonical headings.** Mist, Fluid admin and the theme tooling all locate
sections by heading text, and `update_brand_voice`'s `section` argument matches on them:

```
# Brand Guide
## Brand Overview
## Mission & Values
## Tone of Voice
## Audience
## Vocabulary & Naming
## Visual Style
## Do's and Don'ts
## Brands & Sites We Admire
## Examples
## Sources
```

Add sections if the brand needs them; do not rename or drop these.

## The quality bar: would this be wrong for a different company?

Read back every line you wrote and ask that question. If a sentence would sit just as
comfortably in a supplement brand's guide as in this one, **it is boilerplate — cut it or
replace it with the specific fact.**

| Boilerplate (reject) | Specific (keep) |
|---|---|
| "Friendly and approachable" | "Two beats and a full stop: 'Super. Natural.' No exclamation marks — there isn't one on the whole site." |
| "Modern, clean design" | "~95% ink-on-paper (`#141414` on `#F8F8F5`); `#BF4800` is a punctuation mark, not a hero background." |
| "Quality-focused customers" | "European city commuters, 28-45, replacing a car; will spend €2,399-3,999 and care whether it's serviceable in four years." |
| "Use the brand font" | "Suisse Intl 400/500/600 — proprietary (Swiss Typefaces), not freely licensable. Substitute Inter at `-0.01em` tracking and say so." |
| "Avoid off-brand language" | "Never 'drop', 'restock', 'game-changer', 'Built different'. Never an exclamation mark." |

Two hard rules:

1. **Quote the source.** Real headlines, real taglines, real product-description
   sentences, pulled verbatim from pages you actually fetched. A tone section with no
   quoted examples is an opinion, not a guide.
2. **Numbers, not adjectives.** Hex values, font names + weights, price bands, product
   counts, market/currency, founding year. Every one of these is checkable by the QA
   step; adjectives are not.

Leave the `<!-- … -->` prompt comments in place only for sections you genuinely could not
source, and say so in the report rather than inventing content. A short honest guide
beats a long invented one — but a run that fills in only two sections has not done this.

## Where the content comes from (you already have it)

| Section | Source you already fetched in Step 3 / Step 4 |
|---|---|
| Brand Overview | homepage hero + `og:description` + about page; product line-up with real prices; founding year; scale numbers the brand publishes (riders, units, years) |
| Mission & Values | about / mission / manifesto page, sustainability or "our story" pages, careers page |
| Tone of Voice | **verbatim headlines and body copy** harvested across ≥3 page types (home, PDP, a content page). Look for sentence shape, casing, punctuation habits, person/tense, whether exclamation marks or emoji appear at all |
| Audience | who the copy addresses, price band, markets/locale (`html lang`, currency, shipping page), the secondary audiences the site has pages for (business, students, trade, refurb) |
| Vocabulary & Naming | product/model naming pattern, trademarked feature names (`™`), the words the site uses for its customer ("rider", "member", "athlete"), the primary CTA verb, category terms, price formatting |
| Visual Style | CSS custom properties and `@font-face` from the site's stylesheet (see below); imagery conventions read off real product shots |
| Do's and Don'ts | invert everything above into concrete guardrails, plus anything the site conspicuously never does |
| Brands & Sites We Admire | brands the site stocks/partners with, press outlets it quotes, explicit comparisons in press quotes |
| Examples | 3-5 on-brand snippets quoted verbatim, **and 3 off-brand lines** written specifically to be rejected for this brand |
| Sources | every URL you actually read, plus the stylesheet filename |

### Harvesting the palette and typography from the source stylesheet

Modern storefronts declare their real design tokens in CSS custom properties. This is
far more reliable than eyeballing a screenshot.

1. Fetch the page HTML and pull the `<link rel="stylesheet">` hrefs (Shopify/Hydrogen
   themes usually have one main bundle).
2. Fetch that stylesheet and read:
   - `:root { --color-*: … }` — the brand's own names for its own colors. Values may be
     space-separated RGB triples (`--color-primary: 20 20 20` → `#141414`).
   - `@font-face { font-family: …; src: url(….woff2) }` — the **real** family names and
     the exact weights shipped. Three weights means three weights; don't invent an italic.
   - Spacing/size custom properties (`--spacing-section-y`, `--font-size-display`) —
     these are the layout rhythm the theme step needs.
3. Rank the raw hex frequency across the stylesheet as a cross-check on which colors are
   structural vs incidental.
4. **Check the license** of every `@font-face` family. Proprietary faces (Swiss
   Typefaces, Commercial Type, Klim, Lineto, most foundry faces) cannot be re-hosted.
   Name the face, name the closest free substitute, and record both — the theme step and
   the font-substitution QA step both read this.

## Persistence contract (what "done" means)

1. `update_brand_voice` returned `ok` — the local `brand.md` exists and is the document
   you wrote, not the unfilled skeleton.
2. It reports the document was synced to Fluid (`brand_md` on brand guidelines). Verify
   with `fluid_api("/api/settings/brand_guidelines", "GET")` and confirm `brand_md` is
   non-null and starts with `# Brand Guide`.
3. Structured brand fields were pushed **separately** via
   `PATCH /api/settings/brand_guidelines` (`color`, `secondary_color`, `logo_url`, …) —
   see [api-endpoints.md](api-endpoints.md). `brand_md` is the prose layer; it does not
   replace those fields, and those fields do not replace it.

**If the API push fails, the step is not failed.** The local `brand.md` is what
`<brand_voice>` reads, so every downstream agent is already served. Record the failure
verbatim in `remaining_for_human` and move on.

> Historical note, re-verified 2026-07-25: prod Cloud Armor once false-positived
> (rule 932100) on brand text containing code spans/backticks and blocked the save. A
> 9.5 KB `brand.md` containing fenced code blocks, backticks, hex values, `<script>`
> tags, SQL-ish strings and shell commands now PATCHes and round-trips byte-identically.
> The FP is not currently live on this endpoint — but treat the API push as
> best-effort-with-a-recorded-reason rather than a hard gate, because the WAF is not
> under our control.

## Reporting

The Step 9 report gets a Brand block, and `STEP_OUTPUT` gets a `brand_md` object:

```jsonc
"brand_md": {
  "written": true,
  "path": "<workspaceRoot>/<slug>/brand.md",
  "synced_to_api": true,          // false + reason in remaining_for_human if it failed
  "sections_filled": ["Brand Overview","Mission & Values","Tone of Voice","Audience",
                      "Vocabulary & Naming","Visual Style","Do's and Don'ts",
                      "Brands & Sites We Admire","Examples","Sources"],
  "sections_left_as_prompts": [],
  "palette": { "primary": "#141414", "contrast": "#F8F8F5", "accent": "#BF4800" },
  "fonts": [{ "name": "Suisse Intl", "weights": [400,500,600],
              "licensable": false, "substitute": "Inter" }],
  "verbatim_quotes": 8,           // how many real source lines you quoted
  "source_urls": ["https://…", "…"]
}
```

## Related

- `marketing/brand-setup` — the interactive, human-in-the-loop version of this document.
  Use it when a person is available to interview. This reference covers the autonomous
  derive-from-the-website path, which is what the onboarding workflow runs.
