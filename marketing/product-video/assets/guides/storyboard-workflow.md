This reference applies after the Mist entrypoint has completed intake and verified a renderer. Mist-specific tool/policy rules in SKILL.md and mist-rendering-bridge.md take precedence over shell examples in this reference.

# Storyboard workflow

Make a product story that remains editable scene by scene. Preserve the user's brand, runtime, selected assets and review stage. The full editor route uses a working Storyboard checkout; the portable route includes its own frozen native runtime and permitted device models. Company media remain project inputs.

For another brand, establish a small source set: approved page/UI states, vector wordmark and font, product/people imagery, permitted device models, and licensed audio. Capture or rebuild what the new story needs. The included device projection and flyover camera are starters; they do not supply a complete rendering stack. Prove one representative shot with the new assets before expanding the film.

## Find the actual project

- Locate the checkout and running server. Read its `AGENTS.md`, `projects/CLAUDE.md`, the project's `art-direction.md`, and shared motion components. Discover the available Storyboard tools and current project before choosing commands.
- Native Storyboard uses React scenes driven by `SceneProps.t`. Keep that runtime; do not migrate to HyperFrames or Remotion as part of ordinary refinement.
- Preserve existing servers and unfinished work. Follow the checkout's setup instructions if setup is needed. Large music/SFX engines are optional; existing audio and synthesized cues do not require starting them.
- Change scene ordering and durations through Storyboard's tools while the app is running. Treat project internals and source assets as owned work, not disposable caches.
- For a new project, use the editor or the verified native API recipe in [references/device-ui.md](device-ui.md). Discover the actual returned project ID; the initial name determines it and collisions can add a suffix.

## Establish the story and visual rules

Use the supplied brief and context. Resolve missing audience, message, aspect ratio, duration or source access only when it affects the result. For an existing film, retain established choices unless the requested edit needs a change.

Map each beat to a focal subject, supporting copy, source UI, resting pose and intended transition. If several sites or roles are involved, show their relationship rather than touring every page. A useful overview can put the public site on a monitor, the workspace on a laptop and a personal page on a phone. Labels are optional when the content itself is clear.

Plan source UI text, large film-level story copy and optional voiceover separately. When adapting an approved film with explanatory headlines, preserve that role using the new company's truthful benefits. UI labels alone do not replace the story copy. Record each headline, source basis and reading hold alongside the demonstrated action.

Carry chosen reference techniques into a short treatment inventory in the brief/art direction: technique, requested/reference basis, purpose, actual scene IDs, source assets and visual evidence. When the user selects a layered page flyover, preserve that establishing beat and read [landing-page-flyover.md](landing-page-flyover.md) while allocating its time. Select a coherent subset of physical lighting, device handoffs, product landings and interaction zooms for the story; preserve explicit user choices and explain material omissions. Derive this direction from the brief rather than adding a mandatory technical quiz.

Check coverage by action and payoff: a page title or sidebar label is not a demonstration. Distinguish what the film demonstrates, what is merely visible, and what is omitted. Near completion, recommend only changes that clarify a core benefit; do not expand a short overview into a tour of every feature. Check for existing staggers before recommending another one.

Write a small motion vocabulary: related easing curves, timing ranges, stagger, reading holds and the main transition family. Keep it in the project's art direction and `components/motion.ts`. Prefer purposeful changes in emphasis over making every object move.

For a new motion reference or repetitive framing, read **Motion reference variety**. Keep the source company explicit, choose a few complementary treatments, and review their movement before another full export.

For a supplied film or reusable recipe extraction, read **Reverse engineer reference** for source-confirmed shot contracts, separate story-copy planning, output-pixel background checks and a bounded local still-analysis helper. Use the Mist bridge's permitted tools; those helper examples do not override command policy.

Before allocating new scene durations or correcting a long hold, read **Pacing and variation**. Rootist is one worked example; derive the structure, primary representation and visual rhythm from this company. Audit meaningful actions and reading intervals against the actual normal-speed preview.

## Build controllable layers

Read **Source UI fidelity** before authoring a screen. Reuse actual source markup/styles or measured source geometry and compare against the real rendered page at the same viewport/state. Preserve source typography, controls and responsive/header behavior; approximation is not the default. Keep editorial motion separate from the product UI.

