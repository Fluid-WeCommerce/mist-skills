# 04 — Routing

There is **no auto-assignment**. This step is required, per product, and it is the single most
common real-world fault.

## Assign

```
PATCH /api/company/v1/products/{productId}
{ "product": { "application_theme_template_id": <bundle template id> } }
```

A plain PATCH is sufficient and takes effect immediately (verified end to end). In the admin
Bundle Builder this is the required **"Select template"** field.

## Verify — on the PLAIN storefront URL

```
https://<company>.fluid.app/home/products/<slug>          # no ?preview=
```

Assert: our marker `data-bb-root` present; the previous implementation's markers
(`data-bundle-section`, `data-dbp-*`) absent; HTTP 200, not a 302 to /404.

Use `canonical_url` from the API response — never a URL composed from a slug you chose. The
create/update endpoints ignore a `slug` you send and generate one from the title.

## The trap that will bite later

`application_theme_template_id` is **not a column**. It is a `template_resources` join scoped
to the company's currently-active theme. So:

- **Switching or cloning a theme silently un-routes every bundle.** Cloning copies templates,
  not the join rows.
- `?preview=true&theme_template_id=<id>` works because it overrides the active-theme lookup —
  which is why preview is safe and proves nothing about live routing.

`bundle-manifest.json` records `{ themeId, templateId, productIds[] }` precisely so
re-routing after a theme change is one idempotent replay instead of an archaeology exercise.
Say this to the user out loud when handing over.

## Un-routing an old implementation

Archetype B companies often have the hand-authored picker injected directly into
`product/default`. Removing that injection is part of the job — otherwise every ordinary
product keeps paying for picker markup. Do it as a separate, reviewable change.
