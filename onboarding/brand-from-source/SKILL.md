---
name: brand-from-source
description: >-
  Read a company's public website once and set up its Fluid brand in a single
  unattended pass: logo, app icon, favicon, OG image and description, primary
  and secondary colors, heading and body fonts, and a first brand.md. Asks the
  user nothing. Built to be the opening step of an onboarding workflow.
---

# Brand From Source

Turn a live website into the active Fluid company's brand record. One pass, no
interview, no questions — a workflow step that waits for an answer stalls the
whole run.

This is the **structured** brand layer plus a first-draft voice document. The
conversational deep-dive lives in `marketing/brand-setup`; run that later, with
a human, to enrich what this step lays down.

Everything writes through `fluid_api(path, method, body)` and the Mist DAM
tools. The active company and token are injected. Never ask for credentials,
never call raw fetch or curl against the Fluid API.

Read
[`../onboarding-prefill/references/api-endpoints.md`](../onboarding-prefill/references/api-endpoints.md)
for the exact `brand_guidelines` contract before you write. The rules below are
about **what to extract**; that file is the authority on **how to persist**.

## Resolve scope

Take the source site from `context.website_url`. Standalone, ask once if it is
missing — but in workflow mode a missing URL is a recorded blocker, not a
question. Confirm the active company with `GET /api/company/v1/companies/me`
and say which company you are about to write to before writing.

## Step 1 — Capture the source once

One capture feeds every extraction below. Do not crawl the same page repeatedly
to answer separate questions.

Call `crawl` on the source home page with `formats: ["html", "rawHtml", "screenshot"]`,
`capturePageEvidence: true`, and a desktop viewport. That single call returns
four things this skill depends on:

- **`rawHtml`** — the post-hydration document, where the icon and OpenGraph
  tags actually live.
- **`documents.stylesheet`** in `.mist-desktop/source-baselines/` — the site's
  own CSS, each block labelled `[site]`, `[third-party-widget]`, or
  `[browser-artifact]`. Read only `[site]` blocks. Browser artifacts are
  Chrome's own error-page styling and will poison a palette if you let them in.
- **`landmarks[]` with `styleRef` into `landmarkStyles[]`** in the page-evidence
  sidecar — **resolved** computed styles for every visible heading, paragraph,
  list item, link, and button: exact color, background, font family, size,
  weight, line height, letter spacing. These are the values the browser
  actually applied. Prefer them over anything you would derive by reading the
  cascade yourself, and over anything you would eyedrop off a screenshot.
- **the screenshot** — for confirming that the mark you picked is the mark a
  human sees, and nothing else.

If the home page is thin (a splash or age gate), capture one more real page and
say which page you used.

## Step 2 — Identity assets

Pull candidates from `rawHtml`, not from guesses at conventional paths:

| Field | Source, in order of preference |
| --- | --- |
| `logo_url` | The standalone brand mark in the rendered global header — usually an `<img>` or inline `<svg>` inside `header`/`[role=banner]`. Prefer an SVG or the largest raster. |
| `icon_url` | `<link rel="apple-touch-icon">`, then a 180px+ icon from the web app manifest (`<link rel="manifest">`). |
| `favicon_url` | `<link rel="icon">` / `shortcut icon`, preferring the largest declared `sizes`, then `/favicon.ico` only if declared nowhere. |
| `default_og_image` | `<meta property="og:image">` (absolute-resolved). |
| `default_og_description` | `<meta property="og:description">`, else `<meta name="description">`. Persist it verbatim — do not rewrite the company's own words. |
| `name` | `<meta property="og:site_name">`, else the `<title>` with page-specific suffixes stripped. Do not overwrite a company name that is already set and differs only in styling. |

The logo must be the canonical standalone mark — not a partner lockup, not a
campaign graphic, not a Fluid default. If the header only carries a wordmark
lockup, take it and record that in `unresolved` so a human can swap it.

Every image goes through the DAM before it is persisted: upload the remote URL,
then PATCH `brand_guidelines` with the DAM URL. Never point a brand field at
the source site's CDN — those links rot and leak the source domain.

## Step 3 — Colors, from resolved values

Primary and secondary come from what the page actually renders.

