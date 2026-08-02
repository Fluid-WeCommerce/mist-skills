---
name: Claim fidelity audit
description: Find claims that survived a site clone, a new market, or a translation while the footnote, citation, or FDA disclaimer that substantiated them did not — the orphaned claims that turn a compliant page into a regulatory exposure.
icon: shield-check
---

# Goal

Audit {{company.name}}'s live catalog and content for **orphaned claims** — a marketing claim
whose substantiation did not travel with it.

A compliant claim is a pair: the claim *and* the thing that backs it — a footnote marker, a
cited study, an FDA disclaimer, a typicality statement. Cloning a site, opening a second
market, or translating a catalog breaks the pair far more often than it breaks the claim.
The claim is the headline; the disclaimer is small print at the bottom of a template that no
longer renders. Nothing looks broken. The page just quietly became a regulatory exposure.

Fluid already scans persisted content for FTC/FDA violations. What it does not do is ask
whether a claim's *companion* survived a migration. That is what this audit adds, and it is
the one thing an external crawler structurally cannot check — it never saw the source pair.

**Scope note, state it in the output:** this reads what is in Fluid now. It cannot diff
against the original source site unless you supply one, so it detects *missing
substantiation*, not *altered wording*.

# Steps

1. Establish the surface you are auditing. Call
   `fluid_api("/api/settings/languages", "GET")` and
   `fluid_api("/api/settings/company_countries", "GET")`. Capture every enabled language
   `iso` and every market. The company's default language is the audit baseline; every
   other enabled language is a fidelity risk. If only one language is enabled, say so and
   skip step 6 — do not invent a second locale.

2. Pull the live catalog. Paginate
   `fluid_api("/api/v202604/company/products?page[limit]=100", "GET")`, following
   `meta.pagination.next_cursor` until it is null. Do the same for
   `/api/v202604/company/posts`, `/api/v202604/company/pages`,
   `/api/v202604/company/categories` and `/api/v202604/company/collections`.
   `limit` is not strictly honoured — read `meta.pagination.total_count`, never the array
   length. An empty `meta.pagination` (`{}`) means zero rows: report that resource type as
   empty rather than rendering an audit against nothing.

3. For each resource, assemble its claim-bearing text: `title`, `description`,
   `introduction`, `feature_text`, **and `seo.description`**. `description` is rich text and
   arrives carrying markup — strip tags before matching, or a `<sup>*</sup>` footnote marker
   will read as the literal string `sup` and every marker check will pass falsely.

   **`seo.description` is not optional.** Collections routinely have `description: null` and
   carry their entire marketing claim in `seo.description`, which renders in `<head>` and in
   search results. Fluid's own compliance scanner reads `description` and not `seo.description`,
   so those resources score a perfect 10.0 while carrying live unsubstantiated claims. Auditing
   only `description` reproduces the platform's own blind spot. Mark which field each finding
   came from.

4. Detect **claims**. Match case-insensitively and record the exact quoted sentence:
   - **Superiority** — `#1`, `number one`, `best`, `leading`, `most recommended`, `top-rated`
   - **Efficacy statistics** — any `NN%`, `n=`, `X out of Y`, `saw improvement`, `saw less`
   - **Clinical** — `clinically proven`, `clinically tested`, `randomized`, `placebo-controlled`,
     `double-blind`
   - **Credentialed endorsement** — a profession asserted as backing, e.g.
     `dermatologist-recommended`, `physician-formulated`, `doctor-approved`,
     `vet-recommended`, `pharmacist-recommended`. Match the *pattern*
     (`<profession>-recommended|-formulated|-approved|-developed`), not a fixed list
   - **Timeframe** — `in N months`, `by month N`, `within N weeks`, `results in`
   - **Disease/health verbs** — `cures`, `treats`, `heals`, `prevents`, `reverses`, `fights`,
     `combats`, `eliminates`, `restores`, `blocks`
   The last group is severity **critical** on its own: a disease claim is prohibited outright,
   substantiated or not.

