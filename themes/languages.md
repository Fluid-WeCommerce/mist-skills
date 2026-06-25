---
name: translating-theme-languages
description: |
  Translate a Fluid Liquid theme into every language the company has enabled. Use when the
  user wants to localize a theme, translate copy, fill in missing translations, add a new
  language, or sync `locales/*.json` with the company's enabled languages. The skill (1) reads
  the company's enabled languages from the Fluid API, (2) asks whether to translate a single
  template or the whole site, (3) asks whether to re-translate everything or only fill missing
  keys, (4) adds a `locales/{iso}.json` for any enabled language that's missing one, and (5)
  translates the strings like an international e-commerce professional — idiomatic, on-brand,
  and conversion-aware, never word-for-word machine output. Source of truth is `locales/en.json`
  and the `{{ 'key' | t }}` filter; the skill edits locale files in place and never writes to
  the live theme or store API without explicit approval.
---

# Translating Theme Languages (Fluid)

This skill localizes a Fluid theme. Fluid themes resolve user-facing copy through the
translation filter — `{{ 'cart.checkout' | t }}` — backed by one JSON file per language under
`locales/`. `locales/en.json` is the **source of truth**; every other `locales/{iso}.json`
mirrors its key structure with translated values. This skill keeps those files complete and
correct for **exactly the languages the company has turned on**, and writes translations a
professional localizer would ship — not raw machine output.

**It edits `locales/*.json` in place** (every change is reversible). It **never** runs
`fluid theme push` or any store write without explicit approval.

## How translations work in a Fluid theme

| Piece | What it is |
|---|---|
| `locales/en.json` | Source locale. Keys → English strings. Defines the canonical key set. |
| `locales/{iso}.json` | One file per language (`es`, `de`, `fr`, `fil`, …). Same keys, translated values. |
| `{{ 'key.path' | t }}` | The Liquid filter that resolves a dotted key against the active locale, falling back to `en`. |
| `{{ 'key' | t: count: n, name: x }}` | Interpolation — placeholders are passed as filter args and referenced as `%{name}` in the value. |
| `<html lang="{{ request.locale.iso_code }}">` | The active locale, set per request. |

Locale files are **nested JSON**, dotted in Liquid:

```json
{
  "cart": {
    "title": "Your cart",
    "checkout": "Checkout",
    "item_count": { "one": "%{count} item", "other": "%{count} items" }
  }
}
```

→ `{{ 'cart.checkout' | t }}` and `{{ 'cart.item_count' | t: count: 3 }}`.

**ISO codes** are 2–3 letters (`en`, `es`, `de`, `pt`, `fil`). The filename is the ISO code:
`locales/es.json`. Match whatever casing/extension the existing files use.

---

## The five steps

Run these in order. Steps 2 and 3 are **questions to the user** — ask them, don't assume.

### 1. Find the company's enabled languages