- Use a source SVG for a wordmark and vector assets for simple icons and cursors. Inspect the SVG for embedded raster content; an SVG extension alone does not make it sharp. Load the actual brand font when permitted.
- Reconstruct important UI text, controls, cards, tabs, selected states and progress as native elements. A screenshot can supply static detail; it should not flatten the elements the user wants to control.
- Keep product cutouts, screen content, device body, pointer, stage and lighting separate. Preserve original packaging and copy. Use image generation for composition exploration or supporting scenery when appropriate, not as a replacement for exact UI or packaging.
- All motion must resolve from supplied time. No autonomous animation loop, random wall clock, CSS transitions, live iframe or independently playing video inside a scene. Renderer initialization and synchronous repainting are acceptable when the result is determined by scene props.
- When footage is necessary, use extracted frames indexed by time. Keep the action's real ordering and transition behavior; do not manufacture a whole-screen fade for a UI action that switches directly.

## Devices and screens

Read the checkout's `docs/devices-and-stage.md` before using the built-in stage. Its first version uses image textures for screens. Do not describe those textures as editable webpage layers. For independently animated UI, use the project's screen-projection components or construct native UI above the device plane.

For a new project without a projection helper, read [references/device-ui.md](device-ui.md). This skill includes a tested starter for native UI over the built-in laptop and phone. Its demonstrated scope is fixed camera/device poses; it does not bundle device models or the app.

Use **Turn** (yaw) to face a laptop or phone toward the center; **Roll** rotates it sideways and **Tilt** leans it. Choose the axis deliberately. A flat rotated device image does not provide new model views or realistic geometry lighting.

For spatial device shots, prefer a perspective camera and actual model geometry when available. Orthographic views can suit diagrams, but inspect front/back convergence before using them for a product laptop. Keep camera, model and native screen projection on the same pose; the included fixed-pose starter does not acquire animated projection support automatically.

Measure the visible device silhouette, not transparent image bounds. Move the body, projected screen and attached shadow together. Check safe spacing at the largest camera move and at both ends of the scene.

Clip a phone's entire screen assembly to its display shape, including status icons, header, scroll content, overlays and cart. Keep status icons fixed while content can pass behind them. Avoid computing the status-bar fill from the average color of scrolling content: that causes flashes. A chosen translucent material must composite the content in the same coordinate system. Check the island, battery edge, header seams, sheet corners, home-indicator area and padding below the checkout button.

Use a reusable cursor asset with a fixed hotspot. Project the hotspot onto the screen but keep the visible cursor large enough for the finished video. Tie the click press and sound to one named moment; remove a second baked cursor if it doubles the pointer.

When an on-screen phone becomes the next shot, lift that existing preview from its actual screen plane. Keep it parallel to its parent display until detachment, and move the body, screen, clipping and chrome as one assembly. For a punch-in, transform the whole device assembly and cursor together, then return to the handoff pose.

## Light and depth

For a landing page treated as a physical sheet, with a low perspective flight past lifted photographs/cards, a full-page rise and a return into a monitor, read [references/landing-page-flyover.md](landing-page-flyover.md). It includes a dependency-free example camera and the fixes for long-view popping. Use this as a brief establishing shot when the page design matters; keep the subsequent product interaction readable.

For a physical window-light look, move a real light, camera or occluder through the set. Keep the contact shadows consistent with the receiver plane and object elevation. Avoid adding unrelated drop shadows to every flat tile.

Anchor foliage shadows to a plausible offscreen caster and light direction; a recognizable floating silhouette is not automatically more realistic. Separate pale hardware from a pale wall with room reflections, a studio flag or light placement rather than an unrelated glow or oval shadow.

Use one global timeline for shared lighting: `scene.start + t`. Both sides of a continuing cut should sample the same physical set. Move the window, foliage or viewing point around story beats, and hold the light while the viewer reads. If hardware highlights are baked, keep light changes modest or render new poses so the hardware and floor agree.

Apply the same light field to flat portraits or logo tiles at their real positions. Use a projected light crop on lifted UI sheets so text remains native and sharp. Window size, softness and an occasional recognizable foliage shadow are art-direction choices, not mandatory decoration.

