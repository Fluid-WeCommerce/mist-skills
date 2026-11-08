---
name: Smart Dashboard
description: Self-fabricate a live business dashboard from real data — gather what every department cares about, render it with show_dashboard, then learn what the user wants front-and-center and remember it.
icon: layout-dashboard
category: mist
---

# Smart Dashboard

Build {{company.name}} a live "Command Center" dashboard from **real data**, show
it in the preview panel with the `show_dashboard` tool, then **ask the user what
matters more or less** and remember their answer so every future dashboard leads
with what they care about.

Today is {{today}}.

This is a **build → present → learn** loop. Do NOT dump every number you can find.
A great dashboard is opinionated: a headline, a handful of KPIs, one or two
breakdowns, and the few lists that drive action.

## Prerequisites

This skill calls `show_dashboard` / `list_dashboards`, the dashboard-panel tools
shipped by the smart-dashboard feature (fluid-mono PR #7235). If your Mist
Desktop build predates that PR, these tools won't be registered — `run_skill`
will still load this playbook, but the tool calls below will fail. Update to a
build that includes PR #7235 before running this skill.

## 0. Read the company's dashboard preferences FIRST

Before gathering anything, check `<memory>` (the company's `memory.md`, already in
your context) for a **"Dashboard preferences"** section — sections the user has
told you to prioritize or drop, preferred period (today/week/month), favorite
metrics, ordering. Honor it. Also call `list_dashboards` to see if a saved
dashboard already exists that you should reopen or iterate on rather than
rebuilding from scratch.

If the user named a focus in their request ("just show me revenue and
subscriptions"), that overrides the default department sweep below.

## 1. Gather what each department would want shown

The dashboard should reflect what a full C-suite would put on the wall. Derive the
metric priorities from the boardroom advisors — each "seat" instinctively watches
a different slice of the business. Pull a **bounded** set of real numbers (a
handful of queries total, not per-department exhaustive scans) via `fluid_api` /
`db_query`. **Degrade gracefully:** on a 403, an empty result, or a missing table,
drop that card and move on — never block the whole dashboard on one query, and
never invent numbers.

| Department (advisor)      | What they want on the dashboard                                         | Good card types                             |
| ------------------------- | ----------------------------------------------------------------------- | ------------------------------------------- |
| Finance (Fred, CFO)       | Revenue vs. prior period, AOV, refund/chargeback drag, payment approval | `hero_chart`, `stat_tiles`, `donut_chart`   |
| Logistics (Leanna, COO)   | Fastest sellers, days-of-cover / low stock, ship SLA, slow movers       | `leaderboard`, `stat_rows`, `mini_table`    |
| Engineering (Dave, CTO)   | Slowest storefront pages, security/config risk, recent ship activity    | `top_list`, `insight_banner`                |
| Compliance (Karen, CCO)   | Risky health/income claims, missing disclosures, low compliance scores  | `insight_banner`, `mini_table`              |
| Sales (Shelby, CRO)       | Enrollment/recruiting momentum, hot markets, converting UGC             | `stat_tiles`, `leaderboard`, `hero_chart`   |
| Marketing (Maverik, CMO)  | Best/worst converting pages & products, winning messaging, funnel leaks | `top_list`, `stat_rows`, `donut_chart`      |
| Customer (Cathy, CCO)     | Top return reasons, delivery experience, complaint/cancellation spikes  | `mini_table`, `stat_rows`, `insight_banner` |
| Field Leadership (Lester) | Hot sellers low on stock, stale material, portal/app freshness          | `leaderboard`, `insight_banner`             |

You do not need every row — pick the departments whose data you can actually pull
and that matter for this company. Aim for a dashboard of **4–7 sections**.

## 2. Assemble the descriptor

Compose a single dashboard descriptor and pass it to `show_dashboard`. Shape:

- `title` (e.g. "Command Center"), optional `subtitle`, optional `dataAsOf` (ISO
  timestamp of when you gathered the data — set it so the panel shows freshness).
- `sections[]`: each has an optional caps `title` + `accent` + `meta`, and
  `cards[]` on a 12-col grid.

**Card types** (each carries data + display config; put RAW numbers in `metric`
with a `format` hint — never a pre-formatted string):

- `stat_tiles` — a 4-up KPI row. `tiles[]` of `{ label, metric, trend?, highlighted? }`.
- `hero_chart` — the headline contrast card. `variant: "bar" | "area"`, `xKey`,
  `series[]` (one may be `highlight: true`), `data[]` rows, optional `headline`,
  `granularity`, `trend`. Use for the revenue-over-time hero.
- `donut_chart` — a breakdown. `segments[]` of `{ label, value, metric? }` +
  optional `centerLabel` / `centerMetric` + `footerLabel`.
- `stat_rows` — icon rows: `{ label, sublabel?, metric, trend?, accent? }`.
- `mini_table` — `columns[]` + `rows[]` (cells keyed by column key, each
  `{ value, sub?, accent?, bold? }`), optional `moreLabel`.
- `leaderboard` — ranked `entries[]` of `{ name, subtitle?, metric, trend? }`.
- `top_list` — grouped `groups[]` (label + `items[]` of `{ label, metric }`).
- `insight_banner` — a one-line finding: `{ text, emphasis?, accent }`.
- `media_cards` — optional media grid.
- `section_header` — an inline caps divider inside a section.

**Format hints:** `currency` ($1,235), `currency_compact` ($847K), `number`
(1,234), `compact` (1.2K), `percent` (94 → 94%), `ratio_percent` (0.94 → 94%),
`duration_days` (3 → "In 3 days"), `text`.

**Accents** (semantic, theme-aware): `accent` (blue/info), `green` (success),
`orange` (warning), `red` (risk/live), `purple` (secondary), `neutral`. Keep dark
`hero_chart` cards to **≤ 2** — they're headline accents, not the whole page.

**Trends:** `{ direction: "up" | "down" | "flat", value?, format? }` — the sign is
derived from `direction`, so pass a non-negative `value` (e.g. `{ up, 13, percent }`
→ "+13%").

A good first dashboard mirrors the "Command Center" reference: a revenue
`hero_chart`, a REV/ORD/AOV/CONV `stat_tiles` row, a revenue-breakdown
`donut_chart`, a top-products `leaderboard`, a live `stat_rows` card, and an
`insight_banner` for the single biggest opportunity.

If `show_dashboard` returns a validation error, it lists exactly which fields
failed — fix those and call it again. Don't re-gather data; just repair the shape.

## 3. Present, then LEARN (human-in-the-loop)

After `show_dashboard` succeeds, the dashboard is on screen. Now **ask the user, in
one short message, which sections matter more or less** — e.g. "This leads with
revenue and top products. Want me to push subscriptions up, or drop the traffic
list?" Then **END YOUR TURN and wait** for their answer. Do not keep calling tools.

When they answer, **record the durable preference** with `update_memory` under a
"Dashboard preferences" note — what to prioritize, what to drop, preferred period,
favorite metrics. Be specific and lasting ("Always lead the dashboard with
subscription health; they don't care about page-traffic lists"). This is what makes
the next dashboard build itself the way they like.

## 4. Offer to save / iterate

`show_dashboard` already saves the dashboard for the company. Offer to rebuild it
with their preferences applied, adjust the period, or add a section. If they want a
different named dashboard (e.g. "Subscriptions" vs "Command Center"), give it a
distinct `title` — it saves under its own id and appears in the panel's Saved menu.
