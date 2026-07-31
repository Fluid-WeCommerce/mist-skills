---
name: Suggested Changes
description: Review Lighthouse performance and compliance findings for this store, then approve or dismiss each recommended fix — approvals are applied and their impact is tracked.
icon: sparkles
category: themes
---

<!--
  In-repo source for the Suggested Changes skill (apps/mist-desktop).
  PUBLISH: this file ships with the app repo for review/versioning, but
  Mist Desktop loads skills from (a) the Fluid-WeCommerce/mist-skills
  community repo (mirrored into <userData>/community-skills/) or
  (b) the user's local skills dir. To use it before it lands upstream,
  copy this folder to ~/Fluid/skills/suggested-changes/SKILL.md.
-->

# Goal

Surface the highest-impact suggested changes for {{company.name}}'s storefront from Fluid's monitoring agents (Lighthouse speed scans and FTC/FDA compliance scans), get an explicit human decision on each via the `human_in_the_loop` tool, apply what's approved, and record the before/after outcome.

# Hard rules

1. **Every suggestion goes through `human_in_the_loop`.** Never apply a change the user hasn't approved through the card. Never re-ask about a suggestion the tool reports as already approved or dismissed — the tool consults the local decision store for you; trust its answer and move on.
2. **Stable suggestion ids.** Always pass a deterministic `suggestion_id` built from the source facts so re-detection maps to the same record:
   - Lighthouse: `lighthouse:<resource_type>:<resource_id>:<opportunity_id>` (e.g. `lighthouse:product:9474:render-blocking-resources`)
   - Compliance: `compliance:<resource_type>:<resource_id>:issue-<issue_id>` (e.g. `compliance:product:9474:issue-812`)
3. **Small batches.** Present at most 3 suggestion cards per turn, then END your turn and wait. The user's Approve/Dismiss clicks come back as user messages ("Approved: …" / "Dismissed: …").
4. **Record outcomes.** After performing an approved change, call `human_in_the_loop` again with `mode: "record_outcome"`, the same `suggestion_id`, and the new score / state when you have them.

# Steps

## 1. Gather scan results via `fluid_api`

Start with active products (expand to media / posts / collections if the user asks):

- `GET /api/v2025-06/products?per_page=25` — list products; skip archived ones.
- For each product id:
  - `GET /api/v202506/products/{id}/lighthouse` — latest Lighthouse scan. The response `item` carries `core_metrics.performance_score` (0-100), `category_scores`, and `optimization_opportunities[]` (`id`, `title`, `description`, `savings_ms`, `savings_bytes`).
  - `GET /api/v202506/products/{id}/compliance` — latest compliance scan. The response `item` carries `score` (0-10), `status` (poor/fair/good/excellent), `summary`, and `compliance_issues[]` (`id`, `issue_text`, `issue_type`, `severity`, `recommendation`).
- If either endpoint answers `"No … scan exists. Scan has been triggered automatically."`, a scan is now pending server-side — note the resource and tell the user to re-run this skill later for it. Don't poll.

The same sub-resources exist for `media/{id}`, `playlists/{id}`, `categories/{id}`, `collections/{id}`, `posts/{id}`, and `enrollment_packs/{id}` under `/api/v202506/`.

## 2. Build and rank suggestions

- One suggestion per compliance issue and per Lighthouse optimization opportunity.
- Rank: compliance `critical` > `high` severity first, then Lighthouse opportunities by `savings_ms` (largest first), then remaining compliance issues.
- Keep only suggestions you can actually act on (copy changes via `fluid_api` PATCH, theme/code edits via file tools when the project is a theme, image compression via `compress_media` + `dam_upload`, …). For things you can't automate, still present the card but say so in `proposed_action` ("I'll draft the corrected copy for you to paste") — the decision is still worth recording.

## 3. Present via `human_in_the_loop`

For each suggestion (top 3 first):

```
human_in_the_loop({
  suggestion_id: "compliance:product:9474:issue-812",
  source: "compliance",
  title: "Remove medical claim from Neuro product description",
  description: "\"supports brain healing\" is flagged high-severity (Medical). Summary: <scan summary>.",
  current_score: 6.5,
  proposed_action: "PATCH the product description to \"may support cognitive wellness\" per the scan's recommendation.",
  before_payload: { score: 6.5, status: "fair", issue_text: "…" },
  metadata: { resource_type: "product", resource_id: 9474, issue_id: 812, severity: "high" }
})
```

- If the tool returns a card payload: the user is looking at Approve/Dismiss buttons. Present your batch, summarize briefly, END YOUR TURN.
- If the tool returns "already APPROVED/DISMISSED": do not show it again. If it notes a score change on an approved item, mention it to the user as a one-line follow-up ("Lighthouse for Neuro went 62 → 81 since you approved the script fix") — no new approval prompt.

## 4. Act on decisions

- On `Approved: …` — perform exactly the `proposed_action`. **First determine WHERE the change lives — the resource or its template:**
  - **Resource data** — structured fields like price, title, description, images, SKUs, variants — lives on the resource itself. Change it with `fluid_api` (PATCH the resource; mutations are recorded in the Time Machine automatically).
  - **Template content** — marketing copy, headlines, claims language, layout, scripts, styling — lives on that resource's TEMPLATE (the theme/template that renders it), not the resource record. Inspect the resource's template (e.g. its `application_theme_template` reference / the theme's template files) and make the change there with the file tools or the template's API, not by PATCHing the resource.
  - When a finding could be either (e.g. a compliance issue quoting text that appears in both the description field and the template copy), check BOTH, fix where the offending content actually is, and say which one you changed.
- Then fetch the freshest score if cheap (`GET …/lighthouse` or `…/compliance`) and call `human_in_the_loop` with `mode: "record_outcome"`, `after_score`, and an `after_payload` snapshot. Note: fresh scans take time server-side — if the score hasn't updated yet, record the state payload now; the next run of this skill auto-captures the new score on re-detection.
- On `Dismissed: …` — skip it forever (the store enforces this) and continue with remaining suggestions.

## 5. Wrap up

When the batch is exhausted, summarize: how many suggestions were presented / approved / dismissed / applied, and any before → after score movements so far.
