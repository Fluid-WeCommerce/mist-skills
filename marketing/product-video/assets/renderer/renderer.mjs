#!/usr/bin/env node
/** Native Storyboard bridge. No package dependencies; Node 22.12+.
 * Every command finishes promptly; rendering itself belongs to Storyboard.
 */
import fs from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { captureNativeFrames } from './capture.mjs';

const ID = /^[a-z0-9][a-z0-9-]{0,63}$/;
const ACTIVE = new Set(['queued', 'rendering', 'encoding']);
const ROOTS = ['components', 'assets', 'music', 'sounds'];
const STATE = '.mist-desktop/product-video-renderer';
const MARKER = '.mist-product-video-owner.json';
const executeFile = promisify(execFile);
const hash = (data) => createHash('sha256').update(data).digest('hex');
const fail = (message) => { throw new Error(message); };
const exists = async (file) => fs.lstat(file).then(() => true, (e) => e.code === 'ENOENT' ? false : Promise.reject(e));
const json = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));

function relativeName(value, label = 'path') {
  if (typeof value !== 'string' || !value || value.includes('\\') || value.includes('\0') || value.includes(':') || value.startsWith('/') || value.split('/').some((v) => !v || v === '.' || v === '..')) fail(`Unsafe ${label}: ${String(value)}`);
  return value;
}

function inside(root, file) {
  const rel = path.relative(root, file);
  return rel !== '' && !rel.startsWith(`..${path.sep}`) && rel !== '..' && !path.isAbsolute(rel);
}

/** Reject symlinks, including an existing ancestor of a not-yet-created path. */
async function safePath(root, relative, allowMissing = false) {
  const rel = relativeName(relative);
  const target = path.resolve(root, ...rel.split('/'));
  if (!inside(root, target)) fail(`Path escapes its root: ${rel}`);
  let cursor = root;
  for (const part of rel.split('/')) {
    cursor = path.join(cursor, part);
    const st = await fs.lstat(cursor).catch((e) => {
      if (e.code === 'ENOENT' && allowMissing) return null;
      throw e;
    });
    if (st?.isSymbolicLink()) fail(`Symlinks are not accepted: ${rel}`);
  }
  return target;
}

async function atomicJson(file, value) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  const temp = `${file}.${randomUUID()}.tmp`;
  await fs.writeFile(temp, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
  await fs.rename(temp, file);
}

async function fileHash(file) {
  const digest = createHash('sha256');
  for await (const chunk of createReadStream(file)) digest.update(chunk);
  return digest.digest('hex');
}

async function regular(root, relative) {
  const file = await safePath(root, relative);
  if (!(await fs.lstat(file)).isFile()) fail(`Expected a regular file: ${relative}`);
  return file;
}

async function tree(root, dir, files) {
  const base = await safePath(root, dir);
  if (!(await fs.lstat(base)).isDirectory()) fail(`Expected a directory: ${dir}`);
  for (const entry of (await fs.readdir(base, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const rel = `${dir}/${entry.name}`;
    relativeName(rel);
    if (entry.isSymbolicLink()) fail(`Symlinks are not accepted: ${rel}`);
    if (entry.isDirectory()) await tree(root, rel, files);
    else if (entry.isFile()) files.push({ relative: rel, file: await regular(root, rel) });
    else fail(`Unsupported file type: ${rel}`);
  }
}

function number(value, min, max, label, integer = false) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max || (integer && !Number.isInteger(value))) fail(`Invalid ${label}`);
  return value;
}

function settings(raw) {
  if (!raw || typeof raw.name !== 'string' || !raw.name.trim()) fail('project.json needs a name');
  return {
    name: raw.name.trim(),
    width: number(raw.width, 64, 7680, 'width', true),
    height: number(raw.height, 64, 7680, 'height', true),
    fps: number(raw.fps, 1, 120, 'fps', true),
  };
}

