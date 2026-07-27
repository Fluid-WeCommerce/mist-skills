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
- page-evidence sidecar: rendered text, landmarks, bounded section anchors +
  computed typography/layout styles, media, viewport, route, and screenshot
  receipt, plus Mist-generated `documents.html` and `documents.markdown`
  path/SHA-256/byte-length receipts for the exact companion files.

Do not reconstruct any file from chat output. A successful screenshot without
all three companion files is an incomplete cell.
Do not reuse a legacy sidecar that lacks either signed document receipt:
recapture that viewport. Matching basenames alone are not evidence that HTML or
Markdown came from the same crawl.

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

Do not hand-transcribe the evidence-derived arrays. After all six crawl bundles
are complete, call Mist's local-only deterministic builder exactly once:

```json
{
  "manifest_path": "clone-manifest.json",
  "evidence_run_started_at": "<current-turn UTC boundary>",
  "routes": {
    "home": {
      "built_path": "/",
      "desktop": {
        "page_evidence_path": "<Home desktop .page-evidence.json>",
        "html_path": "<Home desktop .html>",
        "markdown_path": "<Home desktop .md>"
      },
      "mobile": {
        "page_evidence_path": "<Home mobile .page-evidence.json>",
        "html_path": "<Home mobile .html>",
        "markdown_path": "<Home mobile .md>"
      }
    },
    "shop": {
      "built_path": "<future Fluid Shop path>",
      "desktop": {
        "page_evidence_path": "<Shop desktop .page-evidence.json>",
        "html_path": "<Shop desktop .html>",
        "markdown_path": "<Shop desktop .md>"
      },
      "mobile": {
        "page_evidence_path": "<Shop mobile .page-evidence.json>",
        "html_path": "<Shop mobile .html>",
        "markdown_path": "<Shop mobile .md>"
      }
    },
    "pdp": {
      "built_path": "<future Fluid PDP path>",
      "desktop": {
        "page_evidence_path": "<PDP desktop .page-evidence.json>",
        "html_path": "<PDP desktop .html>",
        "markdown_path": "<PDP desktop .md>"
      },
      "mobile": {
        "page_evidence_path": "<PDP mobile .page-evidence.json>",
        "html_path": "<PDP mobile .html>",
        "markdown_path": "<PDP mobile .md>"
      }
    }
  },
  "hero_copy": {
    "headline": "<verbatim or null>",
    "headline_reason": "<required only when null>",
    "subheadline": "<verbatim or null>",
    "subheadline_reason": "<required only when null>",
    "primary_cta": "<verbatim or null>",
    "primary_cta_reason": "<required only when null>"
  }
}
```

The tool name is `build_theme_source_inventory`. It reads descriptor-held
bytes, verifies each screenshot/HTML/Markdown file against the Mist-generated
path/SHA-256/byte-length receipts inside its sidecar, verifies the six
viewports and freshness boundary, copies every signed desktop section exactly,
assigns one future mapping per signed section, and emits one media item per
rendered element and viewport. It atomically replaces only
`evidence_run_started_at`, `section_inventory`, `visual_routes`,
`priority_media`, and hero evidence paths; it preserves `page_manifest`,
`brand_tokens`, and unrelated downstream fields. If it reports a missing
signed document receipt, recapture that cell with the current Mist build; do
not rename/copy an older document into place. For other failures, repair the
named path/capture or recrawl the incomplete cell and call it again.
Never replace it with `write_file`/`edit_file` transcription of section,
receipt, landmark, or media arrays. Require
`SOURCE_INVENTORY_BUILD: written` before continuing.

Each `visual_routes.<route>` must use this structure:

```json
{
  "source_url": "https://source.example/route",
  "built_path": "/future-fluid-route",
  "landmarks": [
    {
      "source_anchor": "#exact-sidecar-section-anchor",
      "built_section": "#stable-future-fluid-section-id"
    }
  ],
  "source_evidence": {
    "desktop": {},
    "mobile": {}
  }
}
```

Create exactly one ordered landmark mapping for every entry in that route's
desktop `sidecar.rendered.sections`. `source_anchor` is the exact signed
section `anchor`, not a guessed tag/class or a generic `main`. Do not replace
the section list with the much larger `rendered.landmarks` accessibility/link
list. `built_section` is the stable section id/selector later build steps must
implement.

Use this exact shape for each desktop/mobile evidence cell. Copy values from
the crawl-returned page-evidence sidecar and the file receipts; do not invent
them. The screenshot receipt is the cell itself—do not nest it under a
`screenshot` key.

```json
{
  "captured_at": "<sidecar.capturedAt>",
  "requested_viewport": { "width": 1440, "height": 900 },
  "final_url": "<sidecar.finalUrl>",
  "status": 200,
  "overlay_handling": "none, or exact actions taken before capture",
  "path": ".mist-desktop/source-baselines/<capture>.png",
  "sha256": "<raw PNG sha256>",
  "bytes": 123456,
  "width": 1440,
  "height": 5678,
  "page_evidence": {
    "path": ".mist-desktop/source-baselines/<capture>.page-evidence.json",
    "sha256": "<raw sidecar sha256>",
    "bytes": 12345,
    "media": 42,
    "landmarks": 8,
    "sections": 14
  },
  "documents": {
    "html": {
      "path": ".mist-desktop/source-baselines/<capture>.html",
      "sha256": "<raw HTML sha256>",
      "bytes": 123456
    },
    "markdown": {
      "path": ".mist-desktop/source-baselines/<capture>.md",
      "sha256": "<raw Markdown sha256>",
      "bytes": 12345
    }
  }
}
```

