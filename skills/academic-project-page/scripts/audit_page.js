// Playwright CLI: run-code --filename /path/to/this/file.js
// Audits the currently loaded generated page. Failures are defects to fix before delivery;
// warnings need a look at screenshots. Restores the previous viewport; does not navigate.
async (page) => {
  const previousViewport = page.viewportSize();
  const failures = [];
  const warnings = [];
  const evidence = {};

  try {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.evaluate(() => document.fonts.ready);

    // Static structure, text, and contrast at desktop width.
    const report = await page.evaluate(() => {
      const out = { failures: [], warnings: [], evidence: {} };
      // checkVisibility also treats content inside a closed <details> as hidden; offsetParent does not.
      const visible = el => el.checkVisibility();
      const label = el => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.classList.length ? '.' + [...el.classList].join('.') : ''}`;

      // Placeholder conventions of common project-page templates; HTML comments are ignored.
      const markup = document.documentElement.outerHTML.replace(/<!--[\s\S]*?-->/g, '');
      const placeholder = (markup.match(/\bTODO\b/) || markup.match(/\[INSERT[^\]]*\]|lorem ipsum|YOUR[ _](?:REPO|DOMAIN|NAME)|PAPER_(?:TITLE|ID)|ARXIV PAPER ID|AUTHOR PERSONAL LINK/i));
      if (placeholder) out.failures.push(`Template placeholder remains: "${placeholder[0]}"`);

      const ids = [...document.querySelectorAll('[id]')].map(el => el.id).filter(Boolean);
      const duplicates = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
      if (duplicates.length) out.failures.push(`Duplicate ids: ${duplicates.join(', ')}`);

      const headings = [...document.querySelectorAll('h1, h2, h3, h4, h5, h6')].filter(h => !h.closest('dialog'));
      if (headings.filter(h => h.tagName === 'H1').length !== 1) out.failures.push('Page needs exactly one h1');
      headings.reduce((prev, h) => {
        const level = +h.tagName[1];
        if (level > prev + 1) out.failures.push(`Heading level skipped before "${h.textContent.trim().slice(0, 40)}"`);
        return level;
      }, 1);

      document.querySelectorAll('img:not([alt])').forEach(img => out.failures.push(`Image without alt: ${img.getAttribute('src')}`));
      // Icon-font markup (Font Awesome, Academicons) draws nothing when no icon font or script is loaded.
      document.querySelectorAll('i[class*="fa-"], i[class*="ai-"], span[class*="fa-"]').forEach(el => {
        const before = getComputedStyle(el, '::before').content;
        if (['none', 'normal', '""'].includes(before) && !el.querySelector('svg') && el.getBoundingClientRect().width < 1)
          out.failures.push(`Icon draws nothing (no icon font loaded): <${el.tagName.toLowerCase()} class="${el.className}">; paste its inline SVG instead (references/icons.md)`);
      });
      document.querySelectorAll('a, button').forEach(el => {
        if (!el.closest('dialog') && !(el.getAttribute('aria-label') || el.textContent.trim() || el.querySelector('img[alt]:not([alt=""])')))
          out.failures.push(`Control without an accessible name: ${el.outerHTML.slice(0, 80)}`);
      });

      // Synthesized bold: a web font used at a weight none of its loaded faces covers.
      const faces = [...document.fonts].filter(f => f.status === 'loaded');
      const covers = (face, weight) => { const [lo, hi = lo] = face.weight.split(' ').map(Number); return weight >= lo - 50 && weight <= hi + 50; };
      const seen = new Set();
      document.querySelectorAll('body *').forEach(el => {
        if (!visible(el) || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
        const style = getComputedStyle(el);
        const family = style.fontFamily.split(',')[0].replace(/["']/g, '').trim();
        const weight = +style.fontWeight;
        const familyFaces = faces.filter(f => f.family.replace(/["']/g, '') === family);
        const key = `${family} ${weight}`;
        if (familyFaces.length && !familyFaces.some(f => covers(f, weight)) && !seen.has(key)) {
          seen.add(key);
          out.failures.push(`${family} is used at weight ${weight} but that weight is not loaded (synthesized bold), e.g. ${label(el)}`);
        }
      });
      out.evidence.loadedFaces = faces.map(f => `${f.family} ${f.weight}`);

      // Text contrast against the nearest opaque background (WCAG AA).
      const parse = c => c.match(/[\d.]+/g).map(Number);
      const luminance = c => { const [r, g, b] = parse(c).slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
      const background = el => { for (let e = el; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; const a = parse(c)[3]; if (a === undefined || a > .9) return c; } return 'rgb(255, 255, 255)'; };
      document.querySelectorAll('body *').forEach(el => {
        // Fallback content inside media elements is never rendered when the media loads.
        if (el.closest('dialog, svg, video, audio, canvas, object, iframe, noscript') || !visible(el)) return;
        if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
        const style = getComputedStyle(el);
        const [l1, l2] = [luminance(style.color), luminance(background(el))];
        const ratio = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
        const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.66 && +style.fontWeight >= 700);
        if (ratio < (large ? 3 : 4.5)) out.failures.push(`Contrast ${ratio.toFixed(2)}:1 below ${large ? 3 : 4.5}:1 for ${label(el)} "${el.textContent.trim().slice(0, 30)}"`);
        if (parseFloat(style.fontSize) < 12) out.warnings.push(`Text below 12px: ${label(el)} "${el.textContent.trim().slice(0, 30)}"`);
      });

      // Layout consistency.
      // Carousel libraries clone slides for infinite loops ([data-cloned]); clones are not repeats.
      const sources = [...document.querySelectorAll('main img, section img')].filter(img => !img.closest('dialog, [data-cloned]')).map(img => new URL(img.currentSrc || img.src, location.href).pathname);
      const repeated = [...new Set(sources.filter((src, i) => sources.indexOf(src) !== i))];
      if (repeated.length) out.warnings.push(`Same image shown more than once: ${repeated.join(', ')}`);

      // Compare content-sized media only; small portraits and logos may be round by design.
      const radii = new Set([...document.querySelectorAll('section img, section video')].filter(m => !m.closest('dialog, [data-cloned]') && visible(m) && m.getBoundingClientRect().width >= 240).map(m => getComputedStyle(m).borderTopLeftRadius));
      if (radii.size > 1) out.warnings.push(`Media use different corner radii: ${[...radii].join(', ')}`);

      // Within one section, left-aligned blocks in the first column should share one left edge.
      const inLaterColumn = el => {
        for (let a = el; a && a.tagName !== 'SECTION'; a = a.parentElement) {
          const r = a.getBoundingClientRect();
          for (let s = a.previousElementSibling; s; s = s.previousElementSibling) {
            const q = s.getBoundingClientRect();
            if (q.width && q.right <= r.left + 1 && q.bottom > r.top && q.top < r.bottom) return true;
          }
        }
        return false;
      };
      out.evidence.sectionLeftEdges = {};
      document.querySelectorAll('section').forEach(section => {
        if (section.querySelector('h1') || section.querySelector('section')) return;
        const edges = new Map();
        section.querySelectorAll('h3, p, table, details, pre, figure').forEach(el => {
          if (el.closest('dialog, li, figure figure, td, th, summary, .publication-links') || !visible(el)) return;
          if (/^(H3|P)$/.test(el.tagName) && getComputedStyle(el).textAlign === 'center' || el.closest('.has-text-centered') || inLaterColumn(el)) return;
          const edge = Math.round(el.getBoundingClientRect().left);
          if (!edges.has(edge)) edges.set(edge, `${el.tagName.toLowerCase()} "${el.textContent.trim().slice(0, 30)}"`);
        });
        const name = section.id || section.querySelector('h2')?.textContent.trim().slice(0, 30) || label(section);
        out.evidence.sectionLeftEdges[name] = [...edges.keys()];
        if (edges.size > 1) out.warnings.push(`Section "${name}" starts content at ${edges.size} left edges: ${[...edges].map(([x, what]) => `${x}px ${what}`).join('; ')}`);
      });

      // Numeric columns read best right-aligned, so digits line up.
      const number = /^[~≈<>≥≤+\-−–\s]*\d[\d.,]*\s*(±\s*[\d.,]+\s*)?(%|×|x|ms|s|m|k|M|B|G|GB|MB|dB|fps|px)?(\s*\([^)]*\))?\*?$/;
      document.querySelectorAll('table').forEach(table => {
        if (!visible(table) || table.closest('dialog') || table.querySelector('[colspan], [rowspan]')) return;
        const rows = [...table.rows];
        const headRows = table.tHead ? table.tHead.rows.length : 1;
        const head = rows[headRows - 1], body = rows.slice(headRows);
        if (!head || body.length < 2) return;
        const caption = table.caption?.textContent.trim().slice(0, 40) || table.closest('figure')?.querySelector('figcaption')?.textContent.trim().slice(0, 40) || 'untitled';
        [...head.cells].forEach((th, c) => {
          const cells = body.map(row => row.cells[c]).filter(cell => cell && cell.textContent.trim());
          const name = th.textContent.trim();
          if (cells.length < 2 || /year|\bids?\b|^#|rank|\bno\b|seed|date/i.test(name)) return;
          const texts = cells.map(cell => cell.textContent.trim());
          if (texts.every(t => /^(19|20)\d\d$/.test(t)) || texts.filter(t => number.test(t)).length < texts.length * .8) return;
          const left = cells.filter(cell => /^(left|start)$/.test(getComputedStyle(cell).textAlign)).length;
          if (left > cells.length / 2) out.warnings.push(`Table "${caption}" column "${name.slice(0, 30)}": numbers are left-aligned; right-align numeric columns`);
        });
      });

      const disclosed = [...document.querySelectorAll('details img')].map(img => img.alt).filter(alt => /architect|pipeline|overview|method/i.test(alt));
      if (disclosed.length) out.warnings.push(`Method/architecture figure hidden in a disclosure: "${disclosed[0].slice(0, 50)}"`);

      const citations = [...document.querySelectorAll('pre, code')].filter(el => /@\w+\{/.test(el.textContent));
      if (citations.length && !citations.some(visible)) out.warnings.push('Citation exists but is hidden; show it as a visible BibTeX section');

      const navLinks = [...document.querySelectorAll('nav a[href^="#"]')];
      navLinks.forEach(a => { if (!document.querySelector(a.getAttribute('href'))) out.failures.push(`Navigation link to missing section ${a.getAttribute('href')}`); });

      out.localRefs = [...new Set([...document.querySelectorAll('[src], [href], [poster], [data-zoom-src], source[srcset], img[srcset]')]
        .flatMap(el => ['src', 'href', 'poster', 'data-zoom-src'].map(attr => el.getAttribute(attr)))
        .filter(ref => ref && !/^(https?:|mailto:|#|data:|javascript:)/.test(ref)))];
      document.querySelectorAll('iframe').forEach(frame => {
        if (!frame.getAttribute('title')) out.failures.push(`Iframe without a title (screen readers announce it by title): ${(frame.getAttribute('src') || '').slice(0, 80)}`);
      });
      document.querySelectorAll('video').forEach(video => {
        if (video.closest('[data-cloned]')) return;
        const name = (video.currentSrc || video.querySelector('source')?.getAttribute('src') || '').split('/').pop();
        if (!video.autoplay && !video.getAttribute('poster')) out.warnings.push(`Video without a poster shows a blank frame until played: ${name}`);
        if (!video.getAttribute('width') || !video.getAttribute('height')) out.warnings.push(`Video without width/height attributes shifts layout while loading: ${name}`);
        if (video.autoplay && !video.hasAttribute('playsinline')) out.warnings.push(`Autoplay video without playsinline will not play inline on iOS: ${name}`);
      });
      out.videos = [...document.querySelectorAll('video source[src], video[src]')].map(el => new URL(el.getAttribute('src'), location.href).href);
      return out;
    });
    failures.push(...report.failures);
    warnings.push(...report.warnings);
    Object.assign(evidence, report.evidence);

    // A poster that is one flat colour (a black first frame) shows the visitor nothing. Sample it small;
    // same-origin posters only, and a tainted canvas is skipped.
    const posters = await page.evaluate(async () => {
      const bad = [];
      for (const video of document.querySelectorAll('video[poster]')) {
        if (video.closest('[data-cloned]')) continue;
        try {
          const src = new URL(video.getAttribute('poster'), location.href);
          if (src.origin !== location.origin) continue;
          const img = new Image();
          img.src = src.href;
          await img.decode();
          const canvas = document.createElement('canvas');
          canvas.width = 48; canvas.height = 27;
          const context = canvas.getContext('2d');
          context.drawImage(img, 0, 0, 48, 27);
          const data = context.getImageData(0, 0, 48, 27).data;
          const lum = [];
          for (let i = 0; i < data.length; i += 4) lum.push(.2126 * data[i] + .7152 * data[i + 1] + .0722 * data[i + 2]);
          const mean = lum.reduce((a, b) => a + b) / lum.length;
          const deviation = Math.sqrt(lum.reduce((a, b) => a + (b - mean) ** 2, 0) / lum.length);
          // A blank frame is flat; a near-black one may carry noise, so allow a little more spread when it is dark.
          if (deviation < 4 || (mean < 25 && deviation < 10)) bad.push(`${src.pathname.split('/').pop()} (mean ${Math.round(mean)}, spread ${deviation.toFixed(1)})`);
        } catch { /* cross-origin, tainted canvas or undecodable: skip */ }
      }
      return bad;
    });
    posters.forEach(poster => warnings.push(`Video poster is a blank or near-black frame: ${poster}; pick a frame by looking at candidates`));

    // Root-relative paths only break when the page is served beneath a repository subpath.
    if (new URL(page.url()).pathname !== '/' && report.localRefs.some(ref => ref.startsWith('/'))) failures.push('Root-relative paths (/static/...) break repository-subpath hosting; use ./static/...');
    // A dev server injects its client and serves source files; GitHub Pages serves only the built site.
    // The browser silently merges a second <body> or <head> (a pasted or doubled template), so read the source as served.
    const serving = await page.evaluate(async () => ({
      dev: [...document.querySelectorAll('script[src], link[href]')].map(el => el.getAttribute('src') || el.getAttribute('href'))
        .filter(src => /\/@vite\/client|\/@react-refresh|webpack-dev-server|livereload\.js|\/_next\/static\/development/.test(src)),
      canonical: document.querySelector('link[rel="canonical"]')?.href || document.querySelector('meta[property="og:url"]')?.content || '',
      doubled: await fetch(location.href).then(r => r.text()).then(source => {
        const bare = source.replace(/<!--[\s\S]*?-->/g, '').replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, '');
        return ['html', 'head', 'body'].filter(tag => (bare.match(new RegExp(`<${tag}[\\s>]`, 'gi')) || []).length > 1);
      }).catch(() => []),
    }));
    if (serving.doubled.length) warnings.push(`Malformed page source: more than one <${serving.doubled.join('>, <')}> tag (a doubled template block); browsers merge them, so repeated content such as a second skip link shows. Keep one of each.`);
    if (serving.dev.length) warnings.push(`Dev server markup in the page: ${serving.dev.slice(0, 2).join(', ')}. Audit the built site served with preview_server.py, not the dev server.`);
    const named = serving.canonical ? new URL(serving.canonical, page.url()).pathname.replace(/[^/]*$/, '').replace(/^\/|\/$/g, '') : '';
    if (new URL(page.url()).pathname === '/' && named)
      warnings.push(`Served at / but the page's canonical URL is under /${named}/; serve with preview_server.py --base ${named} to test it as GitHub Pages will serve it.`);
    for (const ref of report.localRefs) {
      const response = await page.request.get(new URL(ref, page.url()).href);
      if (!response.ok()) failures.push(`Missing local resource ${ref} (${response.status()})`);
      await response.dispose();
    }

    // Seeking needs byte-range support; python -m http.server lacks it (GitHub Pages has it).
    for (const video of report.videos) {
      const response = await page.request.get(video, { headers: { Range: 'bytes=0-1' } });
      if (response.status() !== 206) failures.push(`Preview server ignores Range for ${video.split('/').pop()} (status ${response.status()}); videos cannot seek. Serve with scripts/preview_server.py`);
      await response.dispose();
    }

    for (const width of [375, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      const layout = await page.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
        await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
        const visible = el => el.checkVisibility();
        // Vector images scale cleanly, so only raster images count as stretched.
        const upscaled = [...document.images].filter(img => visible(img) && !img.closest('dialog') && !/\.svg(\?|#|$)/i.test(img.currentSrc) && img.naturalWidth && img.getBoundingClientRect().width > img.naturalWidth * 1.1)
          .map(img => `${img.getAttribute('src')} at ${Math.round(img.getBoundingClientRect().width / img.naturalWidth * 100)}%`);
        const teaser = document.querySelector('.teaser');
        const media = teaser ? [...teaser.querySelectorAll('img, video')].filter(visible).map(m => m.getBoundingClientRect()) : [];
        const sideBySide = media.length > 1 && Math.abs(media[0].top - media[1].top) < 2;
        // A box whose shape differs from the media's own shape letterboxes it (fixed height + object-fit).
        const letterboxed = teaser ? [...teaser.querySelectorAll('img, video')].filter(visible).filter(m => {
          const natural = m.tagName === 'IMG' ? m.naturalWidth / m.naturalHeight : (m.videoWidth || +m.getAttribute('width')) / (m.videoHeight || +m.getAttribute('height'));
          const box = m.getBoundingClientRect();
          return natural && Math.abs(box.width / box.height - natural) / natural > .05;
        }).map(m => m.getAttribute('src') || m.querySelector('source')?.getAttribute('src')) : [];
        return {
          letterboxed,
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
          upscaled,
          teaserHeights: sideBySide ? media.map(r => Math.round(r.height)) : null,
          // Line of each non-space title character, to find a break right after an in-word hyphen and a one-word last line.
          title: (() => {
            const h = document.querySelector('h1');
            if (!h) return { hyphen: [], orphan: null };
            const chars = [], walker = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
            for (let node; (node = walker.nextNode());) for (let i = 0; i < node.length; i++) {
              if (/\s/.test(node.data[i])) { chars.push({ ch: ' ' }); continue; }
              const range = document.createRange();
              range.setStart(node, i); range.setEnd(node, i + 1);
              const rect = range.getClientRects()[0];
              chars.push({ ch: node.data[i], top: rect ? rect.top : null, bottom: rect ? rect.bottom : null });
            }
            const hyphen = [];
            chars.forEach((c, i) => {
              const n = chars[i + 1];
              if (!/[-‐]/.test(c.ch) || !n || c.top === null || n.top === null || !/\p{L}/u.test(n.ch) || !/\p{L}/u.test(chars[i - 1]?.ch || '')) return;
              if (n.top > c.top + 5) {
                const text = chars.map(x => x.ch).join('');
                const start = text.lastIndexOf(' ', i) + 1, end = text.indexOf(' ', i);
                hyphen.push(text.slice(start, end < 0 ? undefined : end));
              }
            });
            const placed = chars.filter(c => c.top !== null);
            const lastTop = placed.length ? placed[placed.length - 1].top : 0;
            const last = chars.slice(chars.findIndex(c => c.top !== null && Math.abs(c.top - lastTop) < 2)).map(c => c.ch).join('').trim();
            const multiline = placed.some(c => c.top < lastTop - 2);
            return { hyphen, orphan: multiline && last && !last.includes(' ') && last.length <= 10 ? last : null };
          })(),
          titleLines: (() => { const h = document.querySelector('h1'); return h ? Math.round(h.getBoundingClientRect().height / parseFloat(getComputedStyle(h).lineHeight)) : 0; })(),
        };
      });
      if (layout.overflow) failures.push(`Horizontal overflow at ${width}px`);
      if (layout.upscaled.length) warnings.push(`Images stretched beyond natural size at ${width}px (blurry): ${layout.upscaled.join('; ')}`);
      if (layout.teaserHeights && Math.max(...layout.teaserHeights) - Math.min(...layout.teaserHeights) > 4)
        warnings.push(`Teaser media differ in height at ${width}px: ${layout.teaserHeights.join(' vs ')} px. Use aspect-ratio grid columns.`);
      if (layout.letterboxed.length) warnings.push(`Teaser media letterboxed at ${width}px (box shape differs from the media): ${layout.letterboxed.join(', ')}. Remove the fixed height; use aspect-ratio grid columns.`);
      layout.title.hyphen.forEach(word => failures.push(`Title breaks inside "${word}" at ${width}px; wrap the term in <span class="nowrap">`));
      if (layout.title.orphan) warnings.push(`Title ends with a single word "${layout.title.orphan}" alone on its last line at ${width}px; rebalance the title (text-wrap: balance)`);
      evidence[`titleLines@${width}`] = layout.titleLines;
    }

    // Text a scroll-reveal never shows: scroll through the page, then list text still at opacity ~0.
    // Floating controls and deliberately hidden panels (visibility: hidden) are not content.
    const hiddenText = () => page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) {
        window.scrollTo(0, y);
        await new Promise(resolve => setTimeout(resolve, 120));
      }
      await new Promise(resolve => setTimeout(resolve, 600));
      const found = [];
      for (const el of document.querySelectorAll('body *')) {
        if (![...el.childNodes].some(node => node.nodeType === 3 && node.data.trim())) continue;
        if (el.closest('[inert], [aria-hidden="true"], dialog, details:not([open]), script, style, noscript, template')) continue;
        if (!el.checkVisibility() || getComputedStyle(el).visibility === 'hidden') continue;
        let opacity = 1, pinned = false;
        for (let a = el; a && a !== document.documentElement; a = a.parentElement) {
          const cs = getComputedStyle(a);
          opacity *= parseFloat(cs.opacity);
          if (/fixed|sticky/.test(cs.position)) pinned = true;
        }
        if (opacity < 0.1 && !pinned) found.push(`${el.tagName.toLowerCase()} "${el.textContent.trim().replace(/\s+/g, ' ').slice(0, 40)}"`);
      }
      window.scrollTo(0, 0);
      return found;
    });
    await page.setViewportSize({ width: 1440, height: 900 });
    const hiddenNormally = await hiddenText();

    // Motion the page starts by itself must stop for visitors who prefer reduced motion.
    // Scripts often read the preference at load, so the page is reloaded with the preference emulated.
    const cdp = await page.context().newCDPSession(page);
    try {
      await page.setViewportSize({ width: 1440, height: 900 });
      await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
      await page.goto(page.url());
      const motion = await page.evaluate(async () => {
        const positions = () => [...document.querySelectorAll('.carousel, .carousel *, [class*="slider-container"]')]
          .filter(el => el.children.length).map(el => `${getComputedStyle(el).transform}|${el.scrollLeft}`);
        const before = positions();
        await new Promise(resolve => setTimeout(resolve, 5600));
        return {
          playing: [...document.querySelectorAll('video')].filter(v => !v.paused && !v.ended && v.readyState > 2 && !v.closest('[data-cloned]'))
            .map(v => (v.currentSrc || '').split('/').pop()),
          carouselMoved: positions().some((position, i) => position !== before[i]),
          endless: document.getAnimations().filter(a => a.playState === 'running' && a.effect?.getComputedTiming?.().iterations === Infinity).length,
        };
      });
      evidence.reducedMotion = motion;
      if (motion.playing.length) failures.push(`Videos keep playing under prefers-reduced-motion: ${motion.playing.join(', ')}. Use static/js/reduced-motion.js.`);
      if (motion.carouselMoved) failures.push('A carousel keeps advancing under prefers-reduced-motion. Disable autoplay when the preference is set.');
      if (motion.endless) warnings.push(`${motion.endless} endless CSS animation(s) keep running under prefers-reduced-motion.`);
      const hiddenReduced = (await hiddenText()).filter(text => !hiddenNormally.includes(text));
      if (hiddenReduced.length) warnings.push(`Text hidden under reduced motion: ${hiddenReduced.length} element(s) stay invisible, e.g. ${hiddenReduced.slice(0, 3).join('; ')}. Show content by default and animate it only under prefers-reduced-motion: no-preference.`);
    } finally {
      await cdp.send('Emulation.setEmulatedMedia', { features: [] });
      await page.goto(page.url());
      await cdp.detach();
    }

    const result = { status: failures.length ? 'fail' : 'pass', failures, warnings, evidence };
    if (failures.length) throw new Error(`Page audit failed:\n- ${failures.join('\n- ')}\nWarnings:\n- ${warnings.join('\n- ') || 'none'}`);
    return result;
  } finally {
    if (previousViewport) await page.setViewportSize(previousViewport);
  }
}
