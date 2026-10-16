# Layered landing-page flyover

Use this for an establishing shot that turns the actual landing page into a physical sheet, flies close past selected details, rises to reveal its length, then returns to the hero and joins the product walkthrough. A brief version can precede a monitor interaction. The latest Rootist film allocates 7.6 seconds to this shot, with movement beginning half a second under the departing scene. Those timings and its brand assets are examples to adapt.

When adapting the Rootist-style site film, recommend this as a signature treatment while planning. Give it actual scene IDs and a time budget in the treatment inventory, and name the new company's page and lifted subjects. Preserve its intended depth, pace and handoff as the film changes. A simpler screenshot pan should be recorded as a changed treatment rather than counted as the layered flyover. Other films can choose a different establishing idea when their brief supports it.

## Prepare the page as layers

Freeze the approved page at a known viewport and record its width, total height and hero height. Keep exact source copy, images, SVG logos and fonts. Capture after fonts and lazy imagery settle; disable only autonomous source animations for the capture. A live website is an observation source, not the production scene runtime.

Represent the page with an opaque backing, static page tiles, and a few independently lifted assets. For each tile record `file, x, y, width, height` in the same page coordinate system. For lifted pieces also record `id, kind`, the visible bounds, and the cropped texture bounds. Texture padding is not the object's painted bounds. Remove the lifted asset from the flat underlay so two copies do not become visible as it tilts. Preserve unselected detail in the page tiles.

Choose a small number of subjects whose depth helps tell the story: a hero product, a photo, a testimonial or a feature card. Give cards modest solid edges and photographs thinner ones. Let objects lift as the camera approaches and settle after it passes. Keep text-heavy UI mostly on the page so it stays legible. Do not add floating logo squares or a new end title unless requested; the approved example resolves back into the source hero itself.

## Capture and renderer helpers

The kit includes the complete company-neutral page renderer, native React wrapper, camera, Three.js r185 (MIT), and a standalone DOM-to-layer capture tool. Capture uses an existing system Chrome/Edge/Chromium through a temporary isolated profile and the bundled pngjs7 codec (MIT). It needs Node22.12+, without the full Storyboard editor, Playwright, npm installation, a browser download or a paid service. The portable player supplies React, the native runtime and licensed device models. Company source media remain project inputs.

- After portable player materialization, run `npm run video -- capture --config capture-config.json`. The setup copies the capture helper and its dependencies with the player. Alternatively run the exact returned `assets/flyover/capture-layers.mjs` path through a declared project script. Preserve its sibling helper and vendor directory.
- In the JSON config set absolute `outputDir` (a new destination), the approved HTTP(S) `sourceUrl`, actual `heroSelector`, and `pieces: [{id,kind,selector,index?}]` discovered from that page. Supported kinds: photo, card, chip, bottle, testimonial. Use `width:1440`, `viewportHeight:900`, `deviceScale:2`; optional `chromiumExecutable` or VIDEO_BROWSER selects an existing browser, while `freezeHeader`/`freezeStyles` retain the real source header/animation state. There is no `runtimeDir` dependency. Use a small number of real subjects; overlapping selections must become one real parent assembly. A piece's painted shadows/filters must fit its selected bounds; otherwise freeze that effect or select the full source parent rather than inventing pixels.
- Capture makes only GET/HEAD requests; writes and MP4 requests are blocked. It does not use a signed-in browser profile, bypass access restrictions or submit site actions. It settles fonts/lazy images, freezes video posters and CSS animation, measures source geometry, then captures the source and the underlay with pieces hidden. Missing source images, out-of-bounds/overlapping pieces or nonexact reassembly fail; inspect recorded source errors and resource failures. Captures are bounded to20000CSSpx/100million pixels; select a shorter source for larger sites. A failed capture removes its own new output and never replaces a prior approved capture.
- It produces `LandingLayers.json`, base tiles, padded piece textures, `source-full.png`, `base-full.png`, `frozen-source.html` and `capture-report.json` with dimensions, selected bounds, source URL, blocked/failed requests, tool provenance and exact pixel-reassembly proof. Keep the source evidence local; it is not a portable offline website or a general reuse license. Copy only layout/tiles/pieces needed by the shot into the video assets. Capture failure is not permission to approximate the UI or silently downgrade the layered flyover to a screenshot pan.