async function sourcePlan(projectRoot, config) {
  const sourceRoot = await safePath(projectRoot, config.sourceDir);
  if (!(await fs.lstat(sourceRoot)).isDirectory()) fail('sourceDir must be a directory');
  const manifestFile = await regular(sourceRoot, 'project.json');
  const raw = await json(manifestFile);
  const meta = settings(raw);
  if (!Array.isArray(raw.scenes) || !raw.scenes.length) fail('project.json needs at least one scene');
  const ids = new Set();
  const files = [];
  const scenes = [];
  for (const scene of raw.scenes) {
    if (!ID.test(scene?.id) || ids.has(scene.id)) fail('Each scene needs a unique file-safe id');
    ids.add(scene.id);
    if (typeof scene.name !== 'string' || !scene.name.trim()) fail(`Missing scene name: ${scene.id}`);
    number(scene.duration, 0.1, 600, `duration of ${scene.id}`);
    const rel = `scenes/${scene.id}.tsx`;
    files.push({ relative: rel, file: await regular(sourceRoot, rel) });
    scenes.push({ id: scene.id, name: scene.name.trim(), duration: scene.duration });
  }
  for (const dir of ROOTS) if (await exists(path.join(sourceRoot, dir))) await tree(sourceRoot, dir, files);
  let artDirection = '';
  if (await exists(path.join(sourceRoot, 'art-direction.md'))) artDirection = await fs.readFile(await regular(sourceRoot, 'art-direction.md'), 'utf8');
  for (const rel of raw.requiredAssets ?? []) {
    relativeName(rel, 'required asset');
    if (!ROOTS.some((dir) => rel.startsWith(`${dir}/`))) fail('Required assets must be inside assets, components, music, or sounds');
    await regular(sourceRoot, rel);
  }
  let music = null;
  if (raw.music) {
    relativeName(raw.music.file, 'music file');
    if (raw.music.file.includes('/')) fail('music.file must be a filename inside music/');
    await regular(sourceRoot, `music/${raw.music.file}`);
    music = { file: raw.music.file, start: number(raw.music.start ?? 0, 0, 86400, 'music start'), volume: number(raw.music.volume ?? 0.3, 0, 1, 'music volume') };
  }
  const records = await Promise.all(files.map(async (file) => ({ ...file, sha256: await fileHash(file.file) })));
  const contentHash = hash(JSON.stringify({ meta, scenes, music, artDirection, files: records.map(({ relative, sha256 }) => ({ relative, sha256 })).sort((a, b) => a.relative.localeCompare(b.relative)) }));
  return { meta, scenes, files: records, artDirection, music, sourceRoot, contentHash };
}

function origin(value) {
  const url = new URL(value);
  if (url.protocol !== 'http:' || !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || url.username || url.password || url.pathname !== '/' || url.search || url.hash) fail('rendererUrl must be an HTTP loopback origin, such as http://127.0.0.1:5199');
  return url.origin;
}

async function loadConfig(projectRoot, configFile) {
  const config = await json(await regular(projectRoot, configFile));
  const url = origin(config.rendererUrl);
  if (typeof config.projectsDir !== 'string' || !path.isAbsolute(config.projectsDir)) fail('projectsDir must explicitly name the local Storyboard projects directory');
  const projectsDir = await fs.realpath(config.projectsDir);
  const sourceDir = relativeName(config.sourceDir ?? 'video', 'sourceDir');
  const outputDir = relativeName(config.outputDir ?? 'exports', 'outputDir');
  if (outputDir === sourceDir || outputDir.startsWith(`${sourceDir}/`)) fail('outputDir must not be inside sourceDir');
  if (!['three', 'mutracer'].includes(config.render?.renderer)) fail('Choose render.renderer: three or mutracer');
  const render = { renderer: config.render.renderer, scale: number(config.render.scale ?? 1, 0.25, 4, 'render scale') };
  if (config.render.fps !== undefined) render.fps = number(config.render.fps, 1, 120, 'render fps', true);
  if (config.runtimeDir !== undefined && (typeof config.runtimeDir !== 'string' || !path.isAbsolute(config.runtimeDir))) fail('runtimeDir must be an absolute path to the existing Storyboard checkout');
  const runtimeDir = config.runtimeDir ? await fs.realpath(config.runtimeDir) : null;
  if (runtimeDir && !inside(runtimeDir, projectsDir)) fail('Configured projectsDir must be inside runtimeDir');
  let chromiumExecutable;
  if (config.chromiumExecutable !== undefined) {
    if (typeof config.chromiumExecutable !== 'string' || !path.isAbsolute(config.chromiumExecutable) || !(await fs.stat(config.chromiumExecutable)).isFile()) fail('chromiumExecutable must be the explicit path to an existing browser executable');
    chromiumExecutable = config.chromiumExecutable;
  }
  const executables = {};
  for (const name of ['ffprobe', 'ffmpeg']) {
    const value = config[`${name}Executable`] ?? name;
    if (typeof value !== 'string' || !value.trim() || value.includes('\0')) fail(`${name}Executable must name an existing executable or a command on PATH`);
    executables[name] = value;
  }
  const requiredRuntimeFiles = [];
  if (config.requiredRuntimeFiles?.length) {
    if (typeof config.runtimeDir !== 'string' || !path.isAbsolute(config.runtimeDir)) fail('runtimeDir must explicitly name the local Storyboard checkout when requiredRuntimeFiles are configured');
    for (const check of config.requiredRuntimeFiles) {
      const file = await regular(runtimeDir, relativeName(check.file, 'runtime file'));
      const sha256 = await fileHash(file);
      if (check.sha256 !== undefined && (!/^[a-f0-9]{64}$/.test(check.sha256) || check.sha256 !== sha256)) fail(`Runtime file fingerprint does not match: ${check.file}`);
      requiredRuntimeFiles.push({ file: check.file, sha256, bytes: (await fs.stat(file)).size, expectedProvided: check.sha256 !== undefined, matchesExpected: check.sha256 !== undefined ? true : null });
    }
  }
  return { rendererUrl: url, projectsDir, sourceDir, outputDir, render, requiredRuntimeFiles, runtimeDir, chromiumExecutable, executables };
}

