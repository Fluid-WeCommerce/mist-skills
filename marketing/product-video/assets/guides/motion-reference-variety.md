# Reference-derived motion variety

Use when a user asks to learn from a motion reference, or an approved film spends too long in one framing. Change the representation and viewer's focus, while retaining the selected story and company sources. This is an optional treatment library, not a mandate to use every effect.

## Observed reference

[Rabi Guha's OpenUI launch film](https://x.com/rabi_guha/status/2110737805823672518/video/1), reviewed 2026-10-15. Times below are approximate seconds in its 89-second first video. The film was inspected as actual video frames at several sampling rates; these notes describe the visible techniques, not the software used to make them. The portable skill contains none of its footage, logos, screenshots, music or spoken script.

| Reference range | Visible motion grammar | Adaptation criterion |
| --- | --- | --- |
| 0–11 | Filmed presenter, desk perspective and brief historical cutaways | Use only if the company provides suitable footage. An optional bookend, not a reason to generate a fake founder. |
| 12–18 | A small interface element gives way to a field of response cards; the shot changes scale | Move from one real item to the broader company collection when that contrast is the point. Avoid decorative grids of unreadable filler. |
| 20–30, 48–56 | Two contrasting UI outputs, followed by a camera push into the useful one and a specific control | Show two actual states or an honest editorial comparison. Track the chosen subject into a readable interaction; do not fabricate a competitor or feature. |
| 33–35, 41–46 | Short kinetic phrases, one accented word, a small dimensional token crossing the sentence, focus/blur during travel | Reveal words through masks, keep an anchor/baseline, and accent a meaningful company word. Reserve blur for travel; settle crisp for reading. Use licensed company artwork if a token is useful. |
| 57–64 | An explanatory canvas with boxes, curved connectors and dimensional objects; the camera follows the chain, then reveals its result | Draw a connector toward the next node before following it. Choose a real relationship worth explaining. A technical diagram does not automatically suit a consumer product. |
| 65–73 | A short typographic resolution with supporting UI entering the wider frame | Give the message a clear reading hold, then make the next action visible. |
| 75–89 | Return to filmed bookend, supporting number, final brand resolve | Use only verified company numbers and appropriate footage. A moving logo exit is optional. |

The useful contrast is **context → graphic explanation → focused UI proof**. The change in scale carries attention. Simply adding the same slide-up to every shot does not recreate that variety.

## Choose and implement a coherent subset

Preserve approved signatures such as the physical-page flyover. For a short website film, one editorial insert between browsing and the next meaningful interaction can supply variety without extending the film or removing its reading time. Record the source, purpose, real scene/time range and evidence in the existing treatment inventory. Keep adaptations distinct from literal reference observations.

Copy `assets/motion/KineticPhrase.tsx` for a seek-safe word-mask reveal and `assets/motion/SourcePhotoCard.tsx` for staggered source-photograph entrances. Both use the existing native Storyboard runtime; callers supply real company text, asset paths, time and palette. These helpers introduce no new dependency, generator or rendering engine. A photograph panel is an editorial illustration, not proof of an actual UI control.

For a photo-to-UI match, use the existing device projection helpers. Keep the outgoing image and its crop stable at departure; sample the live destination rectangle/quad from the same global timeline as the screen scroll. Interpolate both the projected quad and the image's native container dimensions so `object-fit` resolves to the exact destination crop. Hide the destination copy until handoff. The final overlay pose and the first native pose must agree, including corners and opacity. Keep the entering device behind the established foreground image until seating.

For a connected explanation, draw the curve from source to destination, stagger node arrivals and let the camera follow that flow. Let the final view explain the relationship. Use 3D only where depth helps; do not turn an ordinary ingredient list into an invented production machine.

Use short overlaps and readable holds. Tune roughly 0.5–0.8-second reveals and 0.1–0.16-second photo staggers to the actual film; these are starting points. Avoid a pause before a continuing camera flight, and avoid masking a late arrival with the next wipe. One or two supporting accents are usually enough; no sound is required for every word or image.

## Keep the company content binding explicit

In Mist, get the expected company from the active workspace/context (`{{company.name}}`), not from a previous film or skill example. Populate the quiz from that company's actual features. Carry the chosen company's pages, original media URLs, hashes, exact copy and CTA into `video/source-map.json` and the brief. Reference videos supply craft only.

`assets/renderer/verify-company-sources.mjs` is an optional reusable provenance check to copy beside the project's renderer adapter. Before export run it with the expected active company, for example:

```sh
node tools/product-video/verify-company-sources.mjs --company 'The active company' --root .
```

The default map is `video/source-map.json`; use `--source-dir` or `--map` for a different project layout. It checks the brief/map/active company agreement, company source-page origins, declared visual hashes, required visual coverage and traced copy against frozen local source text. It also catches untraced files in `video/assets/brand`. It does not discover undeclared remote media, prove rights clearance, approve claims or certify what a finished frame shows. Inspect the actual source use and film as well.

For an editorial headline, set `editorial: true` and include a nonblank `sourceQuote` copied from the declared frozen `sourceFile`; `text` holds the honest paraphrase used in the film. The checker verifies that underlying quote exists, not that the paraphrase is semantically justified. Review the wording against the real action. Exact UI copy omits `editorial` and must match its own `text` in the source.

Minimal map shape (all paths relative to the project root):

```json
{
  "version": 1,
  "company": "The active company",
  "sourceOrigins": ["https://company.example"],
  "assets": [{
    "file": "video/assets/brand/product.jpg",
    "kind": "company-source",
    "sourcePage": "https://company.example/shop",
    "sourceUrl": "https://company.example/media/product.jpg",
    "sha256": "actual-sha256-of-the-local-file"
  }],
  "copy": [{
    "text": "Exact words used in the film",
    "sourcePage": "https://company.example/shop",
    "sourceFile": "source-research/shop-text.txt"
  }]
}
```

Use `company-capture` for captured company-page layers, `ui-reconstruction` for a faithful native-UI capture and `neutral` only for company-free backing pixels. All but neutral require an allowed company `sourcePage`. Hash the actual input files; do not turn a wrong-company asset into a valid record merely by relabelling it. Include all required visuals and brand-folder files. A shared image CDN is not evidence of company ownership; its referring company page matters.

## Review before the next full export

Capture a settled frame and a compact motion sequence for the new insert, plus closely spaced frames through the departure/landing and a repeated intermediate seek. Check word clipping, crop, depth order, duplicate images, screen mask, reading time and continuous scene boundaries. Keep a review-only or render hold intact. Do not trigger a full export, path tracer, paid asset search or image-generation campaign simply to assess a new motion idea.

Sunrider's local test adapts this as an ingredient photo triptych, source-heading word reveal and aloe-photo match into the laptop accordion at 17.2–22.2 seconds. That is one demonstrated adaptation, not a fixed template or timing for other companies.
