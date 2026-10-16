# New projects and editable device screens

Use this reference when starting a native Storyboard project without existing screen-projection components. The included starter was exercised in an isolated eight-second, two-scene fictional-brand preview on October 14, 2026. Its laptop and phone bodies use Storyboard's real 3D runtime; their independently editable screens remain native React/SVG layers. This is a focused preview test, not evidence of arbitrary model poses, moving cameras, another machine or MP4 export.

## Create the project through the running app

Discover the current server and tools first. Use the editor's New Project action when practical. If no project-creation MCP tool is exposed, the verified API is:

```text
POST /api/projects
Content-Type: application/json
{"name":"a-unique-project-slug","width":1920,"height":1080,"fps":30}
```

Read the returned `id`; never assume it equals the name. The current store derives a slug from that first name and makes it unique against existing folders. Then set the intended display name without changing the ID:

```text
PATCH /api/projects/<returned-id>
Content-Type: application/json
{"name":"Brand · Product story"}
```

Project creation supplies an Intro scene, art direction, shared motion module and asset folder. Add scenes, set durations and order through the available native tools/API. Do not replace an existing project to obtain a preferred ID. These routes were confirmed in `server/api.ts`, `server/projects.ts` and `src/editor/api.ts`; recheck them if the app version differs.

## Copy the tested projection starter

From this skill's `assets/device-ui/`, copy:

| Source | New project destination |
| --- | --- |
| `projection.tsx` | `components/projection.tsx` |
| `modelMetrics.ts` | `components/modelMetrics.ts` |
| `tokens.ts` | `components/tokens.ts` |
| `screen-underlay.png` | `assets/screen-underlay.png` |
| `tools/model-metrics.mjs` | `tools/model-metrics.mjs` |
| `tools/tsconfig.trial.json` | `tools/tsconfig.trial.json` |

Preserve any existing files and integrate their interfaces instead of overwriting them. The tokens retain the fictional Moss pilot's colors, names and UI slots so the geometry matches the tested example. Adapt those values to the actual brief. No Rootist assets or device binaries are included.

The source files use `storyboard` and React from the existing checkout. The neutral 2×2 screen underlay carries no UI. Set the app's output size to the same width and height as `dimensions`.

Compose the stage and screens in a shared wrapper:

```tsx
import { DeviceStage, Fill } from 'storyboard';
import { ProjectedScreen } from './projection';
import { dimensions, stageConfig } from './tokens';

// LaptopUI and PhoneUI are independently authored native components.
export function Set({ globalT }: { globalT: number }) {
  return (
    <Fill style={{ overflow: 'hidden' }}>
      <DeviceStage config={stageConfig(globalT)} t={globalT}
        width={dimensions.width} height={dimensions.height} />
      <ProjectedScreen kind="laptop"><LaptopUI globalT={globalT} /></ProjectedScreen>
      <ProjectedScreen kind="phone"><PhoneUI globalT={globalT} /></ProjectedScreen>
    </Fill>
  );
}
```

`screenPoint(kind, x, y)` maps a native UI position to the output canvas. Use it for a cursor hotspot or a product destination. `matrixForQuad()` maps a native rectangle onto four output corners; the pilot used it to move one bottle directly onto the laptop's product slot without a duplicated landing frame.

The projection wrapper now clips the entire native assembly to `displayOutline`, measured from the bundled screen geometry, before applying perspective. A rectangular screen bounding box and a guessed CSS radius can spill across the bezel even if `overflow: hidden` is present. For the bundled convex OLED, the measurement script retains 132 perimeter points; the laptop has its own measured perimeter. Keep status chrome, page, cart and fixed bottom safe area inside this one outer clip. Avoid a second guessed inner phone radius. The convex-outline measurement is specific to these displays; a concave notch or a different model requires an actual outline rather than an assumed hull. Inspect corners, island, battery, bottom text and the largest camera punch at full resolution.

## Keep geometry and camera consistent

`tokens.ts` supplies the exact same camera and device poses to both the native stage and projection. Do not update only one of those paths. Its stage uses `animate: false`, with explicit time-driven key-light motion; fixed camera/device poses make the tested screen mapping stable.

Measured screen corners in `modelMetrics.ts` depend on the checkout's bundled `laptop.glb` and `phone.glb`, its model-normalization logic and camera convention. If the models or runtime change, remeasure before use. The optional measurement script looks for the current screen material names and reads models without copying or changing them. Run it only after copying it into the project layout above:

```sh
# From <storyboard-checkout>/projects/<returned-id>/
node tools/model-metrics.mjs
```

It writes this project's `components/modelMetrics.ts` (corners plus normalized display outline) and `evidence/model-metrics.json`. For an owning Mist source tree outside the native checkout, pass `--runtime-dir /absolute/storyboard --project-dir /absolute/owning/video` so measurement updates the source that will be synchronized. Those destinations and its imports are relative to the script. It requires the existing vendored Three.js/GLTFLoader and shared device models; no package install or engine is needed.

For animated camera/device poses, derive stage and projection from the same time-sampled values and inspect start, extremes and end. The included helper reads fixed token values. Simply enabling built-in interpolation does not make its native screen follow the mesh. Avoid back-facing displays and occlusion between overlay UI and another device; those configurations were not validated by the pilot.

## Compile and visually verify

The copied focused config extends the checkout's TypeScript settings and includes all this project's scenes and components. With existing dependencies, from the project directory:

```sh
../../node_modules/.bin/tsc --noEmit --project tools/tsconfig.trial.json
```

Use native `render_frames`, inspect the actual images and run `check_seams` for a continuous boundary. Imported JSX can fail even when the scene's diagnostics return `error: null`. A reused capture page can retain a stale Vite overlay; reload/replace that page after fixing compilation and capture again. Preview all scenes from beginning to end. Measure the mix with `check_audio`, and distinguish measured audibility from listening.

The pilot passed focused compilation, 14 inspected full-resolution captures, a 0% changed-pixel continuous cut, one click with no clipping risk, and eight-second editor playback. It had no soundtrack and no exported MP4. Keep those evidence limits when describing the skill's reliability.

## Starter scope and actual product fidelity

This kit supplies device projection, not an approved design for a company’s UI. Its neutral fonts/colors/layout examples are not product defaults. Follow the source UI fidelity reference before populating screens, and compare the actual page at the device’s intended viewport. Preserve the source UI while using the projection/camera helpers.