For Three.js/MuTracer selection, native-screen compositing, render quality, GPU benchmarking or moving the export to another computer, read [references/rendering-and-export.md](rendering-and-export.md). A renderer toggle only changes components wired to that renderer; describe the actual physical layers and any separate flyover pass accurately.

## Transitions that land cleanly

- Put shared boundary poses and target coordinates in components imported by both scenes. Compare the outgoing final frame and incoming first frame before adding a fade.
- For a direct letter-to-product transformation, overlap the appearance change with one curved trip to the destination. Do not park products in an intermediate row and start another flight unless the story calls for that pause.
- Recompute targets in the device's screen coordinate system as the device moves. At landing, match the native product's position, scale, orientation and scroll offset, then hand off without showing both copies.
- A regular tile grid uses whole-cell positions and equal square sizes. If a logo becomes a tile, its background can appear on landing and its wordmark invert at that same impact. Choose irregular layouts only deliberately.
- Before a group contracts into a button, a small outward anticipation can clarify the action. Give the contraction a readable trajectory and a settled end; check motion extremes for clipping.
- Give related objects separate departure and landing times when a simultaneous move obscures their order. Keep coupled parts on one clock. Derive a following flood/wipe from the last arrival so it cannot cover objects still in flight. Do not stagger every object just for consistency.
- During overlapping transitions, set the foreground/rear assembly order deliberately. An incoming panel can establish behind outgoing subjects, rather than covering them merely because it mounts later in the DOM.
- Keep navigation faithful. A tab change should not make already-landed product images float independently of the real page. Animate a cart sheet continuously in the native phone assembly rather than jumping between screenshots.

For a copyable collection clock and practical interaction/audio checks, read [references/choreography-and-sound.md](choreography-and-sound.md). Its timings are examples to tune, not universal brand rules.

## Review and deliver

Use `render_frames` at resting poses, changed actions, motion extremes and scene boundaries. Inspect the actual images. Use `check_seams` for intended continuous cuts; intentional visible cuts need not score zero. Preview the complete timeline and look for duplicate overlays, abrupt substitutions, mismatched lighting and insufficient holds.

Verify the treatment inventory against the actual produced scenes and their time ranges. A layered flyover needs visible page depth, independently lifted subjects and its planned approach/rise/return, supported by inspected images and motion. Record chosen techniques that remain absent, incomplete or deferred. A tilted screenshot, working device frame or technically valid MP4 does not establish that the reference film's visual craft transferred.

Compile imported scene components as well as the scene entry file with a focused TypeScript config. Scene diagnostics alone can miss imported JSX errors. If a capture still shows an old Vite error overlay after a fix, reload or replace that capture page and inspect a fresh image; an empty errors array is not visual proof. The focused config recipe is in [references/device-ui.md](device-ui.md).

Reuse shared moment definitions for picture and `sounds`. Choose music for the brand, place clicks on interactions, and reserve swooshes for meaningful travel. Use `check_audio` for missing sources, audibility and headroom, then review the complete mix and focused clips. A narrow-band audibility score does not measure comfort; do not boost a deliberately quiet click or spray until every cue reports clear. Distinguish listening from measurement. Keep an asset/license ledger for sourced audio and models.

Honor instructions to hold rendering, publishing or sending. Within the authorized scope, use Storyboard's native export. Verify the actual MP4's resolution, frame rate, duration, audio, full decode and representative frames; a successful preview is not proof of the final file. State the renderer actually selected. If comparing a path tracer, time a representative moving frame before promising a whole-film export; availability is not proof that the exported cut uses it. Preserve previous approved files and keep focused review clips beside the full cut.

Before a full export, preflight every scene and required capture sequence, not just the benchmark shot. The asset manifest and MP4 verification helpers in [references/rendering-and-export.md](rendering-and-export.md) check declared files and encoded output. They do not certify motion, comfortable sound levels or complete dependency discovery. Keep known abrupt cuts visible in review notes; a technically successful export can still need editorial polish.

On a continuous cut, compare boundary frames. On a changed motion, also seek forward, backward and to the same intermediate frame again. Report the comparison threshold and actual differences; a perceptual match must not be called byte-identical. Skill frontmatter validation and timing-helper checks do not prove an arbitrary new brand film is visually good.
