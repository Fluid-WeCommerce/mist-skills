# Dev preview and visual-parity protocol

This is the visual gate shared by theme clone and theme refine. It compares the
live source and the local Fluid preview at matched viewports using named
semantic landmarks.

Equal-scroll-offset screenshots are invalid evidence. If the clone hero is
180px too tall, every later equal-offset pair compares unrelated content.

## Required route and viewport matrix

The flagship onboarding workflow must capture:

| Route | Source                                         | Local preview                   |
| ----- | ---------------------------------------------- | ------------------------------- |
| Home  | canonical homepage                             | `/`                             |
| Shop  | primary collection/shop index                  | `/shop` or the real local index |
| PDP   | flagship or most complex multi-variant product | `/home/products/<fluid-slug>`   |

Capture every route at:

- desktop: `1440 × 900`
- mobile: `390 × 844`

Tablet is optional and never substitutes for desktop or mobile.

## Capability contract

### In Fluid Mist

Use Mist's managed capabilities. They are available on a fresh computer and do
not require a global Fluid CLI, Node package, browser binary, or user-owned
Firecrawl key:

- `crawl` — source content, rendered HTML, exact-viewport full-page screenshot,
  final URL, and HTTP status
- `start_preview` — long-lived theme dev server with port management
- `screenshot_preview` — local same-origin navigation plus exact-viewport
  viewport/full-page capture
- `preview_state` — exact local/prod URL awareness
- `read_preview_console` — browser warnings, exceptions, and failed resources
- `read_local_server_logs` — theme-dev stdout/stderr
- `run_cli` — bounded one-shot commands such as `fluid --version`,
  `fluid theme --help`, and `fluid theme push`

Use `start_preview`, not `run_cli fluid theme dev`. `run_cli` is intentionally
bounded and a dev server is long-lived.

Do not use `command -v fluid` as Mist's health check. A stale ambient shim can
be broken even while Mist's bundled CLI is healthy. Verify with:

```text
run_cli({ command: "fluid", args: ["--version"] })
run_cli({ command: "fluid", args: ["theme", "--help"] })
```

### Outside Fluid Mist

A project-local Playwright harness is an acceptable fallback when it is already
locked in the project. Do not require a global Playwright or global Fluid CLI.
If neither managed capture nor a project-local browser exists, report
`STATUS: needs-review — visual capture capability unavailable`; do not silently
convert a code review into a visual pass.

## Step 1 — Build the visual route manifest

Write `clone-manifest.json` before implementation:

The manifest and any `baselines/` directory stay local. Preserve the theme's
existing `.fluidignore` rules and add exact entries for `clone-manifest.json`
and `baselines/` before starting theme dev. Without those entries, the live
watcher treats QA files as theme resources and repeatedly reports rejected
uploads.

```json
{
  "visual_routes": {
    "home": {
      "source_url": "https://source.example/",
      "built_path": "/",
      "landmarks": [
        {
          "id": "hero",
          "source_selector": "main section:nth-of-type(1)",
          "built_selector": "[data-section-id=\"home_hero\"]"
        },
        {
          "id": "product-family",
          "source_selector": "main section:nth-of-type(2)",
          "built_selector": "[data-section-id=\"home_products\"]"
        }
      ]
    }
  }
}
```

Create selectors from rendered HTML inspection, not guesses. Every visible
source section gets one landmark in source order. Stable built selectors should
use the template section instance ID.

Each route also records:

- source page title and final URL
- source HTTP status
- ordered section headings
- image/video URLs and focal/crop notes per landmark
- overlay handling performed during capture
- current source and built evidence paths/timestamps

## Step 2 — Capture clean source baselines

For each source route, call `crawl` twice. Keep global chrome:

```json
{
  "url": "https://source.example/",
  "formats": ["markdown", "html", "screenshot"],
  "only_main_content": false,
  "screenshot_options": {
    "full_page": true,
    "quality": 90,
    "viewport": { "width": 1440, "height": 900 }
  }
}
```

Repeat with `{ "width": 390, "height": 844 }`.

If a geo, cookie, age, or newsletter dialog obscures the page:

1. inspect the returned HTML;
2. identify a concrete close/decline/continue selector;
3. repeat the capture with a constrained `click` action and a short `wait`;
4. record the selector and action in the manifest.

Example:

```json
{
  "actions": [
    { "type": "wait", "milliseconds": 750 },
    { "type": "click", "selector": "dialog button[aria-label=\"Close\"]" }
  ]
}
```

