// Zero-dependency headless Chrome driver over the DevTools Protocol (Node 22+ built-in WebSocket).
// It exposes the small part of Playwright's Page API that audit_page.js and check_style.js use,
// so the same check files run under `playwright-cli run-code` or under scripts/audit.mjs.
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

export function findChrome() {
  const env = process.env.CHROME_PATH;
  if (env && existsSync(env)) return env;
  const pf = process.env.PROGRAMFILES || 'C:\\Program Files';
  const pf86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
  const local = process.env.LOCALAPPDATA || '';
  return [
    join(pf, 'Google/Chrome/Application/chrome.exe'),
    join(pf86, 'Google/Chrome/Application/chrome.exe'),
    join(local, 'Google/Chrome/Application/chrome.exe'),
    join(pf86, 'Microsoft/Edge/Application/msedge.exe'),
    join(pf, 'Microsoft/Edge/Application/msedge.exe'),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium',
    '/usr/bin/chromium-browser', '/snap/bin/chromium', '/usr/bin/microsoft-edge',
  ].find(path => path && existsSync(path)) || null;
}

// A run killed before cleanup leaves its profile behind; remove this tool's profiles older than a day.
function sweepStaleProfiles(root) {
  const day = 24 * 60 * 60 * 1000;
  let names = [];
  try { names = readdirSync(root); } catch { return; }
  for (const name of names) {
    if (!name.startsWith('page-audit-')) continue;
    const path = join(root, name);
    try { if (Date.now() - statSync(path).mtimeMs > day) rmSync(path, { recursive: true, force: true }); } catch {}
  }
}

// profileRoot keeps the throwaway browser profile inside the caller's working folder (default: the OS temp folder).
export async function launch({ profileRoot = tmpdir() } = {}) {
  mkdirSync(profileRoot, { recursive: true });
  sweepStaleProfiles(profileRoot);
  const executable = findChrome();
  if (!executable) throw new Error('No Chrome, Edge, or Chromium found. Install one or set CHROME_PATH.');
  const profile = mkdtempSync(join(profileRoot, 'page-audit-'));
  const chrome = spawn(executable, [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--mute-audio', 'about:blank',
  ], { stdio: 'ignore' });

  // Chrome writes the port it picked to DevToolsActivePort in the profile.
  const portFile = join(profile, 'DevToolsActivePort');
  for (let i = 0; i < 100 && !existsSync(portFile); i++) await sleep(100);
  if (!existsSync(portFile)) throw new Error('Chrome did not start its DevTools endpoint.');
  const port = readFileSync(portFile, 'utf8').split('\n')[0].trim();
  const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page');

  const socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let nextId = 0;
  const pending = new Map();
  const listeners = new Map();
  socket.onmessage = ({ data }) => {
    const message = JSON.parse(data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      message.error ? reject(new Error(`${message.error.message} (${message.error.code})`)) : resolve(message.result);
    } else if (message.method) (listeners.get(message.method) || []).forEach(callback => callback(message.params));
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const once = method => new Promise(resolve => {
    const callback = params => { listeners.set(method, listeners.get(method).filter(c => c !== callback)); resolve(params); };
    listeners.set(method, [...(listeners.get(method) || []), callback]);
  });

  await send('Page.enable');
  await send('Runtime.enable');
  const page = createPage(send, once);
  const close = async () => {
    try { socket.close(); } catch {}
    // Windows keeps profile files locked until Chrome has exited.
    const exited = chrome.exitCode !== null ? Promise.resolve() : new Promise(resolve => chrome.once('exit', resolve));
    chrome.kill();
    await Promise.race([exited, sleep(5000)]);
    try { rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); }
    catch (error) { console.error(`note: could not remove browser profile ${profile} (${error.code}); a later run removes it after a day.`); }
  };
  return { page, close };
}

function createPage(send, once) {
  let currentUrl = 'about:blank';
  let viewport = { width: 1280, height: 900 };

  const evaluateExpression = async expression => {
    const { result, exceptionDetails } = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true });
    if (exceptionDetails) throw new Error(exceptionDetails.exception?.description || exceptionDetails.text);
    return result.value;
  };

  const page = {
    url: () => currentUrl,
    viewportSize: () => ({ ...viewport }),
    async setViewportSize(size) {
      viewport = { ...size };
      await send('Emulation.setDeviceMetricsOverride', { width: size.width, height: size.height, deviceScaleFactor: 1, mobile: false });
    },
    async goto(url) {
      await page.setViewportSize(viewport);
      const loaded = once('Page.loadEventFired');
      const { errorText } = await send('Page.navigate', { url });
      if (errorText) throw new Error(`Could not open ${url}: ${errorText}`);
      await loaded;
      currentUrl = await evaluateExpression('location.href');
      await evaluateExpression('document.fonts.ready.then(() => true)');
      await sleep(500);
    },
    evaluate: (fn, arg) => evaluateExpression(`(${fn})(${arg === undefined ? '' : JSON.stringify(arg)})`),
    locator: selector => ({
      first: () => ({
        count: () => evaluateExpression(`document.querySelector(${JSON.stringify(selector)}) ? 1 : 0`),
        evaluate: (fn, arg) => evaluateExpression(`(${fn})(document.querySelector(${JSON.stringify(selector)}), ${arg === undefined ? 'undefined' : JSON.stringify(arg)})`),
      }),
    }),
    request: {
      async get(url, options = {}) {
        const response = await fetch(url, { headers: options.headers || {} });
        return { ok: () => response.ok, status: () => response.status, dispose: async () => { await response.body?.cancel(); } };
      },
    },
    context: () => ({ newCDPSession: async () => ({ send, detach: async () => {} }) }),
    async screenshot({ path, fullPage = false }) {
      let clip;
      if (fullPage) {
        const { cssContentSize } = await send('Page.getLayoutMetrics');
        clip = { x: 0, y: 0, width: viewport.width, height: Math.ceil(cssContentSize.height), scale: 1 };
      }
      const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: fullPage, ...(clip ? { clip } : {}) });
      writeFileSync(path, Buffer.from(data, 'base64'));
    },
  };
  return page;
}
