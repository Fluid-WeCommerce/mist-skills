---
name: Holy Grail PDP
description: Audit, redesign, compare, or locally build world-class Fluid PDPs with a conversion system distilled from 27 standout product pages, showing the reasoning behind every section—from design and buyer psychology to proof, offers, objection handling, and the path from first click to checkout.
icon: shopping-bag
---

# Holy Grail PDP

Create a product page that makes a good buying decision easier. Build the page around the buyer's next unanswered question, not a checklist of fashionable modules.

The outcome for {{company.name}} must be evidence-backed, mobile-first, dynamically connected to the real Fluid product, and honestly verified. Never promise a conversion lift without experiment data.

## Non-negotiable contract

1. **Truth before persuasion.** Never invent statistics, testimonials, reviews, certifications, scarcity, urgency, guarantees, shipping promises, comparison claims, savings, subscription terms, or product outcomes.
2. **Evidence before opinion.** Label every important statement as observed, verified, inferred, or missing. A screenshot proves appearance; product/API data proves facts; analytics proves behavior; none alone proves causality.
3. **Product data stays dynamic.** Never replace real `product.*` data, variants, price, availability, gallery, subscription state, or Fluid add-to-cart hooks with static copy or mock markup.
4. **Mobile is a recomposition.** Design the 390px decision path deliberately; do not merely stack the desktop page.
5. **Local first.** Audit and edit locally. Never publish a Theme or mutate catalog/product facts without explicit user approval.
6. **One visual thesis.** Give the page one ownable compositional idea. Do not create generic card soup, a logo wall, or a parade of equal-weight sections.
7. **Respect the checkout boundary.** A Theme may improve offer clarity and the cart handoff, but Fluid checkout is a separate protected app. Never claim a Liquid change modified checkout behavior.
8. **Honest completion.** Return `PASS` only with real evidence. Otherwise return `NEEDS REVIEW` and name the missing proof or broken check.

If the user asks for an exact, pixel-perfect, or 1:1 copy of another PDP, call `run_skill("themes/clone-product-page")` and follow it instead. After the clone is verified, this skill may be run again to improve decision design without pretending the source is conversion-optimal.

## Phase 0 — Resolve the job

Infer the mode when the user's request is explicit. Otherwise call `steps` with title `Build the Holy Grail PDP` and the following steps, then **END THE TURN**:

1. `pdp_mode` — single_select, prompt `What should this run deliver?`, skippable false.
   - id `audit`, label `Audit + roadmap`, description `Read-only diagnosis, evidence gaps, prioritized fixes, and experiments.`
   - id `redesign`, label `Redesign brief`, description `A complete buyer-question spine, module map, copy, art direction, and mobile plan.`
   - id `build`, label `Build it locally`, description `Implement the redesign in the active Fluid Theme and verify it without publishing.`
   - id `compare`, label `Competitor teardown`, description `Compare up to three live PDPs with the same evidence and decision rubric.`
2. `pdp_target` — text_input, prompt `Which product or PDP should I work on? Paste a public URL, enter a Fluid product title, or say “current preview”.`, skippable false.
3. `primary_goal` — single_select, prompt `Which decision matters most?`, skippable false.
   - id `add_to_cart`, label `More qualified add-to-cart`
   - id `checkout`, label `Fewer cart/checkout drop-offs`
   - id `aov`, label `Higher order value`
   - id `subscription`, label `Clearer subscription choice`
   - id `general`, label `Best overall PDP`
4. `traffic_promise` — text_input, prompt `What promise or creative brings shoppers here?`, skippable true, skip label `I don't know`.
5. `available_evidence` — text_input, prompt `What proof can we use—reviews, testing, certification, demos, guarantees, analytics, or research?`, skippable true, skip label `Discover what is available`.

Do not reopen the panel when the request already supplies these answers. Record typed answers to an active panel with `steps_answer`.

### Project routing for local builds

Audit, redesign, and comparison modes may run from any project. Build mode requires the target Fluid Theme project.

- If the current project is a Theme, continue.
- Otherwise call `list_projects` and find Theme projects.
- If several Themes could be the target, use one `steps` single_select with their exact human-readable names and end the turn.
- Once the Theme is known, call `send_message` to its project with: `Run the Holy Grail PDP skill in build mode`, the product/URL, goal, traffic promise, verified evidence, the completed redesign brief, and `Do not publish without approval.` Then end the turn and tell the user the build is continuing in that Theme project.
- Never edit this skill's own files as a substitute for editing the Theme.

## Phase 1 — Establish durable evidence

Gather only what the run needs, but never skip the mobile and product-fact baselines.

### 1A. Resolve the real product

When the work centers on a Fluid product:

