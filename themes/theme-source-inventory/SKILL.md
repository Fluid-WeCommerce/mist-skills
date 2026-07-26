---
name: theme-source-inventory
description: >-
  Capture a fresh, complete, machine-verifiable source evidence bundle before
  building or refining a Fluid theme. Use for page discovery, exact Home/Shop/PDP
  copy and section inventory, rendered HTML and CSS tokens, full-page desktop
  and mobile screenshots, and exhaustive image/video enumeration. Do not use
  this skill to build, upload, push, publish, or activate a theme.
---

# Theme Source Inventory

Create the source-of-truth bundle that later Fluid theme steps consume. This is
a discovery-only operation: do not edit theme sections/templates, enumerate the
Fluid catalog, upload DAM media, start theme dev, push, publish, or activate.

The active company, theme project, and source site are already scoped by Mist.
Never ask for credentials or switch companies.

Read `themes/references/pixel-fidelity-core.md` before capturing evidence.

## 1. Establish a fresh run boundary

Before the first source request:

1. Record the current UTC time as `evidence_run_started_at`.
2. Never copy this value from an existing manifest.
3. Preserve unrelated downstream manifest fields, but replace every source
   evidence cell with evidence captured during this turn.
4. Ensure the earliest `captured_at` is on or after the run boundary and no more
   than 30 minutes after it. An older boundary is stale even if the new captures
   sort after it.

## 2. Select the three priority routes

Select and record:

- `home`: the canonical homepage.
- `shop`: the primary all-products, collection, or category list page.
- `pdp`: a flagship or structurally complex, multi-variant product page.

Use redirects and canonical links to record final URLs. Map up to four important
static pages and two additional PDPs for structure coverage, but do not expand
the six-cell visual matrix.

## 3. Capture three independent evidence layers

For each priority route, capture 1440×900 and 390×844 with:

```json
{
  "formats": ["markdown", "html", "screenshot"],
  "only_main_content": false,
  "capture_page_evidence": true,
  "screenshot_options": {
    "full_page": true,
    "quality": 90,
    "viewport": { "width": 1440, "height": 900 }
  }
}
```

Repeat with the mobile viewport. Keep the exact crawl-returned local paths for:

- complete Markdown: copy and catalog facts;
- complete rendered HTML: DOM, stylesheets, tokens, fonts, and media;
- full-page screenshot: visual order, geometry, crop, and responsive behavior;
- page-evidence sidecar: rendered text, landmarks, media, viewport, route, and
  screenshot receipt.

Do not reconstruct any file from chat output. A successful screenshot without
all three companion files is an incomplete cell.

Inspect every screenshot with `view_project_image`. Open every HTML file with
`read_file`; use targeted later offsets or searches when the needed copy/media
is beyond the first chunk. A leading excerpt alone is not a DOM audit.

## 4. Build exhaustive inventories

Write `clone-manifest.json` with:

- `source_url` and `evidence_run_started_at`;
- `page_manifest`;
- ordered `section_inventory` for Home, Shop, PDP, header, and footer;
- `brand_tokens` with computed colors, font families/weights, stylesheet
  evidence, and an explicit font license/substitution decision;
- verbatim `hero_copy` with Markdown, HTML, and screenshot evidence;
- `visual_routes.home`, `.shop`, and `.pdp`, each with source URL, future built
  path, ordered landmark mappings, and complete desktop/mobile evidence cells;
- `priority_media.items`.

Build `priority_media.items` from the union of all six rendered sidecars plus
the retained HTML/CSS—not from a visual sample. Include every visible:

- image `currentSrc`/`src` and responsive source candidate;
- video `currentSrc`, `<source>`, poster, and format candidate;
- CSS background/content media URL;
- product-grid card, gallery item, rail/cross-sell item, logo, and icon.

Create one item per rendered media element and viewport role. Each item records
its actual `source_url`, a complete `source_candidates` URL array, route,
landmark, viewport role, media kind, and source product identity when
applicable. Video items also record `autoplay`, `loop`, `muted`, `playsinline`,
`controls`, type, and poster. Preserve distinct desktop/mobile elements when
their selected source differs. Do not collapse an entire rail into one item or
discard responsive candidates; keep candidates on their owning item so later
DAM delivery can select one high-quality source without uploading every
transform as a separate asset.

## 5. Protect local evidence

Preserve existing `.fluidignore` rules and add exact entries for:

```text
clone-manifest.json
fluid-catalog-index.json
.mist-desktop/source-baselines/
baselines/
package.json
pnpm-lock.yaml
scripts/
```

## 6. Validate before reporting

Hash all 24 files in one `file_sha256` call and store the exact raw-byte digests
and byte counts. Then run the materialized validator returned with this skill:

```text
python3 <SOURCE_INVENTORY_VALIDATOR_PATH> --manifest clone-manifest.json
```

The validator checks freshness, file/path/hash/size/dimension consistency,
sidecar receipts, real HTML, all six viewports, required video attributes, and
coverage of every URL exposed by the rendered sidecars. Fix every error and run
it again. `SOURCE_INVENTORY_VALIDATION: pass` is required.

The read-only QA reviewer must independently:

1. read the manifest and `.fluidignore`;
2. hash all 24 files in one call;
3. open all six HTML files;
4. view all six screenshots;
5. run the same validator.

## Output

Return:

```text
STEP_OUTPUT
manifest_path:
manifest_sha256:
priority_routes:
landmark_counts:
rendered_media_urls:
manifest_media_urls:
video_count:
evidence_files: 24
validator: pass
hero_copy:
brand_tokens:
secondary_routes:
unresolved:
```

Never report pass from prose, counts, or screenshots alone.
