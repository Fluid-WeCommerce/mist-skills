# Liquid correctness — the checks

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- 0. Unavailable / out-of-scope variables
- 1. Nil-safety and defaults
- 2. Whitespace control
- 3. Unclosed tags / mismatched conditionals
- 4. Filter ordering
- 5. `forloop.first` / `forloop.last` instead of index branching
- 6. `assign` inside a loop for a constant value


Mechanical. Cite line numbers.

### 0. Unavailable / out-of-scope variables

Liquid never raises on `{{ undefined_var }}` — it renders empty. The same is true for `{{ available.but.missing.field }}`. Together this means _typos and out-of-context drops are invisible at runtime._ The reviewer catches them.

The variables a template can read fall into three buckets:

| Bucket                       | Available in…                                           | Examples                                                                                                                   |
| ---------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Always available globals** | every template                                          | `request`, `cart`, `customer`, `shop`, `settings` (global), `linklists`                                                    |
| **Resource context**         | the matching page template, plus any section it renders | `product` (only on `product/{variant}/index.liquid` and sections rendered from it); `collection`, `category`, `post`, etc. |
| **Section / block scope**    | inside that section only                                | `section`, `section.settings`, `section.blocks`, `block`, `block.settings`                                                 |
| **Component args**           | inside a component only when explicitly passed          | only the keys passed to `{% render 'name', key: value %}`                                                                  |

Things that go wrong:

| You see                                                                                                                                      | Severity  | Why                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| `{{ product.title }}` inside a section that's rendered on the homepage (`home_page/default/index.liquid`) without an explicit `product:` arg | `blocker` | `product` is only in scope on product page templates. On `home_page` it's `nil`, silently rendering empty.                                                            |
| `{{ collection.products }}` inside `sections/main_navbar/index.liquid`                                                                       | `blocker` | `collection` is not in scope in a navbar section. Pass the resource explicitly via a block setting (`collection` type) and read `block.settings.collection.products`. |
| `{{ cart.item_count }}` in a component without `cart` passed as a `render` arg                                                               | `should`  | `cart` is global, so this often works, but if the component is intended to be self-contained, accept `cart:` explicitly.                                              |
| `{{ section.settings.thing }}` where the schema does not declare `thing`                                                                     | `blocker` | Typo or stale reference. Validator does not catch this — it only checks the schema, not the template. Grep the schema for the `id` and fix.                           |
| `{{ block.settings.thing }}` where the block's `settings:` array does not declare `thing`                                                    | `blocker` | Same as above for blocks.                                                                                                                                             |
| `{{ block.settings.x }}` inside a section that has `blocks` declared but NOT inside a `{% for block in section.blocks %}` loop               | `blocker` | `block` is only in scope inside the iteration; outside it's `nil`.                                                                                                    |
| Inside a component, reading `section.settings.*` (component receives no `section` arg)                                                       | `blocker` | Components are partials. They only see what's passed via `{% render %}`. The caller must pass `section: section` (rare) or the specific values needed.                |
| Inside a component, reading `block.settings.*` without `block:` passed as an arg                                                             | `blocker` | Same as above — components are not block-aware unless told.                                                                                                           |
| `{{ foo }}` where `foo` was `{% assign foo = ... %}`-ed inside an `{% if %}` branch but is read after the `{% endif %}` with no fallback     | `should`  | Liquid `assign` has file-level scope, but readers downstream may see `nil` if the branch didn't run. Either move the assign above the `if`, or add `                  | default: ...` at the read site. |
| `{{ for_loop_var }}` after a `{% endfor %}` (using the loop variable outside the loop)                                                       | `blocker` | Loop variables don't escape `{% endfor %}`. The reference renders empty.                                                                                              |
| `{{ forloop.first }}` outside a `{% for %}`                                                                                                  | `blocker` | Only valid inside a loop.                                                                                                                                             |

**Audit each file before approving:**

```bash
# Find references to settings keys that aren't declared in the same file's schema
awk '
  /{% schema %}/,/{% endschema %}/ { schema = schema "\n" $0; next }
  /(section|block)\.settings\.[a-zA-Z_][a-zA-Z0-9_]*/ {
    for (i = 1; i <= NF; i++) {
      if ($i ~ /(section|block)\.settings\.[a-zA-Z_][a-zA-Z0-9_]*/) {
        match($i, /(section|block)\.settings\.[a-zA-Z_][a-zA-Z0-9_]*/)
        ref = substr($i, RSTART, RLENGTH)
        gsub(/^(section|block)\.settings\./, "", ref)
        if (schema !~ "\"id\":[ ]*\"" ref "\"") print FILENAME ": unknown settings.'"'"'" ref "'"'"'"
      }
    }
  }
' sections/*/index.liquid
```

