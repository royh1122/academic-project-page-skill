// Playwright CLI: run-code --filename /path/to/this/file.js
// Typography check against a theme profile (references/theme-profile.json by default).
// The profile lists selectors with expected computed values; numbers are pixels (or font weights)
// compared within the profile's tolerances, colours are compared per RGB channel, fontFamily is the
// first family in the computed list. "optional": true skips a selector the page does not use.
// Profile lookup: the second argument (object or path), else $THEME_PROFILE, else
// <this skill>/references/theme-profile.json found from the running script, else ./references/.
async (page, profileArg) => {
  const previousViewport = page.viewportSize();
  const failures = [];
  const evidence = {};
  const expect = (condition, message) => { if (!condition) failures.push(message); };

  const loadProfile = () => {
    if (profileArg && typeof profileArg === 'object') return profileArg;
    const fs = globalThis.process?.getBuiltinModule?.('node:fs');
    const path = globalThis.process?.getBuiltinModule?.('node:path');
    if (!fs || !path) throw new Error('check_style.js: cannot read the theme profile here; pass the parsed profile as the second argument.');
    const candidates = [
      typeof profileArg === 'string' ? profileArg : null,
      process.env.THEME_PROFILE,
      process.argv[1] ? path.join(path.dirname(process.argv[1]), '..', 'references', 'theme-profile.json') : null,
      path.join(process.cwd(), 'references', 'theme-profile.json'),
    ].filter(Boolean);
    const found = candidates.find(file => fs.existsSync(file));
    if (!found) throw new Error(`check_style.js: no theme profile found (tried ${candidates.join(', ')}). Set THEME_PROFILE.`);
    evidence.profile = found;
    return JSON.parse(fs.readFileSync(found, 'utf8'));
  };

  const parseColor = value => {
    const text = String(value).trim();
    const hex = text.match(/^#([\da-f]{3}|[\da-f]{6})$/i);
    if (hex) {
      const h = hex[1].length === 3 ? [...hex[1]].map(c => c + c).join('') : hex[1];
      return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)).concat(1);
    }
    const nums = text.match(/[\d.]+/g);
    if (!/^rgba?\(/.test(text) || !nums) return null;
    return [...nums.slice(0, 3).map(Number), nums[3] === undefined ? 1 : Number(nums[3])];
  };
  const firstFamily = value => value.split(',')[0].replace(/["']/g, '').trim();

  const profile = loadProfile();
  const tol = { px: 0.5, weight: 0, color: 2, ...(profile.tolerances || {}) };

  const compare = (key, expected, actual) => {
    const spec = expected && typeof expected === 'object' ? expected : { value: expected };
    const want = spec.value;
    if (key === 'fontFamily') return firstFamily(actual) === want;
    if (typeof want === 'number') {
      const limit = spec.tolerance ?? (key === 'fontWeight' ? tol.weight : tol.px);
      const got = parseFloat(actual);
      return Number.isFinite(got) && Math.abs(got - want) <= limit;
    }
    const wantColor = /^(#|rgb)/.test(want) ? parseColor(want) : null;
    if (wantColor) {
      const got = parseColor(actual);
      const limit = spec.tolerance ?? tol.color;
      return !!got && got.slice(0, 3).every((c, i) => Math.abs(c - wantColor[i]) <= limit) && Math.abs(got[3] - wantColor[3]) < 0.02;
    }
    return actual === want;
  };
  const show = value => (value && typeof value === 'object' ? value.value : value);

  try {
    await page.setViewportSize(profile.viewport || { width: 1440, height: 1000 });
    await page.evaluate(() => document.fonts.ready);

    for (const { selector, expect: expected, optional } of profile.rules || []) {
      const element = page.locator(selector).first();
      if (!await element.count()) {
        if (!optional) failures.push(`Missing baseline element: ${selector}`);
        continue;
      }
      const actual = await element.evaluate((el, keys) => {
        const style = getComputedStyle(el);
        return Object.fromEntries(keys.map(key => [key, style[key]]));
      }, Object.keys(expected));
      evidence[selector] = actual;
      for (const [key, value] of Object.entries(expected)) {
        expect(compare(key, value, actual[key]), `${selector}: expected ${key}=${show(value)}, got ${actual[key]}`);
      }
    }

    // The family a declaration names is not proof: check the face Chromium actually rendered.
    const fontChecks = profile.renderedFonts || [];
    if (fontChecks.length) {
      const client = await page.context().newCDPSession(page);
      try {
        await client.send('DOM.enable');
        await client.send('CSS.enable');
        const { root } = await client.send('DOM.getDocument');
        evidence.renderedFonts = {};
        for (const { selector, family } of fontChecks) {
          const { nodeId } = await client.send('DOM.querySelector', { nodeId: root.nodeId, selector });
          if (!nodeId) {
            failures.push(`Missing font-inspection element: ${selector}`);
            continue;
          }
          const { fonts } = await client.send('CSS.getPlatformFontsForNode', { nodeId });
          evidence.renderedFonts[selector] = fonts;
          expect(fonts.some(font => font.familyName.includes(family)), `${selector}: actual rendered ${family} face not found`);
        }
      } finally {
        await client.detach();
      }
    }

    if (failures.length) throw new Error(`Style verification failed (${profile.name || 'theme profile'}):\n${failures.join('\n')}\nEvidence: ${JSON.stringify(evidence)}`);
    return { status: 'pass', profile: profile.name, evidence };
  } finally {
    if (previousViewport) await page.setViewportSize(previousViewport);
  }
}
