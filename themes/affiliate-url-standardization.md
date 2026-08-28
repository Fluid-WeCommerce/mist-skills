---
name: Affiliate URL standardization
description: Rewrite every affiliate/storefront link in the active theme to the /{{username}}/ prefix — replacing affiliate_guid/share_guid outputs, hardcoded guid segments, and hardcoded "home" prefixes.
icon: link
---

# Goal

In the active theme project, standardize every affiliate/storefront URL so it is prefixed with `/{{username}}/`.

`{{username}}` is the platform's affiliate-hydration sentinel (see docs.fluid.app/themes/affiliate-hydration): the FairShare SDK replaces it with the resolved affiliate's username in `href`/`action`-style attributes, and anonymous visitors fall back to `home`. Any link that hardcodes a guid, a Liquid guid variable, or the literal `home` in that first path segment pins the link to one affiliate (or to no affiliate) and breaks attribution.

Target pattern for every affiliate storefront link, wherever it appears — schema settings (`url`, `button_url`, `footer_logo_url`, block/setting `default` values), `href="..."` inside schema `text`/HTML strings, or Liquid-built URLs:

```
/{{username}}/<rest-of-the-path>
```

# What to replace

1. **Liquid affiliate variables used as the URL prefix** — `{{ affiliate_guid }}`, `{{affiliate_guid}}`, `{{ share_guid }}`, `{{share_guid}}` → `{{username}}` (normalize spacing to exactly `{{username}}`).

2. **Hardcoded guid/ID segments used as the URL prefix** — a numeric or short-hex segment right after the leading slash, followed by a storefront path. Examples seen in real themes:
   - `/85e354/shop` → `/{{username}}/shop`
   - `/506/pages/enrollment-page` → `/{{username}}/pages/enrollment-page`
   - `/5c72f2/collection/shop-rose-cole` → `/{{username}}/collection/shop-rose-cole`
   - `/005d8d/products/somanight-2092` → `/{{username}}/products/somanight-2092`

   Storefront path segments that identify these links: `shop`, `products`, `product`, `collections`, `collection`, `pages`, `page`, `categories`, `category`, `posts`, `post`, `enrollments`, `join`, `cart`.

3. **Hardcoded `home` used as the URL prefix** — authors write `home` thinking it is the username value, but `home` is only the *anonymous fallback* the router resolves when no username is present; hardcoding it strips affiliate attribution from the link. Replace when `home` occupies the username slot of a storefront path:
   - `"url": "/home/enrollments/affiliate-enrollment"` → `"/{{username}}/enrollments/affiliate-enrollment"`
   - `href="/home/products/make-3-breakthrough"` → `href="/{{username}}/products/make-3-breakthrough"`
   - `href="/home"` (link to store home) → `href="/{{username}}"`
   - Liquid default-filter fallbacks: `{{ block.settings.url | default: '/home/enrollments/affiliate-enrollment' }}` → `| default: '/{{username}}/enrollments/affiliate-enrollment'` — fix these alongside the schema `default` value they mirror.

4. **Bare affiliate-identifier variables in Liquid logic that build these URLs** — use `username` instead:
   - `{% if affiliate_guid != blank %}` → `{% if username != blank %}`
   - `{% assign logo_link = company.home_page_url | append: affiliate_guid %}` → `... | append: username %}`

# Leave exactly as-is (do NOT change)

- **JS/SDK field names and property reads.** The parameter key `share_guid:` in `FairShareSDK.lookupAffiliate({ share_guid: ... })` and property access like `newAffiliateData.share_guid` are API contract names. Only a *value* becomes `"{{username}}"` when it is a Liquid output; the key/property name stays.
- **External/absolute URLs to any domain** (e.g. `https://makewellness.fluid.app/home/page/...`) — different routes, not affiliate storefront links, even when they contain `/home/`.
- **Liquid variable names that merely contain `home`** — `company.home_page_url`, `home_page`, etc. The `home` replacement applies only to literal URL path segments.
- **Asset/CDN paths, anchor links (`#...`), `mailto:`/`tel:` links**, and any URL that is not the affiliate storefront pattern.
- **Code comments describing URL shapes** (e.g. `// /<6-char-share_guid>/products/<slug>`) — documentation, not links.

# Process

1. **Search** the theme with `list_dir` + file search across `*.liquid` and `*.json`:
   - `affiliate_guid` and `share_guid` (all spacings)
   - guid-like prefixes: regex `["'(=]/([0-9]{2,6}|[0-9a-f]{4,8})/(shop|products?|collections?|pages?|categor(y|ies)|posts?|enrollments|join|cart)`
   - hardcoded home prefixes: regex `["'(=]/home(/|["')])`
2. **Apply the replacements** above with `edit_file`, one file at a time. Preserve surrounding formatting; change only the URL prefix or variable name.
3. **Verify**: re-run every search from step 1 and confirm zero remaining matches in URL positions. Report:
   - every file changed, with a count of replacements per class (variable / guid / home / logic),
   - every occurrence intentionally left, with the reason (SDK key, external domain, variable name, comment, asset path).