Translations are only worth shipping for languages the store actually serves. Read them from
the Fluid API (same credentials as the `fluid-admin` skill — ask the user for the Fluid URL and
API token if you don't have them):

```bash
curl -s "${FLUID_URL}/api/settings/languages" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

This returns the languages enabled on the company. Extract each language's **ISO code** and
name. That set — minus the source locale (`en`) — is the list of `locales/*.json` files the
theme **should** have.

Then diff against disk:

```bash
ls locales/
```

Report three buckets before doing anything:

- **Enabled + file exists** → candidates for translation (step 3 decides scope).
- **Enabled + file missing** → will be created in step 4.
- **File exists + not enabled** → mention it, but **don't delete** it. The company may be
  mid-rollout. Just flag it: "`locales/it.json` exists but Italian isn't enabled — leave it,
  remove it, or enable Italian?"

If the API can't be reached (no token, offline), say so and offer to proceed from the locale
files already on disk, treating each existing `locales/*.json` as an enabled language.

### 2. Ask: one template, or the whole site?

> **Translate the whole site, or a specific template/section?**

- **Whole site** → the full key set in `locales/en.json` is in scope.
- **Specific template** → scope to the keys that template actually uses. Grep the file(s) for
  translation calls and translate only those keys:

  ```bash
  # keys used by one template (and anything it renders)
  grep -rhoE "'[a-z0-9_.]+'\s*\|\s*t\b" product/default/index.liquid sections/ components/ \
    | grep -oE "'[a-z0-9_.]+'" | tr -d "'" | sort -u
  ```

  Keep the question concrete — list the page types / sections you found so the user can pick
  ("`product`, `cart_page`, `home_page`, or all of them?").

### 3. Ask: re-translate everything, or only what's missing?

> **Re-translate every string, or only fill in missing translations?**

- **Missing only (default, safe)** → for each in-scope language, translate only keys that are
  absent from that `locales/{iso}.json` (or present but empty). Leaves human-reviewed
  translations untouched. This is the right choice for an established store.
- **Re-translate everything** → overwrite every in-scope key in every in-scope language.
  Use when the brand voice changed, the existing translations are poor, or the copy was
  bulk-imported by a machine. **Confirm** before overwriting existing non-empty values —
  this discards prior work.

Combine with step 2: the scope is *(templates from step 2) × (languages from step 1)*, and
step 3 decides whether existing values inside that scope are overwritten or preserved.

### 4. Add missing company languages to the schema

For every enabled language with no file, create `locales/{iso}.json` mirroring **the exact key
structure of `locales/en.json`** — same nesting, same keys, same pluralization shape — then
fill the values per step 5. Don't invent keys that aren't in the source, and don't drop keys
the source has. A new locale file is complete only when its key set equals `en.json`'s.

After creating/updating files, the key sets must line up. Quick check per language:

```bash
# keys present in en but missing from es (should be empty when done, unless intentionally scoped)
comm -23 \
  <(jq -r 'paths(scalars) | join(".")' locales/en.json | sort) \
  <(jq -r 'paths(scalars) | join(".")' locales/es.json | sort)
```

### 5. Translate like an international commerce professional

This is the part that separates a real localization from a `Google-Translate` dump. Translate
**meaning and intent**, tuned for an online store in that market.

- **Localize, don't transliterate.** Render the *intent*. "Add to cart" → German
  "In den Warenkorb", not a literal "Zu Karte hinzufügen". Use each market's standard
  e-commerce vocabulary (cart/basket/bag, checkout, shipping, returns).
- **Match register and brand voice.** Carry the source tone — playful stays playful, premium
  stays premium. Pick the right formality for the market (e.g. German *Sie* vs *du*, French
  *vous* vs *tu*; default to the polite form for commerce unless the brand is deliberately
  casual) and stay consistent across the whole file.
- **Respect placeholders exactly.** `%{count}`, `%{name}`, `%{price}` must survive verbatim and
  read naturally in the translated word order. Never translate, reorder away, or drop a token.
- **Handle plurals per language.** Keep the `one`/`other` shape where the source has it, and add
  the forms the *target* language needs — many languages have more than two
  (e.g. Polish `one`/`few`/`many`/`other`, Arabic up to six). Don't collapse them to one string.
- **Keep UI strings tight.** Buttons and labels have limited space. Prefer the concise native
  term over a long literal phrase so the layout doesn't break.
- **Preserve non-translatables.** Brand/product names, SKUs, units, currency/number/date
  formats per locale, HTML in `richtext`-shaped strings, and Liquid/placeholder syntax.
- **Be consistent.** The same source term gets the same translation everywhere in the file
  (one glossary per language). Don't render "Wishlist" three different ways.
- **Flag, don't guess.** If a string is ambiguous without context (a bare "Free", "Order"),
  note it for the user rather than picking a meaning at random.

Write valid JSON: UTF-8, real accented characters (`Ã¼`, `Ã©`, `Ã±` — not escapes), double quotes,
no trailing commas, no comments.

---

## Operating rules

1. **Languages come from the API, not from guessing.** Step 1 defines the target set. Don't
   translate into a language the company hasn't enabled (beyond flagging an orphan file).
2. **Ask scope (step 2) and mode (step 3) before translating.** They change what gets written.
3. **"Missing only" never overwrites existing non-empty values.** "Re-translate everything"
   does — and only after explicit confirmation.
4. **Mirror `en.json` exactly.** Every locale file has the same key set as the source. No extra
   keys, no missing keys, same plural shape.
5. **Never delete an orphan locale file** (exists on disk, not enabled) without asking.
6. **Edit locale files in place; never push.** No `fluid theme push`, no store write
   (e.g. `POST /api/settings/languages` to enable a language) without explicit approval.
7. **Validate JSON after every file.** `jq . locales/{iso}.json` must parse clean.

---

## Workflow output

1. **Report the language audit** from step 1 (enabled+present, enabled+missing, orphan files).
2. **Ask the two questions** (scope, then mode). Wait for answers.
3. **Do the work**: create missing files, translate in scope, one language at a time.
4. **Per language, summarize**: keys added, keys re-translated, keys left untouched, and any
   strings flagged as ambiguous.
5. **Validate**: every touched `locales/*.json` parses (`jq .`) and its key set matches
   `en.json` (`comm` check above).
6. **Offer next steps**: "Files are updated locally and validated. Want me to enable a missing
   language via the API, or push the theme? (both need your go-ahead.)"

## Quick checklist

- [ ] Pulled enabled languages from `GET /api/settings/languages`
- [ ] Audited enabled vs. on-disk locale files; flagged orphans (didn't delete)
- [ ] Asked: whole site or specific template? Scoped the key set accordingly
- [ ] Asked: re-translate all or fill missing only? Confirmed before any overwrite
- [ ] Created `locales/{iso}.json` for every enabled-but-missing language
- [ ] Every locale file mirrors `en.json`'s key set exactly (`comm` check clean)
- [ ] Placeholders (`%{...}`) preserved; plural forms correct for each language
- [ ] Brand voice, register, and e-commerce vocabulary appropriate per market
- [ ] All files valid UTF-8 JSON (`jq .` clean)
- [ ] No `fluid theme push` / no store write without explicit approval
