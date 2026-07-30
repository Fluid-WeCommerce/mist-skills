---
name: launch-setup
description: >-
  Start an onboarding run. Streamlined launches always collect scope, source
  website, theme target, and confirmation in chat before they start. Speed
  launches keep the lightweight website-only path.
---

# Launch Setup

The front door for onboarding a company onto Fluid. Collect the launch inputs,
start the right run, and get out of the way.

This skill has two ways to resolve the workflow:

- **Conversation** — ask whether they want Quality or Speed. If they do not
  choose, use Quality.
- **Run button** — the request itself names a workflow, e.g.
  `Run the "Streamlined Onboard & Launch" workflow (slug:
  streamlined-onboard-launch).` The slug is the mode choice. Do not ask
  Quality versus Speed again.

The resolved modes are:

> **Quality** — builds the whole store: theme with every page, products,
> collections and content, business profile, media and UGC, then a storefront
> walkthrough. Theme built by Fable 5. Roughly an hour.
>
> **Speed** — storefront only: brand, products, home, shop, product page,
> publish. Theme built by Grok 4.5. No content import, no media, no QA pass.
> Roughly twenty minutes, and leaves real work outstanding.

`streamlined-onboard-launch` is Quality. `speed-import` is Speed. Never call
either workflow without an explicitly supplied `website_url`.

## Quality — collect the Streamlined launch scope

Use this path for **every** request resolved to
`streamlined-onboard-launch`, including its direct workflow Run button.

### 1. Discover the active target

Make these two reads before opening the picker:

1. `GET /api/settings/company` to identify the active Fluid company.
2. `GET /api/application_themes?per_page=100` exactly once. Retain only each
   theme's `id` and `name`. If a theme has an id but no usable name, label it
   `Theme #<id>`.

If the active company cannot be identified, stop and explain that a company
must be selected before onboarding can start. If the theme-list read fails,
stop and report that the theme choices could not be loaded. Do not offer a
guessed list, silently default to a theme, or call `run_workflow`.

### 2. Show the required picker

Call `steps` with title `Onboard <company name>` and the four steps below.
Then end the turn and wait for the answers.

1. `run_scope` — `single_select` with `skippable: false`, "What should this
   run do?"
   - `full` — **Full onboarding (recommended):** brand and business data,
     theme, products and content, media and UGC, storefront check, and handoff.
   - `data_theme` — **Data + theme (no products):** brand and business data,
     theme, storefront check, and handoff.
   - `theme_only` — **Theme only:** brand data, theme, storefront check, and
     handoff; no product import or business-data push.
   - `data_only` — **Data onboarding only:** brand and business data plus
     handoff; no theme or products.
2. `website_url` — `text_input` with `skippable: false`, "What URL should we
   pull the store from?" Always show this step. If the triggering request
   supplied an http(s) URL, use its canonical origin as the input's
   `placeholder`; otherwise use the active company's website URL when it is a
   valid http(s) URL, or an empty placeholder when it is not. A placeholder is
   only a hint: require the user to enter an explicit answer. Validate that the
   answer is an http(s) URL. If it is invalid, open a new one-field `steps`
   panel for `website_url` with `skippable: false`, end the turn, and wait for
   a valid answer. (`steps_answer` only mirrors a valid chat-typed answer into
   a panel that is still active; it does not re-open a completed invalid
   input.)
3. `theme_target` — `single_select` with `skippable: false`, "Build a new theme
   or use an existing one?" Add
   `show_if: { step_id: "run_scope", any_of: ["full", "data_theme",
   "theme_only"] }`.
   - First option: id `new`, label `Create a new theme (recommended)`,
     description "Scaffold an isolated theme for this launch."
   - Then add one option per discovered theme: id
     `existing_<theme_id>`, label `Use: <theme name or Theme #id>`,
     description "Build and publish this exact existing theme."
4. `confirm` — `single_select` with `skippable: false`, "Ready to start this
   onboarding run?"
   - `go` — `Yes, launch it`
   - `cancel` — `Not yet`

Do not add product-source or separate media/UGC questions. Streamlined imports
products and content from the confirmed website when `run_scope` is `full`;
media and UGC are also part of `full`.

### 3. Start the Streamlined run

Only continue when `confirm` is `go`. If it is `cancel`, acknowledge the
cancellation in one line and stop without calling `run_workflow`.

Derive the theme fields from the picker:

- `new` → `theme_target: "new"`, `theme_id: null`
- `existing_<theme_id>` → `theme_target: "existing"`,
  `theme_id: <the exact discovered theme id>`
- theme step hidden for `data_only` → `theme_target: null`, `theme_id: null`

Reject an existing-theme answer that does not match the list loaded for this
picker. Never infer a theme from what is active or available locally.

Derive the track flags from `run_scope`:

| Scope | `build_theme` | `import_products` | `push_business_data` | `import_media_and_ugc` |
| --- | --- | --- | --- | --- |
| `full` | `true` | `true` | `true` | `true` |
| `data_theme` | `true` | `false` | `true` | `false` |
| `theme_only` | `true` | `false` | `false` | `false` |
| `data_only` | `false` | `false` | `true` | `false` |

Call `run_workflow` with every field shown here. The raw `run_scope` and all
four booleans are required even though the workflow also derives them:

```jsonc
{
  "workflow_slug": "streamlined-onboard-launch",
  "run_title": "Launch drinkolipop.com",
  "context": {
    "website_url": "https://drinkolipop.com",
    "setup_mode": "quality",
    "run_scope": "full",
    "theme_target": "new",
    "theme_id": null,
    "source_provenance": "first-party migration: the operator supplied this URL through onboarding as their own site, being moved onto their own Fluid tenant",
    "build_theme": true,
    "import_products": true,
    "push_business_data": true,
    "import_media_and_ugc": true,
  },
}
```

Canonicalize `website_url`: keep the http(s) origin, remove tracking
parameters, and omit a trailing path unless the storefront genuinely lives
there. Use that canonical value in both `run_title` and context.

## Speed — keep the lightweight path

For a request resolved to `speed-import`, preserve the existing behavior:

1. Confirm the active company with `GET /api/settings/company` and tell the
   user which company will be changed.
2. Take an http(s) website URL from the request, or ask for it if missing.
3. Call `run_workflow` with slug `speed-import`, a searchable
   `Launch <domain>` title, and context containing the canonical
   `website_url` plus `setup_mode: "speed"`.

Do not show the Streamlined scope/theme picker for Speed and do not add
Streamlined track flags to its context.

## Hand over

`run_workflow` returns immediately and the live progress card renders in this
chat. Confirm in one or two lines:

- which mode started, and what that means they will and will not get
- that the run continues if a step comes back rough — nothing in either
  workflow stops the run, so a weak page becomes a note in the final handoff
  rather than a dead run

Then stop. Do not poll `workflow_status` or narrate steps as they pass. Use
`workflow_status` only when the user asks.

## What each mode actually costs

Worth knowing before you recommend one.

**Full Quality** runs 15 steps over 6 waves. Three source-reading steps open
together, the theme starts building in the second wave, and the product,
business-profile, and media tracks run beside it. Fable 5 on the theme.

**Speed** runs 9 steps over 5 waves on Grok 4.5 throughout, and skips the
onboarding form, collections and content import, media and UGC, and the
storefront walkthrough. Its handoff names what it skipped — read that section
before telling anyone the company is ready.

Neither mode accepts a model override: workflow steps carry fixed models, and
`run_workflow` has no model argument.
