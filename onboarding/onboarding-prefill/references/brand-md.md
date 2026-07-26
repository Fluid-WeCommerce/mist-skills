# brand.md — the company brand guide

`brand.md` is the single highest-leverage artifact this skill produces. Mist injects it
as a `<brand_voice>` block into **every agent turn for this company, forever** — every
workflow step, every QA reviewer, every later theme/portal/widget/copy request. Nothing
else in the onboarding run has that reach.

`STEP_OUTPUT` does not have that reach. It only reaches steps that declare a `dependsOn`,
it is invisible to every QA reviewer, and it dies with the run. **Brand facts that live
only in `STEP_OUTPUT` are lost.** Write them to `brand.md`.

## What goes wrong when you skip it

When brand facts live only in a `STEP_OUTPUT` blob, downstream theme agents cannot see
them and fall back to generic template copy, colors, and type. Nothing appears broken,
but the result no longer resembles the source company. That silent cross-step context
loss is the failure this file exists to prevent.

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

| Boilerplate (reject)        | Specific pattern to fill from the current source                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Friendly and approachable" | "Uses `<sentence pattern>`; source example: `'<verified source quote>'`; `<punctuation rule>` appears across `<pages checked>`."                               |
| "Modern, clean design"      | "`<foreground hex>` on `<background hex>` from `<CSS token>`; `<accent hex>` is reserved for `<observed use>`, not `<unobserved use>`."                       |
| "Quality-focused customers" | "`<specific audience>` in `<market>`, buying within `<observed price band>` and repeatedly addressed around `<verified concern>`."                            |
| "Use the brand font"        | "`<font family>` `<observed weights>` — `<license verdict + evidence>`. Use `<licensed substitute>` at `<tracking/line-height>` when re-hosting is not allowed." |
| "Avoid off-brand language"  | "Never `<words absent or contradicted by the source>`. Follow the source's observed `<casing/punctuation>` rule."                                             |

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

| Section                  | Source you already fetched in Step 3 / Step 4                                                                                                                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Brand Overview           | homepage hero + `og:description` + about page; product line-up with real prices; founding year; scale numbers the brand publishes (riders, units, years)                                                             |
| Mission & Values         | about / mission / manifesto page, sustainability or "our story" pages, careers page                                                                                                                                  |
| Tone of Voice            | **verbatim headlines and body copy** harvested across ≥3 page types (home, PDP, a content page). Look for sentence shape, casing, punctuation habits, person/tense, whether exclamation marks or emoji appear at all |
| Audience                 | who the copy addresses, price band, markets/locale (`html lang`, currency, shipping page), the secondary audiences the site has pages for (business, students, trade, refurb)                                        |
| Vocabulary & Naming      | product/model naming pattern, trademarked feature names (`™`), the words the site uses for its customer ("rider", "member", "athlete"), the primary CTA verb, category terms, price formatting                       |
| Visual Style             | CSS custom properties and `@font-face` from the site's stylesheet (see below); imagery conventions read off real product shots                                                                                       |
| Do's and Don'ts          | invert everything above into concrete guardrails, plus anything the site conspicuously never does                                                                                                                    |
| Brands & Sites We Admire | brands the site stocks/partners with, press outlets it quotes, explicit comparisons in press quotes                                                                                                                  |
| Examples                 | 3-5 on-brand snippets quoted verbatim, **and 3 off-brand lines** written specifically to be rejected for this brand                                                                                                  |
| Sources                  | every URL you actually read, plus each exact stylesheet URL and the color-token / `@font-face` declarations used                                                                                                      |

### Harvesting the palette and typography from the source stylesheet

Modern storefronts declare their real design tokens in CSS custom properties. This is
far more reliable than eyeballing a screenshot.

1. Fetch the page HTML and pull the `<link rel="stylesheet">` hrefs (Shopify/Hydrogen
   themes usually have one main bundle). When rendered/crawl HTML omits `<head>`, use
   `web_fetch` on the canonical page to read the raw HTML and extract the hashed bundle URLs.
   Resolve relative links against the final page URL. Do not search for or synthesize a CDN
   filename—the raw document is the authority.
2. Fetch that stylesheet and read:
   - `:root { --color-*: … }` — the brand's own names for its own colors. Values may be
     space-separated RGB triples (`--color-primary: 18 52 86` → `#123456`).
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
5. Retain the exact stylesheet URL plus the relevant custom-property and `@font-face`
   declarations in the guide's Sources section and structured step output. A reviewer in a
   fresh chat must be able to reproduce the palette, font names, weights, and license verdict
   without access to the worker's transient crawl response.

### Use three source layers, each for what it actually proves

| Layer                                         | Good evidence for                                                         | Does not prove                                                      |
| --------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| AI-friendly Markdown (`/.md`, `<page>.md`)    | exact copy, product facts, links, clean headings                          | rendered section order, media/crop, navigation, responsive behavior |
| Rendered HTML + linked CSS                    | DOM structure, JSON-LD, CSS tokens, font files/weights, computed geometry | the final visual state when overlays or animation obscure it        |
| Clean rendered screenshots (desktop + mobile) | hierarchy, imagery, crop/focal point, rhythm, responsive composition      | exact token names, font license, complete catalog data              |

Use all three for home, the primary shop/collection page, and a representative PDP. If a
Firecrawl screenshot contains a region prompt, cookie dialog, newsletter modal, or blank
overlay, dismiss and recapture with managed crawl/browser tooling; never
describe the obscured
image as the site's intended visual style.

## Persistence contract (what "done" means)

1. `update_brand_voice` returned `ok` — the local `brand.md` exists and is the document
   you wrote, not the unfilled skeleton.
2. It reports the document was synced to Fluid (`brand_md` on brand guidelines). Verify
   with `fluid_api("/api/settings/brand_guidelines", "GET")` and confirm `brand_md` is
   non-null and starts with `# Brand Guide`.
3. Structured brand fields were pushed **separately** via
   `PATCH /api/settings/brand_guidelines` (`color`, `secondary_color`, `logo_url`,
   licensed `fonts[]`, …) — see [api-endpoints.md](api-endpoints.md). `brand_md` is the
   prose layer; it does not replace those fields, and those fields do not replace it.

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
  "palette": {
    "primary": "<hex from source CSS>",
    "contrast": "<hex from source CSS>",
    "accent": "<hex from source CSS>"
  },
  "fonts": [{
    "name": "<family from @font-face>",
    "weights": ["<observed weights>"],
    "licensable": "<true|false + evidence>",
    "substitute": "<licensed substitute when needed>"
  }],
  "verbatim_quotes": 8,           // how many real source lines you quoted
  "source_urls": ["https://…", "…"]
}
```

## Related

- `marketing/brand-setup` — the interactive, human-in-the-loop version of this document.
  Use it when a person is available to interview. This reference covers the autonomous
  derive-from-the-website path, which is what the onboarding workflow runs.
