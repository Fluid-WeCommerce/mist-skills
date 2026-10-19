import { asset, ease, progress } from 'storyboard';

/** Editorial photograph, not an invented website control. Keep the original company image. */
export function SourcePhotoCard({ image, label, t, at, x, y, width, height, rotation = 0, exit = 0, font, hiddenImage = false }: {
  image: string; label: string; t: number; at: number; x: number; y: number; width: number; height: number;
  rotation?: number; exit?: number; font: string; hiddenImage?: boolean;
}) {
  const p = progress(t, at, at + .7, ease.outCubic);
  return <div style={{ position: 'absolute', left: x, top: y, width, opacity: p*(1-exit),
    transform: `translateY(${84*(1-p)-80*exit}px) rotate(${rotation*(1-p)}deg)`, fontFamily: font }}>
    {!hiddenImage ? <div style={{ width, height, borderRadius: 20, overflow: 'hidden' }}>
      <img src={asset(image)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
    </div> : <div style={{ width, height }} />}
    <div style={{ marginTop: 24, fontSize: 30, fontWeight: 700, color: '#111' }}>{label}</div>
  </div>;
}