5. Detect **substantiation** in the same resource. Any of:
   - A footnote marker — `*`, `†`, `‡`, `§`, or a superscript digit adjacent to the claim
   - An FDA disclaimer — match on `have not been evaluated by the Food and Drug Administration`
   - A named source — a proper noun credited as the evidence, plus the generic markers
     `study`, `trial`, `survey`, `data on file`, `(20NN)`, `et al`, `J. <journal abbrev>`.
     **Do not hard-code a list of research firms.** Brands cite whoever surveyed them —
     a market-research company, a journal, a university, their own data. Look for the
     *shape*: a capitalised organisation or author name adjacent to the claim, or a
     year in parentheses. Read the company's own footer once (step 8) and learn which
     sources this brand actually uses, then match those.
   - A typicality statement — `results vary`, `individual results`, `not typical`

   ⚠️ **Exclude the claim's own span before testing for substantiation.** `clinical` appears in
   both vocabularies, so `"clinically proven"` will match itself as its own citation and the
   audit returns a false clean bill on exactly the resources that matter most. Cut the matched
   claim text out first, then look for substantiation in what remains.

   **An orphaned claim is a resource with a match in step 4 and no match here.** That pairing
   is the finding this whole audit exists to produce — rank by it.

6. Check locale fidelity, the highest-yield axis. For each non-default language `iso` from
   step 1, call `fluid_api("/api/v202506/products?lang=<iso>&limit=100", "GET")` and
   paginate. **Use v202506, not v202604.** The v202506 controller runs in `no_fallback`
   mode, so an untranslated field comes back **`nil`**; v202604 silently substitutes English
   and every field will look present. Flag any product where a claim-bearing field is
   translated but a substantiation-bearing field is `nil` — that is a claim standing in
   French with its disclaimer left behind in English, and it is the exact failure the brief
   warns about.

7. Verify the worst offenders with the platform's own scanner. For the **top 10 resources by
   orphan count only**, call
   `fluid_api("/api/v202604/company/products/<id>/compliance", "POST")` then read
   `fluid_api("/api/v202604/company/products/<id>/compliance", "GET")`. Capture `score`,
   `summary`, and each issue's `severity`, `issue_type` and `recommendation`. Three limits to
   respect: the scan is rate-limited to 60/minute behind a circuit breaker, it ignores a
   repeat scan of the same resource within 5 minutes, and it truncates input at 8,000
   characters. Do not loop, do not re-scan, and note in the output if a long resource was
   likely clipped.

8. **Prove it was a fidelity loss, not an absence.** For the two or three worst orphans, take
   the source URL the catalog was cloned from and fetch the matching product page.
   Search it for the same substantiation vocabulary as step 5. If the source page carries an
   FDA disclaimer or a named citation and the Fluid record does not, the pair was **broken by
   the migration** — say so explicitly, with both sides quoted. That is the difference between
   "this catalog has no disclaimers" (weak, and possibly always true) and "the clone dropped
   them" (strong, and actionable). Skip this step only if no source URL is available, and say
   why.

   ⚠️ **Use `crawl`, not `web_fetch`, for this step.** Marketing sites routinely exceed
   `web_fetch`'s 200KB cap, and the FDA disclaimer almost always lives in the **global footer**
   — the first thing truncation removes. A truncated fetch reports "no disclaimer at source"
   and manufactures a false negative on the exact question this step exists to answer. If you
   must use `web_fetch`, confirm the response was not truncated before trusting a negative.

9. Render three Markdown tables:
   - **Orphaned claims** — resource, type, the quoted claim, which substantiation is missing,
     severity. Sorted worst first.
   - **Locale gaps** — locale, product, the claim field that translated, the substantiation
     field that did not.
   - **Scanner verdicts** — resource, score, risk band (RED <5.0, ORANGE 5.0–6.9,
     YELLOW 7.0–8.9, GREEN ≥9.0), top issue.
   Lead with a one-line headline: how many live resources carry a claim, and what percentage
   of those carry its substantiation.

10. Close with **ONE** recommendation, grounded in the counts — for example "38 of 52
   claim-bearing products have no FDA disclaimer; add it to the product description template
   rather than per-product," or "claims are substantiated in en-US but 26 products lost the
   disclaimer in the second locale — fix the translation step, not the products," or "every
   claim carries its footnote; the exposure here is the two disease-verb matches, which no
   disclaimer can cure." Then offer to draft the missing disclaimer text. **Do not write
   anything back** — this is an audit; the fix is the operator's call.

**If no claims are found at all, say so plainly and treat it as a finding, not a pass.** For a
brand whose positioning is clinical, zero claim matches almost certainly means the clone
dropped the marketing copy rather than that the catalog is clean — check whether descriptions
imported at all before reporting a clean bill of health.

**Never state that content is compliant.** This flags likely gaps against a documented
pattern. It is not legal review, and the output should say so in one line.
