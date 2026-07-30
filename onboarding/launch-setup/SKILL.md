---
name: launch-setup
description: >-
  Start an onboard. Quality launches collect the source website, theme target,
  and confirmation in an in-chat picker before they start; speed launches keep
  the lightweight website-only path. Also the launcher the onboarding
  workflows' Run button starts, so a catalog run never begins without a
  website URL. Quality builds the theme with Fable 5 and covers the whole
  store; speed builds it with Grok 4.5 and covers the storefront only.
---

# Launch Setup

The front door for onboarding a company onto Fluid. Collect the launch inputs,
start the right run, get out of the way.

This skill has two entry points, and the difference decides what you ask:

- **Conversation** — someone asked to onboard/launch a company. Ask whether
  they want Quality or Speed. If they do not choose, use Quality.
- **Run button** — the request itself names a workflow, e.g.
  `Run the "Streamlined Onboard & Launch" workflow (slug:
  streamlined-onboard-launch).` That IS the mode choice
  (`streamlined-onboard-launch` = quality, `speed-import` = speed). Do not
  re-ask quality vs speed.

When asking Quality vs Speed in conversation, give the trade in one line each:

> **Quality** — builds the whole store: theme with every page, products,
> collections and content, business profile, media and UGC, then a storefront
> walkthrough. Theme built by Fable 5. Roughly an hour.
>
> **Speed** — storefront only: brand, products, home, shop, product page,
> publish. Theme built by Grok 4.5. No content import, no media, no QA pass.
> Roughly twenty minutes, and leaves real work outstanding.

Either way: **never call `run_workflow` without `website_url` in context.**
Every step of both workflows reads it; a run started without it blocks on its
very first step ("Set up the brand") with nothing written.

## Quality — collect the launch inputs in a picker

Use this path for **every** request resolved to
`streamlined-onboard-launch`, including its direct workflow Run button.

### 1. Discover the active target

Discovery is **at most two tool calls**, then the picker opens immediately:

1. `GET /api/company/v1/companies/me` to identify the active Fluid company —
   starting a run against the wrong company wastes an hour before anyone
   notices. If the active company cannot be identified, stop and explain that
   a company must be selected before onboarding can start.
2. `GET /api/application_themes?per_page=100` exactly once. Retain only each
   theme's `id` and `name`. If a valid id is visible but its name is absent
   because the response was truncated behind large stylesheet fields, label it
   `Theme #<id>` and continue. If the read fails or no theme entries are
   readable at all, offer only "create new" in the picker and note there that
   existing themes couldn't be listed.

Do not probe `db_schema`, `list_projects`, `run_cli`, or alternate API paths
to recover theme names. Discovery errors are picker metadata gaps, not a
reason to wander through unrelated tools, skip the picker, or keep the user
waiting. Never present a guessed theme list.

### 2. Show the picker

Call `steps` with title `Onboard <company name>` and the three steps below.
Then end the turn and wait for the answers.

1. `website_url` — `text_input` with `skippable: false`, "What URL should we
   pull the store from?" Always show this step. If the triggering request
   supplied an http(s) URL, use its canonical origin as the input's
   `placeholder`; otherwise use the active company's website URL when it is a
   valid http(s) URL, or an empty placeholder when it is not. A placeholder is
   only a hint: require the user to enter an explicit answer. Validate that
   the answer is an http(s) URL. If it is invalid, open a new one-field
   `steps` panel for `website_url` with `skippable: false`, end the turn, and
   wait for a valid answer. (`steps_answer` only mirrors a valid chat-typed
   answer into a panel that is still active; it does not re-open a completed
   invalid input.)
2. `theme_target` — `single_select` with `skippable: false`, "Build a new
   theme or use an existing one?"
   - First option: id `new`, label `Create a new theme (recommended)`,
     description "Scaffold an isolated theme for this launch."
   - Then add one option per discovered theme: id `existing_<theme_id>`,
     label `Use: <theme name or Theme #id>`, description "Build and publish
     this existing theme."
   - When the theme list couldn't be read, offer only `new` and say in the
     step description that existing themes couldn't be listed.
3. `confirm` — `single_select` with `skippable: false`, "Ready to start this
   onboarding run?"
   - `go` — `Yes, launch it`
   - `cancel` — `Not yet`

Do not add scope, product-source, or media questions. Every remaining decision
is the workflow's to make.

### 3. Start the run

Only continue when `confirm` is `go`. If it is `cancel`, acknowledge the
cancellation in one line and stop without calling `run_workflow`.

Derive the theme fields from the picker:

- `new` → `theme_target: "new"`, `theme_id: null`
- `existing_<theme_id>` → `theme_target: "existing"`,
  `theme_id: <the exact discovered theme id>`

Reject an existing-theme answer that does not match the list loaded for this
picker. Never infer a theme from what is active or available locally.

Call `run_workflow` with the answers:

```jsonc
{
  "workflow_slug": "streamlined-onboard-launch",
  "run_title": "Launch drinkolipop.com",
  "context": {
    "website_url": "https://drinkolipop.com",
    "setup_mode": "quality",
    "theme_target": "new",
    "theme_id": null,
  },
}
```

`run_title` matters. The same workflow gets run many times and the sidebar
shows only this string — "Launch drinkolipop.com" is findable, "Streamlined
Onboard & Launch" is not.

Canonicalize `website_url`: keep the http(s) origin, remove tracking
parameters, and omit a trailing path unless the storefront genuinely lives
there. Use that canonical value in both `run_title` and context.

## Speed — keep the lightweight path

For a request resolved to `speed-import`, preserve the lightweight behavior:

1. Confirm the active company with `GET /api/company/v1/companies/me` and tell
   the user which company will be changed.
2. Take an http(s) website URL from the request, or ask for it if missing.
3. Call `run_workflow` with slug `speed-import`, a searchable
   `Launch <domain>` title, and context containing the canonical
   `website_url` plus `setup_mode: "speed"`.

Do not show the Quality picker for Speed.

## Hand over

`run_workflow` returns immediately; the run continues in the background and a
live progress card renders in this chat. Tell the user, in two lines:

- which mode started, and what that means they will and will not get
- that the run continues if a step comes back rough — nothing in either
  workflow stops the run, so a weak page becomes a note in the final handoff
  rather than a dead run

Then stop. Do not poll `workflow_status` on a loop, and do not narrate steps as
they pass. Answer with `workflow_status` when the user asks.

## What each mode actually costs

Worth knowing before you recommend one.

**Quality** runs 15 steps over 6 waves. Three source-reading steps open
together, the theme starts building in the second wave, and the product,
business-profile, and media tracks run beside it. Fable 5 on the theme.

**Speed** runs 9 steps over 5 waves on Grok 4.5 throughout, and skips the
onboarding form, collections and content import, media and UGC, and the
storefront walkthrough. Its handoff names what it skipped — read that section
before telling anyone the company is ready.

Neither mode can be told to use a different model mid-run: a workflow step
carries a fixed model, and `run_workflow` takes no model argument. The choice
of mode is the choice of model.
