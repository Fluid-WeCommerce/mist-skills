---
name: Claim Integrity Guard
slug: compliance/claim-integrity-guard
icon: shield-check
purpose: >
  Audit a storefront for orphaned claim-footnote markers, missing or misplaced
  regulatory disclosures, unattributed trademarks, candidate disease-claim language,
  and leftover migration residue — then recover or draft the missing disclosure page.
  Built for regulated consumer-health copy, where a superscript symbol is a legal
  promise that migration tooling routinely breaks.
do_not_use_for: >
  Do NOT use this skill to write new health claims, invent or infer study citations,
  rewrite claim language, or judge whether a claim is substantiated. It verifies that
  disclosures the brand ALREADY relies on are present, reachable, and correctly placed.
  Substantiation and claim wording are decisions for the company and its regulatory
  counsel. This skill reports; it does not adjudicate.
---

# Claim Integrity Guard

## What this skill is for

In regulated consumer-health copy, a superscript symbol is not decoration — it is a
**contract**. A marker promises the reader that a corresponding disclosure exists and is
findable. If the marker renders but the footnote it points to does not exist, or exists
somewhere no shopper will encounter it, the brand is publishing a claim without the
disclosure it depends on.

**Store migrations break this constantly, and that is the primary thing this skill
detects.** Clone and import tooling faithfully carries product copy across — including
the markers — while the footnote block, the disclosure page, and the theme partial that
rendered them stay behind on the old platform. The copy looks perfect. The legal
plumbing is gone. In most real runs the correct conclusion is *"the import dropped the
disclosures"*, not *"this company is non-compliant"* — see Scope of claim below.

**Run this skill when:**
- A catalog has just been imported or cloned from another platform
- The company sells supplements, cosmetics, nutrition, food, fitness, hemp/CBD, or any
  product carrying an efficacy, structure/function, or comparative claim
- Before a launch review, market opening, or executive walkthrough
- Any time product copy contains `*`, `†`, `‡`, `§`, `¹`, or a bracketed footnote

---

## Scope of claim — read before writing any finding

This skill inspects **one Fluid storefront's stored records**. That is all it can speak to.

- A finding describes **the audited store's current data**, never the company's
  production website, its packaging, its regulatory filings, or its intent.
- When the store is a migration target, the correct headline is *"the import did not
  carry disclosures X and Y"*. Verify against the source site before implying anything
  stronger — the source almost always has them.
- Never assert that a company makes unsubstantiated claims. Assert that **a marker on
  this store resolves to no disclosure on this store**. Those are different statements
  and only the second one is yours to make.
- When writing this up publicly (documentation, examples, a shared report),
  **anonymize the company.** A stored example naming a real brand's regulatory posture
  is permanent and discoverable, and is usually wrong about the production site.

---

## Inputs

Nothing required; runs against the active company.

Optional, only if volunteered: **scope** (default: whole storefront) and
**remediation mode** — `report_only` (default) or `report_and_fix`. Never write without
explicit approval; see Step 7.

---

## Step 0 — Determine the regulatory regime before testing anything

The single largest source of wrong findings is applying one jurisdiction's disclosure
rule to a catalog it does not govern. Establish regime first.

**Product category** — infer per product from title, description, category, and
collection membership. Route:

| Category | Regime (US) | Disclosure expectation |
|---|---|---|
| Dietary supplement | DSHEA / 21 CFR 101.93 | Structure/function claims carry the FDA disclaimer |
| Cosmetic / topical | FD&C cosmetic provisions, MoCRA | **No DSHEA disclaimer.** Drug-level claims push the product into unapproved-new-drug territory |
| Conventional food / beverage | FDA food labeling | Authorized/qualified health claims only; no DSHEA disclaimer |
| Hemp / CBD ingestible | FDA position: excluded from the dietary-supplement definition | DSHEA reliance is not available; flag as its own regime, do not test for the disclaimer |
| Device, apparel, literature, merch | — | No claim regime; exclude from claim findings entirely |