Never guess selectors and never delete all dialogs indiscriminately. A product
drawer or mobile menu may be legitimate page content.

A source baseline is invalid when:

- the final URL is not the requested route;
- the status is not 200;
- an overlay hides priority content;
- the screenshot is blank or only a loading skeleton;
- fonts or primary images did not finish loading;
- the screenshot is stale from before the latest source crawl.

AI-friendly Markdown is the copy/data layer, not the visual truth. It commonly
omits navigation, responsive composition, media behavior, and exact spacing.

## Step 3 — Start and diagnose the local preview

Call `start_preview` from the theme project and wait for the ready result. Let
Mist allocate the port.

Before visual work:

1. call `preview_state` and confirm the URL is local;
2. call `read_local_server_logs`;
3. call `read_preview_console`;
4. fix Liquid/runtime errors before comparing pixels.

Fluid detail routes require the credit segment:

```text
/home/products/<fluid-slug>
/home/collections/<fluid-slug>
/home/pages/<fluid-slug>
/home/posts/<fluid-slug>
```

A bare `/products/<slug>` response can be a stale CDN artifact and is not route
health evidence.

## Step 4 — Capture the local matrix

For each route and viewport:

```json
{
  "mode": "full",
  "path": "/home/products/example-slug",
  "width": 1440,
  "height": 900
}
```

Repeat at `390 × 844`. The result must report:

- final local URL and HTTP status after navigation;
- exact temporary viewport;
- full document dimensions;
- whether horizontal overflow exists;
- saved evidence path(s).

Capture a viewport-only image as well when a critical interaction or crop needs
full-resolution inspection.

If the installed Mist build does not yet accept `width` with `mode:"full"`,
take an exact viewport image plus an un-sized full-page image and mark the
width mismatch as a tooling limitation. It cannot satisfy the strict
near-pixel-perfect gate.

## Step 5 — Compare semantic landmarks

For each named landmark compare:

1. presence and order
2. content and primary imagery
3. background and foreground color
4. width, height, padding, and gap
5. heading family, size, weight, line-height, and tracking
6. image aspect ratio, crop, and focal point
7. controls, dividers, radii, shadows, and icon scale
8. desktop-to-mobile composition change

Use the source and built HTML inventories to pair landmarks. Do not pair by
scroll position.

Classification:

- **major** — missing/reordered landmark; wrong main imagery/copy; broken route;
  wrong page type; unusable mobile composition
- **minor** — visible spacing/type/color/crop mismatch that does not change the
  information architecture
- **note** — browser rendering or source animation difference with no practical
  fidelity impact

Fix root causes in this order:

1. missing/wrong data or template structure
2. wrong assets or font files
3. wrong theme tokens
4. container/grid geometry
5. component details
6. micro-spacing

Do not paper over a structural mismatch with arbitrary CSS offsets.

## Passing gate

The final evidence must be captured after the final code change and satisfy:

- all six route/viewport combinations are present and current;
- all routes are HTTP 200 and render the correct template;
- zero priority landmarks are missing or reordered;
- zero majors remain;
- at most two itemized minors remain per priority route;
- landmark width/height/padding/gap are within 5% of source where the same
  responsive composition applies;
- copy, primary imagery, price, and product options match source data;
- no horizontal document overflow at 390px;
- no Liquid/runtime errors in local logs or preview console;
- every touched theme file passes `theme_audit.py`.

If five refine rounds end without this gate, report `STATUS: cap-reached` and
`needs-review`. Cap-reached is not a passing flagship launch result.

## Performance and slow-network behavior

- Capture source baselines once and reuse them until their recorded source
  timestamp changes.
- Keep no more than three remote captures in flight.
- Retry transient 429/5xx/timeouts with bounded exponential backoff and jitter.
- Persist each successful route/viewport result immediately.
- Do not keep every full-resolution screenshot in model context. Save originals
  on disk and attach only the current comparison pair.
- On lower-end computers, run one local preview and one capture at a time.
- If the network drops, resume missing matrix cells rather than recapturing all
  successful cells.

## Required STEP_OUTPUT

```text
STATUS: pass | needs-review | cap-reached
SOURCE_MATRIX: 6/6 current | missing [...]
LOCAL_MATRIX: 6/6 current | missing [...]
ROUTES: home=..., shop=..., pdp=...
MAJORS: [...]
MINORS: [...]
RUNTIME: preview/log status
OVERFLOW: per-route mobile result
EVIDENCE: source and local paths/timestamps
NEXT: highest-impact unresolved root cause, or none
```
