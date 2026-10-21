# Language → Text Direction Map

Key text direction on the **language**, not the country. An Arabic storefront reads
right-to-left whether the market is Saudi Arabia, the UAE, or Egypt.

## Right-to-left (horizontal) — apply RTL treatment

| Language | ISO 639-1 / code | Primary markets |
|---|---|---|
| Arabic | `ar` | Saudi Arabia, UAE, Egypt, Qatar, Kuwait, Iraq, Jordan, Morocco, … |
| Hebrew | `he` (`iw`) | Israel |
| Persian / Farsi | `fa` | Iran |
| Urdu | `ur` | Pakistan, India |
| Pashto | `ps` | Afghanistan |
| Sindhi | `sd` | Pakistan |
| Uyghur | `ug` | — |
| Kurdish (Sorani) | `ckb` | Iraq, Iran |
| Yiddish | `yi` | — |

Any language **not** in this table → **left-to-right**. Default to LTR when unknown.

## Explicitly out of scope

- **Vertical / CJK top-to-bottom** (traditional Japanese `ja`, Chinese `zh`, Korean `ko`,
  Mongolian). These read **left-to-right horizontally on the modern web** — they are NOT RTL.
  Do not apply RTL treatment to them. True vertical typesetting (`writing-mode: vertical-rl`)
  is a separate, much larger effort and is not covered by this skill.

## Detection notes

- Normalize locale variants before lookup: strip region suffix (`ar-SA` → `ar`), and map
  legacy codes (`iw` → `he`, `jp` → `ja`).
- If a company supports multiple languages, direction is per **active locale**, not a single
  company-wide flag — an RTL company may still serve an English (LTR) page.
- The direction test in code is simply: `RTL_LANGS.include?(locale_language_code)`.
