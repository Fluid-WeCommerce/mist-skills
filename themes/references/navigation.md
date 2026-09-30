# Navigation — link_list menus

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Where menus are documented

How menus are created, how a `link_list` setting stores a menu's slug, and how Liquid reads the menu are documented in [Navigation menus](https://docs.fluid.app/themes/navigation-menus). Look it up there with `search_docs` or `query_docs`. This file keeps only the review checks.

The shape to check templates against: a `link_list` setting resolves to a menu with `menu_items`. Each item has `title`, `url`, and nested `sub_menu_items`. There is no `menu.links`, `link.links`, `link.active`, or global `linklists`, so any of those renders nothing.

```liquid
{%- for item in section.settings.menu.menu_items -%}
  <a href="{{ item.url }}">{{ item.title | escape }}</a>
{%- endfor -%}
```

## Findings to surface

| You see | Severity | Fix |
| --- | --- | --- |
| `menu.links`, `link.links`, `link.active`, or `linklists` | `blocker` | Use `menu_items`, `sub_menu_items`, `title`, and `url`. The menu renders empty otherwise. |
| 2+ hardcoded `<a href="/...">` tags that form a navigation (header, footer columns, mobile drawer, social row) | `should` | Replace them with a `link_list` setting and a loop over `menu_items`. |
| Parallel `text` + `url` settings faking a menu (`nav_label_1` / `nav_url_1`, ...) | `should` | Collapse them into one `link_list`, so items gain reordering and nesting in the admin. |
| Footer columns hardcoded one after another | `should` | One block per column, each with its own `link_list`. |
| Breadcrumbs, social-link rows, related-links rails: any list of `{ label, url }` pairs | `should` | Use a `link_list`. |
| A `link_list` `default` that doesn't match an existing menu's slug | `should` | Use a slug returned by the menus API. Don't derive it from the title. |

## When to keep nav items singular

The `link_list` check doesn't apply to:

- **Single CTAs** in marketing sections, such as a hero's primary and secondary buttons. A `text` + `url` pair is fine.
- **Brand logo links**, which almost always go home. A fixed `/` or one `url` setting is fine.
- **Policy links** (Terms, Privacy) that the company can't omit. Even these are usually better as a `link_list` so they can be reordered or extended.