**Markets** — read the open markets, which determines which regimes apply at all:

```
GET /api/settings/company_countries
```

Each entry carries `country.iso`. Map: `US` → DSHEA/FTC · EU member states →
Reg (EC) 1924/2006 (+ Reg 1169/2011 Art. 7) · `GB` → GB nutrition & health claims
register · `CA` → NNHPD product licence/NPN · `AU` → TGA listed medicines.

A store open in more than one regime is normal and must be reported per regime — a
catalog live in both the US and an EU market is under DSHEA **and** 1924/2006
simultaneously, with different requirements.

**If category or market cannot be determined, the regime is `unverified`.** Report it as
such. Never escalate an unknown regime to `critical`.

## Step 1 — Enumerate every surface that can carry copy

Paginate each with `fluid_api` at `page[limit]=100`, following
`meta.pagination.next_cursor` until it is null.

```
GET /api/v202604/company/products?page[limit]=100
GET /api/v202604/company/pages?page[limit]=100
GET /api/v202604/company/posts?page[limit]=100
GET /api/v202604/company/media?page[limit]=100
GET /api/v202604/company/collections?page[limit]=100
GET /api/v202604/company/categories?page[limit]=100
```

Claim copy lives in:
- **Products** — `description.body` (primary), `seo.description`, `seo.title`, `title`
- **Pages and posts** — **`description`**, not a `body` field. Imported page copy lands
  there; reading `body` returns nothing and makes an intact page look empty.

Record per item: resource type, id, title, `canonical_url` **exactly as returned**, and
raw copy fields.

## Step 2 — Normalize, then extract markers

**Normalize before tokenizing.** These are rich-text fields holding imported HTML, so
the marker is frequently not a literal glyph. Run first:

- Decode HTML entities: `&dagger;` `&Dagger;` `&#8224;` `&#8225;` `&ast;` `&#42;`
  `&sect;` `&sup1;` `&nbsp;`
- Unwrap and preserve markup: `<sup>*</sup>`, `<sup class="footnote">†</sup>`,
  `<span class="marker">‡</span>` → the bare glyph
- Normalize unicode variants: `∗` `⁎` `✱` → `*`; `⁺`/`+` in marker position
- Strip `<style>`/`<script>` blocks entirely before scanning

Skipping this under-reports on exactly the imported HTML the skill exists to audit.

**Then tokenize**, longest-match first so `††` is never read as two `†`:
`††`, `‡‡`, `*`, `†`, `‡`, `§`, `¹²³`, `[1]`.

Count a marker only in **trailing claim position** — end of sentence, clause, or
heading. Exclude: `*` inside CSS or code, markdown `**bold**` and `*emphasis*`,
wildcards, `†` inside a URL, and `[1]` that is a markdown reference link
(`[1]: https://…` defined elsewhere in the field).

Split multi-marker runs (`*† ††`) and verify each independently.

Output: `{ marker, resource_type, resource_id, title, field, context_snippet, encoded_as }`.

## Step 3 — Detect convention, then test existence and placement separately

**3a. Detect the store's own convention first.** Marker meaning is not universal —
plenty of brands use `*` for offer terms and `†` for the regulatory disclaimer, the
inverse of the common supplement pattern. Before assuming anything:

1. Look for an existing footnote block anywhere (page, post, product body, theme footer)
   that binds a marker to text. That binding **is** the store's convention — use it.
2. Only if no binding exists anywhere, fall back to the conventional reading below, and
   **label every downstream finding as convention-assumed**.

| Token | Conventional fallback | Typical disclosure |
|---|---|---|
| `*` | Structure/function claim | Regime disclaimer (US supplements: DSHEA) |
| `†` | Study or research citation | Reference |
| `††` / `‡‡` | Additional distinct citation | Numbered reference |
| `‡` | Qualified/comparative claim | Qualifier text |
| `§` | Regional or regulatory scope | Scope statement |