- Copy `create-flyover-renderer.mjs`, `example-camera.mjs`, `FlyoverLayer.tsx` and `vendor/` into the project's `components/flyover/`, retaining names and MIT license. Copy only the declared tiles/pieces/layout into the production assets folder; keep large source evidence beside the review outputs.
- Import `* as THREE from './flyover/vendor/three.module.js'` in the host component and pass it as `three` to `FlyoverLayer`. Supply `t`, frozen `layout`, `assetRoot`, the measured destination `landingQuad`, and the existing screen `matrixForQuad` helper. The wrapper registers textures with Storyboard, synchronously samples the supplied time and disposes its GPU resources.
- Render destination hardware behind the layer near the handoff. Reuse this assembly with negative local time during the outgoing scene's pre-roll. Pass a stable `sourceTime` function when adapting the duration; changing duration alone does not retime the camera's phases.
- `film` can override `width,height,focal,fitMargin`. Match its aspect to the destination aperture, and account for any initial crop with `startQuad` plus `fitMargin` so the overview stays wholly in frame. The renderer remains calibrated to a1440px-wide source; changing only source width is not supported.
- Optional `handoffTexture` is an exact frozen native-UI tile, resolved relative to `assetRoot`. It replaces the source hero while the page is still distant, before the return zoom; this avoids blending two different text layouts during the close return. Picture/crop must still be reviewed. Set `sceneScale` to1.5 or2 for offscreen antialiasing according to measured GPU cost. This pass is Three.js raster rendering, not MuTracer.

The standalone capture was exercised against the actual Sunrider1440×6302 public page at2× with thirteen selected pieces and five base tiles, using system Chrome and no Storyboard installation. It reassembled with zero changed pixels. The prior helper was also exercised on this source. The initial seven-piece capture and later thirteen-piece depth refinement both reassembled with zero changed pixels. That validates this capture and integration, not arbitrary websites, fonts or every aspect ratio. Inspect the actual shot and encoded movie for every new company.

## Camera and timing

Copy [assets/flyover/example-camera.mjs](../flyover/example-camera.mjs) when this particular move is useful. It is the camera math from the working Rootist shot, with no Three.js or browser dependency. It assumes a **1440-pixel-wide source page**, a **1920×1080 output**, and `layout.height` / `layout.heroHeight` in source pixels. It provides `cameraPose(t, layout)`, `flightY`, and `timeAtPageY`. This is a fixed example to adapt, not an aspect-ratio-independent camera system or a complete renderer.

The source camera clock has these phases:

| Source time | Move |
| --- | --- |
| 0–7.75s | Low perspective flight down the page; integrate the smooth speed profile instead of accumulating velocity per frame. |
| 7.75–9.25s | Overlapping crane rise; retreat in log distance, reduce tilt and pin the page's lower edge to limit composition drift. |
| 9.25–9.47s | Brief full-length overhead view. |
| 9.47–9.97s | Return to the hero, flatten the raised layers and retract the page backing/mask. |
| After 9.97s | Exact hero pose for the monitor handoff. |

For another source width or output aspect ratio, recompute the focal distance, fitting distance, focus target and ending hero crop together. Do not only change the canvas dimensions. Perspective convergence belongs to the actual camera; an orthographic product/device view or a skewed screenshot is a different look.

The current sample exports `exampleSourceTime(t)` and `EXAMPLE_TIMING`: a 0.5s pre-roll, a 1.5× source clock through the low flight, a smooth positive-velocity transition into the footer, then the original 1.5s rise, 0.22s full-length view and 0.5s hero return. The scene has a small handoff allowance within its 7.6s duration. It starts at distance 1640 in this source coordinate system, leaving more room before the swoop. Protect these readable phases when fitting the shot into a short film.

```js
import { cameraPose, exampleSourceTime } from './example-camera.mjs';
// t is local to the flyover scene; draw this same assembly in the outgoing
// scene with t = previousSceneT - previousSceneDuration during the pre-roll.
const pose = cameraPose(exampleSourceTime(t), layout);
```

Resolve each interval directly from `SceneProps.t`. For lifted pieces, `timeAtPageY(pieceCenterY, layout)` supplies a source-time arrival; use that same source clock for their lift and settle. Keep related edges, photo planes and shadows on one assembly clock. A frozen source image can provide detail, but independently moving UI must remain a separate layer.

Keep the source clock moving across the scene boundary. Establish the page behind departing foreground objects, then let the camera continue through it; do not fade to a stationary establishing pose and start a second move. Ease the travel speed itself, give the viewer space before the swoop, and protect the rise/overview/return phases when adjusting total duration. Changing only the scene duration can rush the flight or create an unintended pause. Check both sides of the cut and a few moving frames around it.

## Shade and render without popping

Use a perspective Three.js scene with an actual page backing, elevated piece geometry, a consistent key light and a shadow receiver. A depth-of-field pass can soften near/far layers while keeping the subject in focus. Reuse the film's lighting language; a flashlight scan is an optional, separate treatment and was rejected for the Rootist film.

The long overhead view is the fragile point:

