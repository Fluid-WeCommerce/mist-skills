# Mist intake

Use Mist's native `steps` panel before generating. Discover the company's real features and prepare a recommendation first. The user chooses coverage; they do not have to design the film or configure the renderer.

## Defaults and recommendation

Use context already provided. Unless it says otherwise, recommend a customer-facing film of roughly 30–45 seconds in 16:9 at 30fps; choose the actual length from the selected demonstrations. Use the current brand, music and quiet effects, with a source-backed browse/get-started CTA. For an app aimed at members or internal users, choose that audience instead and explain it in the intro. Default to no voiceover. Format, audience and sound are optional overrides, not seven mandatory setup questions.

Retain requested/reference art direction alongside those defaults. Rootist supplies reusable mechanisms, not a default shot order or device tableau. Choose a primary treatment from this company’s evidence; preserve a flyover or other signature when the user selected it, mentioning it briefly in the panel intro. Choose camera, lighting and transitions from the brief yourself. The quiz remains concrete company-feature choices plus the user's own answer, with optional overrides in notes.

Offer 3–6 concrete source-backed coverage choices plus an unchecked `custom_coverage` option labelled “Something else — I’ll describe it.” Pre-check only the 2–3 that form a focused story; leave secondary features unchecked. Show the recommendation and defaults in the panel's intro. Never pre-check invented capabilities, unavailable actions or another brand's features. A source page's title alone is not an action/payoff.

## Native payload example

Adapt the title, intro and options to the active company:

```json
{
  "title": "Choose your video's coverage",
  "intro": "I'll use your brand, a customer-facing story, a focused widescreen film of roughly 30–45 seconds, music and quiet effects. Change any of those in the notes.",
  "steps": [
    {
      "id": "coverage",
      "kind": "multi_select",
      "title": "What should the video cover?",
      "subtitle": "I've selected a focused story based on your actual product. Keep it or change the parts below.",
      "skippable": false,
      "mode": "opt_out",
      "min_selected": 1,
      "options": [
        {
          "id": "feature_one",
          "label": "First discovered benefit",
          "pre_checked": true
        },
        {
          "id": "feature_two",
          "label": "Second discovered benefit",
          "pre_checked": true
        },
        {
          "id": "feature_three",
          "label": "Another discovered feature",
          "pre_checked": false
        },
        {
          "id": "custom_coverage",
          "label": "Something else \u2014 I\u2019ll describe it",
          "description": "Add your own idea in the next field or in chat.",
          "pre_checked": false
        }
      ]
    },
    {
      "id": "notes",
      "kind": "text_input",
      "title": "Your own idea or anything to change?",
      "subtitle": "Optional unless you selected Something else. You can also type your answer in chat.",
      "placeholder": "Describe your own idea, or keep the suggested plan",
      "skippable": true,
      "skip_label": "Use the suggested plan"
    }
  ]
}
```

After opening the quiz, END THE TURN and wait. Pre-checked options are suggestions, not submitted answers. Empty coverage cannot pass; cancelled or pending panels produce no film. If the user answers in chat, record that actual answer with `steps_answer`. Its `completed` result is sufficient; do not ask them to submit again.

Use selected coverage and optional notes to derive the message, scene plan, camera treatment and exact timing. If notes are skipped, apply the displayed defaults. Ask a focused follow-up only for a material contradiction, custom delivery that cannot be inferred, missing source access, or voiceover/script/voice requirements. Do not add a second generic approval question for an already requested render.

## Brief and treatment inventory

Alongside coverage, keep a short `treatments` array in `video/brief.json` and matching scene notes in `video/story.md`. Each entry records `id`, `basis` (user request, reference or agent recommendation), `purpose`, `sceneIds`, `sourceAssets`, and `evidence` (planned times initially, actual image/clip paths after review). Track `status` as planned, present, incomplete or omitted, and give a reason for a material omission. Use real scene IDs from this project and update them when the edit changes.

Add `storyCopy` entries with `text`, `sourceBasis`, `sceneIds`, `range_s` and an intended reading hold for each key benefit. Distinguish editorial paraphrases from exact UI text and optional voiceover. Derive this copy from the selected coverage and sources; the user need not write captions or answer another production quiz. A film adapted from a reference with benefit headlines should retain that storytelling layer.

For example, a chosen `layered-page-flyover` can establish the public site in its landing-page scene, with evidence from the close pass, independent element lift, full-page rise and hero/device handoff. A phone lift or product landing belongs only where the selected story supplies a meaningful destination. This is an art-direction inventory, not a requirement to copy every Rootist effect or ask the user to configure them.

Before export, inspect each chosen treatment in actual frames and motion and update its evidence/status. Render completion and MP4 validity check delivery mechanics; they do not show that a requested flyover or other visual treatment made it into the film.

A delegated integration test may use explicitly stated test choices as the operator's test input. Label those as test choices in evidence rather than attributing them to the human. This proves the quiz flow, not what a future user would select.

## Free-text coverage

The next text field accepts an original idea alongside the selected choices. If the user selects `custom_coverage`, require a nonblank idea before generation: if they skip the field, ask one focused follow-up. Include the actual wording in `video/brief.json` as `customCoverage`. A typed chat answer is equally valid: record `custom_coverage` plus its actual description with `steps_answer`, retaining any other selections they explicitly kept. Do not force their words into an unrelated discovered feature or invent an option id. Native steps can only condition a step on an earlier single-select, so do not attach an unsupported multi-select `show_if`; enforce the custom-description requirement after the panel.

An original idea may need additional source access; distinguish an aspiration from a capability the product demonstrably supports. Resolve only that missing information before dependent generation.

## Beat plan and visual differentiation

Keep a compact `video/beat-map.json` or equivalent story notes: shot family, start/end, actual actions/reveals, reading intervals and payoff. Use **Pacing and variation** to review unexplained holds and repeated framing before export. Record a `directionDecision` in the brief with the primary treatment, company-specific basis, supporting shot families and previous-example patterns omitted. Consider two short treatments internally and select one; no extra required quiz, paid generation or multiple full videos. Approximate duration can shorten to fit the story; honor explicit fixed-length requirements.

## Source UI evidence

Keep `sourceUiStates` in the brief or source ledger: actual URL/section, viewport, scroll/selection state, source fonts/media, native versus captured layers, comparison evidence and unresolved deviations. Use **Source UI fidelity** before authoring. The default quiz covers the user’s story choices; it does not silently authorize UI approximation or redesign. Reuse verified source access and ask only if a material dependency is actually missing.
