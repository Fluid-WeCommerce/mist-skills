# Mist Skills

Community-contributed **Skills** for [Mist Desktop](https://github.com/fluid-commerce/fluid-mono) — repeatable Claude prompts that run against your Fluid environment.

Examples:

- _Pull every order that used the `SUMMER10` promo code in the last 30 days and summarize._
- _Scrape this URL and build it into the active Fluid theme._
- _Audit env vars on every live Mist for missing `STRIPE_PUBLISHABLE_KEY`._

Every skill is a single Markdown file with YAML frontmatter. Mist Desktop pulls them from this repo at launch (background-refresh, never blocks the UI) and renders them in the **Skills** sidebar. Click `▶ Run` and the body becomes a Claude turn with full tool access — reading files, writing files, hitting the Fluid API, running the `fluid` CLI.

## Repo layout

```
mist-skills/
├── manifest.json                 ← single source of truth for what skills exist
├── finance/
│   ├── promo-code-summary.md     ← flat skill: single .md file
│   └── monthly-close.md
├── themes/
│   ├── scrape-into-theme.md      ← flat
│   ├── theme-clone/              ← folder skill (long, ships references)
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── css-js-patterns.md
│   │       └── …
│   ├── theme-refine/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── dev-preview-visual-diff.md
│   └── references/               ← shared refs cited from multiple themes/* skills
│       ├── blocks-vs-sections.md
│       ├── css-js-hygiene.md
│       └── …
├── mist/
│   ├── scaffold-droplet.md
│   └── env-vars-audit.md
├── countries/
│   ├── open-a-country.md          ← flat skill (front-end steps flow)
│   └── compliance-manager/        ← folder skill
│       └── SKILL.md
├── workflows/                     ← declarative multi-step chains (JSON, not skills)
│   ├── open-country.workflow.json
│   ├── finalize-otg-country.workflow.json
│   ├── finalize-nfr-country.workflow.json
│   └── finalize-usd-country.workflow.json
└── README.md
```

Directories under the skill categories are categories (the category shows as a section header in the desktop sidebar). `workflows/` is special — see [Workflows](#workflows) below.

### Two skill shapes

| Shape          | When to use                                                                                                  | Layout                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **Flat**       | The skill body fits on one screen of Markdown and doesn't need supporting tables/snippets — most cases.      | `<category>/<slug>.md`                                                  |
| **Folder**     | The body is long enough that you want to factor out reference material — schemas, code patterns, examples. | `<category>/<slug>/SKILL.md` + `<category>/<slug>/references/*.md`      |

Use the folder shape when the **main body** (the part the agent reasons about every turn) wants to stay lean while still shipping deep reference material. The runtime inlines every referenced file at the end of the prompt under `## Reference — <filename>` headers, capped at **256KB total** so a runaway reference can't blow up the turn.

### Shared references

When several skills in the same category cite the same material, put it in `<category>/references/*.md` (sibling to the skills, not inside one skill's folder) and **list the path explicitly** in each skill's `manifest.json` `references` array. This avoids duplicating bytes and means an edit to a shared reference updates every consuming skill in one commit.

Example: `themes/theme-refine` and a future `themes/theme-audit` both want `themes/references/liquid-correctness.md` — one file, two manifest entries cite it.

## Skill file format

Same format for both shapes — the file is just named differently. **Flat** skills are `<category>/<slug>.md`; **folder** skills put the same content in `<category>/<slug>/SKILL.md` (note the all-caps filename) with references as sibling files in `<category>/<slug>/references/*.md`.

```markdown
---
name: Promo code summary
description: Summarize orders that used a given promo code over a date range.
icon: receipt
---

# Goal

Summarize orders from the last 30 days that used the promo code SUMMER10.

# Steps

1. Hit `GET /api/v202604/orders?filter[promo_code]=SUMMER10&filter[created_at_gte]={{thirty_days_ago}}` against the active company.
2. Compute total orders, total revenue, AOV, and top 5 customers by spend.
3. Render a Markdown table.
```

### Frontmatter fields

| Field         | Required | Notes                                                                          |
| ------------- | -------- | ------------------------------------------------------------------------------ |
| `name`        | yes      | Display name in the sidebar                                                    |
| `description` | yes      | One-sentence summary; shown under the name in the preview pane                 |
| `icon`        | no       | A [Lucide](https://lucide.dev/icons) icon name (e.g. `receipt`, `paint-bucket`, `flame`) |

### Template tokens

The runtime substitutes a fixed set of `{{tokens}}` before the body is sent to Claude. Use them so a skill works regardless of who's running it.

| Token                  | Resolves to                                |
| ---------------------- | ------------------------------------------ |
| `{{user.name}}`        | Active user's display name                 |
| `{{user.email}}`       | Active user's email                        |
| `{{company.name}}`     | Active company's display name              |
| `{{company.subdomain}}`| Active company's subdomain                 |
| `{{company.api_base}}` | API base URL (e.g. `https://api.fluid.app`)|
| `{{today}}`            | Today, ISO-8601 (`2026-06-20`)             |
| `{{thirty_days_ago}}`  | 30 days ago, ISO-8601                      |

Anything that's not a known token is left literal.

## `manifest.json`

```jsonc
{
  "version": 1,
  "skills": [
    {
      "slug": "finance/promo-code-summary",        // unique identifier; the path-without-`.md`
      "name": "Promo code summary",                // matches frontmatter
      "description": "Summarize orders…",          // matches frontmatter
      "category": "finance",                       // matches the directory
      "icon": "receipt",                           // matches frontmatter
      "path": "finance/promo-code-summary.md",     // path inside the repo
      "updated_at": "2026-06-20T18:00:00Z"         // bump on every meaningful body change
    },

    // FOLDER shape — `path` points at SKILL.md, `references[]` lists
    // every supporting file the agent should see alongside the main
    // body. Paths are repo-relative; they can be inside the skill's
    // own `references/` folder OR shared (e.g. `themes/references/…`).
    {
      "slug": "themes/theme-refine",
      "name": "Theme Refine",
      "description": "Refine a Fluid theme to the gold standard…",
      "category": "themes",
      "icon": "sparkles",
      "path": "themes/theme-refine/SKILL.md",
      "updated_at": "2026-06-29T00:00:00Z",
      "references": [
        "themes/theme-refine/references/dev-preview-visual-diff.md",
        "themes/references/blocks-vs-sections.md",
        "themes/references/css-js-hygiene.md"
      ]
    }
  ]
}
```

The desktop pulls `manifest.json` first, diffs it against its cached copy, and re-fetches:

1. Any skill body whose `updated_at` changed.
2. Any reference in the `references[]` array that's missing from the local cache (so adding references later doesn't require an `updated_at` bump on the parent skill — the fetcher will pick them up next refresh).

**Bump `updated_at` whenever you change the body or remove a reference.** Adding a new reference path to the array works without a bump because the missing-file check catches it.

### Manifest fields

| Field         | Required | Notes                                                                                                          |
| ------------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| `slug`        | yes      | Unique. Flat: `<category>/<filename>`. Folder: `<category>/<folder-name>`.                                     |
| `name`        | yes      | Must match the file's frontmatter `name`.                                                                      |
| `description` | yes      | Must match the file's frontmatter `description`.                                                               |
| `category`    | yes      | Must match the parent directory name.                                                                          |
| `icon`        | no       | Lucide icon name.                                                                                              |
| `path`        | yes      | Flat: `<category>/<filename>.md`. Folder: `<category>/<folder>/SKILL.md`.                                       |
| `updated_at`  | yes      | ISO-8601 UTC. Bump on body changes.                                                                            |
| `references`  | no       | Array of repo-relative paths. Omit for flat skills. List every file the agent should see alongside the body.   |

## Workflows

A **skill** is a prompt the user reads and runs. A **workflow** is a declarative, multi-step chain the desktop's orchestrator runs across dedicated agent chats — each step gets QA-reviewed against acceptance criteria and reworked automatically on failure. Skills and workflows compose: an interactive skill (e.g. `countries/open-a-country`) collects the user's answers through the steps panel, then hands off to a workflow (`open-country`) that does the writes.

Workflows live in `workflows/` as **plain JSON** (`<slug>.workflow.json`) and are listed in `manifest.json` under a `workflows` array (separate from `skills`). The desktop syncs them into its cache exactly like skill bodies and loads them with this precedence, most-specific winning:

```
built-in (compiled into the app)  <  community (this repo)  <  user (~/Fluid/workflows/)
```

So a workflow shipped in the app can be **hot-fixed from this repo without an app release** — same win skills get — and a user can still fork one locally.

### Workflow file shape

Every field below is shown together for reference; in practice most steps
set only `id`, `name`, one of `prompt`/`skill`, and `acceptance`.

```jsonc
{
  "revision": "2026-07-25",                    // bump on every edit — recovery refuses a run whose stored definition no longer matches
  "slug": "open-country",                      // matches the manifest entry; a user file of the same slug overrides this one
  "name": "Open a Country",
  "description": "…",
  "launcherSkill": "countries/open-a-country", // optional vetted skill that gathers run context before run_workflow
  "maxParallel": 5,                            // 1-10, default 5. How many dependency-satisfied steps may run at once
  "steps": [
    {
      "id": "create-country",
      "name": "Create the company country",

      // Exactly ONE of prompt / skill:
      "prompt": "…",                           // inline instructions for this step's agent turn
      // "skill": "countries/compliance-manager",  ← or delegate to a skill by slug

      "target": { "type": "manager" },         // where it runs. "manager" = the project the run was started from
      // "target": { "type": "kind", "kind": "theme", "fallbackToManager": true }
      //   kind ∈ theme | portal | mist | widget — first sibling project of that kind with a local checkout.
      //   fallbackToManager:true degrades to the manager project instead of failing when none exists.

      "model": "anthropic/claude-opus-5",      // optional gateway slug for this step. Omit to use the run's model

      "dependsOn": [],                         // step ids that must be satisfied first. Steps with satisfied deps run in parallel
      "acceptance": ["…"],                     // what QA verifies against real state. Required when qa.enabled

      "qa": {
        "enabled": true,                       // default true. false = the work turn IS the step; nothing verifies it
        "strictness": "standard",              // strict | standard | lenient (default standard)
        "onFail": "continue",                  // what happens after the rework budget is spent — see below
        "model": "openai/gpt-5.6-sol",         // optional: reviewer model. Omit to use the step's, then the run's
        "requiredTools": [                     // optional machine-enforced evidence floor
          {
            "tool": "view_project_image",
            "minSuccessfulCalls": 6,
            "distinctBy": ["path"]             // reopening one file six times still counts as one
          },
          {
            "tool": "read_preview_dom",
            "input": { "mode": "all" }         // input is a recursive partial match
          }
        ]
      },
      "maxReworkRounds": 2,                    // 0-5, default 2. Fix-and-recheck rounds before onFail applies

      "runIf": { "flag": "build_theme" },      // optional: only run when this run-context flag is truthy (see below)
      "recovery": { "mode": "manual" }         // optional: opt in to retrying THIS step after a failure. Absent = no recovery
    }
  ],

  // Optional. Derive boolean flags from the caller's context before the first
  // dispatch, so runIf can gate on them. Fill-only: an explicitly-passed key wins.
  "deriveContext": [
    { "set": "build_theme", "when": { "in": { "key": "run_scope", "values": ["full", "theme_only"] } } }
    // predicates: { "equals": { key, value } } | { "in": { key, values } } | { "includes": { key, value } }
  ],

  // Optional. Names the step whose QA verdict IS the business outcome.
  "finalGate": { "stepId": "launch-readiness-review", "allowNeedsReview": true }
}
```

#### QA — `qa` (optional, on by default)

A QA step is a **second full model turn in a fresh chat**, with an independent
reviewer that never sees the worker's transcript. It verifies `acceptance`
against actual state using tools, and returns PASS/FAIL.

- `enabled: false` — no reviewer. The step passes as soon as its agent says it's
  done. Right for steps that fail loudly on their own (a scaffold either produced
  files or threw); wrong for anything whose failure mode is "the agent believes it
  worked". A step with `enabled: true` and no `acceptance` is **rejected** — a
  reviewer with nothing to check against manufactures a PASS the run then trusts.
- `strictness` — moves the bar for *unverifiable* criteria and cosmetic
  shortfalls only. A genuine violation fails at every level.
  - `strict` — anything unverifiable fails; ambiguity resolves against passing.
  - `standard` — unverifiable fails, but criteria that explicitly allow a
    pass-with-notes outcome are honored.
  - `lenient` — fails what would actually break the store; cosmetic gaps pass
    with a note.
- `onFail` — what happens once `maxReworkRounds` is spent:
  - `continue` (default, and the historical behaviour) — the step is marked
    **needs-review**, its findings are carried into dependents' prompts, and the
    run finishes `completed-with-issues`. The work landed; a human should check it.
  - `stop` — treated as a failure: dependents are **skipped** and the run fails.
    For steps where continuing on unverified work does damage rather than just
    leaving a mess.
- `requiredTools` — optional machine-enforced evidence. A prose PASS is
  overridden to FAIL unless the fresh QA chat's persisted trace contains the
  required number of successful calls.
  - `input` recursively matches a subset of the call input. Arrays are also
    subset-matched.
  - `distinctBy` lists dotted input fields whose values must differ across
    calls. Use it for multi-route and multi-artifact matrices, such as
    `["path", "width"]`.
  - This proves that evidence was gathered; `acceptance` still defines whether
    the evidence is good enough.

#### Parallelism — order, `dependsOn` and `maxParallel`

The orchestrator dispatches **every** step whose dependencies are satisfied, up
to `maxParallel` (itself capped by the desktop's hard ceiling). Two steps with
the same `dependsOn` therefore start together. The desktop's builder writes this
shape by giving a step the *same* dependencies as its predecessor rather than
depending on it.

Each concurrent step is a live, billed model turn, and providers rate-limit well
before the app does — past a point a wider fan-out finishes **slower** once
retries start. Raise `maxParallel` only for steps that are genuinely independent.

#### Conditional steps — `runIf` (optional)

A step may declare `"runIf": { "flag": "<contextKey>" }`. The step runs **only if that boolean flag is truthy in the run's start context** (the `context` object the fronting skill passes to `run_workflow`). If the flag is falsy or absent, the step is **condition-skipped**: marked `skipped`, but — unlike a step skipped because a dependency failed — it **satisfies its dependents**, so downstream steps still run. A run whose only non-passed steps are condition-skips still completes successfully.

Use it to let **one** workflow cover scoped runs instead of maintaining separate workflow files. Example: `onboard-launch-company` derives `build_theme` / `import_products` flags from a `run_scope` picker, and tags the theme-track and product-track steps with `runIf` so a "data only" run skips the theme + product steps while still running data gathering, its QA, and the launch review.

Guidance for implementers:
- The fronting skill must put the boolean in the `run_workflow` `context` (e.g. derive `build_theme` from a `run_scope` answer). An absent flag reads as "don't run."
- `runIf` gates a **whole step**. For finer-grained skips inside a step, branch in the step's `prompt` instead (a prompt step can self-skip and emit `STEP_OUTPUT { skipped: true }`).
- Prefer `runIf` over per-scope workflow copies — it keeps one source of truth and the progress card shows the skip explicitly.
- Requires desktop engine support (fluid-mono `mist-desktop` ≥ the runIf release). Older builds ignore the unknown key and simply run the step, so tagging is backward-safe — but don't rely on skipping until the engine ships it.

#### Version gating — read before publishing

Unknown keys are **dropped silently** by older desktop builds, so a workflow
using a newer field still loads there — it just quietly loses that behaviour
(`qa.onFail: "stop"` becomes "continue", a per-step `model` reverts to the run's,
or `qa.requiredTools` is not enforced).

`maxParallel` is the exception and the one that actually breaks: it is
**range-validated**, and the ceiling has moved 3 → 5 → 10. A build on an older
ceiling **rejects the whole file** — the loader logs a warning and skips it, so
the workflow simply doesn't appear. Keep `maxParallel` within the oldest ceiling
still in the field, or hold the workflow until the raise ships.

Manifest entry (in the top-level `workflows` array):

```jsonc
"workflows": [
  { "slug": "open-country", "path": "workflows/open-country.workflow.json", "updated_at": "2026-07-04T00:00:00Z" }
]
```

Bump `updated_at` on any change, same as skills.

> **Trust:** workflows are more powerful than skills — they autonomously fan out agent turns that make real API writes. That's why what merges here is the trust boundary: only maintainers approve PRs to this repo; publish-tier contributors can't. Keep a workflow's writes idempotent, and prefer delegating judgment-heavy steps to a `skill:` so the logic stays reviewable.

## Tools

Skills and workflow steps run with Claude's full tool set in Mist Desktop. **Tools are code — they're compiled into the app and can't be added or changed from this repo.** This section is the reference for *which* tools a skill or workflow can call by name; to change a tool's behavior, change the app.

| Tool | What it does |
| ---- | ------------ |
| `fluid_api(path, method, body)` | Call the user's Fluid API with their token — the workhorse for reads and writes. |
| `country_atlas(country_code, [agreement_local_id])` | Fluid's per-market pre-setup profile (modes, launch checklists, agreements, tax/legal settings, payment methods, address layout, languages). Pass `agreement_local_id` for one agreement's full legal text. |
| `country_settings(country_code)` | The compliance rulebook projected from the atlas (disclosure pages, cookie/VAT/unit-price rules) — what `compliance-manager` reads. |
| `steps` / `steps_answer` / `steps_mark_item` | Open an interactive click-through panel, record a typed-in answer, or check off a live "setting up…" item. |
| `run_workflow(workflow_slug, [context])` / `workflow_status` | Kick off a workflow chain (passing collected answers as `context`) and check a run's progress. |
| `run_skill(slug)` | Load another skill's body and follow it (skill composition). |
| File I/O: `read_file`, `write_file`, `edit_file`, `list_dir` (+ `*_in` cross-project variants) | Read/write files scoped to the active project. |
| `run_cli` | The `fluid` CLI (`fluid theme push`, `fluid mist push --watch`, …), allowlisted subcommands only. |
| `web_fetch`, `crawl` | Fetch a URL as text, or crawl a page (markdown + screenshot). |
| `dam_upload`, `compress_media`, `video_ripper`, `video_metadata` | Push media into the Fluid DAM, shrink it (bundled ffmpeg), rip/inspect a social video. |
| `screenshot_preview`, `start_preview`, `read_recent_log_tail`, `retry_lifecycle` | Drive + inspect a running dev preview. |
| `db_query`, `sql_answer_card`, `list_projects` | Query a connected Mist database and list projects. |
| `product_card`, `resource_card`, `order_card` | Render a rich card for a product / storefront resource / order in the chat. |
| `human_in_the_loop` | Gate a change on the user's approval. |

Name the exact tool + endpoint you expect in a skill or workflow step, not "figure it out from the docs."

## Contributing a skill

1. Fork this repo.
2. Pick a category directory (or add a new one — directories are categories).
3. **Choose your shape**:
   - **Flat** (most cases) — create `<category>/<your-slug>.md` with the frontmatter + body shown above.
   - **Folder** (when the skill needs supporting reference material) — create `<category>/<your-slug>/SKILL.md` for the main body, then drop reference files in `<category>/<your-slug>/references/*.md`. Cite shared category references from `<category>/references/` instead of duplicating them.
4. Add an entry to `manifest.json`:
   - Use the current UTC time for `updated_at`.
   - For folder skills, populate the `references[]` array with every supporting file (own folder + any shared references).
5. Open a PR. Title: `feat(<category>): <skill name>`.

### Authoring guidance for new agents writing skills

- **Keep the main body lean**. The agent re-reads it every turn — if it's 2k lines of schema reference, every turn pays the token cost. Move "look this up if you need it" material into `references/`.
- **Frontmatter `description` should be one sentence**, action-first ("Translate a Fluid theme into…", not "This skill is for…"). Mist Desktop shows it under the name.
- **Bump `updated_at` whenever the SKILL body changes**. Adding a brand-new reference path to the manifest is free (the fetcher's missing-file check catches it); editing an existing reference *also* needs an `updated_at` bump on the parent skill so users pick up the change.
- **One canonical reference per concept**. If two skills cite the same material, put it in `<category>/references/` and link both manifest entries at it. Don't fork the file.
- **Write the body as if the user is reading it before clicking Run**. Skills are prompts, not scripts — the user sees what's about to happen.
- **Be specific about tools**. Skills run with the full tool set Claude has in Mist Desktop:
  - File I/O scoped to the active project.
  - The `fluid` CLI (`fluid theme push`, `fluid mist push --watch`, etc.).
  - A `fluid_api(path, method, body)` tool that hits the user's Fluid API with their token.
  - `dam_upload` for pushing media into the Fluid DAM.
  - `compress_media` (bundled ffmpeg) for shrinking videos / images before upload.

  Name the exact endpoint or command you expect the agent to run, not "look at the docs and figure it out."

## Why this lives outside `fluid-commerce/fluid`

So community PRs ship faster than the Rails monolith's release cadence, and so the catalogue can grow without burdening the core API surface with a domain model for "skills."

## License

[MIT](./LICENSE) — fork, modify, and ship freely.
