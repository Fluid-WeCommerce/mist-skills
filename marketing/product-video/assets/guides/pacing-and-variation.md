# Pacing and variety without template copies

Use while planning a new film, when a shot hangs, or when several company videos look alike. Keep approved treatments, company content and delivery holds. Reuse reliable mechanics without inheriting a previous film's structure.

## Budget attention before allocating duration

Plan each beat as **new information → visible proof → readable payoff → next beat**. Give it a start, action range, settled reading interval and exit. A scene file can contain several beats; its duration is not its reading hold. Track the viewer's focus, not just whether something changes pixels.

For a short music-led product film, flag approximately three seconds without a new meaningful action, reveal or justified reading interval. This is a review trigger, not an automatic cut or a universal maximum. Dense explanation, narration and deliberate atmosphere can need more time. A drifting light, looping grain, slow camera creep or louder sound does not by itself resolve an empty hold. Shorten it or advance the actual story.

Start the next real interaction as soon as the prior payoff is understood. Leave enough time after text/accordion content settles to read what the film expects the viewer to read, then move on. Do not keep a frame simply because its scene was assigned 10 or 16 seconds. When length is approximate, a good 35-second film can be better than a padded 45-second one. If the duration is an explicit requirement, redistribute time to substantive demonstrations rather than silently shortening it.

Watch the complete preview once at normal speed. Inspect the longest declared quiet intervals and repeated framings. Still thumbnails and compiler checks cannot prove pacing. Camera travel can be continuous through a transition while the subject still gets a reading hold; do not remove useful pauses indiscriminately.

`assets/reference-analysis/review-pacing.mjs` optionally reviews a small `video/beat-map.json`. It reports gaps in declared events/actions longer than the review threshold and long unbroken framings. It does not infer motion or meaning from pixels, validate an explanation, or prove the plan matches the actual video. Copy it beside an existing project adapter, add an allowed project script, and review its flags against the live timeline before export. It installs nothing.

```json
{
  "version": 1,
  "duration": 12,
  "reviewGap": 3,
  "reviewFraming": 7,
  "shots": [{
    "id": "real-feature",
    "start": 0,
    "end": 12,
    "family": "native-ui-closeup",
    "events": [{"at": 0, "label": "Feature appears"}, {"at": 6, "label": "Result appears"}],
    "actions": [{"start": 1, "end": 3, "label": "Demonstrated drag"}],
    "reading": [{"start": 6, "end": 10, "reason": "Read the actual result", "text": "Source-backed result text"}]
  }]
}
```

Read the whole report, including explained long reading intervals. Do not relabel idle time as an action to clear a warning. Use measured/source-confirmed timings where available, keep sound/cursor/camera on the same clock, and update scene durations through the running editor/API. After retiming, compare continuing boundaries and a repeated intermediate seek. Preserve prior approved exports until a new one is actually produced and verified.

## Choose a different story structure when the company calls for it

Rootist is one worked example, not the default skeleton for every brand. The layered flyover, phone lift and physical device ensemble are optional techniques unless selected by the user. For an existing approved project, preserve those explicit choices. For a new company, silently consider two concise treatments from its sources and select the one that best demonstrates the chosen benefits; this is planning, not two paid generation runs or another mandatory quiz.

| Company evidence / selected story | Suitable primary treatment | Complementary proof |
| --- | --- | --- |
| Distinctive product/ingredient photography | Editorial full-frame imagery, clear typography and subject match cuts | Brief source UI close-up showing the real selection or explanation |
| A useful multi-step application task | Follow one actual item through native UI states | Result emphasis or an honest before/after, with one restrained camera move |
| Real people and a service experience | Genuine company footage/portraits and task-led chapters | Source booking/onboarding action; avoid invented testimonials |
| A relationship or data story | Sourced diagram, map or chart with progressive disclosure | The real interface or outcome that the explanation supports |
| Several connected roles/sites/devices | Spatial ecosystem overview with clear hierarchy | Follow one role into a focused demonstration |

Do not force a presenter, map, diagram or 3D model merely to satisfy variety. Source availability and the actual product decide. Full-frame UI, editorial imagery, typography, diagrams and spatial scenes are different representations; a new camera angle on the same two-device tableau is only a framing change.

Record the chosen primary treatment, why it fits the company, supporting shot families, and which previous-film patterns are deliberately omitted. If adapting a prior example, compare the outline before building: hero subject, shot order, dominant representation, typography behavior and transition logic. Change substantive choices where the new story warrants it; swapping logos/colors and keeping the same sequence is a template reskin. A deliberately consistent campaign series is a valid exception when requested.

Within one film, alternate emphasis rather than cycling every effect. A useful rhythm can be **wide context → close proof → editorial explanation → result**; another film may open with the result and reveal the process later. Avoid consecutive long shots with the same subject scale, layout and purpose. Repeat a motif only when it builds recognition or shows a meaningful state change. Keep related easing, type and sound coherent while the representations vary.

## Learn from references without cloning them

[HyperFrames' recreation guidance](https://hyperframes.heygen.com/prompting/recreating-references) describes transcribing actual motion and timing, correcting specific values and preserving the settled implementation. Use that method to isolate reusable mechanisms. For a literal recreation, match the chosen reference. For a new company's film, transfer the mechanism and craft while choosing a fresh narrative structure. See `reverse-engineer-reference.md` for source-confirmed examples and observation limits.

Sunrider's focused correction is an example: the broad device section begins scrolling less than a second after the flyover handoff, briefly focuses on products, then changes to source ingredient photography. Two accordion clicks are 2.7 seconds apart. The total cut reduces from 45 to 35 seconds without accelerating the selected page flyover. Those are this project's choices, not durations for the next company.
