# Company profile — NOT YET GENERATED

> **This is the unfilled template.** Run **Part A of `SKILL.md`** (§A1–A6) against the live company
> and write the result to `company-profile.md`. The implementation should **refuse to boot** while
> this banner is present: without a profile the assistant has no name, no voice, no lane map and no
> suppression list, so it will recommend spare parts and invent a personality.

Runtime rule once filled in: this file says **WHERE to look** and **HOW to speak**. Every price,
stock state, URL and account fact is still read live, every turn.

---

## Identity
- Company name:
- Storefront host / shop handle:
- Default country / currency · enabled languages:
- Account surfaces the customer can reach (and which are embeddable — see `platform-limits.md`):
- Category noun (the word shoppers use):
- Profile captured (ISO date):

## Persona  (§A4–A5)
- **Name** (`ASSISTANT_NAME`):
- **Pronouns**:
- **Role**:
- **Vibe** (1–2 lines in the brand's register):
- **Signature move**:

### Name history
The operator chooses the name (§A4) and renaming is customer-visible (§A4b) — read that section
before changing it. Append a row each time; never overwrite one.

| Name | Pronouns | Chosen by | Date | Candidates offered | Reason (for a rename) |
|---|---|---|---|---|---|

## Voice
- Source: supplied brand guide / derived from storefront copy — **say which**
- On-brand phrasings:
- CTA verbs the brand actually uses:
- **Off-brand vocabulary the guide rejects** (this becomes an outbound guard — word-boundary matched,
  because a brand coinage can contain a banned substring):
- The guide's own off-brand counter-example, if it has one:
- Extra copy bans beyond SKILL.md §2:

## Lane map  (Step 3)
| Shopper signal | Collection slug | id | When it wins |
|---|---|---|---|
| best / most popular | | | |
| broad browse | | | |
| entry price | | | |
| key feature | | | |
| gift (+ price bands) | | | |
| sale | | | |
| subscription | | | |

## Family collections
| Product line | slug | id |
|---|---|---|

## Never recommend  (Step 4)
- Collections: `slug` (id) …
- Title patterns: …
- Deliberate exceptions (words that look like junk but are real products here): …
- **Which lane lifts suppression** (see below) — everywhere else it stays on:

## Parts lane  (Step 5)
- Parts collection slug (id):
- Page cap for this lane (bigger than recommendations):
- **Part synonyms** — words customers use that appear in no product title (`handle → knob`, …):
- Parts that are **not** in the parts collection (the lane must keyword-search as well):
- Price band of the parts range:
- Diagnosis words deliberately NOT mapped to parts (symptoms go to a human):

## Bundles and configurable products  (Step 5b)
Which products the assistant may cart, and which it must send to their own page (SKILL.md §3.9).
- `filter[bundle]=true` returns (count, slugs):
- Collections whose NAME says "bundle" but whose products are ordinary (`is_bundle: false`):
- **Cartable** — fixed bundles, nothing to choose:
- **Configurable** — always open the page, never cart:
- Non-bundle products that still need customer input first (personalisation, gift-card amount,
  made-to-order):

## Best seller  (Step 6)
- `best_seller_slug`:
- **Evidence** (why this and not collection position 1):
- Collection ordering actually observed:
- Superlative map — popular / cheapest / premium:
- Name-prefix collisions needing exact-token match:

## Product ladder  (Step 7)
| Product | Slot | Reference price (captured) | Slug | Notes |
|---|---|---|---|---|

## Description coverage  (Step 8)
Can problem-matching work here? (`needs-and-safety.md`)
- Do hero products have real description prose?
- Do descriptions contain the words a **customer** would use for the problem solved?
- Rough share of the catalogue with usable description text:
- **Verdict: is the problem-matching lane switched on for this company?**

## Decision facts  (Step 9)
The 1–3 questions to ask before recommending, and why each one decides it.

## Publishable claims  (Step 10)
| Claim the assistant may quote | Source | Company-wide, or attachable to a product? |
|---|---|---|

Counts that are **not** ratings:

## Handoff topics
Subjects with no real page behind them, which therefore always go to a human rather than an invented
policy (returns, refunds, shipping times, warranty, …):

**If the catalogue is ingestible or applied to skin:** is there a published ingredient/allergen
statement per product? If not, allergens are a **mandatory** handoff topic — see
`needs-and-safety.md`.

## Content
- Policy / support page slugs (returns, shipping, warranty, compatibility, contact, about):
- Pages known to return empty bodies:
- **Policy areas with no page at all** (these can only go to a human):

## Caveats
- Markets/currencies with unpriced products (the $0-cart trap):
- Out-of-stock staples:
- Subscription discount actually configured? (may be zero)
- Duplicate / draft collections suppressed:
- Auto-generated or UUID-suffixed slugs:
- Re-profile trigger:
