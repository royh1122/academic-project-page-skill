// Layout checks at 375, 768 and 1440 px: headings and captions covered by another element or cut off by an ancestor,
// in-page jumps that land under a fixed bar, blank bands, uneven side margins, and tap targets under 24 x 24 px.
// Playwright function expression; audit.mjs runs it. Warnings only; each message ends with its fix.
async (page) => {
  const warnings = [];
  const previousViewport = page.viewportSize();
  // The same finding at several widths is reported once, with the widths.
  const seen = new Map();
  const note = (key, width, detail, fix) => {
    if (seen.has(key)) seen.get(key).widths.push(width);
    else seen.set(key, { widths: [width], detail, fix });
  };
  try {
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      const found = await page.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
        const frame = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        const label = el => {
          const text = (el.getAttribute('aria-label') || el.textContent || el.getAttribute('src') || '').trim().replace(/\s+/g, ' ').slice(0, 40);
          return `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : el.classList[0] ? '.' + el.classList[0] : ''}${text ? ` "${text}"` : ''}`;
        };
        const away = el => el.closest('[inert], [aria-hidden="true"], dialog, details:not([open])');
        const shown = el => el.checkVisibility({ opacityProperty: true, visibilityProperty: true }) && !away(el)
          && el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0;
        const pinned = node => { for (let a = node; a && a !== document.body; a = a.parentElement) if (/fixed|sticky/.test(getComputedStyle(a).position)) return a; return null; };
        const lines = el => { const range = document.createRange(); range.selectNodeContents(el); return [...range.getClientRects()].filter(r => r.width > 2 && r.height > 2); };
        // Three points along each line of text; the element on top there must be the text's own.
        const coverer = el => {
          for (const r of lines(el)) for (const x of [r.left + 3, (r.left + r.right) / 2, r.right - 3]) {
            const y = (r.top + r.bottom) / 2;
            if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
            const top = document.elementFromPoint(x, y);
            if (top && !el.contains(top) && !top.contains(el)) return top;
          }
          return null;
        };
        const out = { covered: [], anchors: [], clipped: [], bands: [], margins: [], targets: [] };
        for (const el of [...document.querySelectorAll('h1, h2, h3, h4, figcaption, caption')].filter(shown)) {
          el.scrollIntoView({ block: 'center', behavior: 'instant' });
          await frame();
          const top = coverer(el);
          if (top && !pinned(top)) out.covered.push(`${label(el)} under ${label(top)}`);
        }

        // Cut off: a line of text runs past the top or bottom of an ancestor that hides vertical overflow, or straddles the
        // side of one that hides horizontal overflow (a sideways scroller, like a table container, is fine). Text wholly
        // beside the box is an off-screen carousel slide; a box of 2 px or less is visually hidden on purpose.
        const cutBy = new Map();
        for (const el of [...document.querySelectorAll('h1, h2, h3, h4, figcaption, caption, p, li, td, th, dd, blockquote')].filter(shown)) {
          for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
            const cs = getComputedStyle(a);
            const hidesY = /hidden|clip/.test(cs.overflowY), hidesX = /hidden|clip/.test(cs.overflowX);
            if (!hidesY && !hidesX) continue;
            const box = a.getBoundingClientRect();
            if (box.width <= 2 || box.height <= 2) break;
            const beside = r => r.right <= box.left || r.left >= box.right;
            const cut = lines(el).some(r => !beside(r) && (hidesY && (r.bottom > box.bottom + 2 || r.top < box.top - 2)
              || hidesX && (r.right > box.right + 2 || r.left < box.left - 2)));
            if (cut) { cutBy.set(a, [...(cutBy.get(a) || []), label(el)]); break; }
          }
        }
        for (const [box, items] of cutBy) out.clipped.push(`${items.length} text element(s) inside ${label(box)}, e.g. ${items.slice(0, 2).join('; ')}`);

        // Jumps to in-page targets: scrollIntoView honours scroll-margin and scroll-padding, as a link does.
        const targets = new Set([...document.querySelectorAll('a[href^="#"]')].map(a => decodeURIComponent(a.getAttribute('href').slice(1))).filter(Boolean));
        for (const id of targets) {
          const target = document.getElementById(id);
          if (!target || !shown(target)) continue;
          target.scrollIntoView({ block: 'start', behavior: 'instant' });
          await frame();
          const heading = target.matches('h1, h2, h3, h4') ? target : target.querySelector('h1, h2, h3, h4') || target;
          const top = coverer(heading);
          const bar = top && pinned(top);
          if (bar && !heading.contains(bar)) out.anchors.push({ id, bar: `${label(bar)} (${Math.round(bar.getBoundingClientRect().height)} px)` });
        }
        window.scrollTo(0, 0);
        await frame();

        // Blank bands: vertical gaps with no text, media or control, taller than half a screen.
        const content = [];
        for (const el of document.querySelectorAll('body *')) {
          if (pinned(el) || !shown(el)) continue;
          const media = /^(IMG|VIDEO|SVG|CANVAS|IFRAME|OBJECT|EMBED|INPUT|SELECT|TEXTAREA|BUTTON|HR|TABLE)$/i.test(el.tagName);
          const text = [...el.childNodes].some(node => node.nodeType === 3 && node.data.trim());
          if (!media && !text) continue;
          const r = el.getBoundingClientRect();
          content.push([r.top + scrollY, r.bottom + scrollY, el]);
        }
        content.sort((a, b) => a[0] - b[0]);
        let reach = content.length ? content[0][1] : 0, last = content[0]?.[2];
        for (const [top, bottom, el] of content.slice(1)) {
          if (top - reach > innerHeight * 0.5) out.bands.push(`${Math.round(top - reach)} px between ${label(last)} and ${label(el)}`);
          if (bottom > reach) { reach = bottom; last = el; }
        }

        // Side margins: the innermost box holding all of a section's content should sit centred.
        const width = document.documentElement.clientWidth;
        for (const section of document.querySelectorAll('body > section, main > section, body > header, main > header, body > main > *, body > footer')) {
          if (!shown(section) || pinned(section)) continue;
          const items = content.filter(([, , el]) => section.contains(el)).map(([, , el]) => el);
          if (items.length < 2) continue;
          // A list or table indents by design, so the column is the block around it.
          let column = items[0].parentElement;
          while (column && column !== section && (!items.every(el => column.contains(el)) || /^(UL|OL|DL|TABLE|TBODY|THEAD|TR)$/.test(column.tagName))) column = column.parentElement;
          if (!column) continue;
          const r = column.getBoundingClientRect();
          const left = r.left, right = width - r.right;
          if (Math.abs(left - right) > 4 && left >= 0 && right >= 0) {
            const heading = section.querySelector('h1, h2, h3');
            out.margins.push(`${heading ? `"${heading.textContent.trim().replace(/\s+/g, ' ').slice(0, 30)}"` : label(section)} sits ${Math.round(left)} px from the left edge and ${Math.round(right)} px from the right`);
          }
        }

        // Targets: links and buttons under 24 x 24 px, except links inside running text and targets with room
        // around them (a 24 px circle on the target's centre touches no other target), as WCAG 2.5.8 allows.
        const controls = [...document.querySelectorAll('a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [role="link"]')].filter(shown);
        const rects = controls.map(el => el.getBoundingClientRect());
        const small = [];
        controls.forEach((el, i) => {
          const r = rects[i];
          if (r.width >= 24 && r.height >= 24) return;
          if (el.tagName === 'A' && getComputedStyle(el).display === 'inline') {
            const block = el.parentElement?.closest('p, li, td, dd, figcaption, caption, blockquote, div, span');
            if (block && block.textContent.trim().length > el.textContent.trim().length + 2) return;
          }
          const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
          const crowded = controls.some((other, j) => {
            if (j === i || other.contains(el) || el.contains(other)) return false;
            const o = rects[j];
            const dx = Math.max(o.left - cx, 0, cx - o.right), dy = Math.max(o.top - cy, 0, cy - o.bottom);
            return Math.hypot(dx, dy) < 12;
          });
          if (crowded) small.push(`${label(el)} ${Math.round(r.width)}x${Math.round(r.height)}`);
        });
        out.targets = small;

        // Focus under a bar: replay Tab down the page (each control scrolled to the bottom edge, the least scrolling, as
        // most browsers do) and Shift+Tab back up (each to the top edge), so bars that react to scroll direction behave as
        // they would. A control mostly covered by a fixed or sticky bar fails WCAG 2.4.11. scroll-padding counts.
        const bars = [...document.querySelectorAll('body *')].filter(n => /fixed|sticky/.test(getComputedStyle(n).position));
        const hidden = new Set();
        const tabbable = controls.filter(el => !pinned(el)).slice(0, 80);
        window.scrollTo(0, 0);
        await frame();
        for (const [el, block] of [...tabbable.map(el => [el, 'end']), ...tabbable.slice().reverse().map(el => [el, 'start'])]) {
          el.scrollIntoView({ block, behavior: 'instant' });
          await frame();
          const r = el.getBoundingClientRect();
          const bar = bars.find(b => {
            if (b.contains(el) || !b.checkVisibility({ opacityProperty: true, visibilityProperty: true })) return false;
            const o = b.getBoundingClientRect();
            const w = Math.min(r.right, o.right, innerWidth) - Math.max(r.left, o.left, 0);
            const h = Math.min(r.bottom, o.bottom, innerHeight) - Math.max(r.top, o.top, 0);
            if (w <= 0 || h <= 0 || w * h < r.width * r.height / 2) return false;
            const top = document.elementFromPoint(Math.max(r.left, o.left, 0) + w / 2, Math.max(r.top, o.top, 0) + h / 2);
            return top && b.contains(top);
          });
          if (bar) hidden.add(`${label(el)} under ${label(bar)}`);
        }
        out.focus = [...hidden];
        window.scrollTo(0, 0);
        return out;
      });
      found.covered.forEach(item => note(`c:${item}`, width, `Text covered: ${item}`, 'Move or resize the element on top, or give the text room.'));
      // One finding per bar, listing the jumps it hides.
      for (const bar of new Set(found.anchors.map(a => a.bar))) {
        const ids = found.anchors.filter(a => a.bar === bar).map(a => `#${a.id}`);
        note(`a:${bar}`, width, `Jump to ${ids.length > 4 ? `${ids.slice(0, 4).join(', ')} and ${ids.length - 4} more` : ids.join(', ')} lands the heading under ${bar}`,
          "Add scroll-padding-top to html equal to the bar's height.");
      }
      found.clipped.forEach(item => note(`k:${item.split(', e.g.')[0].replace(/^\d+ /, '')}`, width, `Text cut off: ${item}, which hides overflow`, 'Remove its fixed height or max-height, or let it grow.'));
      found.bands.forEach(item => note(`b:${item.replace(/^\d+ px/, '')}`, width, `Blank band of ${item}`, 'Remove the empty element or its fixed height.'));
      found.margins.forEach(item => note(`m:${item.split(' sits')[0]}`, width, `Uneven side margins: ${item}`, 'Remove the extra margin or padding so the column is centred.'));
      if (found.targets.length) note(`t:${found.targets.map(t => t.replace(/ \d+x\d+$/, '')).join()}`, width,
        `Targets under 24 x 24 px with others within reach: ${found.targets.slice(0, 4).join('; ')}${found.targets.length > 4 ? ` and ${found.targets.length - 4} more` : ''}`,
        'Make them at least 24 px or space them 24 px apart (WCAG 2.5.8).');
      if (found.focus.length) note(`f:${found.focus.map(f => f.split(' under ')[1]).filter((b, i, a) => a.indexOf(b) === i).join()}`, width,
        `Focus can land under a fixed or sticky bar: ${found.focus.length} control(s), e.g. ${found.focus.slice(0, 2).join('; ')}`,
        "Add scroll-padding-top or scroll-padding-bottom on html equal to the bar's height, or stop fixing the bar.");
    }
    for (const { widths, detail, fix } of seen.values()) warnings.push(`${detail} (at ${widths.join(', ')} px). ${fix}`);
    return { status: 'pass', warnings };
  } finally {
    await page.evaluate(() => window.scrollTo(0, 0));
    if (previousViewport) await page.setViewportSize(previousViewport);
  }
}
