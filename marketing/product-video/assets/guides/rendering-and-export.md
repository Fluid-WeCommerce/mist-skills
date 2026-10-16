# Physical rendering and finished-film delivery

Use this reference when introducing real 3D devices, choosing a path tracer, preparing a full export, or moving that export to another machine. It describes the native Storyboard pipeline verified on October 15, 2026. Inspect the target checkout before relying on its interfaces. The flyover kit includes its licensed Three.js dependency. It includes no MuTracer runtime, device models, denoising weights or private project.

## Choose the layers deliberately

Keep the important UI as native React/SVG: text, controls, charts, pointer and phone chrome. Use actual device geometry for changing perspective, reflections and physical shadows. Derive the screen projection and model pose from the same camera and sampled time. A photographic bezel can still be useful in a fixed view; identify it accurately.

Use a perspective camera for spatial product/device shots. Inspect the front/back convergence; a laptop's near edge should not inexplicably look narrower than its far edge. Keep the screen parallel to its parent device until a deliberate detachment. Orthographic projection remains appropriate for an intentionally diagrammatic view.

Put lights, casters, devices and receiver planes in a common set. Match an object's elevation to its wall/floor shadow, and use a dark reflection flag or lighting contrast to separate pale hardware from a pale surface. A floating oval added beneath an image cannot substitute for the device's actual shadow. For an analytics relief map, use real raised land/pin geometry, a blue water surface, coherent key/fill and restrained staggered pin/count changes. Color, labels and emphasis belong to the target brand. A map on an ordinary webpage can face the reader directly; the film's camera treatment is a separate choice.

Interactive Three.js is useful while arranging shots. MuTracer can supply the converged physical beauty pass in preview or export when its integration exists and the GPU supports it. The renderer selector alone does not implement that integration. Inspect the current scene adapter and confirm the requested backend in actual captures. Native DOM text and a custom Three.js flyover can coexist with MuTracer-lit hardware and backgrounds. Describe that division rather than calling every pixel ray-traced.

## Standard first; offer path tracing after delivery

Use `render.renderer: "three"` for normal previews and the first full export unless the user selected a different mode. The supplied configuration example uses that default. Deliver and verify this standard version before suggesting a more expensive finish; keep it as the baseline.

After a standard delivery, include one short optional-upgrade sentence:

- **Compatible adapter and GPU verified:** “I can also render a higher-quality path-traced version with MuTracer. It takes longer; a short comparison is a useful first step.”
- **Adapter not yet wired:** “A path-traced finish is an option, but this project needs the renderer adapter connected first. I can set that up and test a short comparison.”
- **Runtime/GPU unavailable:** identify that dependency rather than implying a working quality toggle.

Do not start the upgrade because it was offered. Once the user chooses it, retain the approved composition, edit, UI and sound; benchmark a few moving frames on the actual target hardware, inspect the difference, and report the measured or estimated full-render time before a costly full run when needed. Reuse scene data/materials through a compatible adapter; do not regenerate the film with AI just to change the rendering engine. Native UI and raster-only/custom-shader passes can remain composited separately; identify which layers actually gain traced lighting, their trace resolution/samples and the output resolution. A path-tracer label is not proof of visible improvement.

The Mist bridge accepts `three` or `mutracer`; this proves job selection only. For an optional quality config, copy the existing per-machine config, change `render.renderer` to `mutracer`, and pass that separate file through the supported `--config` option only after compatible scene code/runtime/weights are verified. Keep the main config on `three`. Do not create a nominal “HQ” preset whose scene silently stays on raster rendering.

### The two projects previously compared

