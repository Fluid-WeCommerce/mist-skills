import type { CSSProperties, ReactNode } from 'react';
import type { DevicePose } from 'storyboard';
import { modelMetrics } from './modelMetrics';
import { camera, devicePoses, dimensions } from './tokens';

type Vec = readonly [number, number, number];
type Point = { x: number; y: number };
const rad = (n: number) => (n * Math.PI) / 180;
const dot = (a: Vec, b: Vec) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const sub = (a: Vec, b: Vec): Vec => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a: Vec, b: Vec): Vec => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (v: Vec): Vec => {
  const l = Math.hypot(...v);
  return [v[0] / l, v[1] / l, v[2] / l];
};
function world(p: Vec, pose: DevicePose): Vec {
  const a = rad(pose.roll),
    b = rad(pose.pitch),
    c = rad(pose.yaw);
  const x1 = p[0] * Math.cos(a) - p[1] * Math.sin(a),
    y1 = p[0] * Math.sin(a) + p[1] * Math.cos(a);
  const y2 = y1 * Math.cos(b) - p[2] * Math.sin(b),
    z2 = y1 * Math.sin(b) + p[2] * Math.cos(b);
  return [
    (x1 * Math.cos(c) + z2 * Math.sin(c)) * pose.size + pose.x,
    y2 * pose.size + pose.y,
    (-x1 * Math.sin(c) + z2 * Math.cos(c)) * pose.size + pose.z,
  ];
}
function project(p: Vec): Point {
  const az = rad(camera.azimuth),
    el = rad(camera.elevation),
    d = camera.distance;
  const eye: Vec = [Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d + camera.targetY, Math.cos(az) * Math.cos(el) * d];
  const forward = norm(sub([0, camera.targetY, 0], eye)),
    right = norm(cross(forward, [0, 1, 0])),
    up = cross(right, forward);
  const v = sub(p, eye),
    z = dot(v, forward),
    f = dimensions.height / (2 * Math.tan(rad(camera.fov) / 2));
  return { x: dimensions.width / 2 + (f * dot(v, right)) / z, y: dimensions.height / 2 - (f * dot(v, up)) / z };
}
export function screenCorners(kind: 'laptop' | 'phone'): Point[] {
  return modelMetrics[kind].corners.map((p) => project(world(p as unknown as Vec, devicePoses[kind])));
}
export function homography(q: Point[]) {
  const [a, b, c, d] = q,
    dx1 = b.x - c.x,
    dx2 = d.x - c.x,
    dx3 = a.x - b.x + c.x - d.x;
  const dy1 = b.y - c.y,
    dy2 = d.y - c.y,
    dy3 = a.y - b.y + c.y - d.y;
  const det = dx1 * dy2 - dx2 * dy1,
    g = (dx3 * dy2 - dx2 * dy3) / det,
    h = (dx1 * dy3 - dx3 * dy1) / det;
  return { a: b.x - a.x + g * b.x, b: d.x - a.x + h * d.x, c: a.x, d: b.y - a.y + g * b.y, e: d.y - a.y + h * d.y, f: a.y, g, h };
}
export function screenPoint(kind: 'laptop' | 'phone', x: number, y: number): Point {
  const h = homography(screenCorners(kind)),
    size = dimensions[kind],
    u = x / size.width,
    v = y / size.height,
    w = h.g * u + h.h * v + 1;
  return { x: (h.a * u + h.b * v + h.c) / w, y: (h.d * u + h.e * v + h.f) / w };
}
export function matrixForQuad(q: Point[], width: number, height: number) {
  const h = homography(q);
  return `matrix3d(${h.a / width},${h.d / width},0,${h.g / width},${h.b / height},${h.e / height},0,${h.h / height},0,0,1,0,${h.c},${h.f},0,1)`;
}
/** Clip in the native display plane BEFORE the perspective transform. */
export function displayClip(kind: 'laptop' | 'phone') {
  const { width, height } = dimensions[kind];
  const inset = kind === 'phone' ? 0.75 : 0.35;
  const outline = modelMetrics[kind].displayOutline;
  return `polygon(${outline.map(([u,v]) => `${100 * (inset + u * (width-2*inset)) / width}% ${100 * (inset + v * (height-2*inset)) / height}%`).join(',')})`;
}
export function ProjectedScreen({ kind, children, style }: { kind: 'laptop' | 'phone'; children: ReactNode; style?: CSSProperties }) {
  const size = dimensions[kind];
  return (
    <div
      data-layer={`${kind}-screen`}
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: size.width,
        height: size.height,
        transform: matrixForQuad(screenCorners(kind), size.width, size.height),
        transformOrigin: '0 0',
        clipPath: displayClip(kind),
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
