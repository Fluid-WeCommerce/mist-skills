import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = args.indexOf(name);
  if (i >= 0 && !args[i + 1]) throw new Error(`Missing value for ${name}`);
  return i >= 0 ? path.resolve(args[i + 1]) : fallback;
};
const runtimeDir = arg('--runtime-dir', fileURLToPath(new URL('../../../', import.meta.url)));
const projectDir = arg('--project-dir', fileURLToPath(new URL('../', import.meta.url)));
const THREE = await import(pathToFileURL(path.join(runtimeDir, 'src/runtime/device-stage/vendor/three.module.js')));
const { GLTFLoader } = await import(pathToFileURL(path.join(runtimeDir, 'src/runtime/device-stage/vendor/GLTFLoader.js')));

// The bundled OLED has a convex rounded perimeter. Its bounds are NOT its display mask.
// Retain the measured perimeter rather than guessing a CSS border radius.
function convexOutline(points) {
  const unique = [...new Map(points.map(p => [p.map(v => v.toFixed(7)).join(','), p])).values()]
    .sort((a,b) => a[0]-b[0] || a[1]-b[1]);
  const cross = (o,a,b) => (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
  const half = list => {
    const h=[];
    for (const p of list) {
      while (h.length > 1 && cross(h.at(-2), h.at(-1), p) <= 1e-9) h.pop();
      h.push(p);
    }
    return h.slice(0,-1);
  };
  return [...half(unique), ...half([...unique].reverse())].map(p => p.map(v => +v.toFixed(8)));
}


globalThis.ProgressEvent ||= class ProgressEvent {
  constructor(type, init) {
    this.type = type;
    Object.assign(this, init);
  }
};

// Read only the two shared runtime models. Strip textures in memory for this geometry measurement.
const models = { laptop: 'UpOvKwLUUXPmnPU', phone: 'OLED' };
const all = {};
for (const [kind, materialName] of Object.entries(models)) {
  const raw = await fs.readFile(path.join(runtimeDir, `public/device-stage/${kind}.glb`));
  const jsonLength = raw.readUInt32LE(12);
  const json = JSON.parse(raw.subarray(20, 20 + jsonLength).toString());
  const binAt = 20 + jsonLength;
  const bin = raw.subarray(binAt + 8, binAt + 8 + raw.readUInt32LE(binAt));
  json.buffers = [{ byteLength: bin.length, uri: `data:application/octet-stream;base64,${bin.toString('base64')}` }];
  delete json.images;
  delete json.textures;
  delete json.samplers;
  json.materials = json.materials.map((m) => ({ name: m.name, pbrMetallicRoughness: {} }));
  const gltf = await new GLTFLoader().parseAsync(JSON.stringify(json), '');
  const group = new THREE.Group(),
    orient = new THREE.Group();
  group.add(orient);
  orient.add(gltf.scene);
  group.updateMatrixWorld(true);
  const screens = [];
  gltf.scene.traverse((o) => {
    if (o.isMesh && (Array.isArray(o.material) ? o.material : [o.material]).some((m) => m.name === materialName)) screens.push(o);
  });
  let bounds = new THREE.Box3().setFromObject(orient),
    size = bounds.getSize(new THREE.Vector3());
  if (kind === 'phone') {
    if (size.z > size.y && size.z > size.x) orient.rotation.x = -Math.PI / 2;
    else if (size.x > size.y) orient.rotation.z = Math.PI / 2;
    group.updateMatrixWorld(true);
  }
  const s = screens[0],
    normals = s.geometry.getAttribute('normal'),
    n = new THREE.Vector3();
  for (let i = 0; i < normals.count; i++) n.add(new THREE.Vector3().fromBufferAttribute(normals, i));
  n.normalize().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(s.matrixWorld));
  const screenDepth = new THREE.Box3().setFromObject(s).getCenter(new THREE.Vector3()).z;
  const bodyDepth = new THREE.Box3().setFromObject(orient).getCenter(new THREE.Vector3()).z;
  if (kind === 'phone' ? screenDepth < bodyDepth : n.z < 0) orient.rotation.y += Math.PI;
  group.updateMatrixWorld(true);
  bounds = new THREE.Box3().setFromObject(orient);
  size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  orient.position.set(-center.x, -bounds.min.y, -center.z);
  group.scale.setScalar(1 / size.y);
  group.updateMatrixWorld(true);
  const points = [];
  for (const mesh of screens) {
    const positions = mesh.geometry.getAttribute('position');
    for (let i = 0; i < positions.count; i++)
      points.push(new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld));
  }
  const b = new THREE.Box3().setFromPoints(points);
  // Laptop lid is planar but tilted. Pick the screen's depth at each horizontal edge.
  const depthAt = (y) => points.filter((p) => Math.abs(p.y - y) < 0.0001).reduce((sum, p, _, a) => sum + p.z / a.length, 0);
  const zTop = depthAt(b.max.y),
    zBottom = depthAt(b.min.y);
  const corners = [
    [b.min.x, b.max.y, zTop],
    [b.max.x, b.max.y, zTop],
    [b.max.x, b.min.y, zBottom],
    [b.min.x, b.min.y, zBottom],
  ];
  all[kind] = {
    corners,
    displayOutline: convexOutline(points.map(p => [(p.x-b.min.x)/(b.max.x-b.min.x), (b.max.y-p.y)/(b.max.y-b.min.y)])),
    bounds: { min: b.min.toArray(), max: b.max.toArray() },
    bodyAspect: size.x / size.y,
    vertices: points.length,
  };
}
await fs.mkdir(path.join(projectDir, 'evidence'), { recursive: true });
await fs.writeFile(path.join(projectDir, 'evidence/model-metrics.json'), JSON.stringify(all, null, 2));
await fs.writeFile(
  path.join(projectDir, 'components/modelMetrics.ts'),
  `// Measured from shared built-in GLBs by tools/model-metrics.mjs. No asset copies.\nexport const modelMetrics = ${JSON.stringify(all, null, 2)} as const;\n`,
);
console.log(JSON.stringify(Object.fromEntries(Object.entries(all).map(([k,v])=>[k,{vertices:v.vertices,outlinePoints:v.displayOutline.length,bounds:v.bounds}])), null, 2));