**3b. Test existence.** Does the disclosure text exist anywhere in the storefront?
Search page/post `description`, product bodies, and — where the theme is readable — the
footer partial, for: `footnote`, `disclaimer`, `references`, `citations`, `claims`,
`fda`, `dshea`, `legal`, `study`, and for the regime's required string. For US dietary
supplements only, search for `not intended to diagnose`.

**3c. Test placement — this is a separate question.** Existence somewhere on the
storefront is not adequacy. Under FTC's clear-and-conspicuous standard a disclosure must
be proximate to the claim it qualifies and actually encounterable; a page nobody can
navigate to is much closer to no disclosure than to a working one. For each disclosure
found, record:

- **inline** — in the same copy field as the claim (strongest)
- **linked-from-claim** — the marker or PDP links to it directly
- **navigable** — reachable from site navigation or footer, but not from the claim
- **orphaned-page** — exists as a record, linked from nowhere
- **unverified** — could not determine from available surfaces (e.g. theme files not
  readable from this context). Say which you checked.

Report existence and placement as two fields, never collapsed into one verdict.

## Step 4 — Classify findings (regime-conditional)

Severity depends on Step 0. A cosmetics-only catalog **cannot** produce a DSHEA finding.

- **critical** — the regime's mandatory disclosure is required for this catalog's
  category and markets, markers are present, and the disclosure exists nowhere.
  Weight upward for pregnancy, fertility, infant, or pediatric SKUs.
- **high** — a marker resolves to no disclosure (`orphaned`); or a disclosure exists but
  is `orphaned-page` / unreachable; or a published page redirects off-domain (Step 6).
- **medium** — marker convention inconsistent between products; the same claim carries
  different markers across surfaces; `seo.description` carries a marker the visible copy
  does not; disclosure is `navigable` but not proximate to the claims it qualifies.
- **low** — ™/®/© used with no attribution block; footnote present but unlinked from its
  marker; disclosure page missing an effective date.
- **unverified** — regime, convention, or placement could not be established. Report
  plainly as unknown. **Never promote an `unverified` to a severity.**

## Step 5 — Candidate disease-claim scan (lead generator, NOT a classifier)

This step produces **leads for human review**. It does not determine whether copy is a
disease claim; that turns on the claim's full context, the population addressed, and the
regime. Label the output as such wherever it appears.

Surface sentences containing: `cures`, `treats`, `prevents`, `reverses`, `heals`,
`eliminates`, `fixes`, `remedies`, `fights <condition>`, or a named disease
(`diabetes`, `hypertension`, `depression`, `anxiety disorder`, `arthritis`,
`Alzheimer's`, `infertility`, `cancer`, `COVID`).

**Mandatory exemptions** — these are not findings:
- The regime disclaimer itself. The DSHEA string contains *"diagnose, treat, cure, or
  prevent any disease"*; flagging it would flag the one piece of copy Step 7 tells you
  to add.
- Negated constructions: *"not intended to…"*, *"does not treat…"*, *"is not a
  treatment for…"*
- Text inside a quoted regulatory notice or policy page

**State the limits of this scan explicitly in the report:**
- **False negatives** — a compliant verb can still carry a disease claim when it
  addresses a diseased population: *"supports healthy blood sugar in diabetics"* passes
  verb-matching and is a disease claim.
- **False positives** — some flagged phrasings are authorized: *"calcium may reduce the
  risk of osteoporosis"* is an FDA-authorized health claim (21 CFR 101.72) and matches
  on both *reduce the risk* and *osteoporosis*.

Report the sentence and its `canonical_url`. **Never rewrite it.**

## Step 6 — Migration residue scan

Imported stores routinely keep live pages pointing back at the previous platform. Search
every page/post `description` and `seo` field for:

