# Pixel-perfect page reconstruction contract

This is the shared execution contract for every Fluid page-clone skill. A page
archetype reference may add requirements, but it may not weaken these gates.

The unit of work is **one source route mapped to one local Fluid route**. Do not
hide unfinished routes behind a broad “site clone complete” statement.

## Required inputs

Resolve these before editing:

- `source_url`: the exact public route to copy
- `built_path`: the exact local Fluid preview route
- `page_type`: the source and Fluid archetype
- `manifest_key`: the entry under `clone-manifest.json.visual_routes`
- `project_path`: the active Fluid theme checkout

In an onboarding workflow, read them from caller context, dependency output,
and `clone-manifest.json`. Do not ask a sleeping user to repeat known inputs.
When run standalone and an input is genuinely missing, ask only for that input.

## 1. Inspect before implementing

Call `crawl` for the exact source route at both required viewports:

```json
{
  "url": "<source_url>",
  "formats": ["markdown", "html", "screenshot"],
  "only_main_content": false,
  "screenshot_options": {
    "full_page": true,
    "quality": 90,
    "viewport": { "width": 1440, "height": 900 }
  }
}
```

Repeat at `390 × 844`. Use the returned final URL and HTTP status. A redirect
to the homepage is not proof that a requested detail route exists.

If a cookie, country, age, or newsletter overlay obscures content, inspect the
returned HTML, repeat with one concrete click selector, and record the action.
Never delete every dialog or guess a selector.

Persist the exact source baseline object returned by Mist: local path,
timestamp, SHA-256, byte count, decoded dimensions, requested viewport, final
URL/status, and overlay handling. A hosted URL or prose label is not durable
evidence.

## 2. Build a source truth table

For every visible semantic landmark, store this in route order:

```json
{
  "id": "stable-landmark-id",
  "source_selector": "<selector inspected from rendered HTML>",
  "built_selector": "[data-section-id=\"...\"]",
  "visible_copy": ["Exact heading", "Exact supporting text", "Exact CTA"],
  "links": [{ "label": "Exact label", "href": "/exact-target" }],
  "media": [],
  "desktop_geometry": {},
  "mobile_geometry": {},
  "interaction_states": []
}
```

`visible_copy` is exact source wording, punctuation, capitalization, price
formatting, and CTA text—not a summary. Normalize only runs of whitespace when
comparing. Never “improve” source copy or substitute generic base-theme text.

Record the ordered normalized strings and a SHA-256 of their JSON encoding as
`source_copy_sha256`. Record the local strings and hash after implementation.
The hashes may differ only for explicitly documented dynamic values such as a
signed-in greeting or live inventory count. Every allowed difference must name
the source string, local string, and reason.

Inspect source HTML for all of:

- `img` plus `srcset`/lazy variants
- `picture source`
- `video`, nested `source`, `poster`, autoplay, loop, muted, and playsinline
- desktop/mobile media-query variants
- SVGs and icons
- headings, buttons, links, prices, badges, labels, and empty states
- menus, drawers, accordions, tabs, carousels, filters, and forms

Markdown is copy assistance, not visual or media truth. Rendered HTML and
screenshots decide.

## 3. Preserve priority media

Every priority source image and video belongs in the route manifest with its
exact source URL, landmark, viewport, and expected behavior.

Use direct remote DAM ingestion first:

```text
dam_upload({ url: "<exact-public-url>", create_media: true })
```

Do not omit a video merely because it looks large. Do not infer a size ceiling
from a previous run. If DAM reports an actual size rejection, call
`compress_media({ url: "<exact-public-url>", ... })`, then immediately upload
the returned temporary path with `dam_upload({ path: ... })` before it expires.
Record original bytes, compressed bytes, settings, and the DAM URL.

For responsive video, implement explicit desktop/mobile `source media`
selection or an equivalent deterministic pattern. QA must prove the live
`currentSrc`, decoded dimensions, and readiness at both widths. A poster image
is a fallback, not a substitute for a source video.

## 4. Implement with Fluid primitives and real data