- [MuTracer](https://github.com/pissang/mutracer): a physically based progressive path tracer, currently WebGPU-first with WebGL2 fallback, Three.js scene conversion and denoising. This is the engine the Rootist-specific physical scene adapter uses. Prefer that existing, tested integration for the optional upgrade when applicable; inspect its pinned version rather than replacing it with upstream defaults.
- [three-gpu-pathtracer](https://github.com/gkjohnson/three-gpu-pathtracer): another physically based Three.js path tracer. Current upstream documentation describes a WebGPU implementation; older WebGL examples/releases are not a reliable description of the current branch. It is an alternative to evaluate, not an installed backend implied by our `mutracer` selector.

Both are path tracers (a form of ray tracing), not two universal high/low quality levels. No general speed/quality winner is established for this video by their READMEs. Compare the same moving scene, hardware, resolution, sampling/denoising and elapsed time before changing engines. Current integration boundary: the Rootist custom physical scene has MuTracer wiring; generic Storyboard DeviceStage and the portable layered-page renderer use Three.js raster rendering until explicitly adapted. The Sunrider trial therefore did not receive traced lighting merely because the editor supports the engine name.

## A deterministic path-tracer adapter

The working integration pins a local MuTracer 0.1.1 runtime and local OIDN weights with their provenance/licenses. For another installation, inspect the available version, supported Three.js/material conversion and denoiser before adapting these patterns. Do not assume the Rootist adapter is part of Storyboard's built-in DeviceStage or install a new dependency without applicable authorization.

Non-obvious requirements from the working adapter:

- Retain one engine and serialize committed GPU jobs per capture page. Reuse render targets and immutable textures; avoid several large scene copies competing for the same GPU.
- Sample all model/light/camera changes from the requested scene/global time. Register model, texture, renderer and convergence promises with Storyboard's render-resource mechanism so capture waits for the requested image. Reject/supersede stale work before presenting it. Initialization or yielding between GPU batches does not give the animation a wall-clock timeline.
- Reset the sample sequence for a new requested frame. The tested final pass uses `converge({samples, samplesPerBatch: 2, sampleSequenceOffset: 0, ...})`; verify this contract against the local runtime. A live progressive preview still needs a completed deterministic frame for export.
- Keep native screens neutral and readable. The working pass uses a neutral emitting screen aperture, a device matte and the native UI above it. Maintain aligned color management and a single visible copy. If a clean wall plate is needed for layered compositing, retain the real beauty pass's shadows/bounce outside the device silhouette; do not replace them with a generic drop shadow.
- Custom material/light conversion may cache results by Three object identity. Update retained converted lights and mark modified environment textures dirty; merely returning a new converter result can leave the old lighting active. Restore temporary visibility/material/environment changes before awaiting GPU work, so the raster scene remains coherent.
- Dispose scene synchronization, render targets, textures and the engine when their owner is released. Keep preview and full-render resources bounded.

The optional quality example proved on the Rootist film:

| Mode | Trace buffer | Visible crop | Samples | Denoising |
| --- | --- | --- | --- | --- |
| Fast preview | 384×224 | 384×216 | 1 | None |
| Settled preview | 960×544 | 960×540 | 24 | JNLM |
| Delivery | 1280×736 | 1280×720 | 12, 3 bounces | OIDN, fixed 512px tiles, local weights |

The final composition is 1920×1080: physical shading is upscaled from the visible trace buffer while native DOM/SVG UI is captured at output size. This is not full-resolution 1080p tracing. The two denoisers explain why sample count alone does not order these modes. Judge the resulting shadows, highlights and moving edges; higher settings are choices to benchmark.

When padding a trace target, adjust the tracing camera's aspect and field of view, then crop the padding symmetrically. For this example, `fovPadded = 2 * atan(tan(fovVisible / 2) * 736 / 720)` with radians. Keep the native screen projection on the intended visible camera. Padding a buffer without this compensation changes the screen fit and creates device/UI drift.

## Benchmark before exporting a film

Use the same scene, moving times, profile, output dimensions and audio policy for comparisons. Record cold startup/shader time separately from warmed moving-frame throughput. Also inspect a second representative scene, such as the relief map. Repeating a cached still is not a moving-shot benchmark.

Confirm the GPU adapter actually used by the renderer. Check competing GPU activity, available memory and whether software rendering is active. Do not stop an unrelated application to improve a number. If the user authorizes pausing a viewport, retain its prior state and restore it; if it is already absent, report that no change was needed.

The verified RTX 3080 Ti example rendered 32 moving Shop frames in 14.32s (0.447s/frame) and encoded their silent 1080p30 clip in 0.50s. The full 50.1s, 1,503-frame film took 590.997s including native encoding. These are observations at the delivery profile above, not a performance promise for another GPU, shot, renderer version or brand.

Use 30fps when it suits the intended motion/delivery. It halves the frame count relative to 60fps at a fixed duration, but does not make each frame cheaper. An approved export FPS override need not alter the saved project's FPS or motion timings. Avoid lowering sampling/quality silently to meet an estimate.

## Include the complete input set

A benchmark bundle may omit footage that later scenes require. Literal `asset()` scans miss dynamic frame names, imported capture-reference JSON, material textures and nested flyover tiles. Keep full required sequences or a verified complete set of referenced frames. Include the selected soundtrack, SFX files/recipes, font files, model textures, local renderer runtime and denoising weights. Preserve attribution records.

The included helper creates a hash manifest of explicitly declared files/directories and verifies the same inputs on the destination. It does not discover dependencies or copy/extract them. From the skill folder, for example:

```sh
python3 scripts/asset_manifest.py create --root /path/to/storyboard \
  --include projects/my-film/project.json projects/my-film/scenes \
    projects/my-film/components projects/my-film/assets \
    projects/my-film/music projects/my-film/sounds \
  --exclude projects/my-film/assets/old-review-exports \
  --output /path/to/transfer/inputs.json
python3 scripts/asset_manifest.py verify --root /path/to/destination/storyboard \
  --manifest /path/to/transfer/inputs.json
```

Replace the example paths and omit nonexistent optional folders. Include shared app dependencies/models separately if the destination lacks them. Exclude old exports, unused pre-rendered device sequences and internal caches only after checking their callers. Do not exclude every image after `frame-00001` merely because a still benchmark passed.

Preflight every scene at its resting/action/transition poses. Inspect the actual pixels and collect failed image, font, model and HTTP requests. An empty scene error list does not catch a missing `<img>`; one observed failure was a black lower laptop screen caused by three absent reference captures. Recover the originals, then recapture the affected scene before starting the full export.

When moving between owned computers, use an available private transfer path and verify bundle hashes. Keep any temporary server narrowly bound, scoped to the intended peer/files and short-lived; close it after delivery. Do not put transfer tokens, machine addresses or private account data in a reusable skill. Sending instructions to another chat still requires the user's authorization. On Windows, inspect how the app constructs Vite filesystem URLs: normalize drive paths to `/@fs/C:/...` for module, asset, diagnostics and output URLs as needed, in an isolated copy. A working Mac absolute path is not portable evidence.

## Native export and recovery

Discover the current export tools/API. The tested native route supports:

```text
POST /api/projects/<actual-project-id>/renders
{"scale":1,"fps":30,"renderer":"three"}
GET /api/projects/<actual-project-id>/renders
```

Track the returned job ID through rendering, encoding and `done`; check its actual `framesTotal`, dimensions, FPS, output and renderer. The current app runs one MuTracer worker. Preserve useful frame/audio checkpoints if supported. The tested Windows copy added isolated JPEG/native-mix checkpointing; that feature is not guaranteed in another checkout. Any resume must match the complete input manifest, render profile, frame time and format rather than mixing old/new frames. Preserve failed evidence and earlier approved exports.

Use the native soundtrack/SFX mixer, retaining shared event clocks and selected gain. Do not flatten independent captures into a silent movie or remux a mismatched older audio timeline. Measure the final encoded audio too. The Rootist mix measured −14.7 LUFS integrated and −4.5 dBFS true peak with 55 cues; those document this film and are not universal delivery targets. Comfortable clicks/sprays still require listening when available.

## Validate and package

Use the included verifier on the actual encoded file. `--decode` performs a full FFmpeg video/audio decode. This checks file integrity and explicit format expectations; it cannot judge composition, motion or sound taste.

```sh
python3 scripts/verify_video.py /path/to/movie.mp4 \
  --width 1920 --height 1080 --fps 30 --duration 50.096 \
  --frames 1503 --require-audio --decode --report /path/to/checks.json
```

Use the new project's real duration/frame count. Inspect scene representatives, special interactions, final card and adjacent boundary frames from the encoded output. At 30fps, neighboring moving frames differ naturally; report the comparison threshold and measured differences without claiming identical seams. In the proved film, the late phone handoffs matched closely, while two earlier visible cut jumps remained review items. Successful encoding and matching source hashes did not resolve those editorial issues.

Return the finished MP4 with a poster/contact sheet and a small record of inputs, selected renderer/profile, output format, render time, audio and known review items. After private transfer, compare the returned file's hash to its source. Refresh the review player's source, duration/FPS, download and draft attachment together; retain the old export. Keep unsent drafts and sending authorization distinct. Stop only render/transfer processes started for the task and preserve a way to reopen the editable project.
