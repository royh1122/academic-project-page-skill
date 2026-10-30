// Playwright CLI: run-code --filename /path/to/this/file.js
// Exercises the interactive parts of the currently loaded page with real key and mouse events:
// figure viewer, carousels, BibTeX copy button, contents menu, More Works menu, and one Tab pass
// through the whole page. It tests only what the page has (a page without these parts reports
// nothing to check), reloads the page afterwards, and restores the viewport.
// Failures are defects to fix; warnings need a judgement.
async (page) => {
  const previousViewport = page.viewportSize();
  const failures = [];
  const warnings = [];
  const evidence = { tested: [] };
  const sleep = ms => page.evaluate(ms => new Promise(resolve => setTimeout(resolve, ms)), ms);
  // Polls a page-side condition (a function expression) until it returns something truthy.
  const until = async (fn, arg, timeout = 1500) => {
    const end = Date.now() + timeout;
    for (;;) {
      const value = await page.evaluate(fn, arg);
      if (value || Date.now() > end) return value;
      await sleep(40);
    }
  };
  const section = async (name, run) => {
    try { await run(); } catch (error) { failures.push(`${name}: the check itself stopped (${String(error.message).split('\n')[0]}).`); }
  };

  const cdp = await page.context().newCDPSession(page);
  const keys = { Enter: [13, '\r'], Escape: [27], Tab: [9], ArrowLeft: [37], ArrowRight: [39], '+': [187, '+'] };
  const press = async name => {
    const [code, text] = keys[name];
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: name, code: name.length > 1 ? name : undefined, windowsVirtualKeyCode: code, ...(text ? { text } : {}) });
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: name, code: name.length > 1 ? name : undefined, windowsVirtualKeyCode: code });
  };
  const clickAt = async (x, y) => {
    await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
    await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
    await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
  };

  // Page-side helpers, installed once per load: window.__ip.
  const install = () => page.evaluate(() => {
    const label = el => !el ? 'nothing' : `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : ''}${
      (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 30) ? ` "${(el.getAttribute('aria-label') || el.textContent).trim().replace(/\s+/g, ' ').slice(0, 30)}"` : ''}`;
    const shown = el => !!el && el.checkVisibility({ visibilityProperty: true, opacityProperty: true });
    const dead = el => !!el.closest('[inert], [aria-hidden="true"]');
    const focusSelector = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, iframe, video[controls], audio[controls], [tabindex], [contenteditable=""], [contenteditable="true"]';
    const usable = el => !el.disabled && el.tabIndex >= 0 && shown(el) && !dead(el) && !(el.type === 'radio');
    const style = el => {
      const cs = getComputedStyle(el);
      return [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow, cs.backgroundColor, cs.borderTopColor, cs.borderBottomColor, cs.color, cs.textDecorationLine, cs.transform];
    };
    window.__ip = { label, shown, dead, focusSelector, usable, style, ids: new WeakMap(), base: new WeakMap(), next: 1 };
  });

  try {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.evaluate(() => document.fonts.ready);
    await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true }).catch(() => {});
    await install();

    // ---- Figure viewer ----
    await section('Figure viewer', async () => {
      const found = await page.evaluate(() => ({
        triggers: document.querySelectorAll('.figure-zoom-trigger').length,
        marked: document.querySelectorAll('img[data-zoom]').length,
      }));
      if (!found.triggers) {
        if (found.marked) warnings.push(`${found.marked} image(s) carry data-zoom but have no zoom button (figure-viewer.js not running?); zoom was not tested.`);
        return;
      }
      evidence.tested.push(`figure viewer (${found.triggers})`);
      const open = () => page.evaluate(() => { const d = document.querySelector('dialog[open]'); return !!d; });
      const tested = Math.min(found.triggers, 8);
      let loadFailures = 0;   // broken images each cost a wait; two make the point
      for (let i = 0, done = 0; i < found.triggers && done < tested && loadFailures < 2; i++) {
        const info = await page.evaluate(index => {
          const trigger = document.querySelectorAll('.figure-zoom-trigger')[index];
          const { label, shown, dead } = window.__ip;
          if (!shown(trigger) || dead(trigger)) return null;
          // Instant: with smooth scrolling (the template's default) the page is still moving when the click lands.
          trigger.scrollIntoView({ block: 'center', behavior: 'instant' });
          const r = trigger.getBoundingClientRect();
          const x = r.left + r.width / 2, y = r.top + r.height / 2;
          const top = document.elementFromPoint(x, y);
          return { name: trigger.getAttribute('aria-label') || label(trigger), x, y, covered: top && !trigger.contains(top) ? label(top) : '',
            expected: (trigger.closest('figure')?.querySelector('figcaption')?.textContent || '').trim() };
        }, i);
        if (!info) continue;   // inside a hidden or off-screen carousel slide
        done++;
        for (const how of done === 1 ? ['keyboard', 'click'] : ['click']) {
          await page.evaluate(index => document.querySelectorAll('.figure-zoom-trigger')[index].focus({ preventScroll: true }), i);
          if (how === 'keyboard') await press('Enter');
          else {
            if (info.covered) { failures.push(`${info.name}: a click on the figure lands on ${info.covered}, so it cannot be opened with a mouse.`); continue; }
            // Scroll again: a close handler may have moved the page.
            const at = await page.evaluate(index => {
              const trigger = document.querySelectorAll('.figure-zoom-trigger')[index];
              trigger.scrollIntoView({ block: 'center', behavior: 'instant' });
              const r = trigger.getBoundingClientRect();
              return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
            }, i);
            await clickAt(at.x, at.y);
          }
          if (!await until(() => !!document.querySelector('dialog[open]'))) {
            failures.push(`${info.name}: ${how === 'keyboard' ? 'Enter' : 'a click'} does not open the figure viewer.`);
            continue;
          }
          const view = await until(() => {
            const d = document.querySelector('dialog[open]');
            const img = d.querySelector('img');
            if (!img || !img.complete || !img.naturalWidth) return null;
            return {
              caption: (d.querySelector('[id*="caption"], [class*="caption"]')?.textContent || '').trim(),
              title: (d.querySelector('[id*="title"]')?.textContent || '').trim(),
              focusInside: d.contains(document.activeElement),
              zoomOut: !d.querySelector('.figure-viewer-zoom')?.hidden,
            };
          }, undefined, 3000);
          if (!view) loadFailures++;
          if (!view) failures.push(`${info.name}: the enlarged image did not load in the viewer.`);
          else {
            if (!view.focusInside) failures.push(`${info.name}: opening the viewer leaves keyboard focus outside it.`);
            if (!view.caption && info.expected) failures.push(`${info.name}: the viewer shows no caption although the figure has one ("${info.expected.slice(0, 50)}").`);
            else if (!view.caption && how === 'keyboard') warnings.push(`${info.name}: the viewer shows no caption (add a figcaption or data-zoom-caption).`);
            if (done === 1 && how === 'keyboard' && view.zoomOut) {
              await press('+');
              const zoomed = await until(() => document.querySelector('dialog[open] .figure-viewer-zoom output')?.textContent.trim() !== '100%' || null, undefined, 600);
              const level = await page.evaluate(() => document.querySelector('dialog[open] .figure-viewer-zoom output')?.textContent);
              evidence.zoomLevelAfterPlus = level;
              if (!zoomed && level === '100%') failures.push(`${info.name}: the + key does not zoom the enlarged figure.`);
            }
          }
          await press('Escape');
          if (!await until(() => !document.querySelector('dialog[open]'))) { failures.push(`${info.name}: Esc does not close the figure viewer.`); await page.evaluate(() => document.querySelector('dialog[open]')?.close()); continue; }
          await sleep(120);   // the dialog's close event (which returns focus) fires just after it stops being open
          const back = await page.evaluate(index => {
            const trigger = document.querySelectorAll('.figure-zoom-trigger')[index];
            const active = document.activeElement;
            return { ok: active === trigger || (!window.__ip.shown(trigger) || window.__ip.dead(trigger)) && !!active && active !== document.body, name: window.__ip.label(active) };
          }, i);
          if (!back.ok) failures.push(`${info.name}: after Esc, focus does not return to the figure's button (it is on ${back.name}).`);
        }
      }
    });

    // ---- Carousels ----
    await section('Carousel', async () => {
      const count = await page.evaluate(() => document.querySelectorAll('[data-carousel]').length);
      for (let c = 0; c < count; c++) {
        const state = () => page.evaluate(index => {
          const carousel = document.querySelectorAll('[data-carousel]')[index];
          const track = carousel.querySelector('.carousel-track');
          const slides = track ? [...track.children] : [];
          const dots = [...carousel.querySelectorAll('.carousel-dot')];
          const focusable = slide => !!slide.querySelector('a[href], button, input, select, textarea, video[controls], [tabindex]:not([tabindex="-1"])');
          return {
            ready: carousel.classList.contains('is-ready'), n: slides.length, hasControls: !!carousel.querySelector('.carousel-next'),
            name: carousel.getAttribute('aria-label') || `carousel ${index + 1}`,
            current: slides.map((s, i) => (!s.inert ? i : -1)).filter(i => i >= 0),
            leaky: slides.map((s, i) => (s.inert || (s.getAttribute('aria-hidden') === 'true' && !focusable(s)) ? -1 : i)).filter(i => i >= 0),
            dot: dots.findIndex(d => d.getAttribute('aria-current') === 'true'),
            dots: dots.length,
          };
        }, c);
        let s = await state();
        if (!s.ready) { failures.push(`${s.name}: the carousel did not initialise (is-ready missing; is index.js loaded?).`); continue; }
        if (s.n < 2 || !s.hasControls) continue;
        evidence.tested.push(`carousel "${s.name}"`);
        await page.evaluate(index => document.querySelectorAll('[data-carousel]')[index].scrollIntoView({ block: 'center', behavior: 'instant' }), c);
        if (s.current.length !== 1) failures.push(`${s.name}: ${s.current.length} slides are exposed at once; exactly one should be (the others inert).`);
        else if (s.leaky.length > 1) failures.push(`${s.name}: off-screen slides ${s.leaky.filter(i => i !== s.current[0]).map(i => i + 1).join(', ')} are neither inert nor hidden from keyboard and screen readers.`);
        const focusButton = cls => page.evaluate(({ index, cls }) => document.querySelectorAll('[data-carousel]')[index].querySelector(cls).focus({ preventScroll: true }), { index: c, cls });
        const step = async (name, action, direction) => {
          const before = await state();
          await action();
          await sleep(80);
          const after = await state();
          const want = (before.current[0] + direction + before.n) % before.n;
          if (after.current[0] !== want || after.current.length !== 1) failures.push(`${s.name}: ${name} did not move from slide ${before.current[0] + 1} to ${want + 1} (now ${after.current.map(i => i + 1).join(', ') || 'none'}).`);
          else if (after.leaky.length > 1) failures.push(`${s.name}: after ${name}, off-screen slides are neither inert nor hidden.`);
          else if (after.dots && after.dot !== want) failures.push(`${s.name}: after ${name}, the dot's aria-current is on ${after.dot + 1} but slide ${want + 1} is showing.`);
        };
        await focusButton('.carousel-next');
        await step('the Next button (Enter)', () => press('Enter'), 1);
        await focusButton('.carousel-prev');
        await step('the Previous button (Enter)', () => press('Enter'), -1);
        await step('the right arrow key', () => press('ArrowRight'), 1);
        await step('the left arrow key', () => press('ArrowLeft'), -1);
        if (s.dots > 2) {
          await page.evaluate(index => { const dots = document.querySelectorAll('[data-carousel]')[index].querySelectorAll('.carousel-dot'); dots[dots.length - 1].click(); }, c);
          await sleep(80);
          s = await state();
          if (s.current[0] !== s.n - 1 || s.dot !== s.n - 1) failures.push(`${s.name}: the last dot does not show the last slide.`);
          await page.evaluate(index => document.querySelectorAll('[data-carousel]')[index].querySelector('.carousel-dot').click(), c);
        }
      }
    });

    // ---- BibTeX copy button ----
    await section('Copy button', async () => {
      const count = await page.evaluate(() => document.querySelectorAll('[data-copy-target]').length);
      if (count) evidence.tested.push(`copy button (${count})`);
      await cdp.send('Browser.grantPermissions', { permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'] }).catch(() => {});
      for (let i = 0; i < count; i++) {
        const before = await page.evaluate(index => {
          const button = document.querySelectorAll('[data-copy-target]')[index];
          const status = document.getElementById(button.dataset.copyStatus || '');
          button.scrollIntoView({ block: 'center', behavior: 'instant' });
          button.focus({ preventScroll: true });
          return { name: window.__ip.label(button), label: button.textContent.trim(), status: status ? status.textContent : null,
            live: status ? status.getAttribute('aria-live') || status.getAttribute('role') : null, sourceMissing: !document.getElementById(button.dataset.copyTarget) };
        }, i);
        if (before.sourceMissing) { failures.push(`${before.name}: data-copy-target points at an id that does not exist.`); continue; }
        await press('Enter');
        const after = await until(index => {
          const button = document.querySelectorAll('[data-copy-target]')[index];
          const status = document.getElementById(button.dataset.copyStatus || '');
          const text = `${button.textContent} ${status ? status.textContent : ''}`;
          return /copied|copy failed/i.test(text) ? { text: text.trim().replace(/\s+/g, ' ') } : null;
        }, i);
        const result = await page.evaluate(index => {
          const button = document.querySelectorAll('[data-copy-target]')[index];
          const status = document.getElementById(button.dataset.copyStatus || '');
          return { label: button.textContent.trim(), status: status ? status.textContent.trim() : '', cls: button.className };
        }, i);
        const changed = result.label !== before.label || result.status !== (before.status || '') || /copied/.test(result.cls);
        if (!after && !changed) failures.push(`${before.name}: pressing it sets no status ("Copied" or "Copy failed" in the button label or the status line); the button looks dead.`);
        else if (before.status !== null && before.live === null) warnings.push(`${before.name}: the copy status element has no aria-live or role, so screen readers will not hear the result.`);
        evidence.copyResult = result;
      }
    });

    // ---- Contents menu ----
    await section('Contents menu', async () => {
      const toggle = await page.evaluate(() => {
        const t = document.querySelector('.page-nav-toggle');
        return t ? { controls: t.getAttribute('aria-controls') || '' } : null;
      });
      if (!toggle) return;
      evidence.tested.push('contents menu');
      // The control appears once the header is scrolled past.
      let ready = false;
      for (const y of [1400, 1200]) {
        await page.evaluate(y => window.scrollTo(0, y), y);
        await sleep(200);
        ready = await page.evaluate(() => window.__ip.shown(document.querySelector('.page-nav-toggle')));
        if (ready) break;
      }
      if (!ready) { warnings.push('The contents button never became visible after scrolling down 1400px; the menu was not tested.'); return; }
      await page.evaluate(() => document.querySelector('.page-nav-toggle').focus({ preventScroll: true }));
      await press('Enter');
      const open = await until(() => {
        const t = document.querySelector('.page-nav-toggle');
        const menu = document.getElementById(t.getAttribute('aria-controls'));
        return menu && window.__ip.shown(menu) && t.getAttribute('aria-expanded') === 'true' ? true : null;
      });
      if (!open) { failures.push('Contents menu: pressing the Contents button with Enter does not open the menu (aria-expanded and visibility must change).'); return; }
      const menu = await page.evaluate(() => {
        const t = document.querySelector('.page-nav-toggle');
        const menu = document.getElementById(t.getAttribute('aria-controls'));
        const norm = s => s.trim().replace(/\s+/g, ' ');
        const headings = [...document.querySelectorAll('main h2, h2')].filter((h, i, all) => all.indexOf(h) === i && !h.closest('dialog, nav, [hidden]') && norm(h.textContent));
        const links = [...menu.querySelectorAll('a[href]')];
        return {
          focusInside: menu.contains(document.activeElement),
          headings: headings.map(h => norm(h.textContent)),
          links: links.map(a => norm(a.textContent)),
          dangling: links.filter(a => a.hash && !document.getElementById(decodeURIComponent(a.hash.slice(1)))).map(a => a.getAttribute('href')),
        };
      });
      const missing = menu.headings.filter(h => !menu.links.includes(h));
      if (missing.length) failures.push(`Contents menu: no entry for ${missing.map(h => `"${h.slice(0, 40)}"`).join(', ')}.`);
      if (menu.dangling.length) failures.push(`Contents menu: entries point at ids that do not exist: ${menu.dangling.join(', ')}.`);
      if (!menu.links.length) failures.push('Contents menu: it opens but has no entries.');
      if (!menu.focusInside) warnings.push('Contents menu: opening it leaves keyboard focus outside the menu.');
      await press('Escape');
      const closed = await until(() => document.getElementById(document.querySelector('.page-nav-toggle').getAttribute('aria-controls')).hidden || !window.__ip.shown(document.getElementById(document.querySelector('.page-nav-toggle').getAttribute('aria-controls'))));
      if (!closed) { failures.push('Contents menu: Esc does not close it.'); return; }
      const where = await page.evaluate(() => ({ ok: document.activeElement === document.querySelector('.page-nav-toggle'), name: window.__ip.label(document.activeElement), expanded: document.querySelector('.page-nav-toggle').getAttribute('aria-expanded') }));
      if (!where.ok) failures.push(`Contents menu: after Esc, focus does not return to the Contents button (it is on ${where.name}).`);
      if (where.expanded !== 'false') failures.push(`Contents menu: after Esc, aria-expanded is "${where.expanded}" instead of "false".`);
      await page.evaluate(() => window.scrollTo(0, 0));
    });

    // ---- More Works ----
    await section('More Works', async () => {
      const found = await page.evaluate(() => !!document.querySelector('.more-works-btn'));
      if (!found) return;
      evidence.tested.push('more works menu');
      await page.evaluate(() => { const b = document.querySelector('.more-works-btn'); b.scrollIntoView({ block: 'center', behavior: 'instant' }); b.focus({ preventScroll: true }); });
      await press('Enter');
      const open = await until(() => {
        const b = document.querySelector('.more-works-btn');
        const panel = document.getElementById(b.getAttribute('aria-controls'));
        return panel && window.__ip.shown(panel) && b.getAttribute('aria-expanded') === 'true' ? { inside: panel.contains(document.activeElement) } : null;
      });
      if (!open) { failures.push('More Works: pressing its button with Enter does not open the panel (aria-expanded and visibility must change).'); return; }
      if (!open.inside) warnings.push('More Works: opening the panel leaves keyboard focus outside it.');
      await press('Escape');
      const closed = await until(() => { const b = document.querySelector('.more-works-btn'); return b.getAttribute('aria-expanded') === 'false' && !window.__ip.shown(document.getElementById(b.getAttribute('aria-controls'))); });
      if (!closed) { failures.push('More Works: Esc does not close the panel.'); return; }
      const ok = await page.evaluate(() => document.activeElement === document.querySelector('.more-works-btn'));
      if (!ok) failures.push('More Works: after Esc, focus does not return to its button.');
    });

    // ---- Keyboard pass: Tab through the whole page once ----
    await section('Keyboard pass', async () => {
      await page.goto(page.url());
      await install();
      const plan = await page.evaluate(() => {
        const { focusSelector, usable, style, base } = window.__ip;
        const all = [...document.querySelectorAll(focusSelector)];
        all.forEach(el => base.set(el, style(el)));
        const expected = all.filter(usable);
        document.activeElement?.blur();
        window.scrollTo(0, 0);
        return { expected: expected.length };
      });
      if (!plan.expected) return;
      evidence.tested.push(`keyboard pass (${plan.expected} controls)`);
      const limit = Math.min(plan.expected + 120, 500);
      const seen = new Map();
      let stuck = 0, lost = 0, first = null, previous = null, wrapped = false;
      const noIndicator = [], hidden = [], tiny = [];
      for (let n = 0; n < limit && !wrapped; n++) {
        await press('Tab');
        const at = await page.evaluate(() => {
          const el = document.activeElement;
          const ip = window.__ip;
          if (!el || el === document.body || el === document.documentElement) return { body: true };
          if (!ip.ids.has(el)) ip.ids.set(el, ip.next++);
          const cs = getComputedStyle(el);
          const r = el.getBoundingClientRect();
          const before = ip.base.get(el);
          const now = ip.style(el);
          const ring = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0 && cs.outlineColor !== 'rgba(0, 0, 0, 0)';
          const shadow = cs.boxShadow !== 'none' && (!before || before[3] !== cs.boxShadow);
          const otherChange = !!before && before.some((value, i) => i >= 4 && value !== now[i]);
          return { id: ip.ids.get(el), name: ip.label(el), frame: /^(IFRAME|OBJECT|EMBED)$/.test(el.tagName), shadow: /^(VIDEO|AUDIO)$/.test(el.tagName), hidden: !ip.shown(el) || ip.dead(el),
            tiny: r.width < 2 || r.height < 2, indicator: ring || shadow || otherChange };
        });
        if (at.body) {
          if (++lost >= 3 && !seen.size) { failures.push('Keyboard pass: Tab never moved focus into the page.'); return; }
          if (seen.size && lost >= 3) wrapped = true;   // focus has left the document for good
          continue;
        }
        lost = 0;
        if (first === null) first = at.id;
        else if (at.id === first) { wrapped = true; break; }
        // Video and audio controls, and embedded frames, take several Tab stops while activeElement stays the same element.
        if (at.id === previous) {
          if (++stuck >= (at.frame || at.shadow ? 40 : 2)) { failures.push(`Keyboard pass: focus is trapped on ${at.name}; Tab no longer moves on.`); return; }
          continue;
        }
        stuck = 0;
        if (seen.has(at.id)) { failures.push(`Keyboard pass: focus loops back to ${at.name} after ${seen.size} stops without reaching the rest of the page.`); return; }
        seen.set(at.id, at.name);
        previous = at.id;
        if (at.hidden) hidden.push(at.name);
        else if (at.tiny) tiny.push(at.name);
        if (!at.hidden && !at.frame && !at.tiny && !at.indicator) noIndicator.push(at.name);
      }
      if (hidden.length) failures.push(`Keyboard pass: focus lands on ${hidden.length} invisible, inert or aria-hidden element(s): ${hidden.slice(0, 4).join('; ')}.`);
      if (noIndicator.length) failures.push(`Keyboard pass: ${noIndicator.length} control(s) show no focus indicator (no outline, box-shadow or other style change when focused): ${noIndicator.slice(0, 4).join('; ')}.`);
      if (tiny.length) warnings.push(`Keyboard pass: focus lands on ${tiny.length} visually hidden element(s) (under 2px): ${tiny.slice(0, 3).join('; ')}. Fine only when a visible sibling shows the focus.`);
      const unreached = await page.evaluate(() => {
        const { focusSelector, usable, ids, label } = window.__ip;
        // Floating controls (a fixed pill shown only after scrolling) may be out of the Tab order while hidden, by design.
        const floating = el => { for (let a = el; a; a = a.parentElement) if (getComputedStyle(a).position === 'fixed') return true; return false; };
        return [...document.querySelectorAll(focusSelector)]
          .filter(el => usable(el) && !ids.has(el) && el.tagName !== 'IFRAME' && !floating(el))
          .map(label);
      });
      evidence.tabStops = seen.size;
      if (unreached.length && wrapped) warnings.push(`Keyboard pass: Tab skipped ${unreached.length} focusable control(s), e.g. ${unreached.slice(0, 3).join('; ')}.`);
    });

    const result = { status: failures.length ? 'fail' : 'pass', failures, warnings, evidence };
    if (failures.length) throw new Error(`Interaction check failed:\n- ${failures.join('\n- ')}\nWarnings:\n- ${warnings.join('\n- ') || 'none'}`);
    return result;
  } finally {
    // Leave the page as the screenshots expect it: reloaded, original viewport.
    try { await page.goto(page.url()); } catch {}
    try { await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: false }); } catch {}
    await cdp.detach();
    if (previousViewport) await page.setViewportSize(previousViewport);
  }
}
