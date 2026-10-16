# Portable scene player and MP4 export

Use this path for a new standard Three.js film when the full Storyboard editor is unavailable. Keep an existing approved editor workflow when it is already useful. The kit freezes the native React/SceneProps.t runtime, including real laptop/phone geometry, fonts, a platform-neutral TSX compiler, a basic HTML player and an asynchronous MP4 exporter. No Storyboard app/server or npm installation is needed. Company UI/media remain project inputs.

## Requirements and materialization

Source-layer capture uses system Chrome/Edge/Chromium plus the bundled codec, with no Storyboard/Playwright install. Preview/build needs Node 22.12+ and a browser with WebGL2. MP4 export additionally needs an existing Chrome/Edge/Chromium, FFmpeg and FFprobe. Check them with `doctor`; do not assume this author's installed tools exist elsewhere or hide package installation in a helper. A browser-only hosted preview can serve the built output after it is built locally.

For a community skill, declare **every** file in `assets/player/` in the catalog manifest. Call `run_skill` and use the exact materialized paths it returns. Do not infer the generation directory. For a local skill, locate the actual installed assets or have the operator materialize the kit; local Markdown inlining alone does not copy binary assets. Declare the flyover helper/vendor files too; materialization copies them to `tools/video-player/capture/`. Preserve the relative layout of the CLI, compiler, runtime, fonts, models, capture tools and licenses.

To retain the kit in the video project, merge a temporary setup script in its existing package.json pointing at the returned cli.mjs:

```json
{"scripts":{"video:setup":"node <exact-materialized-player-path>/cli.mjs materialize --project . --dest tools/video-player"}}
```

Run `npm run video:setup`, then merge `"video": "node tools/video-player/cli.mjs"` into the project scripts. Preserve other scripts; use `video:portable` if an existing `video` script is the editor bridge. The setup command refuses an existing destination, so upgrades go into a new versioned tools directory before changing the script. Do not replace files in an active render.

Mist's existing `run_cli` can invoke these declared npm/pnpm scripts; the kit creates no new agent tools or hosted service. It works within the normal command policy, without installing packages.

## Author, build and review

For layered page capture, discover actual selectors and use the [flyover guide](landing-page-flyover.md); capture does not generate or redesign source UI.

Use the same native source layout as the editor bridge: `video/project.json`, `video/scenes/<id>.tsx`, shared `video/components/`, and local media in `video/assets`, `video/music` and `video/sounds`. The existing renderer/project.example.json gives the manifest shape. Keep required media in `requiredAssets`. Import `storyboard`, React and project-local modules; the bundled compiler supports TSX, JSON, relative static/dynamic imports and import.meta.url. Additional bare npm imports are not silently downloaded. Include permitted local modules or explain the missing dependency. Transpilation is not a complete TypeScript check.

```text
npm run video -- doctor
npm run video -- capture --config capture-config.json
npm run video -- build
npm run video -- preview --port 5201
npm run video -- frames --times 0,4.8,7.25
```

`build` resolves source/output within the active project and writes `video-player/`, preserving editable source. It checks declared media, refuses unrelated output directories and symlink escapes, and replaces only its own generated build after successful compilation. Failed builds leave the last working preview intact. Removed source media do not linger in the new output. The receipt hashes every delivered file.

The player offers play/pause, timeline scrubbing, scene selection and opt-in sound. It pauses in a hidden tab. It keeps the film's original virtual canvas dimensions while scaling the display, so website breakpoints and native screen projections do not change with the viewer's window. Edit the TSX/source files and rebuild; the player is a review surface, not the full visual editor. A new build needs a page reload. Preview does not export automatically.

The generated output is static HTML/JS/assets and can be served by an existing project preview instead of starting another server. Local `preview` binds only 127.0.0.1, serves read-only files, and stays running until stopped. It is not a public share link. Do not rewrite the site's entrypoint just to expose it. For frame review, inspect the returned PNGs with the available image viewer. Check important scene transitions, forward/backward seeks, UI/fonts/models and source fidelity.

All scenes remain deterministic from supplied time. Capture waits for stage resources, fonts and images. Missing rendered images or browser resource failures fail the capture. Keep autonomous video playback, wall-clock motion and live remote assets out of scenes. Runtime version/model hashes are in `provenance.json`; device credits must travel with the output and be carried into public delivery credits when these models are used.

## Sound and asynchronous export

Use local rendered audio files. Scene `sounds` exports work with the native cue shape: at, sound, volume, pitch, pan, align and duration. The player reads same-named files from `video/sounds/`, plus the manifest's music file/offset/gain. Missing cues fail explicitly. Materialize synth recipes to audio before using them; this kit does not include music-generation services. Do not replace supplied audio with another company's example soundtrack. The offline mixer preserves timing and only attenuates to keep peaks under -1 dBFS; this is not a listening or loudness-quality review.

After authorization, a small comparison may use `--from`/`--to`; omit them only when a full render is requested:

```text
npm run video -- export --from 21.2 --to 21.7 --fps 12
npm run video -- status --job <returned-job-id>
npm run video -- cancel --job <returned-job-id>
```

`export` returns a durable job ID promptly. A separate Node worker owns its isolated browser/profile and encoder, so a short CLI call can end while the job continues. Status includes actual frames completed. Only one player export runs per project; building is blocked until it finishes or is cancelled. Cancellation applies during rendering/encoding/verification. Do not delete active ownership locks to start a competing job. If a worker is interrupted externally, preserve its inputs/logs, establish that the exact process is gone, then resolve the stale lock rather than treating a partial MP4 as finished.

The job verifies the build's file hashes, captures frames, mixes sound from the same scene timeline and writes a new uniquely named `exports/video-<job-id>.mp4`. A completed status requires actual dimensions/FPS/frame count/duration/audio and full audiovisual decode to pass. Prior exports stay intact. Use VIDEO_BROWSER, VIDEO_FFMPEG or VIDEO_FFPROBE (or corresponding CLI flags) only for actual installed executable paths. Confirm the finished picture and sound; a valid file alone does not prove editorial quality. The standalone exporter has passed a macOS1080p/12fps sample and an independent Windows640×360/12fps six-frame sample with a real device model, animation, audio and full decode. These short technical tests do not certify every Windows/GPU configuration or whole-film performance.

## Quality and editor boundary

This portable version uses **standard Three.js only**, including the built-in physical device stage. It does not ship MuTracer, three-gpu-pathtracer, GPU denoiser weights, the full Storyboard editor, or a path-tracing switch. Do not accept a renderer flag as evidence of traced output. After standard delivery, offer an optional higher-quality pass through the separately configured editor/compatible physical-stage adapter. Preserve the approved cut, UI and sound; wire and compare a short shot before promising that upgrade.

The skill's quiz, company/source checks, motion/treatment inventory, pacing and review holds still apply. Keep company source content outside this neutral kit. Packaging/local validation is not community catalog publication or a fresh-user Mist end-to-end run. Honor explicit holds on full rendering, uploads, publishing and sending.
