---
name: Region readiness check — all active markets
description: Run a quick compliance pass across every country you're actually open in, ranked by risk, so nothing drifts out of compliance after launch.
icon: map-pinned
---

# Goal

Give `{{company.name}}` a fleet-wide compliance pulse-check across every country it's actually open in as of `{{today}}` — not a deep single-country audit (that's `countries/compliance-manager`), but a fast "is anything drifting" ranked sweep across all of them at once.

# Steps

1. Call `fluid_api("/api/settings/company_countries?limit=100", "GET")`, paginating until exhausted, to get every country the company has actually opened. Keep `country.iso`.
2. For each open country, call the `country_settings` tool with its ISO code. This returns the compliance rulebook: `mandatoryDisclosurePages`, `cookieRule`, `vatInclusiveDisplay`, `unitPriceRule`, `languageCode`, and a `covered` flag.
3. For each country, run a **fast** check (not the full deep audit): confirm the storefront's declared language coverage matches `languageCode` (check available locales), and confirm at least one active agreement exists scoped to that country (reuse the logic from `compliance/agreement-disclosure-drift-audit` if you've already run it this session — otherwise pull `fluid_api("/api/agreements?limit=100", "GET")` once and check all countries against it in one pass rather than one call per country).
4. Score each country **Green** (agreement present + language covered + `covered: true` from the atlas), **Yellow** (one gap), or **Red** (two or more gaps, or `covered: false` meaning Fluid has no atlas data and only generic essentials could be checked).
5. Render a single table: country, score, the specific gap(s) if not Green, and whether it was a full atlas match or generic-only (`covered: false`). Sort Red first, then Yellow, then Green.
6. End with a **Decision**: the single Red country most likely to draw regulatory attention (weight active sales volume if you have it from an orders filter by country, otherwise weight by number of gaps), and recommend running the full `countries/compliance-manager` skill on that one country next for the deep citation-backed audit.
7. Never invent a rule for a `covered: false` country — say plainly that Fluid's atlas doesn't cover it yet and only the generic essentials (privacy policy, terms, refund policy presence) were checked.
