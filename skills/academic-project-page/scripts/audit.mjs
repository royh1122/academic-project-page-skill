#!/usr/bin/env node
// Runs the page audit, the interaction check (keys, clicks, Tab pass) and the theme typography check against a served page, then saves
// full-page screenshots and screen-height slices for the look step. Needs Node 22+ and an installed Chrome, Edge, or
// Chromium; installs nothing. Exit code 1 when any check fails.
import { mkdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { launch } from './lib/chrome.mjs';
import { findingId } from './lib/findings.mjs';

const usage = `Usage: node audit.mjs <url> [--out <dir>] [--no-screenshots] [--skip-style]

  <url>             The served page, e.g. http://127.0.0.1:8000/my-repo/ (start it with preview_server.py)
  --out <dir>       Where screenshots go (default: ./.page-audit)
  --max-slices <n>  Most screen-height slices per width (default 12)
  --no-screenshots  Run the checks only
  --skip-style      Skip check_style.js (for an explicitly requested redesign with different typography)

Prints failures (fix all) and warnings (fix, or defend each in one sentence), each with an [id], then the
screenshot paths and a summary line.`;

// Piping into a pager or `head` closes stdout early; that is not a failure of the checks.
// Keep running so Chrome is still closed and its profile removed.
process.stdout.on('error', error => { if (error.code !== 'EPIPE') throw error; });

const args = process.argv.slice(2);
if (!args.length || args.includes('--help') || args.includes('-h')) {
  console.log(usage);
  process.exit(args.length ? 0 : 2);
}
const url = args.find(arg => /^https?:\/\//.test(arg));
if (!url) { console.error(`Expected an http(s) URL.\n\n${usage}`); process.exit(2); }
const outIndex = args.indexOf('--out');
const out = resolve(outIndex >= 0 ? args[outIndex + 1] : '.page-audit');
const sliceIndex = args.indexOf('--max-slices');
const maxSlices = sliceIndex >= 0 ? Math.max(1, parseInt(args[sliceIndex + 1], 10) || 12) : 12;

// The check files are Playwright function expressions shared with `playwright-cli run-code`.
const here = dirname(fileURLToPath(import.meta.url));
const load = name => (0, eval)(readFileSync(join(here, name), 'utf8'));

// A server error page would otherwise pass the checks, which only look for problems in what loads.
let response;
try { response = await fetch(url); } catch (error) {
  console.log(`Page audit: FAIL\n  Could not reach ${url} (${error.cause?.code || error.message}). Is the preview server running?`);
  process.exit(1);
}
await response.body?.cancel();
if (!response.ok) {
  console.log(`Page audit: FAIL\n  ${url} returned HTTP ${response.status}. Check the server's --root and --base, and that no other server holds the port.`);
  process.exit(1);
}

mkdirSync(out, { recursive: true });
const { page, close } = await launch({ profileRoot: out });
let failed = false;
const findings = [];
try {
  await page.goto(url);
  // Name the page so screenshots are never mistaken for another run's.
  console.log(`Audited ${url} (title: "${await page.evaluate(() => document.title)}")`);

  // Each check either returns { warnings } or throws "<check> failed:\n- a\n- b\nWarnings:\n- c".
  const run = async (title, files, fallback) => {
    const fails = [], warns = [];
    for (const file of files) {
      try {
        warns.push(...((await load(file)(page))?.warnings || []));
      } catch (error) {
        const [head, tail = ''] = error.message.split('\nEvidence:')[0].split('\nWarnings:\n');
        const listed = head.split('\n').slice(1).map(line => line.replace(/^- /, '')).filter(Boolean);
        fails.push(...(listed.length ? listed : [head]));
        warns.push(...tail.split('\n').map(line => line.replace(/^- /, '')).filter(line => line && line !== 'none'));
      }
    }
    console.log(`${title}: ${fails.length ? 'FAIL' : 'pass'}`);
    for (const [level, list] of [['FAIL', fails], ['WARN', warns]]) {
      for (const message of list) {
        const id = findingId(message, fallback);
        console.log(`  ${level} [${id}] ${message}`);
        findings.push({ level, id });
      }
    }
    if (fails.length) failed = true;
  };
  await run('Page audit', ['audit_page.js', 'layout_page.js'], 'page');
  // Real key and mouse events against whatever interactive parts the page has; reloads the page afterwards.
  await run('Interaction check', ['interact_page.js'], 'interaction');
  if (!args.includes('--skip-style')) await run('Typography check', ['check_style.js'], 'typography');

  if (!args.includes('--no-screenshots')) {
    mkdirSync(out, { recursive: true });
    console.log('Screenshots (open every one before reporting):');
    const sliced = [];
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
        // Scroll through once, as a visitor would, so scroll-revealed content is shown in the shots.
        for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) {
          window.scrollTo(0, y);
          await new Promise(resolve => setTimeout(resolve, 80));
        }
        window.scrollTo(0, 0);
        await new Promise(resolve => setTimeout(resolve, 400));
      });
      const path = join(out, `page-${width}.png`);
      await page.screenshot({ path, fullPage: true });
      console.log(`  ${path}  (whole page, for overall rhythm; shrunk when viewed)`);
      // Full-page shots shrink to unreadable when viewed, so also save the page in screen-height slices.
      if (width !== 768) {
        const { height, headings } = await page.evaluate(() => ({
          height: document.documentElement.scrollHeight,
          headings: [...document.querySelectorAll('h2')].filter(h => h.checkVisibility())
            .map(h => [h.getBoundingClientRect().top + scrollY, h.textContent.trim().replace(/\s+/g, ' ').slice(0, 30)]),
        }));
        const count = Math.ceil(height / 900), saved = Math.min(count, maxSlices);
        // Name what each slice shows, so a finding can be matched to the slice that shows it.
        const guide = [];
        for (let i = 0; i < saved; i++) {
          const name = `page-${width}-${String(i + 1).padStart(2, '0')}.png`;
          await page.screenshot({ path: join(out, name), fullPage: true, clip: { x: 0, y: i * 900, width, height: Math.min(900, height - i * 900) } });
          const starting = headings.filter(([y]) => y >= i * 900 && y < (i + 1) * 900).map(([, text]) => text);
          const before = headings.filter(([y]) => y < i * 900).pop();
          guide.push(`    ${name}: ${[...(before ? [`${before[1]} (cont.)`] : i === 0 ? ['header'] : []), ...starting].join(', ')}`);
        }
        sliced.push(`  ${width} px, ${saved} slices of 900 px (legible; open every one):\n${guide.join('\n')}`
          + (count > saved ? `\n    The page is ${height} px tall, so slices stop at ${saved * 900} px; rerun with --max-slices ${count} for the rest.` : ''));
      }
      // Full-page capture leaves an embedded PDF viewer (an out-of-process frame) blank, but a
      // viewport capture paints it once it has loaded: save one of each visible embed.
      const frames = await page.evaluate(() => [...document.querySelectorAll('object[type="application/pdf"], embed[type="application/pdf"]')]
        .filter(el => el.getBoundingClientRect().height > 0).length);
      for (let i = 0; i < frames; i++) {
        await page.evaluate(index => document.querySelectorAll('object[type="application/pdf"], embed[type="application/pdf"]')[index]
          .scrollIntoView({ block: 'center', behavior: 'instant' }), i);
        await new Promise(resolve => setTimeout(resolve, 3000));
        const pdfPath = join(out, `page-${width}-pdf${i + 1}.png`);
        await page.screenshot({ path: pdfPath });
        console.log(`  ${pdfPath}  (embedded PDF; blank in the full-page shot above)`);
      }
    }
    console.log(`Slices in ${out} (open these; the full-page shots above are too small to read):\n${sliced.join('\n')}`);
  }
} finally {
  await close();
}
// One line to read first, and to cite: defended warnings are named by id in the report.
const count = level => findings.filter(f => f.level === level).length;
const ids = [...new Set(findings.map(f => f.id))];
console.log(`Summary: FAIL ${count('FAIL')} / WARN ${count('WARN')}${ids.length ? `: ${ids.join(', ')}` : ''}`);
process.exit(failed ? 1 : 0);
