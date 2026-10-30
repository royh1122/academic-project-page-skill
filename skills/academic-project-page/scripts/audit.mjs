#!/usr/bin/env node
// Runs the page audit, the interaction check (keys, clicks, Tab pass) and the theme typography check against a served page, then saves
// full-page screenshots and screen-height slices for the look step. Needs Node 22+ and an installed Chrome, Edge, or
// Chromium; installs nothing. Exit code 1 when any check fails.
import { mkdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { launch } from './lib/chrome.mjs';

const usage = `Usage: node audit.mjs <url> [--out <dir>] [--no-screenshots] [--skip-style]

  <url>             The served page, e.g. http://127.0.0.1:8000/my-repo/ (start it with preview_server.py)
  --out <dir>       Where screenshots go (default: ./.page-audit)
  --max-slices <n>  Most screen-height slices per width (default 12)
  --no-screenshots  Run the checks only
  --skip-style      Skip check_style.js (for an explicitly requested redesign with different typography)

Prints failures (fix all) and warnings (fix, or defend each in one sentence), then the screenshot paths.`;

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
try {
  await page.goto(url);
  // Name the page so screenshots are never mistaken for another run's.
  console.log(`Audited ${url} (title: "${await page.evaluate(() => document.title)}")`);

  try {
    const audit = await load('audit_page.js')(page);
    console.log('Page audit: pass');
    audit.warnings.forEach(warning => console.log(`  WARN ${warning}`));
  } catch (error) {
    failed = true;
    console.log(error.message.replace(/^Page audit failed:/, 'Page audit: FAIL').replace(/\n- /g, '\n  - '));
  }

  // Real key and mouse events against whatever interactive parts the page has; reloads the page afterwards.
  try {
    const interaction = await load('interact_page.js')(page);
    console.log('Interaction check: pass');
    interaction.warnings.forEach(warning => console.log(`  WARN ${warning}`));
  } catch (error) {
    failed = true;
    console.log(error.message.replace(/^Interaction check failed:/, 'Interaction check: FAIL').replace(/\n- /g, '\n  - '));
  }

  if (!args.includes('--skip-style')) {
    try {
      await load('check_style.js')(page);
      console.log('Typography check: pass');
    } catch (error) {
      failed = true;
      console.log(`Typography check: FAIL\n  ${error.message.split('\nEvidence:')[0].replace(/\n/g, '\n  ')}`);
    }
  }

  if (!args.includes('--no-screenshots')) {
    mkdirSync(out, { recursive: true });
    console.log('Screenshots (open every one before reporting):');
    const sliced = [];
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
      });
      const path = join(out, `page-${width}.png`);
      await page.screenshot({ path, fullPage: true });
      console.log(`  ${path}  (whole page, for overall rhythm; shrunk when viewed)`);
      // Full-page shots shrink to unreadable when viewed, so also save the page in screen-height slices.
      if (width !== 768) {
        const height = await page.evaluate(() => document.documentElement.scrollHeight);
        const count = Math.ceil(height / 900), saved = Math.min(count, maxSlices);
        for (let i = 0; i < saved; i++) {
          await page.screenshot({ path: join(out, `page-${width}-${String(i + 1).padStart(2, '0')}.png`), fullPage: true,
            clip: { x: 0, y: i * 900, width, height: Math.min(900, height - i * 900) } });
        }
        sliced.push(`  ${width} px: page-${width}-01.png ... page-${width}-${String(saved).padStart(2, '0')}.png (${saved} slices of 900 px, legible; open these)`
          + (count > saved ? `; the page is ${height} px tall, so slices stop at ${saved * 900} px (rerun with --max-slices ${count} for the rest)` : ''));
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
process.exit(failed ? 1 : 0);
