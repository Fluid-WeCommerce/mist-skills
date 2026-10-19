/** Render native Storyboard frame.html with the already-installed runtime's
 * Playwright. Owns and closes only the browser it launches. No installations.
 */
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function budget(deadline) {
  const left = deadline - Date.now();
  if (left < 1) throw new Error('Native frame capture reached its time budget; try fewer frames or lower resolution');
  return left;
}

async function bounded(promise, deadline, label) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`${label} timed out; try fewer frames or lower resolution`)), budget(deadline));
    })]);
  } finally { clearTimeout(timer); }
}

export async function captureNativeFrames(input, dependencies = {}) {
  const moduleFile = path.join(input.runtimeDir, 'node_modules/playwright/index.mjs');
  process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(input.runtimeDir, '.storyboard/browsers');
  const playwright = dependencies.playwright ?? await import(pathToFileURL(moduleFile).href);
  let browser;
  const errors = [];
  const frames = [];
  try {
    browser = await playwright.chromium.launch({
      headless: true,
      executablePath: input.chromiumExecutable,
      timeout: Math.min(12000, budget(input.deadline)),
      args: ['--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars', '--mute-audio', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows', ...(process.platform === 'darwin' && process.arch === 'arm64' ? ['--enable-gpu', '--use-angle=metal'] : [])],
    });
    const context = await browser.newContext({ viewport: { width: input.width, height: input.height }, deviceScaleFactor: input.scale });
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    const params = new URLSearchParams({ project: input.projectId, mode: 'capture', renderer: input.renderer });
    if (input.sceneId) params.set('scene', input.sceneId);
    await page.goto(`${input.rendererUrl}/frame.html?${params}`, { waitUntil: 'load', timeout: Math.min(15000, budget(input.deadline)) });
    await page.waitForFunction(() => Boolean(window.__sb), undefined, { timeout: Math.min(10000, budget(input.deadline)) });
    await bounded(page.evaluate(() => window.__sb.ready), input.deadline, 'Loading native scene');
    for (let index = 0; index < input.times.length; index++) {
      const time = input.times[index];
      const result = await bounded(page.evaluate((t) => window.__sb.seek(t), time), input.deadline, `Rendering frame ${index + 1}`);
      if (result.cancelled) throw new Error(`Frame ${index + 1} was superseded by a scene/code change; retry after edits stop`);
      errors.push(...(result.errors ?? []));
      const file = path.join(input.outputDir, `frame-${index + 1}-t${String(time).replace('.', '_')}.png`);
      await page.screenshot({ path: file, type: 'png', animations: 'disabled', caret: 'hide', timeout: budget(input.deadline) });
      frames.push({ file, requestedTime: time, sceneId: result.sceneId, localTime: result.localTime, errors: result.errors ?? [] });
    }
    return { frames, errors: [...new Set(errors)] };
  } finally {
    if (browser) {
      try { await bounded(browser.close(), Date.now() + 3000, 'Closing capture browser'); }
      catch (error) { throw new Error(`Capture browser cleanup failed: ${error.message}. Verify its process closed before another GPU job`); }
    }
  }
}