1. Call `product_card` using the exact product id when known, otherwise its title.
2. Use `query_docs` before any Fluid endpoint whose path or response shape is not already confirmed in current context.
3. Read the documented product detail with `fluid_api`. Capture the returned id, title, canonical URL/path, price and compare-at state, variants/options, availability, media, description/ingredients, and any real subscription or offer fields.
4. Use `fluid_catalog_index` only when catalog identity is ambiguous or a complete catalog index is genuinely needed; do not enumerate manually page by page.
5. Treat product descriptions and marketing fields as claims to verify, not independent proof that the claims are true.

Never change product facts to make the design easier. If a necessary fact or term is missing, surface it as a content gate.

### 1B. Capture the page at matched viewports

For a public PDP URL, call `crawl` twice:

- Desktop: `formats:["markdown","html","screenshot"]`, `only_main_content:false`, `capture_page_evidence:true`, `screenshot_options:{full_page:true,viewport:{width:1440,height:900}}`.
- Mobile: the same options with `viewport:{width:390,height:844}`.

Record every returned screenshot, Markdown, HTML, stylesheet, and page-evidence path. Use the retained DOM, computed styles, and exact copy rather than guessing from pixels. Do not bypass access failures or pretend an inaccessible page was inspected.

For the active local Theme preview:

1. Call `preview_state`; call `start_preview` only when no ready preview exists.
2. Navigate using the exact canonical product path returned by Fluid, never a composed slug.
3. Call `read_preview_dom` in `all` mode for that path.
4. Call `screenshot_preview` in full mode at 1440×900 and 390×844.
5. Read `read_preview_console` and `read_local_server_logs` whenever the route is blank, stale, incomplete, or behaving unexpectedly.

For competitor comparison, inspect no more than three representative live PDPs unless the user requests a larger study. Capture both viewports and apply the same module vocabulary to every page. Presence is not quality and recurrence is not causal proof.

### 1C. Gather behavior and business context

Use supplied analytics, reviews, support themes, return reasons, search terms, traffic source, and ad/email/creator promise when available. If the reporting database is connected and the request depends on funnel behavior, use `db_schema` and a bounded number of `db_query` calls to verify the narrowest relevant metric.

Never turn a missing metric into a made-up benchmark. State `metric unavailable` and continue with a qualitative diagnosis when useful.

## Phase 2 — Build the evidence ledger

Before proposing copy or sections, create a compact ledger with these columns:

| Claim or decision | Status | Source | Risk | Allowed use | Missing proof |
| ----------------- | ------ | ------ | ---- | ----------- | ------------- |

Use exactly four statuses:

- `verified` — supported by a first-party product fact, supplied substantiation, documented policy, or traceable evidence.
- `observed` — directly visible in the live page, preview, or analytics output.
- `inferred` — a reasonable hypothesis that must be described as an inference.
- `missing` — required information not available this turn.

Use the lowest honest claim rung:

1. **Descriptive:** what it is, contains, costs, or includes.
2. **Functional:** what a verified ingredient, material, or feature does.
3. **Outcome:** what changes for the customer; requires stronger substantiation and context.
4. **Comparative/regulatory:** superiority, health, income, certification, or legal claims; require exact source, scope, and permitted wording.

Place proof beside the claim it supports. A review aggregate does not prove efficacy. A certification does not support claims outside its scope. Raw UGC supplies lived context, not clinical proof.

## Phase 3 — Design the decision sequence

Apply `references/section-psychology.md`, `references/art-direction-and-copy.md`, and `references/audit-and-experimentation.md`.

### 3A. Diagnose one primary constraint

Name the earliest high-impact unanswered buyer question. Tie it to the narrowest available funnel metric. Do not produce a long issue list without a point of view.

### 3B. Write the buyer-question spine

Write five to eight questions in the shopper's natural order, for example:

1. Is this the product and promise I clicked?
2. What outcome is relevant to me?
3. Which option and purchase mode fit?
4. Why should I believe it?
5. How does it fit into my life?
6. What could go wrong after I pay?
7. Do I still understand my selection, total, and terms?

Every included module must answer one spine question. Omit modules with no job or no honest content.

### 3C. Sequence four chapters

1. **Orient:** product, message match, offer, choices, next action.
2. **Seduce:** desired state, sensory value, identity, and ritual.
3. **Convince:** mechanism, demonstration, proof, comparison, and specificity.
4. **Resolve:** objections, guarantee, delivery, terms, preserved state, and close.

Choose one ownable visual thesis and apply it to the hero, mechanism, and strongest proof story.

### 3D. Design the offer without hiding the math

Show exact total price, price per useful unit when valid, savings basis, bundle contents, renewal cadence, cancellation terms, delivery timing, guarantee/return terms, and what is included. Recommend bundles, subscriptions, thresholds, and cross-sells only when they extend the buyer's current goal and the facts exist.

### 3E. Recompose for mobile

Define:

