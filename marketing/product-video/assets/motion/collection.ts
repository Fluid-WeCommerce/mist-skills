/** Copy into a native Storyboard project's components/. No assets or runtime dependency. */
export interface CollectionOptions {
  count: number;
  start: number;
  gap: number;
  flight: number;
  anticipation?: number;
  expansion?: number;
  clearance?: number;
}

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const smooth = (x: number) => x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2;
const progress = (t: number, a: number, b: number) => smooth(clamp01((t - a) / (b - a)));

/** Rank is choreography order, not necessarily the item's position in an array. */
export function collectionClock(options: CollectionOptions) {
  const { count, start, gap, flight, anticipation = 0.24, expansion = 0.05, clearance = 0.03 } = options;
  if (!Number.isInteger(count) || count < 1 || ![start, gap, flight, anticipation, expansion, clearance].every(Number.isFinite)
    || gap < 0 || flight <= 0 || anticipation < 0 || expansion < 0 || clearance < 0) {
    throw new Error('Collection needs a positive count/flight and finite, nonnegative intervals.');
  }
  const departure = (rank: number) => {
    if (!Number.isInteger(rank) || rank < 0 || rank >= count) throw new Error('Collection rank is outside its count.');
    return start + gap * rank;
  };
  const arrival = (rank: number) => departure(rank) + flight;
  const lastArrival = arrival(count - 1);
  return {
    departure,
    arrival,
    lastArrival,
    clearAt: lastArrival + clearance,
    piece(t: number, rank: number) {
      const at = departure(rank);
      const windup = anticipation > 0 ? progress(t, at - anticipation, at) : 0;
      const pull = progress(t, at, arrival(rank));
      const scale = (1 + expansion * windup) * (1 - pull);
      return { scale, opacity: progress(scale, 0.02, 0.12), pull };
    },
  };
}