- `myshopify.com`, `shopify.com/cdn`, `bigcommerce`, `squarespace`, `wixsite`
- `window.location.replace`, `window.location.href =`, `<meta http-equiv="refresh">`
- Absolute links to any domain that is not the company's storefront or a known property
- Empty `description` on a `published` page — an imported page rendering blank

A **published** page containing an off-domain redirect is `high`: it silently walks
shoppers off the store. Report page id, title, `canonical_url`, and the exact substring.

## Step 7 — Report first; remediate only on approval

**Always report before writing.** Findings table ordered by severity, then leverage:

| # | Severity | Regime | Finding | Surface | Existence | Placement | Evidence |
|---|---|---|---|---|---|---|---|

Then propose remediation via `human_in_the_loop`, one proposal per fix class, with
`suggestion_id` = `compliance:claim-integrity:<company_id>:<finding_class>` and the
before-state in `before_payload`. End the turn. Never write before an Approve click.

### 7a. Recover the disclosure page — recover, don't compose

Because this skill mostly fires on migrations, the citations usually **still exist on
the source site**. Recovery order:

1. **Recover from source.** If the store was migrated, `crawl` the source site's
   footnote/disclaimer/references page and the source PDPs. Reproduce the brand's own
   text and record provenance (source URL + capture date) for every entry.
2. **Recover from elsewhere in the store.** Reuse any binding found in Step 3a.
3. **Placeholder and escalate.** Only when 1 and 2 both fail, write
   `[citation required — to be supplied by <company>]`. **Never invent a study, a
   journal, an author, a sample size, or a result.** A fabricated citation is far worse
   than a flagged gap.

Create the page with the **`create_page`** tool — never `fluid_api`. From a non-theme
context, ask which theme by its human-readable name. The page carries: the regime's
required statement (verbatim, and only if Step 0 says the regime applies), one entry per
distinct marker keyed to the store's own convention, a trademark attribution block, and
an effective date.

### 7b. Marker normalization — REPORT ONLY, do not write

Inconsistent marker order across products is a useful **signal** — it usually means copy
arrived from multiple sources or a partial import — so keep detecting and reporting it.

**Do not rewrite it.** Reordering `†*` → `*†` is a cosmetic fix to a `medium` finding,
executed as a byte-level diff on regulated copy dense with `™ ® ’ ‡ * &`, against a
convention the skill may have merely assumed. The risk/reward is bad in every direction.
Hand the list to the company.

### 7c. Repair migration-residue pages

```
PATCH  /api/v202604/company/pages/{id}     # strip the redirect, restore real copy
DELETE /api/v202604/company/pages/{id}     # only with explicit per-page approval
```

### 7d. Verify by re-read

Re-fetch every mutated record and confirm the change persisted. A 200 is not proof.

> If any product PATCH is ever required for another reason: **`product.title` is
> mandatory** on `PATCH /api/v202604/company/products/{id}` — omitting it returns
> `422 {product: {title: ["is missing"]}}` even for a copy-only change. Echo the title
> back byte-for-byte.

## Step 8 — Optional executive summary

Render with `show_dashboard`: `stat_tiles` (markers found / orphaned / products affected
/ critical count), `stat_rows` by severity, and an `insight_banner` stating the single
most serious finding in plain language — phrased per Scope of claim, i.e. about the
store's data, not the company's compliance. Raw numeric values with `format` hints.

---

## Worked example (anonymized)

**Subject:** a 30-SKU supplement catalog freshly imported from Shopify into a Fluid
sandbox store, including prenatal, fertility, and infant-adjacent SKUs. Markets open:
one US, one EU. Brand positioning is explicitly clinical.

**Step 0** — Category: dietary supplements throughout, plus two non-claim SKUs (a shaker
and a book) excluded from claim findings. Markets US + EU ⇒ **two regimes apply**:
DSHEA/FTC and Reg (EC) 1924/2006. Findings reported per regime.