- Keep the backing physically behind the page textures; do not place nearly coplanar surfaces at the same depth. The example backing is around `z=-10`, tiles at `z=.1` and its receiving layer at `z=.8` in source-pixel units.
- Fit clipping planes to the current camera distance. The working renderer uses `near=max(100, distance*.12)` and `far=distance+pageHeight+3000`, then updates the projection matrix and the depth-of-field pass's near/far uniforms together. A fixed 50–100000 range lost small layer separation when the camera rose far away.
- Use mipmaps and anisotropy for page textures. Default canvas antialiasing does not antialias an offscreen render target: the renderer supports1.5× or2× before its depth-of-field/downsample pass. Inspect the actual full-page view for shimmer rather than assuming the canvas flag fixes it.
- Use explicit depth/order rules for alpha cutouts and solid edges. Retract or fade nonhero pieces, backing, receiver and masks together during the return. Avoid one-frame visibility thresholds where an object is still noticeable.

Initialize textures once, register their readiness with Storyboard's render-resource mechanism, and synchronously redraw the requested time. Dispose of geometries, textures, render targets and renderer on unmount. Do not use an autonomous animation loop, wall-clock randomness, or live DOM capture in the final scene.

## Join the next shot

Derive the target aperture from the actual monitor screen geometry. Keep the destination monitor behind the flying page, then translate/scale the **whole page assembly** into that aperture. In the last moving frames, hand off to the native hero only after position, crop, scale, orientation and scroll match. Keep one visible copy. Supporting devices can enter after this handoff; a new panel should not suddenly cover established foreground subjects.

If the flyover adds time to an existing film, shift the following demonstration and its sound cues together. Preserve their local interaction order and quiet mix. Update shared lighting clocks for the inserted hold so later light poses do not drift. Change scene duration through the running editor's supported tools/API.

## Verify and reuse honestly

Inspect frames during the close flight, lift, crane rise, full-length hold, hero return and aperture handoff. Seek to the end, back to a middle frame and back again; camera, layer pose, shading and visibility must resolve to the same result. Compare the destination against its native first frame. Check the encoded video too, including the tiny full-page view: preview success is not final-export proof.

Update the treatment inventory with the produced scene/time range and the actual reviewed images or focused clip. Confirm independent lifted geometry/parallax, coherent shadows, a readable close pass and a stable full-page rise/return. Mark absent or incomplete phases accurately; successful compilation, job completion or decode cannot substitute for the chosen treatment being visible in the film.

The bundled camera was checked against the working shot across its phases and out-of-order seeks. That validates the camera sample, not a new brand's layer extraction, renderer, typography, depth of field or final composition. Company page captures and private account access are not bundled. The package does include Three.js and the portable player’s licensed device models and credits; those do not grant reuse rights to captured company media.

When the Rootist checkout exists, the implementation is in `components/LandingFlyover.tsx`, `LandingFlyoverClock.ts`, and `components/flyover/{FlyoverCamera.js,FlyoverRenderer.js,LandingLayers.json}`. The corresponding frozen assets are under `assets/landing-flyover/`. Inspect those files rather than assuming they are installed elsewhere.

## Give the camera something dimensional to reveal

Plan lifted subjects across the meaningful length of the page, not just its first product row. Inspect a close pass in the early, middle and late flight. If a late section is flat, find a real source photo/card/panel whose separation helps the story; do not add invented UI or target a fixed object count. A long camera move and a valid layer manifest alone do not establish the selected treatment.

Vary depth deliberately: keep most cards modest, choose a few photographic foreground accents, and let a social/testimonial group rise in a small stagger. Sunrider's correction expanded seven mostly early/shallow pieces to thirteen source-derived subjects; Rootist used sixteen different subjects. Those counts and brands are examples, not a required template. Preserve approved camera pacing while strengthening the layer choreography.

The renderer accepts optional `motion` per piece, with `lift` (source pixels), `angle` (degrees), `offset` (source-clock seconds), `thickness` (source pixels), `pivot` (`center` or `bottom`) and `radius` (source pixels). For example:

```json
{"motion":{"lift":60,"angle":24,"offset":0.1,"thickness":14,"pivot":"bottom"}}
```

Tune to the subject's dimensions, lens and narrative role. Large source photos can justify a stronger angle than dense UI. Bottom pivots raise the centre by the rotated half-height and preserve the lower page edge, so a tall subject does not intersect its backing. `lift` is clearance above that hinge, not its final centre height; inspect the top edge near the lens before increasing it. Staggers use the same source clock as camera arrival, never an independent timer.

The camera's depth-of-field focus follows the raised subject near frame centre and returns smoothly to the page before the rise. Foreground softness should convey travel without hiding the demonstrated subject. Keep the camera movement itself continuous; changing focus/lifts does not require a new zoom or pause.

New captures record the measured source corner radius. The renderer clips raised textures to it, preventing the original section background from appearing as coloured rectangular corners. Captures without radius metadata keep their original silhouette. If an overlapping text/image group cannot be isolated faithfully, capture the real parent assembly or keep it on the base; do not duplicate the overlaid text on two layers.

Keep source reassembly proof separate from motion proof: exact page reconstruction does not prove good depth, focus or pacing. Inspect the strongest lifts, rounded edges, late flight, overview and return; repeat an intermediate seek and compare the outgoing handoff with the native incoming frame. Retain requested rendering/publication holds.
