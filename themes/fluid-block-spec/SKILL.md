---
name: fluid-block-spec
description: Build or review Fluid theme sections and blocks against the Fluid Builder Block & Section Specification v3 — canonical block types, setting IDs, labels, defaults and control order, shared control groups, section base, resource sections, rendering rules and the pre-ship checklist. Use when creating a new section or block, adding settings to one, or checking a theme's schemas for consistency.
icon: blocks
---

# Fluid Block & Section Spec

The full specification is attached as the reference `fluid-block-spec-v3.md`. It standardizes **which controls a block or section gets, their IDs, labels, defaults and order**. Use it as the source of truth for every new section and block.

## Precedence

1. **Platform behavior:** [docs.fluid.app/themes](https://docs.fluid.app/themes/overview) wins. If the spec and the docs disagree about platform behavior, follow the docs and flag the conflict to the user.
2. **The existing theme's conventions:** match its token names, class prefixes and rendering style. **Never rename a shipped setting ID or block type** — renaming disconnects saved content.
3. **The spec:** applies to every new section and block, and to any theme without a conflicting convention.

## Building a section or block

Follow spec §1 (Build Workflow) in order:

1. **Read the target theme first** — `config/settings_schema.json`, `layouts/theme.liquid`, and one modern section. Confirm the `background_colors`, `font_families` and `text_presets` option groups exist (§3) and note CSS token names and class prefixes.
2. **Classify the section** (§15): content section (uses blocks), resource section (zero blocks, §16), or layout container (§17).
3. **Pick block families** from the taxonomy (§6). Use canonical type names; map aliases to them. Never invent a synonym.
4. **Copy canonical schemas** from §7–§14 verbatim and apply the documented deltas for variants. Keep setting order exactly as written. Paste shared control groups (`CG-*`, §5) where referenced.
5. **Add the Section Base** (§15.1) after the section's content settings; Section Shell always last.
6. **Render per §18** — `{{ block.fluid_attributes }}` on every block, scoped `{% style %}`, palette values into CSS, `media_tag` for media, guards and `| default:` on every optional value.
7. **Responsive in CSS only** (§18.6). No mobile/tablet/desktop settings in any schema.
8. **Write a preset** with realistic content. Nothing may render blank.

Before handing off, run through the **Pre-Ship Checklist (§20)** and report each item as pass/fail. Check the work against the **Anti-Patterns (§19)**.

## Reviewing an existing theme

When asked to check a theme's schemas against the spec, report read-only findings as terse `file:line — issue — spec §` lines, grouped by file. Flag: non-canonical block types or setting IDs (suggest the canonical one, but note that shipped IDs must not be renamed), color/font/text-style settings not using the option groups, mobile/tablet settings, wrong control order, missing `block.fluid_attributes`, unguarded optional values, blocks in resource sections, and missing presets. Don't edit unless the user asks.

## Notes

- Appendix B lists reference implementations by path in the surveyed themes (Yoli, Make Wellness, Puralta, TM3, Oliabo). Those paths are from the author's machine; look for the same themes in the current workspace, and skip them if they aren't present.
- Appendix D lists open items (e.g. `plaintext` type, combined media picker). Check the Fluid docs before relying on anything listed there.
- Append `.md` to any docs.fluid.app URL for raw markdown; `https://docs.fluid.app/llms.txt` is the full index.
