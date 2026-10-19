# Local Mist renderer bridge

This Node 22.12+ CLI connects an active Mist project to an **already running local Storyboard**. Its API commands need no package dependencies; optional frame capture uses the configured Storyboard checkout's already-installed Playwright and Chromium. It does not install packages, start or stop services, publish media, or adopt an existing project. The native app's permitted `npm run` or `pnpm run` tool can invoke the installed script.

## Configure a project

1. Copy `renderer.mjs` and `capture.mjs` into the active Mist project at `tools/product-video/renderer.mjs` and `tools/product-video/capture.mjs`.
2. Merge `package-fragment.json`'s `video` script into that project's existing `package.json`. Preserve its other scripts and dependencies. No package installation is needed.
3. Copy `renderer.config.example.json` to the project root as `renderer.config.json`. Set `projectsDir` to the actual running Storyboard `projects` directory. The bridge checks it against `/api/info`; it rejects remote origins and redirects. Keep `three` as the normal default; select `mutracer` only for a user-chosen optional quality pass. Selecting MuTracer does not convert arbitrary Three.js scene code into path-traced materials: use a compatible stage and verify the result. `doctor` reports API connectivity and optional file checks; it does not prove GPU capability, path-tracer compatibility, visual quality, or a finished render.
4. Author a native Storyboard source tree in `video/`:

```
video/project.json
video/art-direction.md
video/scenes/intro.tsx
video/scenes/product.tsx
video/components/...
video/assets/company-logo.svg
video/music/...          optional
video/sounds/...         optional
```

Use `project.example.json` as the manifest shape. Each listed scene must have `scenes/<id>.tsx`. Put shared code in `components/`; do not import one scene from another (native scene IDs may be mapped during synchronization). Code uses native `SceneProps.t` and Storyboard imports. Art direction, all files below `components`, `assets`, `music`, and `sounds`, and listed scene sources are synchronized. Project metadata, scene order, durations, and art direction use native APIs. Symlinks and escaping paths are rejected. List indispensable media/model files in `requiredAssets` to catch missing files before a renderer project is created. Standard device models can be copied from the configured runtime into `video/assets/models/` after their availability and license have been checked, then listed in `requiredAssets`; the skill package need not distribute those binaries or any other company's media.

For optional runtime fingerprint checks, set an explicit `runtimeDir` in the per-machine configuration and `requiredRuntimeFiles` to an array such as `[{ "file": "package.json", "sha256": "<expected 64-character SHA-256>" }]`. Each path is relative to that runtime directory. An omitted expected hash records the current hash without claiming the runtime matches a known version. Configured model files can be checked the same way. These are local file checks, not a GPU test.

For a soundtrack, set `music` to `{ "file": "track.wav", "start": 0, "volume": 0.3 }` and include `video/music/track.wav`. The bridge imports the actual file using Storyboard's audio API and verifies the selected native track has matching bytes. Scene SFX live in `video/sounds` and use native sound cues. A silent input intentionally renders without a soundtrack; the bridge does not invent one.

## Run from the active Mist project

```
npm run video -- doctor
npm run video -- sync
npm run video -- check
npm run video -- frames --times 0,2,4
npm run video -- submit
npm run video -- status
npm run video -- collect
npm run video -- verify
```

`sync` creates a new isolated native project on its first run; later syncs affect only that bridge-owned project. It returns an editor URL. It never submits a render. `check` validates synchronized source hashes and native scene compilation without rendering. `submit` performs those checks, submits the native background render, saves the real job ID, and returns immediately. Poll `status` in later turns rather than keeping one tool invocation waiting. `cancel` can cancel only the saved bridge-owned job. `collect` requires that exact job to report `done`, copies its nonempty MP4 into `exports/`, and verifies SHA-256. It preserves existing exports and never publishes or uploads them. Run `verify`, then watch/listen to the result before saying the video is ready.

`frames` needs the explicit `runtimeDir` in the per-machine configuration. It launches and closes its own browser using that runtime's existing `node_modules/playwright` and `.storyboard/browsers`; it does not reuse or close the user's tabs. A separately configured `chromiumExecutable` may select an already-installed browser if the runtime normally uses one. `--times` accepts 1 to 4 seconds within the video's duration. Add `--scene <source-scene-id>` for scene-local times, and `--resolution low|normal|high` (default normal = half the canvas dimensions). For example:

```
npm run video -- frames --scene product --times 0,3,7.9 --resolution normal
```

Frame capture checks source hashes/compilation and refuses to compete with any active full Storyboard render. It explicitly passes the configured `three` or `mutracer` selection to native `frame.html`, captures PNGs into `exports/frames/<unique-capture>/`, and writes `report.json` including scene/time, image hashes, and native runtime errors. A report with `ok: false` requires repair; screenshots alone do not prove visual quality. Compatible path-traced scene code is still necessary for MuTracer to affect the stage. Captures stop at their time budget and close their own browser; if a complex scene times out, try one low-resolution frame before increasing quality.

`verify` operates only on the saved, collected output of this bridge's current job. It checks the collected SHA-256, then invokes existing `ffprobe` and `ffmpeg` directly without a shell. It counts actual video frames, checks dimensions, FPS and duration against the completed native job's saved fields, requires an audio stream when a soundtrack was planned, and completely decodes the video and any audio. Expectations come from the submitted job/source snapshot, even if the current video source has since changed. Collected state created by an older adapter is upgraded only when the same completed job and submitted source hash can establish those expectations.

By default the executables are `ffprobe` and `ffmpeg` on PATH. Optional per-machine `ffprobeExecutable` and `ffmpegExecutable` settings may name existing binaries. A missing executable, timeout, mismatch, or decode error produces `ok: false` and a unique JSON evidence file under `exports/`; the CLI exits nonzero and leaves the MP4 untouched. Verification uses the same 45-second command budget and does not install tools. Its evidence records technical validity, not visual quality or perceived loudness; listen and review the finished video as well.

Each command has a 45-second HTTP budget to fit Mist's 60-second CLI limit. If an import is still processing, wait and rerun `sync`. Large media should be prepared before this step. Do not run a second command concurrently. State and ownership live in `.mist-desktop/product-video-renderer/state.json` and the newly created native project's `.mist-product-video-owner.json`.

If Storyboard restarts and forgets a job, `status` and `collect` report that they cannot establish completion. They do not treat a similarly named file as proof. Preserve the output, verify it separately, then explicitly `submit` a new job if needed. If an interrupted CLI leaves a `lock` directory, confirm no bridge command is running before removing only that lock directory. Never delete state or marker files to adopt another project.

The bridge is a local adapter, not a hosted renderer. A Mist installation running on another machine needs a renderer and corresponding per-machine configuration there. The skill remains unpublished until an end-to-end Mist test and a complete second-company video have been reviewed.
