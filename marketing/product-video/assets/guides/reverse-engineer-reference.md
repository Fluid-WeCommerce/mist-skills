# Turn a finished film into reusable shot recipes

Use when adapting an existing film, learning from a supplied reference, or updating this skill from a successful project. Extract the story and mechanism together. A list of effects misses the words, reading time and connected actions that made the original work.

## What HyperFrames contributes

Reviewed 2026-10-15: [Studio](https://www.hyperframes.dev/studio) provides an agent-assisted composition editor. Its [reference-recreation guide](https://hyperframes.heygen.com/prompting/recreating-references) suggests inspecting actual motion, correcting specific values, comparing matching frames and saving the converged implementation. Use that inspection loop without changing the user's chosen runtime.

Studio is an authoring environment, not evidence that an arbitrary MP4 can be recovered into its original layers, camera and source assets. The HyperFrames animation-map helper inspects registered composition timelines; it does not understand a flattened reference movie or native Storyboard `SceneProps.t` code automatically. Its compare tools compare supported compositions, not hidden edit histories. Do not claim to have used the Studio app when only its guidance was reviewed. The desktop download page listed Mac/Linux and Windows coming soon at review time; this says nothing about CLI compatibility.

For an existing Storyboard film, source inspection plus native time-seeking is the useful path. For a movie-only reference, describe visible behavior and label the mechanism as inferred. HyperFrames can be tried separately for a suitable HTML composition; do not port an approved film merely to analyze it.

## A bounded extraction pass

1. Freeze the exact reference: URL, local filename/hash when available, duration, frame rate and version. Prefer approved editable source over guessing from pixels. Keep reference footage outside the shared skill assets.
2. Sample 6–12 representative times across the film, then inspect movement closely around the chosen action or transition. Record the readable resting pose, travel, camera speed and overlap. A still cannot establish an easing curve, continuity or sound comfort.
3. Write one compact contract per useful shot: **purpose → film headline → real UI action → payoff → camera path → layer order → shared clock → handoff → required inputs → evidence**. Separate observed, inferred and source-confirmed details. Save absolute values only when source or measurement supports them.
4. Adapt a small complementary subset to the new company. Preserve requested signatures, but do not require every film to contain every recipe. Use its actual words, photographs, features and CTA. A reference supplies craft, not permission to copy its claims or media.
5. Prove one defining shot; inspect a settled frame, a short motion range and its boundary/repeated seek. Fix the largest discrepancy once, then update the contract with settled values. Expand after that proof. Honor preview/render holds; no paid generation or full export is needed for analysis.

`assets/reference-analysis/reference-frames.mjs` creates a small local still gallery, contact sheet and metadata/hash ledger using Node plus existing FFmpeg/ffprobe. Copy it into a local project only when those tools and command access are available:

```sh
node tools/reference-frames.mjs --input approved-film.mp4 --times 1,6,12,20,30,40 --output review/reference --source https://original-reference
```

Choose times inside the actual duration and an empty output folder. It caps extraction at 12 stills and a 60-second extraction budget, installs nothing and makes no network requests. Requested seek times are not exact variable-frame PTS. This helper does not render a new film, recover layers or automatically identify motion. In Mist, respect `run_cli` policy: use an approved project script or available capture/image tools; do not bypass restrictions to execute a helper.

## Preserve the three text channels

Plan **source UI text**, **film-level story copy outside the devices**, and **optional spoken narration** separately. Source UI labels alone seldom explain the story at video size. When adapting a film with explanatory headlines, preserve their role instead of silently omitting them. Speech is optional; a music-only film can still need story copy.

Map each selected benefit to one brief, readable film headline and its source basis. It may be an honest editorial paraphrase; do not invent a feature, number or health claim. Exact quotations and paraphrases must be distinguished in the source map. Inspect the headline at the largest camera move, leave reading time after its final word settles, and clear it before a conflicting chapter heading.

Copy `assets/motion/StoryCaptions.tsx` with `KineticPhrase.tsx` for native time-driven captions. Supply text, start/end, font and colors. Position it outside the punched-in device assembly so the headline remains stable; tune its width, size and margin for the actual canvas. The helper does not choose copy or prevent collisions automatically.

## Source-confirmed Rootist recipes

The local Rootist example was inspected from editable components and its 50.1-second 1080p30 final file. Times below are local to the named mechanism unless stated otherwise. These are source-specific examples, not defaults for another company. The skill does not include Rootist's project, media, audio or models.

| Recipe | Source-confirmed mechanism | Transfer and proof |
| --- | --- | --- |
| Page flyover | `LandingFlyoverClock.ts`: moving pre-roll begins 0.5s before the visible shot; cruise source time advances at 1.5×, blends with a positive-velocity Hermite curve into rise/overview/return. | Use the bundled layered-page renderer and the new company's independently separated page elements. Match velocity across the preceding reveal; start farther away/slower if the page is unreadable. Preserve the short overview and return budget. Check approach, long view, culling and device aperture handoff. See `landing-page-flyover.md`. |
| Hover → lift → spray → scroll | `PublicHomeInteraction.ts` / source timing: hover 0.95s, clicks 1.50/1.833s, zoom-in 0.68–1.36s to 1.58×, zoom-out 2.07–2.62s, scroll 2.50–3.27s. Cursor, source action frames, camera and sounds share one clock. | Use only a real action the company supplies. Hover lift precedes the two tight clicks; quiet click and source-like action sound accompany the action. Zoom the whole assembly, then scroll the actual next section before departure. Inspect source fidelity and listen to the mixed result. |
| Products become native UI | `StudioProductFlow.tsx`: 0.06s product stagger, curved flight into projected live tile targets; late landing compensates for target drift and scroll. The destination owns products after handoff. | Preserve each product identity, crop, size, depth and destination. Share the time and projected target rather than landing on a static screenshot coordinate. Suppress duplicate copies and check landing at both sides of the cut. |
| Preview phone lifts out | `MySitePhoneLift.tsx`: lift 0.25–1.50s, navigation at 0.85s, 90px sine arc; inverse homography removes baked perspective before the assembly is seated on its parent display. | Keep body, glass and page parallel to the parent screen until detachment, then unflatten during flight. A screen image already in perspective must not receive that perspective twice. Match full quads and screen masks; the bundled fixed-pose starter alone does not implement moving projection. |
| Visitor map accumulates | `VisitorMapState.ts`: six pin arrivals begin 0.66s with 0.11s stagger; spring scale is anchored at each tip, counts follow the same arrival clock. Totals derive from the same city data. | Match map, city list and totals. Pop pins in geographic positions, use consistent demo numbers only where authorized, and keep demo data separate from real analytics availability. Map relief, water/land colors and pin contrast must read at finished video size. |
| Staggered collection resolve | `ClosingMotion.ts`: first departure 1.50s, seven departures 0.07s apart, each flight 0.42s; flood begins 0.02s after the final landing. | Use `assets/motion/collection.ts`, tuning to the actual group. Keep device parts coupled, reserve end-card reading time, and derive the wipe from the final landing so it cannot cover objects still flying. |

The original also carries large benefit headlines throughout the film: for example, “Your link lands on the real store” and “Your own storefront, ready to share.” Those are Rootist-specific messages. Preserve the explanatory role while writing the next company's truthful story. A correctly rendered device tour without this layer is an incomplete adaptation of that treatment.

## Check light and delivery honestly

Inspect rendered pixels where an unlit scene background meets a lit, tone-mapped floor. Identical input hex values do not guarantee the same output color. Match those output values when a seamless neutral studio is intended, or make a deliberate floor/wall distinction. Warm rooms are valid; an accidental yellow band is not a lighting improvement. Preserve actual site colors inside screens.

Record what is available as reusable code, what is a source-backed recipe requiring implementation, and what remains inferred. Do not call a recipe a bundled working component. The Rootist final combined MuTracer physical stage/device/map passes with a separate Three.js flyover and native DOM/SVG UI; not every pixel was path traced. Default new films to standard Three.js, offer an optional supported path-traced finish after review, and verify the selected renderer on the actual export.
