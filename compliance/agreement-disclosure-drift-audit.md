---
name: Agreement & disclosure drift audit
description: Cross-check every legal agreement against the countries you actually operate in, and flag missing, inactive, or orphaned agreements.
icon: file-warning
---

# Goal

Confirm `{{company.name}}` has an active, correctly-scoped agreement for every country it actually sells in as of `{{today}}` — and flag any agreement drift before it becomes a compliance gap.

# Steps

1. Call `fluid_api("/api/settings/company_countries?limit=100", "GET")`, paginating until exhausted, to get the countries the company has actually opened (not the global country reference list) — keep `country.iso`, `country.name`, `id` (the `company_country_id`).
2. Call `fluid_api("/api/agreements?limit=100", "GET")`, paginating until exhausted. Keep `active`, `company_country_ids`, `description`/title, `created_at`, `updated_at`.
3. For every open country from step 1, check whether at least one **active** agreement lists its `company_country_id` in `company_country_ids`. Flag any open country with zero active agreements as a **coverage gap**.
4. Flag drift in the agreement set itself:
   - **Inactive but referenced** — an agreement with `active: false` that's still the only one covering a given country (the gap is worse than it looks — there's a record, but it's off).
   - **Orphaned** — an agreement whose `company_country_ids` don't match any currently-open country (the company stopped selling there, or the agreement predates a country closure) — not urgent, but worth a cleanup pass.
   - **Stale** — an active agreement whose `updated_at` is more than 18 months old, which is worth a fresh legal review even without a specific trigger.
5. Render three sections: **Coverage gaps** (open countries with no active agreement — most urgent), **Inactive/orphaned agreements** (cleanup list), **Stale agreements** (review-due list). Each row names the country and, where relevant, the agreement id/title.
6. End with a **Decision**: the single country posing the most legal exposure (open for selling, zero active agreement) and, if none, the oldest stale agreement worth a refresh first.
7. If every open country has current, active coverage, say so plainly — don't manufacture a finding to fill the report.
