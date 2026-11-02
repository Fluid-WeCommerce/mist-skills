import type { DevicePose, DeviceStageConfig } from 'storyboard';

export const colors = {
  limestone: '#eeeae1',
  ink: '#23382b',
  sage: '#809778',
  paper: '#faf8f2',
  muted: '#6c7869',
  line: '#d7dccf',
};
export const dimensions = { width: 1920, height: 1080, laptop: { width: 1200, height: 730 }, phone: { width: 390, height: 844 } };
// Independent controls. These poses drive both the native model and its projected screen.
export const devicePoses: Record<'laptop' | 'phone', DevicePose> = {
  laptop: { x: -0.05, y: 0.03, z: 0, size: 2.3, yaw: 6, pitch: 0, roll: 0 },
  phone: { x: 2.7, y: 0.05, z: 0.3, size: 2.55, yaw: -8, pitch: 0, roll: 0 },
};
export const ui = {
  laptopProduct: { x: 195, y: 170, width: 200, height: 420 },
  phoneProduct: { x: 142, y: 174, width: 106, height: 223 },
  phoneButton: { x: 26, y: 725, width: 338, height: 62 },
  cart: { x: 0, y: 326, width: 390, height: 518 },
};
export const camera = { azimuth: 0, elevation: 8, distance: 7, targetY: 1.55, fov: 36 };
export function stageConfig(globalT: number): DeviceStageConfig {
  // A real key light moves before the reading hold. Global time preserves light across the cut.
  const u = Math.max(0, Math.min(1, (globalT - 0.2) / 1.6));
  const p = u * u * (3 - 2 * u);
  const pose = { camera, light: { azimuth: -43 + 8 * p, elevation: 52, intensity: 2.6, softness: 5.5 } };
  return {
    version: 1,
    name: 'Moss limestone set',
    duration: 8,
    animate: false,
    background: colors.limestone,
    floor: true,
    start: pose,
    end: pose,
    devices: (['laptop', 'phone'] as const).map((kind) => ({
      id: kind,
      name: kind === 'laptop' ? 'Moss laptop' : 'Moss phone',
      kind,
      screen: 'screen-underlay.png',
      start: devicePoses[kind],
      end: devicePoses[kind],
    })),
  };
}
