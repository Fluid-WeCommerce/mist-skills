---
name: Theme accessibility audit
description: Scan the active theme for common a11y issues and propose fixes.
icon: accessibility
---

# Goal

Audit the active Fluid theme for common accessibility problems and produce a prioritized fix list.

# Steps

1. `list_dir("sections")` and `list_dir("templates")` in the active theme.
2. For each `.liquid` file, read it and check for:
   - `<img>` tags missing `alt` attributes (flag `alt=""` only if it's clearly decorative — explain the call)
   - Buttons/links with no accessible name (no text content, no `aria-label`, no inner `<span class="sr-only">`)
   - Form inputs without an associated `<label>`
   - Headings out of order (an `<h3>` before any `<h2>` in the same section)
   - Color-coded states with no non-color signal (icon, text label)
   - `<a>` tags used as buttons (no `href`)
3. Group findings by severity: blockers (assistive tech can't use this), warnings (degraded experience), nits (small polish).
4. For each finding, show:
   - The file and line range
   - A one-sentence explanation of the problem
   - A suggested fix (with the actual patch the user can apply)
5. Render the report as Markdown. Don't fix anything yet — wait for the user to pick which to apply.
