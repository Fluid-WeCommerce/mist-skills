# Mist rendering bridge

For a new standard film without the editor, use **Portable scene player and MP4 export**. This reference covers the separate full-editor route and optional compatible tracing integration. Its existing-runtime requirement does not apply to the bundled portable player.

## What is provided

The package includes a dependency-free Node adapter in `assets/renderer/`: `renderer.mjs` and its sibling `capture.mjs`, configuration/manifest examples and README. It connects to an already installed, running native Storyboard on the same machine. It installs no dependencies, starts or stops no service, uploads nothing, and only creates new bridge-owned projects. It does not include Storyboard, model binaries, MuTracer or denoiser weights.

Mist's native `run_cli` accepts a declared `npm run` or `pnpm run` script. The current handler has a60-second timeout and blocks package installations and several Git network/destructive commands. The adapter's commands have a45-second budget. Rendering continues in Storyboard after `submit` returns, so it is not killed by a short CLI invocation. Do not disguise a prohibited install inside the adapter.

## One-time local connection

For a Local skill pilot, copy the adapter and any required helpers into the active skill/project sandbox; its folder is separate from the skill source. The Local skill loader inlines Markdown references but does not automatically materialize runtime assets. For a Community package, declare every runtime file in the manifest, call `run_skill`, and use the exact materialized paths it returns. The `video` npm script can point directly at the returned renderer.mjs path: its sibling capture.mjs is materialized beside it. Do not have the model retype adapter source code just to copy it. Do not embed an author's home path in reusable files.

Inside the active project:
1. Place both adapter modules in `tools/product-video/`.
2. Merge the example `video` script into the existing package.json, preserving all other scripts/dependencies. No installation is required.
3. Set `renderer.config.json` to the actual loopback origin, Storyboard `projectsDir`, optional `runtimeDir` for frame captures, project-contained `sourceDir` and `outputDir`, and explicit `render.renderer` / scale / FPS. The bridge checks the project directory against the connected server; remote origins and redirects are rejected.
4. Run `npm run video -- doctor`. This reports connectivity and configured file fingerprints. It is not GPU, image or path-tracer proof. Pin known runtime/model hashes when suitable; unknown hashes are observations, not matches.

See the supplied adapter README for exact configuration and failure/recovery details. A fresh Mist installation needs a renderer installed/configured locally. This package is not a hosted render service.

## Author and verify through the connection

Author `video/project.json`, `video/art-direction.md`, `video/scenes/<id>.tsx`, shared `video/components/`, media in `video/assets/`, and optional `video/music/` and `video/sounds/`. The example manifest gives the exact shape. The adapter maps scene IDs through native metadata APIs and copies source only into its newly owned project. Do not import one scene from another. Scene code uses native `SceneProps.t`, React and Storyboard imports. Keep required media in `requiredAssets` so missing inputs fail before creating a project.

Commands from the active Mist project:

```text
npm run video -- doctor
npm run video -- sync
npm run video -- check
npm run video -- frames --times 0,2,4
npm run video -- submit
npm run video -- status
npm run video -- collect
npm run video -- verify
```

- `sync` returns the actual editable Storyboard URL and hashes; it does not render.
- `check` checks synchronized hashes, metadata and native scene compilation. Imported UI/image failures still need real captures.
- `frames` captures up to4 native PNGs using the configured renderer and the already installed runtime's Playwright/Chromium. It returns project-relative paths and errors. Inspect them with Mist's `view_project_image`. It closes only its own browser and refuses to compete with active full renders. Optional `--scene <source-id>` selects a scene; `--resolution low|normal|high` chooses capture scale.
- `submit` returns the real background job ID. It never means completed. Use later `status` calls and preserve the input snapshot until the job finishes.
- `cancel` affects only the bridge's own saved job.
- `collect` requires that exact job to report `done`, verifies its output belongs to the owned project, preserves prior exports and copies a SHA256-verified MP4 into the active sandbox. Run `verify` on the collected output before delivery. It checks the exact file hash, native-job dimensions, FPS, actual counted frames, duration and required audio, then fully decodes video/audio with existing ffprobe/ffmpeg. It writes a local evidence report; missing tools or failed decode remain failures. Inspect representative encoded frames too.

If the server restarts and forgets a job, the adapter reports that it cannot establish completion. It does not adopt a similarly named file. Preserve the output and verify separately. Sync does not modify a project while its render runs. Do not remove ownership state to adopt another company's project.

## Music and renderer boundaries

Use a preferred licensed soundtrack when supplied. As an optional dependency-free fallback, `assets/audio/original-score.mjs` can create an original synthesized demo score plus a quiet click. It accepts the intended duration and writes new files only; it contains no third-party recording. Add a declared project script if choosing it. This is an optional sound direction, not the universal brand soundtrack. Native music/SFX are mixed by Storyboard, not replaced after export with an unrelated older audio timeline.

Choose Three.js or MuTracer explicitly. A renderer selection changes only compatible components. Storyboard's generic DeviceStage currently uses Three.js; MuTracer requires an actually integrated physical stage, local runtime/assets and GPU support. Test a moving representative frame and report the renderer actually used. Native UI remains separate and sharp. Do not describe the entire film as ray-traced just because the export job says MuTracer.

## Release boundary

The native quiz, local renderer connection, full second-company movie and delivery verification are separate proofs. Record what passed, what was operator-supplied test input, and any manual setup/repairs. Keep the skill, movie and source assets unpublished until explicitly authorized. No DAM upload, community-repository merge, live-site edit or message is implied by a local test.

## Default quality and the optional upgrade

Keep the normal configuration on `three`. After verified standard delivery, offer the optional path-traced finish using **Physical rendering and finished-film delivery**. The `mutracer` enum alone does not make a scene compatible: verify the custom adapter/runtime and actual traced frame first. Keep an upgrade config separate, preserve the standard export, and wait for the user to choose the slower run. If a generic device scene needs adapter work, state that clearly in the offer.

## Sharing scope and machine setup

Use one company-neutral community skill for this workflow. Mist supports company-local skills (`~/Fluid/<company>/skills/`), shared local skills (`~/Fluid/skills/`) and a community catalog. A shared skill receives the active company's context; its media, source UI, brief, quiz answers and generated files belong to that company's project/chat, not to the skill package. A company-local customization is appropriate only when its instructions are specific to that company.

The portable catalog artifact is `marketing/product-video/SKILL.md` plus its declared references/assets and a merged `manifest.json` entry in Fluid-WeCommerce/mist-skills. Update the manifest timestamp when shipping changed helpers/references. Merge through the repository's review process; a local ZIP or installed local skill is not catalog publication.

The catalog now includes the separate portable runtime/player and licensed device models; it does not include the full Storyboard app, company media, managed render service or this author's machine configuration. Testers choosing this editor adapter still need a compatible installed editor runtime and an explicit local renderer configuration; verify the included adapter's doctor/sync/frames/job path on that tester's machine. For a managed renderer, provide and verify an authenticated job interface before advertising it. Do not copy a localhost URL, private Windows host or filesystem path from the author's setup into the shared package as if available to everyone.

Before claiming broad availability, exercise a fresh user's setup: load the community-style assets, resolve active-company content, complete the discovered coverage quiz including a typed custom answer, produce and inspect one signature shot, then complete a standard Three.js export. Keep path tracing an optional upgrade. Schema fixtures and a successful assisted Sunrider run do not establish unattended fresh installation.
