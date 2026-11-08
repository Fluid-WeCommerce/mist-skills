---
name: Scrape a URL into the active theme
description: Fetch a page, extract its layout and copy, scaffold a matching Fluid theme section.
icon: globe
---

# Goal

The user has an external page they want to recreate as a Fluid theme section. Read its structure and build a matching `.liquid` template.

# Steps

1. Ask the user for the URL to scrape if not already in the conversation.
2. Use `run_cli fluid theme crawl <url> --format html --no-main-content-only` to fetch the rendered page HTML (Fluid's managed browser runs it server-side, which avoids CORS / browser quirks).
3. Identify the page's primary content blocks: hero, feature grid, CTA, footer, etc. Ignore site-chrome.
4. For each block, extract:
   - Heading text (and hierarchy)
   - Body copy
   - Image references (URLs only, don't download)
   - Button labels + target URLs
5. Scan the active theme for an existing section that matches the structure (`list_dir("sections/")`, then `read_file` candidates). Reuse if a near-match exists.
6. Otherwise, generate a new `sections/<slug>/index.liquid` file with:
   - Schema block declaring the editable settings (heading, body, image, button text, button URL)
   - Liquid template using Tailwind classes consistent with the theme's existing convention
7. Show the user the diff before writing. After approval, `write_file` the new section.
8. Suggest where to place the section: a `{% section '<slug>' %}` tag in the matching page template (for example `home_page/default/index.liquid`), or add it from the Page Editor's **Sections** panel.
