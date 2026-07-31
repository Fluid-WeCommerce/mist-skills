# Catalogue profiling — building `company-profile.md` for any company

Run once per company during Part A, and again whenever the catalogue changes materially. Output is
`company-profile.md`, the **only** place company facts live.

Five artefacts, in this order:

1. **Lane map** — shopper intent → the collection that actually answers it.
2. **Suppression list** — what must never be recommended.
3. **Pinned best-seller** — because collection order lies (Step 5).
4. **Product ladder** — the price-ordered spine.
5. **Caveats** — where the data will embarrass you.

---

## Why not just search?

**Keyword relevance is unreliable on real catalogues.** Free-text search scores title and
description matches; it has no concept of "this is the flagship" versus "this is a $9 replacement
washer *for* the flagship". On any store with a healthy spare-parts range, the accessories mention
the product noun more densely than the product does.

Two failure modes, both observed live on a real store:

- **Category search:** the store's own core noun returned a pressure insert, a hose, a sprayer, a
  filter and an installation service before any flagship. The $399 hero ranked **12th**.
- **Named search — the one people miss:** searching the *flagship's own name* returned **five spare
  parts and zero flagships** (a tank adapter, bumper pads, a lid, a base plate, a hose — all
  cheaper, all with the product's name in the title).

So the rule is not "use collections for browsing". It is: **products resolve through curated lanes
first, for named lookups too. Keyword search is the fallback, and its results still get the
suppression list applied.**

**Verify this for the company you're setting up.** Run the core noun and one flagship name through
search and read the first ten titles. Record what you find in the profile's caveats — it is the
evidence behind rule zero.

---

## Step 1 — Enumerate

Pull every collection and every product. Capture per collection: id, slug, title, status,
description. Per product: id, title, slug, status, stock, display price, default variant,
subscription support. For large catalogues use the catalog-index tooling rather than paging by hand.

## Step 2 — Classify every collection

| Bucket | Signals | Use |
|---|---|---|
| **Lane** | Answers a shopper question — best sellers, a feature, a use case, a price band, a category | Recommend from these |
| **Family** | One product line's own collection | "Tell me about X" |
| **Merchandising** | Sale, bundles, subscribe & save, seasonal | When the ask matches |
| **Suppress** | Spare parts, replacements, adapters, services, quiz plumbing, upsell rails, drafts, near-duplicates, internal/test collections, filter aids | **Never** recommend |

Three traps that appear in nearly every imported catalogue:

- **Duplicate collections** — two slugs, near-identical titles, different contents. Keep the
  populated published one; suppress the other by slug.
- **Draft collections that still resolve.** A draft collection can be readable and enumerable.
  Check status explicitly; a `200` is not evidence of publication.
- **Quiz / upsell plumbing** — collections that exist to power a site widget, not to be shopped.
  They look like lanes and are not.

Also watch for **title/slug mismatch**: a slug like `gifts-under-500` can display as "Gifts $300
and Up". **Trust the slug for routing, quote the title for display.**

## Step 3 — Build the lane map

One row per intent the company's shoppers actually express, derived from collection titles, the
storefront nav and the brand doc. Typical dimensions: best/popular · broad browse · entry price ·
the key differentiating feature and its absence · use context · gift (plus price bands) · adjacent
categories · sale · bundles · subscription. Record slug **and** id, plus one line on when it wins.

## Step 4 — Build the suppression list

Two layers, because either alone leaks:

1. **Collection-level** — every slug from the Suppress bucket.
2. **Title-level** — a word list that disqualifies a candidate whatever collection it came from.
   Derive it from the actual suppressed titles. Generic starting set: `part · parts · spare ·
   replacement · adapter · insert · hose · filter · valve · lid · cap · plate · bumper · knob ·
   remote · leg · kit · installation · assembly · service · sample · gift card · warranty`.

**A word that is junk at one company is a flagship at another** — "kit" may be the hero bundle.
Test the list against the real product list and record deliberate exceptions in the profile.

**Enforce it server-side in the tool dispatcher, not only in the prompt.** Policy in the prompt is
a suggestion; policy in the dispatcher is a rule, and it protects both answer paths.

## Step 5 — Pin the best-seller (do not trust collection order)

"What's your best one?" is the most common opening question, and the obvious implementation is
wrong.

**A "best sellers" collection is frequently returned in descending product id — newest first — not
by popularity.** Taking position 1 answers "most popular" with the most recently added product.
Verify the ordering before trusting it: pull the lane and compare its order against any independent
popularity signal on the storefront.

So the profile carries an explicit **`best_seller_slug`**, pinned, **with its evidence** — the
storefront's own "best-selling" label, a review count that dwarfs the next nearest, an
order-volume report. One line to change when it changes.

Also record the **superlative map**: which product answers *popular*, *cheapest*, and *premium*.
Ambiguity resolves toward the cheaper reading — a bare "best" means best **seller**, because an
expensive cart nobody meant is far worse than a cheap one they can trade up from.

## Step 6 — Product ladder

Price-ordered, one row per genuine hero, with the slot it fills (entry / mid / flagship / premium /
add-on). This is the tie-break order and the answer to "cheapest way in?".

Record prices as **reference figures with a capture date**, and state that runtime must re-read
them live. The ladder's job is ordering, not quoting.

**Watch for auto-generated slugs.** A product can carry a UUID-suffixed slug from an import. Never
reconstruct a URL from a title — always copy the canonical URL from the response.

**Watch for name prefixes.** Where one product's name is a prefix of another ("Cloud" / "Cloud+"),
record it: resolution must use whole-token equality or the pricier product wins by accident.

## Step 7 — Decision facts

Most catalogues have 1–3 facts that decide which product a customer needs (size, shape, clearance,
power availability, model compatibility, plan tier). Find them in the top products' descriptions
and any compatibility page. Record them as the questions to ask **before** recommending. This
single item removes most wrong recommendations.

## Step 8 — Claims, content, caveats

- **Publishable claims** the assistant may quote, each with its source. Never a claim you can't
  point at. Note explicitly where a number is a **count, not a rating**.
- **Policy/support page slugs**, and **which pages return an empty body** — imported catalogues are
  full of `200`-with-no-content pages, and runtime must treat empty as not-found.
- **A policy area with no page at all** is a caveat worth flagging loudly: those questions can only
  be handed to a human, because improvising legal copy is forbidden.
- **Countries/currencies where products have no active price** — these produce a $0 cart that looks
  normal.
- Out-of-stock staples, duplicate/draft collections you suppressed, and the re-profile trigger.

---

## Template

`company-profile-template.md` in this directory is the file to fill in. It ships with a
NOT-YET-GENERATED banner; the implementation should refuse to boot while that banner is present,
because an assistant with no profile has no name, no voice and no suppression list — it will
recommend spare parts and invent a personality. A loud failure beats a plausible one.