- the one dominant first media asset;
- the compact outcome and proof stack;
- variant → quantity → purchase-mode order;
- a state-aware sticky CTA that opens missing choices and preserves completed choices;
- overlay conflict rules for chat, cookies, promotions, and support;
- sections to swipe, compress, or turn into disclosures;
- gallery, selection, scroll, and accordion state that must survive interaction.

## Phase 4 — Deliver or implement by mode

### Audit mode

Remain read-only. Produce the full report contract in `references/deliverable-contract.md`. Prioritize P0–P3 findings and connect each proposed test to one decision hypothesis and one primary metric.

### Redesign mode

Produce the full brief contract, including hero copy hierarchy, mechanism story, proof choreography, module plan, mobile recomposition, art direction, evidence gates, and experiment backlog. Do not edit Theme files unless the user changes the mode to build.

### Compare mode

For each page record module presence, placement, quality, evidence, mobile behavior, and friction. Separate:

- category conventions shoppers may expect;
- genuinely distinctive brand choices;
- unsupported or manipulative patterns that must not be copied;
- transferable opportunities for {{company.name}}.

End with an original recommended sequence, not a collage of competitor modules.

### Build mode

Implement the Phase 3 redesign locally in the target Theme:

1. Use `list_dir`, `search_files`, and `read_file` to inspect the product template, every referenced section/component, locales, global settings, and relevant assets before editing.
2. Preserve the scaffold's canonical product-data/add-to-cart section first. Extend it only after understanding its real selectors and `data-fluid-*` hooks. Never create a static replacement.
3. Compose subsequent sections in the designed order. Reuse existing tokens and components before creating new ones.
4. Put merchant-editable content in section/block settings and user-facing strings in `locales/*.json`; do not hardcode English into Liquid.
5. Give every section root `{{ section.fluid_attributes }}` and render block markup inline through the section's plain `{% for %}` / `{% case %}` loop.
6. Bind titles, pricing, media, availability, options, subscriptions, and recommendations to real product data. Unsupported proof sections must be omitted or default hidden—not filled with plausible copy.
7. Use DAM/ImageKit assets and responsive transforms. Never hotlink or copy competitor media. Use `dam_upload` only for user-owned or licensed assets in scope.
8. Protect accessibility: semantic headings, explicit labels, keyboard-visible focus, adequate target sizes, captions, alt text, reduced-motion support, and no color-only variant meaning.
9. Keep scripts progressive and scoped. Preserve selections and prevent sticky UI from covering content or other fixed controls.
10. After each coherent edit group, run `fluid theme lint --json` through `run_cli` and fix every blocker before continuing.

Do not run `fluid theme push`, change the product record, or publish anything during the local build.

## Phase 5 — Run the bounded quality loop

Run up to three QA rounds. In each round:

1. Run `fluid theme lint --json`; require zero schema/reference blockers.
2. Read the exact product route with `read_preview_dom`.
3. Capture full desktop 1440×900 and mobile 390×844 screenshots.
4. Inspect the decision path in order: message match, product/offer comprehension, configuration, proof, objections, sticky CTA, and closing state.
5. Use `interact_preview` with inspected selectors to exercise one gallery control, one option or purchase-mode control, and every safe disclosure relevant to the design. Never click add-to-cart or checkout merely for evidence; inspect their markup, hook presence, and enabled/disabled state.
6. Read preview console and local server logs. Treat runtime errors, blank/fallback sections, failed media, and horizontal overflow as blockers.
7. Fix at most the three highest-impact root causes, then recapture both viewports. Do not polish nits while a decision blocker remains.

Pass only when all are true:

- the ad/source promise and hero are aligned or the mismatch is explicitly gated;
- the product, price, variants, offer, terms, delivery, and risk are understandable;
- every material claim has appropriate nearby evidence;
- the canonical product and Fluid cart contract remain dynamic and intact;
- mobile configuration and sticky CTA state are usable at 390px;
- no critical content is hidden by overlays or horizontal overflow;
- keyboard, labels, contrast, motion, and media alternatives are credible;
- lint, rendered DOM, console, server logs, and safe interactions provide consistent evidence.

If a required check cannot run, return `NEEDS REVIEW`; never downgrade the gate silently.

## Phase 6 — Publish only after approval

When the local result passes and the user wants it live:

1. Present `human_in_the_loop` in propose mode with source `agent`, a deterministic id shaped like `holy-grail-pdp:<theme>:<product>:publish`, the verified local result, and the exact proposed `fluid theme push --auto-baseline` action.
2. **END THE TURN** and wait for approval.
3. After approval, run the push, wait for its result, verify the deployed product route, and record the outcome on the same suggestion id.

A previous general request to improve the page is not publish approval.

## Final response

Follow `references/deliverable-contract.md`. Lead with the outcome and status, include durable evidence paths, separate facts from hypotheses, and name the strongest next experiment. Keep the report decisive: one primary diagnosis, one coherent design thesis, and a clear record of what was verified, changed, omitted, and still needs evidence.