1. Start from `[site]` CSS custom properties. A site that declares
   `--color-primary`, `--brand-accent`, or similar has already told you the
   answer; take it.
2. Otherwise use `landmarkStyles`. Rank candidate colors by how much they are
   used on **action surfaces**: the background of buttons and primary CTA
   links, then heading color, then link color. The primary brand color is
   nearly always the CTA background.
3. Secondary is the next most-used non-neutral — the accent behind badges,
   promo bars, or section backgrounds.

Reject as brand colors: pure white, pure black, near-neutrals used only for
body text, and anything appearing solely inside `[third-party-widget]` or
`[browser-artifact]` blocks. Persist as `#RRGGBB` uppercase hex; convert any
`rgb()`/`oklch()` value rather than storing it raw.

Record in your output which evidence produced each color — a custom property
name or the landmark role you counted. A palette you cannot attribute is a
palette you guessed.

## Step 4 — Fonts

Read the heading family from the `landmarkStyles` entry on `h1`/`h2` landmarks,
and the body family from `p`/`li`. Take the **first** family in the stack; the
rest are fallbacks.

Then resolve real files: find matching `@font-face` rules in the `[site]` CSS
and collect the family, weights, styles, and `src` URLs.

Licensing is a hard boundary. Only ingest a webfont when the source clearly
serves a self-hosted file the company is entitled to re-host — a file on the
company's own domain or DAM.

- **Self-hosted, same origin** → upload each real file through the DAM and add
  one `fonts[]` entry per file, with `name`, `file_url`, and whatever of
  `format`, `weight`, `style`, `role` you know.
- **Google Fonts or another open license** → ingest normally; note the license.
- **A commercial foundry's file, or licensing you cannot establish** → do not
  copy the bytes. Record the original family in brand.md, persist a legally
  usable substitute with the closest metrics, and list the substitution in
  `unresolved`.

Never register several declared weights that all resolve to the same file.

## Step 5 — Persist

One `PATCH /api/settings/brand_guidelines` with everything you resolved, body
wrapped in the `brand_guidelines` key. Omit a field you could not establish —
never write a placeholder, and never write a sentinel like `N/A` or `Unknown`
into a brand field.

Then re-`GET` the endpoint and re-fetch each saved asset URL. Require a
successful response, non-empty bytes, and the expected media type. A URL that
saved but 404s is a failure, not a pass.

## Step 6 — First brand.md

Write the voice document with `update_brand_voice`, which keeps the local
`<company>/brand.md` and the API value in sync. Keep it to what the source
actually evidences — a short, honest draft a human will extend:

- who the company is and what it sells, in its own framing
- the tone its real copy uses, with two or three quoted lines as proof
- the audience the copy addresses
- vocabulary it repeats, and terms it visibly avoids
- how the palette and type are used — where the primary color appears, whether
  headings are set in the display face
- an explicit "drafted from the public site, not yet confirmed with the
  company" line

Do not invent a mission the site does not state. An honest three-paragraph
brand.md beats an invented page of one.

**Write brand.md in plain prose.** Do not put backticks, code spans, or fenced
blocks in the body. The upstream WAF inspects this field and rejects payloads
that look like shell content, which fails the save with an error that does not
mention formatting. Hex colors are fine as bare text; write them as plain
`#RRGGBB` words, not inside code formatting.

## Step 7 — Report

Never end this step by asking a question. Anything you could not establish is a
line in `unresolved`, and the step finishes.

End with:

```
STEP_OUTPUT: {
  "company": "<name> (<id>)",
  "source_url": "…",
  "persisted": {
    "name": "…", "logo_url": "…", "icon_url": "…", "favicon_url": "…",
    "default_og_image": "…", "default_og_description": "…",
    "color": "#RRGGBB", "secondary_color": "#RRGGBB",
    "fonts": [{ "name": "…", "role": "heading|body", "file_url": "…", "license": "…" }]
  },
  "evidence": {
    "color_basis": "…", "secondary_basis": "…",
    "heading_family_basis": "…", "body_family_basis": "…"
  },
  "verified": { "reread": true, "assets_refetched": 5, "asset_failures": [] },
  "brand_md_written": true,
  "unresolved": []
}
```
