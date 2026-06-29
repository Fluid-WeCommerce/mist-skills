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
└── README.md
```

Directories are categories. The category shows as a section header in the desktop sidebar.

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
