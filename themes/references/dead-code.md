# Dead code — unused blocks, components, sections, assets

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- What to check
- Sections — unused
- Components — unused
- Block types — declared but never rendered
- Assets — unused
- Output format for removal recommendations
- When dead-code findings turn into fixes


A theme accumulates dead code faster than almost any other codebase: schemas evolve, blocks get renamed, components get inlined, CSS files outlive their consumers. Every dead artifact is **download weight, cognitive load, and a maintenance trap** (someone will eventually edit the dead one wondering why their changes don't show up).

The reviewer's posture: **suggest removal, default to `should`, never delete from a PR without explicit approval.** Most "unused" detections have a small false-positive rate (dynamic strings, future-use), so the recommendation is always "consider removing" with the audit command attached.

### What to check

There are four categories. Each has the same recipe: enumerate what's defined, enumerate what's referenced, take the set difference.

| Category        | Defined                                                | Referenced via                                                                  | Severity                          |
| --------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- | --------------------------------- |
| **Sections**    | `sections/{name}/index.liquid`                         | `{% section 'name' %}` in any `.liquid`                                         | `should`                          |
| **Components**  | `components/{name}/index.liquid`                       | `{% render 'name' %}` / `{% include 'name' %}`                                  | `should`                          |
| **Block types** | `{% schema %}` `blocks: [{ "type": "X", ... }]` arrays | `{% case block.type %}` / `{% if block.type == 'X' %}` in the same section file | `should`                          |
| **Assets**      | files in `assets/` (flat)                              | `{{ 'name' \| asset_url }}` in any `.liquid`                                    | `nit` to flag, `should` to remove |

### Sections — unused

A section file with no `{% section 'name' %}` consumer is dormant. Either it's been deprecated and forgotten, or it was never wired into any page template.

```bash
# From the theme repo root
for d in sections/*/; do
  name=$(basename "$d")
  count=$(grep -rE "\\{%\\s*section\\s+['\"]${name}['\"]" sections/ components/ layouts/ */default/ 2>/dev/null | wc -l)
  [ "$count" -eq 0 ] && echo "UNUSED  $d"
done
```

**False-positive guard:** some sections are added dynamically by users through the editor — these don't appear in any `{% section %}` literal but are still live. Before recommending removal, check `config/sections/*.json` (per-section metadata) — if metadata exists, the section is registered with the editor and probably in use. Drop the severity to `nit` and frame it as "appears unused in templates — confirm before removing".

### Components — unused

A component partial that nothing renders is dead weight. Lower false-positive rate than sections (no editor-driven instantiation).

```bash
for d in components/*/; do
  name=$(basename "$d")
  count=$(grep -rE "\\{%\\s*(render|include)\\s+['\"]${name}['\"]" sections/ components/ layouts/ */default/ 2>/dev/null | wc -l)
  [ "$count" -eq 0 ] && echo "UNUSED  $d"
done
```

**Watch for dynamic render:** `{% render snippet_name %}` where `snippet_name` is a variable. Grep for the literal first; if zero hits, also grep for the bare name as a string anywhere:

```bash
grep -rE "['\"]${name}['\"]" sections/ components/ layouts/ */default/ 2>/dev/null | grep -v "components/${name}/"
```

If that's also zero, it's safe to recommend removal.

### Block types — declared but never rendered

The most insidious form of dead code: a section's `{% schema %}` declares a block type, the editor exposes it to users, users add it, and the template renders **nothing** because the `{% case block.type %}` switch has no matching `when`.

Inside each section file:

```liquid
{% schema %}
{
  "blocks": [
    { "type": "page_header",  "name": "Page Header" },
    { "type": "product_grid", "name": "Product Grid" },
    { "type": "cta_banner",   "name": "CTA Banner" }   ← declared
  ]
}
{% endschema %}

{% for block in section.blocks %}
  {% case block.type %}
    {% when 'page_header' %}  ...
    {% when 'product_grid' %} ...
    {%- comment -%} cta_banner has no `when` branch — silently rendered as nothing {%- endcomment -%}
  {% endcase %}
{% endfor %}
```

**`should`** when the schema declares a block type that the template never handles. **`blocker`** if users have already populated this block in production (visible as orphan data in `settings_data.json` / per-section metadata) — they're staring at an empty section right now.

Quick audit per section:

```bash
for f in sections/*/index.liquid; do
  # block types declared in schema (very rough — schema is JSON inside Liquid)
  declared=$(awk '/{% schema %}/,/{% endschema %}/' "$f" | grep -oE '"type":\s*"[^"]+"' | grep -v '"type": *"[a-z_]+"$' | sed 's/.*"type":\s*"\([^"]*\)".*/\1/' | sort -u)
  # block types referenced in template
  referenced=$(grep -oE "block\.type\s*==\s*['\"][^'\"]+['\"]|when\s+['\"][^'\"]+['\"]" "$f" | grep -oE "['\"][^'\"]+['\"]" | tr -d '"'"'" | sort -u)
  for d in $declared; do
    echo "$referenced" | grep -qx "$d" || echo "UNHANDLED  $f  block type: $d"
  done
done
```

(The above is a heuristic — verify each hit manually before recommending. Block schema lives inside JSON-in-Liquid, which is hard to parse with shell tools.)

### Assets — unused

Files in `assets/` that no Liquid reference. Lowest severity because removal is cheapest and risk lowest.

```bash
for f in assets/*; do
  name=$(basename "$f")
  count=$(grep -rE "['\"]${name}['\"]" --include='*.liquid' --include='*.css' . 2>/dev/null | wc -l)
  echo "$count $name"
done | sort -n | awk '$1 == 0 { print "UNUSED  " $2 }'
```

**False positives to filter:**

- Asset referenced via concatenation: `{% assign css = section.id | append: '.css' %}` — rare, but real.
- Asset referenced from another asset: a CSS file `@import`'ing another CSS file in `assets/`. Re-grep `assets/` itself before recommending removal:
  ```bash
  grep -rl "$name" assets/
  ```

### Output format for removal recommendations

Always frame as "consider removing" with the audit command. Never propose deletion without leaving the human a way to verify:

````
[should] `components/old_card/index.liquid` appears unused

Audit:

```bash
grep -rE "\{%\s*(render|include)\s+['\"]old_card['\"]" sections/ components/ layouts/ */default/ 2>/dev/null
# 0 results
````

If the grep stays at 0 after this PR, consider removing the file. If it's
referenced dynamically (variable name into `render`), keep it and add a
comment at the top noting that.

````

### When dead-code findings turn into fixes

If the user says `open the fix PR`:

1. **Remove sections, components, and assets** in separate commits, one per artifact, so reverting any one is a one-commit revert.
2. **For block types**, the fix is to either:
   - Add the missing `when` branch in the template (preferred — the block was meant to render something), or
   - Remove the declaration from the `{% schema %}` `blocks:` array (only if confirmed no users have populated it).
3. **Run `fluid theme lint --json` after each removal** — the validator catches `{% section 'name' %}` references that became dangling.
4. **Never bulk-delete** across categories in one commit. Each removal is its own decision.

---