`page_evidence.media`, `.landmarks`, and `.sections` are the exact lengths of
`sidecar.rendered.media`, `.landmarks`, and `.sections`. Require
`sidecar.rendered.sectionsTruncated === false`. Full-page screenshot `height`
is the decoded PNG height, not the requested viewport height. `status`, final
URL, capture time, viewport, and the direct screenshot receipt must exactly
match the sidecar.

The deterministic builder creates each ordered section entry from
`sidecar.rendered.sections`, not from memory or visual guessing. It cites the
sidecar path plus the section's exact `anchor` and copies measured rect,
section `style`, and representative `heading`/`body`/`action` values. Use HTML
and screenshots to understand and name sections for later build steps, but
never hand-invent or rewrite a color, font size, spacing, display/grid value,
selector, or section array when the signed sidecar supplies it. If a needed
section is absent or `sectionsTruncated` is true, recapture.

Every `section_inventory.<route>[i]` must retain, at minimum, this exact signed
subset from the route's desktop sidecar:

```json
{
  "sidecar_path": ".mist-desktop/source-baselines/<capture>.page-evidence.json",
  "anchor": "#exact-sidecar-section-anchor",
  "rect": {},
  "style": {},
  "heading": null,
  "body": null,
  "action": null
}
```

Copy `rect`, `style`, `heading`, `body`, and `action` byte-for-byte as JSON
values. The array length and order must equal `sidecar.rendered.sections`.
Semantic `name`/`type` fields may be added, but never replace the signed fields.

`hero_copy.headline`, `.subheadline`, and `.primary_cta` must be verbatim text
present in both retained Home desktop Markdown and HTML after whitespace
normalization. A genuinely absent field is `null` plus a non-empty
`<field>_reason`. Point `hero_copy.evidence_sources.markdown`, `.html`, and
`.screenshot` to the exact retained Home desktop paths; labels such as
`"verified in source"` are not evidence.

The deterministic builder creates `priority_media.items` from the union of all six rendered sidecars—not from a visual sample. Use the retained HTML/CSS to
verify the rendered sidecars did not omit a visible media element; if it did,
recapture instead of adding an unsigned HTML-regex row. Include every visible:

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

Use this minimum per-element shape:

```json
{
  "route": "home",
  "landmark": "#exact-containing-sidecar-section-anchor",
  "viewport_role": "desktop",
  "media_kind": "image",
  "source_url": "https://source.example/current.webp",
  "source_candidates": [
    "https://source.example/current.webp",
    "https://source.example/large.webp"
  ],
  "source_product_identity": null
}
```

Use `desktop` or `mobile`, never `both`. Repeated elements with the same URL
remain repeated items, and unmatched extra manifest items are forbidden. The
manifest item count must equal the total `rendered.media` element count across
all six sidecars. Assign `landmark` to the smallest signed section whose
rectangle contains the media element's center. For video, also add:

```json
{
  "poster": "https://source.example/poster.webp",
  "video_playback_attributes": {
    "autoplay": true,
    "loop": true,
    "muted": true,
    "playsinline": true,
    "controls": false
  }
}
```

Copy every playback boolean from that exact rendered media element. Do not
default attributes, infer them from a file extension, or add an HTML-regex media
item with invented playback values. If retained HTML exposes media that the
sidecar omitted, recapture so the rendered evidence is complete.

Every `source_url` and `source_candidates[]` value must be one bare absolute
HTTP(S) URL. Split `srcset` strings into individual URLs and remove width/density
descriptors such as `800w` or `2x`; never store an entire comma-separated
`srcset` string as one candidate.

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

Do not create a `package.json`, temporary generator, or runtime dependency to
assemble the manifest. Do not call `run_cli`, `pnpm`, `npm`, Node, Python, or a
downloaded validator for this transformation. Use project file tools and the
first-class Mist validator. Never run package-manager remove commands to delete
a helper; they mutate package dependencies rather than deleting a project file.

## 6. Validate before reporting

The builder stores raw-byte digests and byte counts for all 24 files. Independently
hash the same 24 paths in one `file_sha256` call, then call Mist's first-class,
project-scoped validator:

```text
validate_theme_source_inventory({ manifest_path: "clone-manifest.json" })
```

Do not execute a downloaded validator or require Node, Python, packages, or
other global tooling. The Mist capability reads only project-scoped,
descriptor-held bytes and checks freshness, bounded file sizes,
file/path/hash/size/dimension consistency, sidecar receipts, real HTML, all six
viewports, exact signed section anchors/geometry/styles, source-backed hero
copy, one manifest entry per rendered media element and viewport, matching
video attributes, and coverage of every URL exposed by the rendered sidecars.
Fix every error and call it again.
`SOURCE_INVENTORY_VALIDATION: pass` is required.

The read-only QA reviewer must independently:

1. read the manifest and `.fluidignore`;
2. hash all 24 files in one call;
3. open all six HTML files;
4. view all six screenshots;
5. independently call `validate_theme_source_inventory` against the manifest.

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