- Reuse the canonical base-theme section/component when it can express the
  source accurately.
- Extract a shared component only when two routes really share behavior.
- Keep dynamic Fluid resources dynamic. Do not hard-code product cards,
  collection membership, prices, inventory, signed-in state, or blog records
  just to match one screenshot.
- Preserve source section order and responsive composition.
- Use source copy and DAM assets. Remove every unrelated starter placeholder.
- Keep page templates structural; section presets own blocks.
- Do not hand-roll the canonical PDP data section.
- Push theme files before `create_page`; creating a page first can create
  application-theme templates that a later push treats as orphans.

Fix root causes in this order:

1. wrong source/data mapping
2. missing or reordered landmarks
3. wrong asset/font
4. wrong container/grid geometry
5. component details
6. micro-spacing

Arbitrary offsets that only line up one screenshot are a regression, not a fix.

## 5. Run the local proof loop

Start one managed preview with `start_preview`; let Mist own the port. Do not
spawn a second theme server with `run_cli`.

Before comparison:

1. `preview_state` — confirm local environment and exact route
2. `read_local_server_logs` — zero unresolved Liquid/runtime errors
3. `read_preview_console` — zero unresolved exceptions or failed priority assets

For the route under test:

1. `screenshot_preview(mode:"full", path:<built_path>, width:1440, height:900)`
2. `read_preview_dom(path:<built_path>, mode:"all")`
3. repeat the screenshot at `390 × 844`
4. inspect critical crops with viewport captures when needed
5. exercise inspected disclosure/tab/menu selectors with `interact_preview`
6. recapture the changed state

Exact viewport tools make manually collapsing Mist sidebars unnecessary.
Interactive work may visibly drive the user’s pane; background workflow work
uses the isolated project-scoped preview and must not hijack it.

Compare source and local landmarks by identity, never equal scroll offset.
Check:

- presence and order
- exact normalized visible copy
- primary media and breakpoint source
- color and typography
- width, height, padding, gap, crop, and focal point
- controls, radii, dividers, shadows, and icon scale
- desktop-to-mobile composition
- expected interactions

After each meaningful fix, recapture only the affected route/viewports. The
final proof must be newer than the final code change.

## 6. Hard passing gate

The page passes only when all are true:

- source and local desktop/mobile evidence is current and durable
- requested and final routes match and local HTTP status is 200
- every source landmark exists once, in order
- exact source wording is present, with every allowed dynamic difference listed
- zero source landmarks use unrelated placeholder copy or media
- every priority image/video is DAM-backed and ready; zero failed/pending media
- responsive video `currentSrc` and decoded orientation match each viewport
- zero majors remain
- at most two itemized minors remain
- comparable landmark geometry is within 5% of source
- no horizontal document overflow at 390px
- required interactions were exercised from rendered selectors
- console and server logs have no unresolved route/runtime/asset errors
- `theme_audit.py` passes for touched theme files

“Looks good,” “close enough,” a successful build, or a prose QA statement is
not a pass.

## Performance and resilience

- Reuse current durable source baselines; do not recrawl successful cells.
- Keep at most three remote crawls/uploads in flight.
- Persist each successful artifact immediately.
- On slow Wi-Fi, resume missing cells rather than restarting the route.
- Keep one local preview and one capture active on lower-end computers.
- Use responsive DAM assets and avoid shipping desktop media to mobile when the
  source provides a mobile variant.

## Required output

End with:

```text
PAGE_OUTPUT: {
  page_type,
  source_url,
  built_path,
  source_status,
  local_status,
  source_copy_sha256,
  local_copy_sha256,
  allowed_copy_differences:[],
  source_evidence:{desktop,mobile},
  local_evidence:{desktop,mobile},
  landmarks_total,
  landmarks_matched,
  priority_media:{expected,ready,failed,pending},
  interactions:[],
  majors:[],
  minors:[],
  runtime_errors:[],
  status:"pass"|"needs-review"|"cap-reached",
  next
}
```

If five focused repair rounds cannot satisfy the gate, return `cap-reached`.
Never turn that into a pass.
