# Platform handoff

Verify current platform documentation immediately before implementation. Capabilities, supported currencies, price tiers, fees, and APIs can change.

## General handoff

Produce a reviewable manifest containing:

- product or price identifier;
- market or storefront;
- control local price;
- proposed local price;
- eligible cohort;
- experiment allocation;
- start and stop conditions;
- rollback value;
- approval owner.

Do not include secrets or production credentials.

## Billing platforms

- Prefer a dry-run export or request plan before any API write.
- Separate automatic currency presentation from country-specific price overrides.
- Verify tax behavior, rounding, checkout currency, coupons, invoices, and webhooks.
- Do not replace or archive a price that existing subscriptions still reference.

## App stores

- Resolve proposed prices to currently available territory price points.
- Treat subscriptions, one-time purchases, and existing subscriber pricing separately.
- Review tax and proceeds rather than comparing storefront price alone.

## Fluid pricing sections

- Inspect the exact theme and reuse its typography, spacing, buttons, and section conventions.
- Put `{{ section.fluid_attributes }}` exactly once on the outermost section root.
- Scope CSS, IDs, DOM queries, and behavior to `section.id`.
- Make country, currency, price, cadence, plan copy, and CTA editable.
- Render essential price and CTA content in HTML.
- Keep internal scenario charts, assumptions, and projected revenue out of customer-facing markup.
- Validate add, select, edit, duplicate, reorder, remove, and two-instance isolation locally.

Never start a watcher, upload assets, or publish a theme unless the user explicitly requests it.

## Read-only Fluid store audit

Store inspection and implementation are separate phases. During the audit:

- use only the Product API list/detail `GET` operations or a saved export;
- prefer a scoped `products:read` connection;
- copy catalog images into the local report;
- produce recommendation and experiment manifests, not update requests;
- do not invoke product or variant create, update, archive, duplicate, or delete operations.

Only enter an implementation phase after the user separately approves exact
products, countries, prices, cohorts, and rollback values.
