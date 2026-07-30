---
name: launch-setup
description: >-
  Start an onboard. Asks one question — quality or speed — and kicks off the
  matching workflow with the company's website already in context. Quality
  builds the theme with Fable 5 and covers the whole store; speed builds it
  with Grok 4.5 and covers the storefront only.
---

# Launch Setup

The front door for onboarding a company onto Fluid. Ask two things, start the
right run, get out of the way.

## Step 1 — What you need

You need exactly two facts. Get them in one exchange, not two.

1. **The company's current website.** Take it from the request if it is already
   there. Confirm the active Fluid company with `GET /api/settings/company` and
   say which company you are about to onboard — starting a run against the
   wrong company wastes an hour before anyone notices.
2. **Quality or speed.** Ask it plainly, with the trade in one line each:

> **Quality** — builds the whole store: theme with every page, products,
> collections and content, business profile, media and UGC, then a storefront
> walkthrough. Theme built by Fable 5. Roughly an hour.
>
> **Speed** — storefront only: brand, products, home, shop, product page,
> publish. Theme built by Grok 4.5. No content import, no media, no QA pass.
> Roughly twenty minutes, and leaves real work outstanding.

If they do not choose, choose **quality**. A run that skipped the catalog is
much more expensive to discover later than one that took an extra half hour.

Do not ask anything else. Every remaining decision is the workflow's to make.

## Step 2 — Start the run

| Answer | Workflow slug |
| --- | --- |
| quality, or no preference | `streamlined-onboard-launch` |
| speed | `speed-import` |

Call `run_workflow` with that slug, and pass the facts you gathered:

```jsonc
{
  "workflow_slug": "streamlined-onboard-launch",
  "run_title": "Launch drinkolipop.com",
  "context": {
    "website_url": "https://drinkolipop.com",
    "setup_mode": "quality",
  },
}
```

`run_title` matters. The same workflow gets run many times and the sidebar
shows only this string — "Launch drinkolipop.com" is findable, "Streamlined
Onboard & Launch" is not.

`website_url` is the one piece of context every step reads. Pass the canonical
origin, no tracking parameters, and no trailing path unless the storefront
genuinely lives on one.

## Step 3 — Hand over

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
