import { ease, progress } from 'storyboard';
import type { CSSProperties } from 'react';

/** Small reusable masked phrase; the caller supplies the company's verified words and palette. */
export function KineticPhrase({ text, t, start = 0, gap = 0.065, duration = 0.55, accent, accentWord, style }: {
  text: string; t: number; start?: number; gap?: number; duration?: number;
  accent?: string; accentWord?: string; style?: CSSProperties;
}) {
  return <div aria-label={text} style={{ display: 'flex', flexWrap: 'wrap', gap: '0 .25em', ...style }}>
    {text.split(' ').map((word, i) => {
      const p = progress(t, start + i * gap, start + i * gap + duration, ease.outCubic);
      return <span key={`${word}-${i}`} style={{ display: 'inline-block', overflow: 'hidden', paddingBottom: '.12em', marginBottom: '-.12em' }}>
        <span style={{ display: 'inline-block', opacity: p, transform: `translateY(${(1-p)*108}%)`, color: word === accentWord ? accent : undefined }}>{word}</span>
      </span>;
    })}
  </div>;
}
