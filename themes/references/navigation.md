# Navigation — link_list menus

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- Bad — hardcoded nav
- Good — one `link_list` setting
- Findings to surface
- When to keep nav items singular


Any series of `<a>` tags that represents a navigation (header nav, footer columns, mobile drawer, breadcrumbs, social links) belongs in a `link_list` setting — **the engine's menu selector**. Hardcoding nav items locks the company into a code change for every new link.

`link_list` is one of the canonical setting types (a single-resource picker). It points at a _menu_ the company configures in admin; the theme reads it as an iterable of menu items.

### Bad — hardcoded nav

```liquid
<nav class="main-nav">
  <a href="/shop">Shop</a>
  <a href="/about">About</a>
  <a href="/blog">Blog</a>
  <a href="/contact">Contact</a>
</nav>
```

Or this — better, but still wrong: company-level text/URL settings paired into "nav items":

```json
{
  "settings": [
    { "type": "text", "id": "nav_label_1", "label": "Item 1 label" },
    { "type": "url", "id": "nav_url_1", "label": "Item 1 link" },
    { "type": "text", "id": "nav_label_2", "label": "Item 2 label" },
    { "type": "url", "id": "nav_url_2", "label": "Item 2 link" }
  ]
}
```

### Good — one `link_list` setting

```json
{
  "settings": [
    {
      "type": "link_list",
      "id": "menu",
      "label": "Menu",
      "default": "main-menu"
    }
  ]
}
```

```liquid
{%- assign menu = section.settings.menu -%}
<nav class="main-nav" aria-label="Main navigation">
  {%- for link in menu.links -%}
    <a href="{{ link.url }}"
       class="main-nav__link {% if link.active %}is-active{% endif %}">
      {{ link.title | escape }}
    </a>
  {%- endfor -%}
</nav>
```

The company now picks an existing menu in admin (the editor surfaces all menus the store has configured), and adds/reorders/renames items without ever touching code. Multi-level dropdowns work via `link.links` (children).

### Findings to surface

| You see                                                                                                                       | Severity | Fix                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2+ hardcoded `<a href="/...">` tags that visually form a navigation (header, footer columns, mobile drawer, social row)       | `should` | Replace with a `link_list` setting and a `{% for link in menu.links %}` loop.                                                                      |
| Multiple parallel `text` + `url` settings used to fake a menu (`nav_label_1` / `nav_url_1`, `nav_label_2` / `nav_url_2`, ...) | `should` | Collapse to one `link_list`. Each menu item gains drag-reorder, depth, and active-state tracking.                                                  |
| Section that lists footer columns by hardcoding the same column twice                                                         | `should` | One block per column with a `link_list` inside the block. Users add/remove/rename columns.                                                         |
| Iterating `linklists` (the global) without exposing a `link_list` picker                                                      | `nit`    | Acceptable for "site-wide menu" cases, but giving the user a `link_list` setting is more flexible — the section can be reused for different menus. |
| Breadcrumbs, social-link rows, related-links rails — anything that's a list of `{ label, url }` pairs                         | `should` | All belong in a `link_list`. Don't reinvent.                                                                                                       |

### When to keep nav items singular

The `link_list` heuristic does not apply to:

- **Single CTAs** in marketing sections — these are real "hero button" / "secondary button" roles. A standalone `text` + `url` (or one `link_list` with `limit: 1` if you want consistency) is fine.
- **Brand logo links** — the logo's `href` is almost always "go home"; a fixed `/` is acceptable, or expose a single `url` setting.
- **Legal/footer links that are _required by policy_** (Terms, Privacy) and not the company's call to omit — but even these are usually better as a `link_list` so they can be reordered or extended.

---
