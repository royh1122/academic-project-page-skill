#!/usr/bin/env node
// Runs the page audit and the theme typography check against a served page, then saves
// full-page screenshots for the look step. Needs Node 22+ and an installed Chrome, Edge, or
// Chromium; installs nothing. Exit code 1 when any check fails.
import { mkdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { launch } from './lib/chrome.mjs';

const usage = `Usage: node audit.mjs <url> [--out <dir>] [--no-screenshots] [--skip-style]

  <url>             The served page, e.g. http://127.0.0.1:8000/my-repo/ (start it with preview_server.py)
  --out <dir>       Where screenshots go (default: ./.page-audit)
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

// The check files are Playwright function expressions shared with `playwright-cli run-code`.
const here = dirname(fileURLToPath(import.meta.url));
const load = name => (0, eval)(readFileSync(join(here, name), 'utf8'));

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
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
      });
      const path = join(out, `page-${width}.png`);
      await page.screenshot({ path, fullPage: true });
      console.log(`  ${path}`);
    }
  }
} finally {
  await close();
}
process.exit(failed ? 1 : 0);
