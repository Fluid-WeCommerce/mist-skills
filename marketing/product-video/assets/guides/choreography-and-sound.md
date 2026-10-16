# Choreography and sound refinements

Use this reference for a staggered collection, an interactive product moment, a screen-to-device lift, or an audio polish pass. The working Rootist project supplies examples; the only portable code here is the small collection clock. It does not include models, UI, audio or a renderer.

## Stagger an assembly without breaking its parts

Copy `assets/motion/collection.ts` from the skill into the target project's `components/`. The clock is a pure function of scene time and does not use browser history, CSS animation or timers.

```tsx
import { collectionClock } from '../components/collection';

// Example only: tune the gap, distance, duration and reading hold for this shot.
const collect = collectionClock({ count: 4, start: 1.5, gap: .07, flight: .42 });
const destination = { x: 960, y: 850 };

// Inside the scene: rank expresses departure order; it need not equal the data index.
const pose = collect.piece(t, rank);
const style = {
  position: 'absolute' as const, inset: 0,
  transformOrigin: `${destination.x}px ${destination.y}px`,
  transform: `scale(${pose.scale})`, opacity: pose.opacity,
};
// <div style={style}><DeviceBody /><ProjectedScreen /><PhoneChrome /></div>
// A flood/wipe begins at collect.clearAt. An accent can land on collect.arrival(rank).
```

The wrapper must use the same canvas coordinate system as `destination`. Group a device body and projected screen before transforming them. For Three.js sprites, apply the same scale to their centers about the destination, dimensions and elevation. Do not stagger the screen separately from its body. Assign explicit ranks when collecting clockwise, nearest-first or according to story importance.

A small outward wind-up makes the inward pull readable. A following flood must wait for the last arrival, including any later phone or wordmark. Keep enough time after the final reveal to read the end card. An individual faint landing accent or a single grouped accent can be enough; seven arrivals do not require seven loud clicks.

Check the first anticipation, first departure, an overlapping flight, last arrival and following flood. Also compare the continuous scene boundary and repeat a middle seek after visiting the end. Test the helper in isolation, but inspect a real frame too: mathematical correctness does not prove correct transform origins, clipping, projection or depth order.

## Source-faithful interaction and emphasis

Observe the actual website interaction before rebuilding it. Preserve the visible order of hover, lift/open, click/press, effect and scroll. A plausible replacement section can still be wrong; use the real section's geometry, words and product artwork. Keep source recordings and film timing separate.

Define shared interaction moments once. Use them for the pointer, product action, camera and audio. If a source interaction needs a live simulation, capture deterministic time-indexed frames or bake a trajectory for the film. Do not leave the production scene running its own simulation clock.

A brief punch-in can reward a distinctive interaction or make small analytics legible. Crop the whole assembly, including the cursor and device, rather than enlarging only the native screen content. Return to the exact shared pose before the next handoff. When a preview phone detaches, inherit the parent screen's orientation until the lift begins, then interpolate toward the independent phone pose.

Check outgoing and incoming layer order mid-transition. Established foreground objects should not be covered accidentally by a newly mounted panel. Keep an incoming panel behind them until the intended handoff, or give the occlusion an explicit story purpose.

## Mix for comfortable emphasis

Listen when audio playback is available, and use measurements for clipping, missing sources, level relationships and repeatability. Do not claim to have listened when only measuring.

- Check the full film, then focused interaction clips. Accents that are individually modest can pile up at a click, burst or landing.
- Fix gain and harsh frequency content before applying broad compression. Short, dry effects usually need less level than a long cinematic cue.
- A cue can score highly against a quiet frequency band while still being uncomfortable. A low audibility score does not justify raising every supporting sound.
- Keep repeated clicks in a coherent family and level range. Reserve large movement sounds for useful travel. Do not sonify every pin, count or navigation item.
- Align a landing's audible peak, accounting for the source's attack and any pitch/playback-rate change. Use the same arrival clock as the visual.
- Keep the selected track unless the user asks to change it. Prefer gain, a shorter tail or a softened derivative over replacing an approved sound without reason. Retain the original.

For gain comparisons, `20 * log10(newGain / oldGain)` gives the dB change. Filtering also changes energy; measure the rendered derivative rather than attributing every reduction to its gain value. Integrated LUFS and true peak describe delivery level/headroom, not taste. Choose targets for the delivery context rather than treating one film's result as mandatory.

Cuelume is an optional source of small synthesized UI cues: https://github.com/danielwh2/cuelume . In the Rootist pass, its pinned offline renderer produced repeatable isolated WAVs. If using it elsewhere, inspect the current source and license, freeze chosen single-cue files, and record the version/seed. Do not use a review montage as a cue or add a new runtime merely to play a fixed sound. A physics library is optional too; bake or analytically sample trajectories so seeking remains deterministic.

## Verify the delivered artifact

Use a short comparison clip for the changed motion or mix. When a whole export is authorized, verify the actual encoded film and refresh links to the new version; a preview or job-start response is not completion. Record the renderer actually selected, format, audio and any failed checks. Preserve the old export and unsent draft. A local handoff URL, published link and sent message are distinct delivery states.

## Gain follows the actual source

A fixed soundtrack gain is not a sensible cross-company default: measure the supplied track first. For a music-only film, a recording already around−20LUFS does not need the same ducking as loud music under speech. In the Sunrider local test, applying0.3 to an original score at−19.7LUFS produced a final−30.2LUFS mix; raising the bed to0.8 was the focused correction. These are observations for that source, not universal targets. Keep intentionally quiet click gains separate, and distinguish measured level/headroom from listening comfort.