**Step 2** — Markers on 8 sampled products: `*†` ×2, `*† ††` ×1, `†*` ×1 (reversed),
bare `*` ×4. All literal glyphs in this importer's output; entity normalization still
required as importers differ.

**Step 3a** — No footnote block found anywhere in the store, so no binding could be
detected. Conventional fallback used; **all marker findings labelled convention-assumed.**

**Step 3b/c** — 25 pages present (terms, privacy, returns, reviews policy, standards,
clinical study, traceable ingredients). No footnotes/disclaimer/references page.
No occurrence of `not intended to diagnose` anywhere. Existence: **absent**.
Placement: **n/a**.

**Findings:**
- **critical (US regime)** — markers present catalog-wide, regime disclosure absent
  entirely, catalog includes fertility and prenatal SKUs.
- **critical (EU regime)** — claims present with no reference to permitted-claim basis;
  regime requires separate assessment.
- **high** — all `*`/`†` markers orphaned across 30 products.
- **high** — one published page contains
  `window.location.replace("https://<redacted>.myshopify.com")`, live, walking shoppers
  onto the source platform's dev shop.
- **medium** — marker order inconsistent on one product (convention-assumed).
- **medium** — `seo.description` duplicates marker-bearing copy on all 30 products.
- **low** — three ™/® marks in titles and copy with no attribution block.

**Correctly-compliant language, no finding raised:** *"helps fill nutrient gaps"*,
*"supports the body's natural cortisol response"*, *"designed to support conception
outcomes"*. The catalog's **language** is careful structure/function phrasing; only its
**disclosures** are missing.

**Conclusion as written in the report:** *the import did not carry the disclosure layer
across.* The source site was confirmed to publish footnotes and the FDA disclaimer, so
this is a **migration-tooling gap on the sandbox store**, not a statement about the
brand's production compliance.

**Remediation:** disclosure page recovered from the source site with provenance
recorded; residue page stripped of its off-domain redirect; marker inconsistency
reported to the company unmodified.

---

## Gotchas

- **Cursor pagination, not page numbers.** Follow `next_cursor` to null or every count
  you print is wrong.
- **Page copy is in `description`.** Not `body`. Intact pages look empty otherwise.
- **Markers are often encoded.** `<sup>`, `&dagger;`, `&#8224;` — normalize before
  tokenizing (Step 2).
- **`*` is heavily overloaded.** Inlined CSS, markdown bold, wildcards. Several policy
  pages in the worked example open with a CSS blob; a naive scan flags all of them.
  Require trailing claim position.
- **Marker meaning is per-store.** Detect the convention; never assume it and then act
  on the assumption.
- **DSHEA is US dietary supplements only.** Not cosmetics, not food, not CBD, not the
  EU. Regime-gate every disclosure test.
- **The disclaimer contains the prohibited verbs.** Exempt it explicitly or Step 5
  flags the mandatory text.
- **Existence ≠ adequate placement.** Report both.
- **Never compose a URL.** Quote `canonical_url` verbatim; slugs regenerate server-side.
- **Never invent a citation.** Recover, or placeholder and escalate.
- **Never rewrite a health claim, and never normalize markers by machine.**
- **`unverified` is a real answer.** Don't launder it into `absent`.
- **Never characterize a company from a sandbox store.** See Scope of claim.

## Success criteria

- Regime established per category and per open market before any disclosure test
- Every surface enumerated to the end of pagination
- Entity/tag normalization performed before tokenizing
- Store's own marker convention detected, or fallback explicitly labelled as assumed
- Every marker classified for existence **and** placement, separately
- Disease-claim scan reported as leads, with its false-positive and false-negative
  limits stated in the report itself
- Migration residue scanned across all pages and posts
- Findings ordered by severity, regime-tagged, `canonical_url` copied verbatim
- Findings phrased as statements about the store's data, never the company's posture
- No write without an approved `human_in_the_loop` proposal; no machine marker rewrite
- Every mutation verified by re-read