(Heuristic — multi-line settings refs and computed keys will produce false positives. Use it to surface candidates, then verify.)

**When in doubt, ask one question:** _"What scope is this template in, and was the variable passed into that scope?"_ If the answer is "nothing passed it", it's not available — replace with a settings read or a `render` arg.

### 1. Nil-safety and defaults

Liquid is forgiving. `nil.foo` does not raise — it renders empty. That's worse than an error, because the bug ships silently.

**`should`** when a `section.settings.*` or `block.settings.*` value is used without `default:` in schema AND without `| default:` in the template:

```liquid
{%- comment -%} Bad: empty <h2> if heading is blank {%- endcomment -%}
<h2>{{ section.settings.heading }}</h2>

{%- comment -%} Good {%- endcomment -%}
<h2>{{ section.settings.heading | default: 'Featured products' }}</h2>
```

**`blocker`** when a method-chain on a resource picker is unguarded and the page can render with a blank picker:

```liquid
{%- comment -%} Bad: `.first_variant.price` chain blows up if product is blank {%- endcomment -%}
<span>{{ section.settings.product.first_variant.price | money }}</span>

{%- comment -%} Good {%- endcomment -%}
{%- assign p = section.settings.product -%}
{%- if p != blank and p.first_variant != blank -%}
  <span>{{ p.first_variant.price | money }}</span>
{%- endif -%}
```

### 2. Whitespace control

Liquid keeps every whitespace character outside tags. In tight loops, this inflates HTML by KBs. **`should`** when a `for`/`if` block in markup context lacks `-`:

```liquid
{%- comment -%} Bad: 6 blank lines per category {%- endcomment -%}
{% for category in categories %}
  <li>
    {% render 'category_card', category: category %}
  </li>
{% endfor %}

{%- comment -%} Good {%- endcomment -%}
{%- for category in categories -%}
  <li>{%- render 'category_card', category: category -%}</li>
{%- endfor -%}
```

Rule of thumb: control tags (`{%- ... -%}`) get dashes; output tags (`{{ ... }}`) usually don't, except when adjacent to control tags.

### 3. Unclosed tags / mismatched conditionals

**`blocker`.** Liquid's parser is permissive — an unclosed `{% if %}` will consume the rest of the template silently. Quick count check:

```bash
grep -cE '{%-?\s*(if|for|case|capture|comment|unless)\b' file.liquid
grep -cE '{%-?\s*end(if|for|case|capture|comment|unless)\b' file.liquid
```

The two counts must match.

### 4. Filter ordering

Filters apply left-to-right. **`blocker`** when `escape` is applied before a sanitizer (re-escapes already-escaped entities) or after `truncate` (cuts in the middle of an entity, producing `&am`).

```liquid
{%- comment -%} Bad: truncate cuts inside &amp; {%- endcomment -%}
{{ user_content | escape | truncate: 50 }}

{%- comment -%} Good: truncate first, escape last {%- endcomment -%}
{{ user_content | truncate: 50 | escape }}
```

### 5. `forloop.first` / `forloop.last` instead of index branching

**`nit`** — but worth pointing out for performance + readability:

```liquid
{%- comment -%} Bad {%- endcomment -%}
{%- for item in items -%}
  {% if forloop.index == 1 %}<div class="first">{% endif %}
  ...
{%- endfor -%}

{%- comment -%} Good {%- endcomment -%}
{%- for item in items -%}
  {% if forloop.first %}<div class="first">{% endif %}
  ...
{%- endfor -%}
```

### 6. `assign` inside a loop for a constant value

**`should`.** Hoist invariants out:

```liquid
{%- comment -%} Bad: assigned every iteration {%- endcomment -%}
{%- for product in products -%}
  {%- assign card_class = 'card card--' | append: section.settings.style -%}
  <div class="{{ card_class }}">...</div>
{%- endfor -%}

{%- comment -%} Good {%- endcomment -%}
{%- assign card_class = 'card card--' | append: section.settings.style -%}
{%- for product in products -%}
  <div class="{{ card_class }}">...</div>
{%- endfor -%}
```

---
