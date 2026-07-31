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

## Persona  (§A3–A4)
- **Name** (`ASSISTANT_NAME`):
- **Role**:
- **Pronouns**:
- **Vibe** (1–2 lines in the brand's register):
- **Signature move**:
- Chosen by (operator) on (date), from candidates:

## Voice
- Source: supplied `brand.md` / derived from storefront copy — **say which**
- On-brand phrasings:
- Banned phrasings:
- CTA verbs the brand actually uses:
- Extra copy bans beyond SKILL.md §1:

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

## Best seller  (Step 5)
- `best_seller_slug`:
- **Evidence** (why this and not collection position 1):
- Collection ordering actually observed:
- Superlative map — popular / cheapest / premium:
- Name-prefix collisions needing exact-token match:

## Product ladder  (Step 6)
| Product | Slot | Reference price (captured) | Slug | Notes |
|---|---|---|---|---|

## Decision facts  (Step 7)
The 1–3 questions to ask before recommending, and why each one decides it.

## Publishable claims  (Step 8)
| Claim the assistant may quote | Source |
|---|---|

Counts that are **not** ratings:

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
