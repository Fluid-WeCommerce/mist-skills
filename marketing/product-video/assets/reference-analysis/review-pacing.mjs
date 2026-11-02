import fs from 'node:fs/promises';

// Reviews a declared editorial beat map, not pixels. No install, network, rendering or file mutation.
try {
  const file = process.argv[2];
  if (!file) throw new Error('Usage: node review-pacing.mjs video/beat-map.json');
  const map = JSON.parse(await fs.readFile(file, 'utf8'));
  const valid = n => typeof n === 'number' && Number.isFinite(n);
  if (map.version !== 1 || !valid(map.duration) || map.duration <= 0 || !Array.isArray(map.shots) || !map.shots.length) throw new Error('Invalid beat map');
  const gap = map.reviewGap ?? 3, framing = map.reviewFraming ?? 7;
  if (!valid(gap) || gap <= 0 || !valid(framing) || framing <= 0) throw new Error('Invalid review thresholds');
  const flags = [], intervals = [], ids = new Set();
  const label = s => typeof s === 'string' && s.trim();
  for (const shot of map.shots) {
    if (!label(shot.id) || ids.has(shot.id) || !label(shot.family) || !valid(shot.start) || !valid(shot.end) || shot.start < 0 || shot.end <= shot.start || shot.end > map.duration) throw new Error('Invalid or duplicate shot');
    ids.add(shot.id); intervals.push([shot.start, shot.end]);
    const covered = [[shot.start, shot.start], [shot.end, shot.end]];
    for (const e of shot.events ?? []) {
      if (!valid(e.at) || e.at < shot.start || e.at > shot.end || !label(e.label)) throw new Error(`Invalid event: ${shot.id}`);
      covered.push([e.at, e.at]);
    }
    for (const a of shot.actions ?? []) {
      if (!valid(a.start) || !valid(a.end) || a.start < shot.start || a.end > shot.end || a.end <= a.start || !label(a.label)) throw new Error(`Invalid action: ${shot.id}`);
      covered.push([a.start, a.end]);
    }
    for (const r of shot.reading ?? []) {
      if (!valid(r.start) || !valid(r.end) || r.start < shot.start || r.end > shot.end || r.end <= r.start || !label(r.reason)) throw new Error(`Invalid reading hold: ${shot.id}`);
      if (r.end - r.start > gap) flags.push({shot:shot.id, type:'reading-review', start:r.start, end:r.end, reason:r.reason});
      covered.push([r.start, r.end]);
    }
    covered.sort((a,b)=>a[0]-b[0]);
    let through=shot.start;
    for (const [start,end] of covered) {
      if (start-through>gap+1e-7) flags.push({shot:shot.id, type:'unexplained-hold', start:through, end:start, seconds:Number((start-through).toFixed(3))});
      through=Math.max(through,end);
    }
    if (shot.end-shot.start>framing) flags.push({shot:shot.id,type:'long-framing',seconds:Number((shot.end-shot.start).toFixed(3)),family:shot.family});
  }
  intervals.sort((a,b)=>a[0]-b[0]); let through=0;
  for (const [start,end] of intervals) {
    if (start>through+1e-7) flags.push({type:'unmapped-time',start:through,end:start});
    through=Math.max(through,end);
  }
  if (map.duration>through+1e-7) flags.push({type:'unmapped-time',start:through,end:map.duration});
  console.log(JSON.stringify({valid:true,duration:map.duration,shots:map.shots.length,reviewGap:gap,flags,limits:'Declared planning data only. Review the actual normal-speed preview; this does not verify motion, meaning, reading comfort or map-to-code agreement.'},null,2));
} catch(e) {
  console.error(JSON.stringify({valid:false,error:e.message}));process.exitCode=1;
}
