---
name: Brand Setup
description: >-
  Interview the company to build a living brand.md — a brand-voice document
  that Mist, themes, portals, and widgets read to match the company's tone and
  style. Prefills colors/name from brand guidelines and saves via the
  update_brand_voice tool. Also use to append a single brand decision later.
icon: palette
---

# Brand Setup

Build (or extend) `{{company.name}}`'s **brand.md** — a prose document describing how the
company sounds, who it's for, and what "on-brand" looks like. Mist, themes, portals, and
widgets all read this to generate copy and make style choices that feel like the company
wrote them.

This is the **voice and style** layer. Structured brand data — logo, color swatches, fonts —
lives in the brand guidelines settings, not here. brand.md describes how those are *used*, in
prose.

The active Fluid company is already selected in Mist. All Fluid API calls go through
`fluid_api(path, method, body)` (token injected). Save with the **`update_brand_voice`** tool —
it writes the local per-company brand.md, adds `(— {{user.name}})` attribution, and syncs
`brand_md` to the settings endpoint. Never ask for credentials.

## Step 0 — Load current state (don't make the user repeat themselves)

1. **brand.md** — Mist injects the current brand.md into this turn's context as a
   `<brand_voice>` block. Read it. If it has real content, this is an **addition** run
   (jump to "Appending a later decision"). If it's empty or just the blank template, this is
   a **first setup** — run the interview.
2. **Brand guidelines** — `fluid_api("/api/settings/brand_guidelines", "GET")` to prefill the
   brand name and colors (`name`, `color` = primary, `secondary_color`, `logo_url`). Use these
   so you never ask "what's your primary color?" when it's already on file — instead confirm
   how it's *used*.

Skip any interview question you can already answer from these two sources.

## Step 1 — Interview (first setup only)

Ask in **small batches of 2-4 questions**, in plain language, each with a short example so the
user knows the shape of a good answer. After each batch, reflect back what you heard in a
sentence before moving on. Do not dump all questions at once.

**Batch 1 — Overview & mission**
- In a sentence or two, who are you and what do you sell?
- What's the "why" — the mission or belief that drives decisions?
- The 3-5 values that guide how you operate (e.g. "sustainability over speed").

**Batch 2 — Tone of voice**
- If your brand were a person talking to a customer, how would they sound? 2-3 adjectives
  (e.g. "warm, direct, a little playful — never corporate").
- Paste or link a piece of copy (email, product description, post) that feels exactly right.
- Anything that reads as *off-brand*? (too formal, too silly, too salesy)

**Batch 3 — Audience**
- Primary customer: age range, lifestyle, what they care about.
- Any secondary audience worth calling out (gift buyers, resellers, B2B)?

**Batch 4 — Vocabulary & naming**
- Words/phrases you always use — product names, category terms, signature phrases.
- Words/phrases to avoid — competitor terms, jargon, anything that reads wrong.
- Capitalization or naming conventions (e.g. always "drops," never "releases").

**Batch 5 — Visual style** (prefilled from brand guidelines — confirm, don't re-ask)
- "I see your primary color is `<color>` and secondary `<secondary_color>`. How are they
  used — bold accents, or mostly neutral with a pop?" (If nothing's on file, ask them to
  describe the palette in words.)
- Typography feel: modern/geometric, classic/serif, handwritten/friendly, technical/mono?
- Imagery: photography vs. illustration, bright vs. moody, people- vs. product-forward?
- Roundedness: soft rounded corners/shapes, or sharp/angular?

**Batch 6 — Inspiration & guardrails**
- Brands or sites you admire — for their voice, their look, or both? What specifically?
- Hard do's and don'ts (e.g. "always mention the guarantee," "never use exclamation points,"
  "never disparage competitors by name").

If the user is in a hurry, offer to draft with what you have and leave the template's comment
prompts in place for the rest.

## Step 2 — Assemble brand.md

Use this **exact** skeleton — headings must match verbatim (same words, casing, order) so
future automated edits target the right section. This is the same template Mist ships when
`brand_md` is empty.

```markdown
# Brand Guide

_A living document. Sections are prompts — fill in what's true for your brand and
delete what isn't. Agents (Mist, themes, portals, widgets) read this to match
your voice and style._

## Brand Overview
<!-- One paragraph: who you are, what you sell, what you stand for. -->

## Mission & Values
<!-- Why you exist; the 3-5 values that guide decisions. -->

## Tone of Voice
<!-- How you sound. e.g. "Warm, direct, a little playful. Never corporate." -->

## Audience
<!-- Who you're speaking to. Primary + secondary personas. -->

## Vocabulary & Naming
<!-- Words you use / avoid. Product naming conventions. Capitalization rules. -->

## Visual Style
<!-- Color usage, typography feel, imagery style, spacing/roundedness. -->

## Do's and Don'ts
<!-- Concrete guardrails. "Do X." "Never Y." -->

## Brands & Sites We Admire
<!-- Links + one line on what you like about each. -->

## Examples
<!-- Snippets of on-brand copy, taglines, product descriptions. -->
```

Fill each section from the matching batch: Brand Overview + Mission & Values ← batch 1,
Tone of Voice ← batch 2, Audience ← batch 3, Vocabulary & Naming ← batch 4, Visual Style ←
batch 5, Do's and Don'ts + Brands & Sites We Admire ← batch 6, Examples ← the sample copy
from batch 2 plus anything else volunteered.

Write in the user's own words — this is their voice, not a generic fill-in. If a section has
nothing yet, leave its HTML comment prompt in place as a placeholder rather than inventing
content. In Visual Style, describe how the colors are *used*; don't just re-list hex codes.

## Step 3 — Save (first setup)

Call the **`update_brand_voice`** tool with `mode: "replace"` and the full assembled document
as `content`. The tool writes the local company brand.md and syncs `brand_md` to
`/api/settings/brand_guidelines`. If the sync degrades (endpoint not yet deployed), it keeps
the local copy — mention that to the user rather than blocking.

Then summarize what was captured, list any sections left as placeholders, and remind the user:

- Colors, logo, and fonts are structured brand-guidelines fields (managed in Fluid settings /
  the theme), not in brand.md — brand.md is the prose/voice layer that complements them.
- Future brand decisions can be captured incrementally — just tell Mist and it will append
  them with attribution (see below), no need to rewrite the whole doc.

## Appending a later decision (addition run)

When brand.md already exists and the user just made a single brand decision mid-conversation
("never say 'cheap' — use 'accessible'", "we're going more playful now"):

- **Do not re-interview or regenerate the document.** Draft a short paragraph or bullet for the
  one relevant section only.
- Call `update_brand_voice` with `mode: "append"` and just that new snippet as `content`
  (pass the target `section` if the tool signature accepts it). The tool appends it under the
  right heading, adds the `(— {{user.name}})` attribution, and syncs.
- Confirm what you added and where.

Example snippet to append under **Vocabulary & Naming**:

```markdown
Always "members," never "customers." Avoid "cheap" — use "accessible" instead.
```

(The tool adds the `_(— {{user.name}})_` attribution; don't write it yourself.)

## Rules

- Ask in small batches; skip anything already known from the `<brand_voice>` block or brand
  guidelines. Never make the user repeat themselves.
- Headings in the assembled doc must match the template verbatim.
- First setup → `mode: "replace"`. A single later decision → `mode: "append"`, one section only.
- Let `update_brand_voice` own attribution and API sync — don't PATCH `brand_md` by hand.
- brand.md is prose/voice; colors, logo, and fonts stay in the structured brand-guidelines /
  theme fields.