async function request(config, route, method = 'GET', body, binary = false) {
  const remaining = config.deadline - Date.now();
  if (remaining <= 0) fail('Bridge command reached its 45 second time budget. Work and ownership state are preserved; retry the command');
  const response = await fetch(`${config.rendererUrl}/api${route}`, {
    method, redirect: 'error', signal: AbortSignal.timeout(Math.min(20000, remaining)),
    headers: body === undefined ? undefined : { 'content-type': binary ? 'application/octet-stream' : 'application/json', ...(binary ? { 'x-filename': encodeURIComponent(binary) } : {}) },
    body: body === undefined ? undefined : binary ? body : JSON.stringify(body),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) fail(`Storyboard ${method} ${route}: ${response.status} ${result.error ?? response.statusText}`);
  return result;
}

async function health(config) {
  const info = await request(config, '/info');
  if (typeof info.projectsDir !== 'string' || await fs.realpath(info.projectsDir) !== config.projectsDir) fail('Configured projectsDir does not match the connected Storyboard server');
  return info;
}

async function readState(projectRoot) {
  const file = await safePath(projectRoot, `${STATE}/state.json`, true);
  return await exists(file) ? json(file) : null;
}

async function saveState(projectRoot, state) {
  const file = await safePath(projectRoot, `${STATE}/state.json`, true);
  await atomicJson(file, state);
}

async function owned(projectRoot, config, state) {
  if (!state || state.version !== 1 || !ID.test(state.projectId) || state.projectRoot !== projectRoot || state.rendererUrl !== config.rendererUrl || state.projectsDir !== config.projectsDir || typeof state.ownerToken !== 'string') fail('No matching bridge-owned project. Run sync to create a new project; existing projects cannot be adopted');
  const dir = await safePath(config.projectsDir, state.projectId);
  const marker = await json(await regular(dir, MARKER));
  if (marker.ownerToken !== state.ownerToken || marker.projectRoot !== projectRoot || marker.projectId !== state.projectId) fail('Renderer ownership marker does not match. No changes were made');
  const remote = await request(config, `/projects/${state.projectId}`);
  if (remote.id !== state.projectId || await fs.realpath(remote.dir) !== dir) fail('Storyboard project location does not match the owned folder');
  return { dir, remote };
}

async function jobs(config, state) {
  const result = await request(config, `/projects/${state.projectId}/renders`);
  if (!Array.isArray(result.jobs)) fail('Storyboard returned no render job list');
  return result.jobs;
}

async function currentJob(config, state) {
  if (!state.job?.id) fail('No render has been submitted from this bridge');
  const job = (await jobs(config, state)).find((item) => item.id === state.job.id && item.projectId === state.projectId);
  if (!job) fail(`Render job ${state.job.id} is no longer known to Storyboard (possibly restarted). The bridge cannot claim it completed. Existing output is preserved; verify it separately before a new submit`);
  if (!['queued', 'rendering', 'encoding', 'done', 'error', 'cancelled'].includes(job.status)) fail('Storyboard returned an unknown render status');
  return job;
}

async function copySource(dir, file, relative = file.relative) {
  const destination = await safePath(dir, relative, true);
  await fs.mkdir(path.dirname(destination), { recursive: true });
  await fs.copyFile(file.file, destination);
  // A source edited during sync must not be presented as the synchronized snapshot.
  if (await fileHash(destination) !== file.sha256) fail(`Source changed during sync: ${file.relative}. Run sync again`);
  return { relative, sha256: file.sha256 };
}

const metaFingerprint = (remote) => hash(JSON.stringify({ name: remote.name, width: remote.width, height: remote.height, fps: remote.fps, scenes: remote.scenes.map(({ id, name, duration }) => ({ id, name, duration })) }));

async function sync(projectRoot, config, state) {
  // Validate the complete source set before creating or editing anything remotely.
  const plan = await sourcePlan(projectRoot, config);
  let dir;
  let remote;
  if (!state) {
    const before = await request(config, '/projects');
    if (!Array.isArray(before)) fail('Storyboard returned no project list');
    const ownerToken = randomUUID();
    remote = await request(config, '/projects', 'POST', { ...plan.meta, name: `${plan.meta.name} · Mist ${ownerToken.slice(0, 8)}` });
    if (!ID.test(remote.id) || before.some((p) => p.id === remote.id)) fail('Storyboard did not create a new isolated project; refusing to adopt an existing one');
    dir = await safePath(config.projectsDir, remote.id);
    if (await fs.realpath(remote.dir) !== dir) fail('Created project is outside configured projectsDir');
    state = { version: 1, projectRoot, rendererUrl: config.rendererUrl, projectsDir: config.projectsDir, projectId: remote.id, ownerToken, sceneMap: plan.scenes.some((s) => s.id === 'intro') && remote.scenes.some((s) => s.id === 'intro') ? { intro: 'intro' } : {}, createdAt: new Date().toISOString() };
    await fs.writeFile(await safePath(dir, MARKER, true), `${JSON.stringify({ ownerToken, projectRoot, projectId: remote.id }, null, 2)}\n`, { flag: 'wx' });
    await saveState(projectRoot, state);
  } else ({ dir, remote } = await owned(projectRoot, config, state));
  if ((await jobs(config, state)).some((job) => ACTIVE.has(job.status))) fail('A render is active for this owned project. Wait or cancel it before sync');
  const route = `/projects/${state.projectId}`;
  await request(config, route, 'PATCH', plan.meta);
  for (const scene of plan.scenes) {
    const nativeId = state.sceneMap[scene.id];
    if (nativeId && remote.scenes.some((s) => s.id === nativeId)) await request(config, `${route}/scenes/${nativeId}`, 'PATCH', { name: scene.name, duration: scene.duration });
    else {
      const created = await request(config, `${route}/scenes`, 'POST', { name: scene.id, duration: scene.duration });
      if (!ID.test(created.id)) fail('Storyboard returned an invalid scene id');
      state.sceneMap[scene.id] = created.id;
      await saveState(projectRoot, state);
      await request(config, `${route}/scenes/${created.id}`, 'PATCH', { name: scene.name, duration: scene.duration });
    }
  }
  const keep = plan.scenes.map((scene) => state.sceneMap[scene.id]);
  remote = await request(config, route);
  for (const scene of remote.scenes) if (!keep.includes(scene.id)) await request(config, `${route}/scenes/${scene.id}`, 'DELETE');
  await request(config, `${route}/order`, 'PUT', { order: keep });
  const copied = [];
  for (const file of plan.files) if (!file.relative.startsWith('scenes/')) copied.push(await copySource(dir, file));
  for (const scene of plan.scenes) {
    const file = plan.files.find((f) => f.relative === `scenes/${scene.id}.tsx`);
    const target = `scenes/${state.sceneMap[scene.id]}.tsx`;
    copied.push(await copySource(dir, file, target));
  }
  await request(config, `${route}/art-direction`, 'PUT', { text: plan.artDirection });
  if (plan.music) {
    const expectedMusicHash = plan.files.find((f) => f.relative === `music/${plan.music.file}`).sha256;
    const hasExpectedMusic = async (project) => {
      const file = project.music?.file;
      if (typeof file !== 'string' || file.includes('/') || file.includes('\\')) return false;
      const candidate = await regular(dir, `music/${file}`).catch(() => null);
      return candidate !== null && await fileHash(candidate) === expectedMusicHash;
    };
    if (!await hasExpectedMusic(await request(config, route))) {
      const audio = await fs.readFile(path.join(plan.sourceRoot, 'music', plan.music.file));
      await request(config, `${route}/music`, 'POST', audio, plan.music.file);
      const deadline = Math.min(Date.now() + 20000, config.deadline);
      let ready = false;
      while (Date.now() < deadline) {
        const p = await request(config, route);
        if (await hasExpectedMusic(p)) { ready = true; break; }
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
      if (!ready) fail('Soundtrack import has not completed. Wait briefly and run sync again');
    }
    await request(config, `${route}/music`, 'PATCH', { start: plan.music.start, volume: plan.music.volume });
    state.musicSourceHash = expectedMusicHash;
  } else {
    if (remote.music) await request(config, `${route}/music`, 'DELETE');
    state.musicSourceHash = null;
  }
  remote = await request(config, route);
  state.synced = { contentHash: plan.contentHash, files: copied, metadataHash: metaFingerprint(remote), at: new Date().toISOString() };
  await saveState(projectRoot, state);
  return { command: 'sync', projectId: state.projectId, sourceHash: plan.contentHash, scenes: plan.scenes.length, duration: plan.scenes.reduce((sum, scene) => sum + scene.duration, 0), editorUrl: `${config.rendererUrl}/#/${state.projectId}/${keep[0]}`, message: 'Source synchronized. No render has been submitted' };
}

async function check(projectRoot, config, state) {
  const { dir, remote } = await owned(projectRoot, config, state);
  if (!state.synced) fail('Run sync before check or submit');
  const plan = await sourcePlan(projectRoot, config);
  if (plan.contentHash !== state.synced.contentHash) fail('Source changed after sync. Run sync again before submit');
  if (metaFingerprint(remote) !== state.synced.metadataHash) fail('Native project metadata changed after sync. Review it and run sync again');
  for (const file of state.synced.files) if (await fileHash(await regular(dir, file.relative)) !== file.sha256) fail(`Native renderer source changed after sync: ${file.relative}. Review it before synchronizing again`);
  for (const scene of remote.scenes) {
    const result = await request(config, `/projects/${state.projectId}/scenes/${scene.id}/diagnostics`);
    if (result.error) fail(`Scene ${scene.name} does not compile: ${result.error}`);
  }
  return { command: 'check', projectId: state.projectId, sourceHash: plan.contentHash, soundtrackPlanned: Boolean(plan.music), scenes: remote.scenes.length, message: 'Synchronized source hashes and native scene compilation passed. This is not GPU, visual, audio, or completed-render proof' };
}

async function submit(projectRoot, config, state) {
  const checked = await check(projectRoot, config, state);
  if ((await jobs(config, state)).some((job) => ACTIVE.has(job.status))) fail('A render is already active for this project; use status');
  const job = await request(config, `/projects/${state.projectId}/renders`, 'POST', config.render);
  if (typeof job.id !== 'string' || job.projectId !== state.projectId) fail('Storyboard returned an invalid render job');
  state.job = { id: job.id, projectId: state.projectId, sourceHash: checked.sourceHash, soundtrackPlanned: checked.soundtrackPlanned, submittedAt: new Date().toISOString(), options: config.render };
  await saveState(projectRoot, state);
  return { command: 'submit', projectId: state.projectId, job, message: 'Render submitted to Storyboard. Use status in a later command; this is not a completion result' };
}

async function expectedSnapshot(projectRoot, config, state, job) {
  if (job.id !== state.job?.id || job.projectId !== state.projectId || job.status !== 'done' || !/^[a-f0-9]{64}$/.test(state.job.sourceHash)) fail('A matching completed native job and saved source hash are required for verification');
  let soundtrackPlanned = state.job.soundtrackPlanned;
  // Upgrade older bridge state only when the complete source snapshot still
  // matches the actual submitted job, never from a subsequently edited plan.
  if (typeof soundtrackPlanned !== 'boolean') {
    const plan = await sourcePlan(projectRoot, config);
    if (plan.contentHash !== state.job.sourceHash) fail('Older job state does not record soundtrack expectations, and source changed after submission. Preserve the file and verify that older render separately');
    soundtrackPlanned = Boolean(plan.music);
    state.job.soundtrackPlanned = soundtrackPlanned;
  }
  return {
    jobId: job.id,
    sourceHash: state.job.sourceHash,
    width: number(job.width, 1, 30720, 'native render width', true),
    height: number(job.height, 1, 30720, 'native render height', true),
    fps: number(job.fps, 1, 1440, 'native render fps'),
    framesTotal: number(job.framesTotal, 1, 10000000, 'native render frame total', true),
    soundtrackPlanned,
    renderer: job.renderer ?? state.job.options.renderer,
  };
}

async function collect(projectRoot, config, state) {
  const { dir } = await owned(projectRoot, config, state);
  const job = await currentJob(config, state);
  if (job.status !== 'done') fail(`Render is ${job.status}; only a completed job can be collected${job.error ? `: ${job.error}` : ''}`);
  if (typeof job.output !== 'string' || !/^[\w.-]+\.mp4$/.test(path.basename(job.output)) || await fs.realpath(path.dirname(job.output)).catch(() => null) !== path.join(dir, 'renders')) fail('Render output is not inside this owned project');
  const source = await regular(dir, `renders/${path.basename(job.output)}`);
  const stat = await fs.stat(source);
  if (stat.size === 0) fail('Completed render file is empty');
  const sha256 = await fileHash(source);
  const filename = `${state.projectId}-${state.job.id.replace(/[^\w-]/g, '_')}.mp4`;
  const relative = `${config.outputDir}/${filename}`;
  const destination = await safePath(projectRoot, relative, true);
  await fs.mkdir(path.dirname(destination), { recursive: true });
  if (await exists(destination)) {
    if (await fileHash(await regular(projectRoot, relative)) !== sha256) fail('The local export already exists with different content; refusing to overwrite it');
  } else {
    const temp = `${destination}.${randomUUID()}.tmp`;
    try {
      await fs.copyFile(source, temp, 1); // COPYFILE_EXCL
      if (await fileHash(temp) !== sha256) fail('Render changed while being collected');
      await fs.link(temp, destination); // Never replace a concurrently-created export.
    } finally { await fs.rm(temp, { force: true }); }
  }
  state.collected = { jobId: job.id, file: relative, sha256, bytes: stat.size, expected: await expectedSnapshot(projectRoot, config, state, job), at: new Date().toISOString() };
  await saveState(projectRoot, state);
  return { command: 'collect', projectId: state.projectId, jobId: job.id, ...state.collected, absoluteFile: destination, message: 'Completed output copied locally and SHA-256 verified. Playback/audio verification is still required. Nothing was published' };
}

function fpsValue(value) {
  if (typeof value !== 'string') return NaN;
  const [numerator, denominator = '1'] = value.split('/');
  return Number(numerator) / Number(denominator);
}

async function verify(projectRoot, config, state, options) {
  await owned(projectRoot, config, state);
  const collected = state.collected;
  if (!collected || collected.jobId !== state.job?.id || !collected.file?.startsWith(`${config.outputDir}/`) || !/^[a-f0-9]{64}$/.test(collected.sha256)) fail('Only the saved, collected output of this bridge’s current job can be verified');
  const file = await regular(projectRoot, collected.file);
  const sha256 = await fileHash(file);
  if (sha256 !== collected.sha256) fail('Collected video bytes changed after collection; refusing to verify a different file');
  if (!collected.expected) {
    collected.expected = await expectedSnapshot(projectRoot, config, state, await currentJob(config, state));
    await saveState(projectRoot, state);
  }
  const expected = collected.expected;
  if (expected.jobId !== collected.jobId || expected.sourceHash !== state.job.sourceHash) fail('Saved verification expectations do not match the collected render job');
  const report = {
    command: 'verify', ok: false, projectId: state.projectId, jobId: collected.jobId,
    file: collected.file, absoluteFile: file, sha256, bytes: (await fs.stat(file)).size,
    expected: { ...expected, duration: expected.framesTotal / expected.fps },
    checks: {}, verifiedAt: new Date().toISOString(),
    proof: 'Saved render bytes, container metadata, counted video frames, required soundtrack presence, and complete audiovisual decode. Visual quality and perceived loudness still require review',
  };
  const run = async (name, args) => {
    const remaining = config.deadline - Date.now() - 1000;
    if (remaining < 1) fail('Verification reached its 45 second time budget; no successful verification is claimed');
    try {
      return await (options.execFile ?? executeFile)(config.executables[name], args, { timeout: remaining, killSignal: 'SIGKILL', maxBuffer: 2 * 1024 * 1024, encoding: 'utf8', windowsHide: true });
    } catch (error) {
      if (error.code === 'ENOENT') fail(`${name} is unavailable. Configure ${name}Executable to an existing binary or make it available on PATH; no installation was attempted`);
      if (error.killed) fail(`${name} verification exceeded the command time budget and was stopped; no successful verification is claimed`);
      fail(`${name} verification failed: ${String(error.stderr ?? error.message).trim().slice(0, 4000)}`);
    }
  };
  try {
    const probe = await run('ffprobe', ['-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', file]);
    const metadata = JSON.parse(probe.stdout);
    const video = metadata.streams?.find((stream) => stream.codec_type === 'video');
    const audio = metadata.streams?.filter((stream) => stream.codec_type === 'audio') ?? [];
    if (!video) fail('The collected file has no video stream');
    const actual = {
      width: Number(video.width), height: Number(video.height), fps: fpsValue(video.avg_frame_rate),
      frames: Number(video.nb_read_frames), duration: Number(video.duration ?? metadata.format?.duration),
      containerDuration: Number(metadata.format?.duration),
      audioStreams: audio.length,
      audio: audio.map((stream) => ({ codec: stream.codec_name, channels: stream.channels, sampleRate: Number(stream.sample_rate) })),
    };
    report.actual = actual;
    const tolerance = Math.max(0.05, 2 / expected.fps);
    report.checks = {
      sha256: true,
      resolution: actual.width === expected.width && actual.height === expected.height,
      fps: Number.isFinite(actual.fps) && Math.abs(actual.fps - expected.fps) < 0.0001,
      frameCount: Number.isInteger(actual.frames) && actual.frames === expected.framesTotal,
      duration: Number.isFinite(actual.duration) && Math.abs(actual.duration - report.expected.duration) <= tolerance,
      containerDuration: Number.isFinite(actual.containerDuration) && Math.abs(actual.containerDuration - report.expected.duration) <= tolerance,
      requiredAudio: !expected.soundtrackPlanned || audio.length > 0,
      fullDecode: false,
    };
    const failed = Object.entries(report.checks).filter(([name, passed]) => name !== 'fullDecode' && !passed).map(([name]) => name);
    if (failed.length) fail(`Video does not match its saved native render job: ${failed.join(', ')}`);
    await run('ffmpeg', ['-nostdin', '-hide_banner', '-v', 'error', '-xerror', '-i', file, '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-']);
    report.checks.fullDecode = true;
    report.ok = true;
    report.message = 'Exact collected render passed metadata, actual frame-count, soundtrack-presence, and complete decode checks. Nothing was published';
  } catch (error) { report.error = error.message; }
  const relative = `${config.outputDir}/${state.projectId}-${collected.jobId.replace(/[^\w-]/g, '_')}-verify-${new Date().toISOString().replace(/[:.]/g, '-')}-${randomUUID().slice(0, 8)}.json`;
  const reportFile = await safePath(projectRoot, relative, true);
  await atomicJson(reportFile, report);
  if (report.ok) {
    state.verified = { jobId: collected.jobId, sourceHash: expected.sourceHash, sha256, report: relative, at: report.verifiedAt };
    await saveState(projectRoot, state);
  }
  return { ...report, report: relative, absoluteReport: reportFile };
}

async function frames(projectRoot, config, state, options) {
  if (!config.runtimeDir) fail('frames requires runtimeDir in renderer.config.json so it can use the existing installed Playwright and Chromium');
  const times = options.times;
  if (!Array.isArray(times) || times.length < 1 || times.length > 4 || times.some((t) => typeof t !== 'number' || !Number.isFinite(t) || t < 0)) fail('frames needs --times with 1 to 4 finite, nonnegative seconds, e.g. --times 0,2,4');
  if (!['low', 'normal', 'high'].includes(options.resolution ?? 'normal')) fail('Choose frames resolution: low, normal, or high');
  await check(projectRoot, config, state);
  const { remote } = await owned(projectRoot, config, state);
  let sceneId = null;
  if (options.scene !== undefined) {
    if (!ID.test(options.scene)) fail('Invalid scene id');
    sceneId = state.sceneMap[options.scene] ?? options.scene;
    if (!remote.scenes.some((s) => s.id === sceneId)) fail('Scene does not belong to this bridge-owned project');
  }
  const duration = sceneId ? remote.scenes.find((s) => s.id === sceneId).duration : remote.scenes.reduce((sum, s) => sum + s.duration, 0);
  if (times.some((t) => t > duration)) fail(`Frame times exceed the ${sceneId ? 'scene' : 'video'} duration (${duration} seconds)`);
  const allProjects = await request(config, '/projects');
  if (!Array.isArray(allProjects)) fail('Storyboard returned no project list');
  const active = (await Promise.all(allProjects.map(async (p) => {
    if (!ID.test(p.id)) fail('Storyboard returned an invalid project id');
    return (await request(config, `/projects/${p.id}/renders`)).jobs.filter((job) => ACTIVE.has(job.status));
  }))).flat();
  if (active.length) fail('A full Storyboard render is active. Wait for it to finish before frame captures so GPU work does not compete');
  await regular(config.runtimeDir, 'node_modules/playwright/index.mjs');
  const relative = `${config.outputDir}/frames/${new Date().toISOString().replace(/[:.]/g, '-')}-${randomUUID().slice(0, 8)}`;
  const outputDir = await safePath(projectRoot, relative, true);
  await fs.mkdir(outputDir, { recursive: true });
  const scale = options.resolution === 'low' ? 0.25 : options.resolution === 'high' ? 1 : 0.5;
  const capture = options.captureFrames ?? captureNativeFrames;
  const result = await capture({ runtimeDir: config.runtimeDir, chromiumExecutable: config.chromiumExecutable, rendererUrl: config.rendererUrl, projectId: state.projectId, sceneId, width: remote.width, height: remote.height, renderer: config.render.renderer, scale, times, outputDir, deadline: config.deadline - 3000 });
  if (!Array.isArray(result.frames) || result.frames.length !== times.length) fail('Capture did not return every requested frame');
  const files = [];
  for (const frame of result.frames) {
    if (!inside(outputDir, frame.file) || path.extname(frame.file) !== '.png') fail('Capture returned a frame outside its owned output folder');
    const rel = path.relative(projectRoot, frame.file).split(path.sep).join('/');
    const file = await regular(projectRoot, rel);
    const handle = await fs.open(file, 'r');
    const signature = Buffer.alloc(8);
    try { await handle.read(signature, 0, 8, 0); } finally { await handle.close(); }
    if (!signature.equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) fail('Capture returned an invalid PNG file');
    files.push({ ...frame, file: rel, absoluteFile: file, sha256: await fileHash(file) });
  }
  const errors = [...new Set([...(result.errors ?? []), ...files.flatMap((frame) => frame.errors ?? [])])];
  const report = { command: 'frames', ok: !errors.length, projectId: state.projectId, sceneId, renderer: config.render.renderer, width: Math.round(remote.width * scale), height: Math.round(remote.height * scale), frames: files, errors, message: 'Captured native Storyboard frames locally using the selected renderer. Inspect these images for visual quality; this does not prove a complete video or audio mix' };
  await atomicJson(path.join(outputDir, 'report.json'), report);
  return report;
}

export async function runBridge(projectRoot, command, options = {}) {
  projectRoot = await fs.realpath(projectRoot);
  if (!['doctor', 'sync', 'check', 'frames', 'submit', 'status', 'cancel', 'collect', 'verify'].includes(command)) fail('Usage: npm run video -- doctor|sync|check|frames|submit|status|cancel|collect|verify [--config renderer.config.json]');
  const config = await loadConfig(projectRoot, options.configFile ?? 'renderer.config.json');
  config.deadline = Date.now() + 45000;
  const info = await health(config);
  if (command === 'doctor') return { command, connected: true, rendererUrl: config.rendererUrl, projectsDir: config.projectsDir, features: info.features ?? [], serverModel: info.model ?? null, sourceDir: config.sourceDir, render: config.render, runtimeFiles: config.requiredRuntimeFiles, proof: 'API connectivity and configured file checks only; no GPU, renderer smoke test, or visual proof', message: 'Connected to the existing local Storyboard service. No service was started and no render was submitted' };
  const lock = await safePath(projectRoot, `${STATE}/lock`, true);
  await fs.mkdir(path.dirname(lock), { recursive: true });
  try { await fs.mkdir(lock); } catch (e) { if (e.code === 'EEXIST') fail('Another bridge command is active (or left a lock after interruption). Verify no command is running before removing the lock directory'); throw e; }
  try {
    const state = await readState(projectRoot);
    if (command === 'sync') return await sync(projectRoot, config, state);
    if (command === 'check') return await check(projectRoot, config, state);
    if (command === 'frames') return await frames(projectRoot, config, state, options);
    if (command === 'submit') return await submit(projectRoot, config, state);
    if (command === 'collect') return await collect(projectRoot, config, state);
    if (command === 'verify') return await verify(projectRoot, config, state, options);
    await owned(projectRoot, config, state);
    const job = await currentJob(config, state);
    if (command === 'cancel') {
      if (ACTIVE.has(job.status)) await request(config, `/renders/${encodeURIComponent(job.id)}/cancel`, 'POST');
      return { command, projectId: state.projectId, job: await currentJob(config, state), message: ACTIVE.has(job.status) ? 'Cancellation requested for this bridge’s own job' : 'Job is already terminal; no cancellation was sent' };
    }
    return { command, projectId: state.projectId, job, progress: job.framesTotal > 0 ? Math.min(1, job.framesDone / job.framesTotal) : null };
  } finally { await fs.rmdir(lock); }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [command, ...args] = process.argv.slice(2);
    const options = {};
    for (let i = 0; i < args.length; i += 2) {
      if (i + 1 >= args.length) fail(`Missing value for ${args[i]}`);
      if (args[i] === '--config') options.configFile = args[i + 1];
      else if (command === 'frames' && args[i] === '--times') options.times = args[i + 1].split(',').map((value) => value.trim() ? Number(value) : NaN);
      else if (command === 'frames' && args[i] === '--scene') options.scene = args[i + 1];
      else if (command === 'frames' && args[i] === '--resolution') options.resolution = args[i + 1];
      else fail(`Unsupported argument: ${args[i]}`);
    }
    const result = await runBridge(process.cwd(), command, options);
    console.log(JSON.stringify(result, null, 2));
    if (result.ok === false) process.exitCode = 1;
  } catch (error) {
    console.error(JSON.stringify({ ok: false, error: error.message }));
    process.exitCode = 1;
  }
}
