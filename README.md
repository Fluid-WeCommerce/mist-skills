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
├── manifest.json        ← single source of truth for what skills exist
├── finance/
│   ├── promo-code-summary.md
│   └── monthly-close.md
├── themes/
│   ├── scrape-into-theme.md
│   └── new-section.md
├── mist/
│   ├── scaffold-droplet.md
│   └── env-vars-audit.md
└── README.md
```

Directories are categories. The category shows as a section header in the desktop sidebar.

## Skill file format

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
    }
  ]
}
```

The desktop pulls `manifest.json` first, diffs it against its cached copy, and re-fetches only the skill bodies whose `updated_at` has changed. **Bump `updated_at` whenever you change a skill's body** — otherwise users won't see the update.

## Contributing a skill

1. Fork this repo.
2. Pick a category directory (or add a new one — directories are categories).
3. Create `<your-slug>.md` with the frontmatter + body shown above.
4. Add an entry to `manifest.json` (use the current UTC time for `updated_at`).
5. Open a PR. Title: `feat(<category>): <skill name>`.

Skills run with the full tool set Claude has in Mist Desktop:

- File I/O scoped to the active project
- The `fluid` CLI
- A `fluid_api(path, method, body)` tool that hits the user's Fluid API with their token

Write the body assuming Claude can call any of those — be specific about which endpoint, what to read, what to write. Skills are prompts, not scripts; the user reads the body before they run it.

## Why this lives outside `fluid-commerce/fluid`

So community PRs ship faster than the Rails monolith's release cadence, and so the catalogue can grow without burdening the core API surface with a domain model for "skills."

## License

[MIT](./LICENSE) — fork, modify, and ship freely.
