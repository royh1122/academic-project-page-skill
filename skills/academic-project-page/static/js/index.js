// Page behaviour for the academic project page template. Plain JavaScript, no dependencies.
// Each feature does nothing when its markup is absent, so remove markup freely.
//   - More Works menu      (.more-works)
//   - Copy BibTeX          ([data-copy-target])
//   - Back to top          (.scroll-to-top)
//   - Carousels            ([data-carousel]; data-autoplay="6000" opts in to rotation)
// Adapted from the Academic Project Page Template (CC BY-SA 4.0); jQuery and bulma-carousel removed.
(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // ---------- More Works menu ----------
  document.querySelectorAll('.more-works').forEach(menu => {
    const toggle = menu.querySelector('.more-works-btn');
    const panel = menu.querySelector('.more-works-panel');
    const close = menu.querySelector('.close-btn');
    if (!toggle || !panel) return;

    const setOpen = (open, returnFocus) => {
      toggle.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      if (open) panel.querySelector('a, button')?.focus();
      else if (returnFocus) toggle.focus();
    };
    setOpen(false);
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    close?.addEventListener('click', () => setOpen(false, true));
    document.addEventListener('click', event => {
      if (!menu.contains(event.target) && toggle.getAttribute('aria-expanded') === 'true') setOpen(false);
    });
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        event.stopPropagation();
        setOpen(false, true);
      }
    });
    menu.addEventListener('focusout', event => {
      if (event.relatedTarget && !menu.contains(event.relatedTarget)) setOpen(false);
    });
  });

  // ---------- Copy BibTeX ----------
  document.querySelectorAll('[data-copy-target]').forEach(button => {
    const source = document.getElementById(button.dataset.copyTarget);
    const label = button.querySelector('.copy-text');
    const status = document.getElementById(button.dataset.copyStatus);
    if (!source) return;
    const idleLabel = label ? label.textContent : '';
    let timer;

    const fallbackCopy = text => {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.append(area);
      area.select();
      const ok = document.execCommand('copy');
      area.remove();
      return ok;
    };

    const announce = (ok) => {
      clearTimeout(timer);
      button.classList.toggle('is-copied', ok);
      if (label) label.textContent = ok ? 'Copied' : 'Copy failed';
      if (status) status.textContent = ok ? 'BibTeX copied to the clipboard.' : 'Copy failed. Select the BibTeX text and copy it manually.';
      timer = setTimeout(() => {
        button.classList.remove('is-copied');
        if (label) label.textContent = idleLabel;
        if (status) status.textContent = '';
      }, 2500);
    };

    button.addEventListener('click', async () => {
      const text = source.textContent;
      try {
        await navigator.clipboard.writeText(text);
        announce(true);
      } catch {
        let ok = false;
        try { ok = fallbackCopy(text); } catch {}
        announce(ok);
      }
    });
  });

  // ---------- Back to top ----------
  const toTop = document.querySelector('.scroll-to-top');
  if (toTop) {
    const update = () => toTop.classList.toggle('is-visible', window.scrollY > 400);
    window.addEventListener('scroll', update, { passive: true });
    update();
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
      // Move focus to the top of the document so keyboard users continue from there.
      const target = document.getElementById('main-content');
      if (target) target.focus({ preventScroll: true });
    });
  }

  // ---------- Carousels ----------
  const icon = name => `<i class="fas fa-${name}" aria-hidden="true"></i>`;

  document.querySelectorAll('[data-carousel]:not(.is-ready)').forEach(carousel => {
    const track = carousel.querySelector('.carousel-track');
    const viewport = carousel.querySelector('.carousel-viewport');
    const slides = track ? [...track.children] : [];
    if (slides.length < 2) {
      carousel.classList.add('is-ready');
      return;
    }

    const count = slides.length;
    const interval = Number(carousel.dataset.autoplay) || 0;
    let index = 0;
    let playing = interval > 0 && !reducedMotion.matches;
    let hovered = false;
    let focused = false;
    let inView = false;
    let viewerOpen = false;
    let timer = null;

    slides.forEach((slide, i) => {
      slide.setAttribute('role', 'group');
      slide.setAttribute('aria-roledescription', 'slide');
      slide.setAttribute('aria-label', `${i + 1} of ${count}`);
    });

    // Controls: previous, one dot per slide, next, and a pause/play button only when rotation is enabled.
    const controls = document.createElement('div');
    controls.className = 'carousel-controls';
    controls.innerHTML = `
      <button type="button" class="carousel-button carousel-prev" aria-label="Previous slide">${icon('chevron-left')}</button>
      <div class="carousel-dots" role="group" aria-label="Choose a slide">
        ${slides.map((_, i) => `<button type="button" class="carousel-dot" aria-label="Show slide ${i + 1} of ${count}"></button>`).join('')}
      </div>
      <button type="button" class="carousel-button carousel-next" aria-label="Next slide">${icon('chevron-right')}</button>
      ${interval ? `<button type="button" class="carousel-button carousel-toggle"></button>` : ''}`;
    carousel.append(controls);
    const dots = [...controls.querySelectorAll('.carousel-dot')];
    const toggle = controls.querySelector('.carousel-toggle');

    const videos = slide => [...slide.querySelectorAll('video')];
    // Muted carousel videos play only while their slide is current, the carousel is on screen,
    // and the visitor has not asked for reduced motion. Everything else stays paused.
    const syncVideos = () => {
      slides.forEach((slide, i) => videos(slide).forEach(video => {
        const shouldPlay = i === index && inView && !reducedMotion.matches && video.muted;
        if (shouldPlay && video.paused) video.play().catch(() => {});
        else if (!shouldPlay && !video.paused) video.pause();
      }));
    };

    const render = () => {
      track.style.transform = `translateX(-${index * 100}%)`;
      slides.forEach((slide, i) => {
        const current = i === index;
        // Off-screen slides leave the tab order and the accessibility tree.
        slide.inert = !current;
        if (current) slide.removeAttribute('aria-hidden');
        else slide.setAttribute('aria-hidden', 'true');
      });
      dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === index)));
      syncVideos();
    };

    const go = (next, fromUser) => {
      index = (next + count) % count;
      render();
      if (fromUser) restart();
    };

    const stop = () => { clearInterval(timer); timer = null; };
    const restart = () => {
      stop();
      if (playing && !hovered && !focused && !viewerOpen && inView && !document.hidden) timer = setInterval(() => go(index + 1), interval);
    };
    const renderToggle = () => {
      if (!toggle) return;
      toggle.setAttribute('aria-label', playing ? `Pause automatic slide show` : `Start automatic slide show`);
      toggle.innerHTML = icon(playing ? 'pause' : 'play');
      // Announce slide changes only when the visitor is driving them.
      track.setAttribute('aria-live', playing ? 'off' : 'polite');
    };

    controls.querySelector('.carousel-prev').addEventListener('click', () => go(index - 1, true));
    controls.querySelector('.carousel-next').addEventListener('click', () => go(index + 1, true));
    dots.forEach((dot, i) => dot.addEventListener('click', () => go(i, true)));
    toggle?.addEventListener('click', () => { playing = !playing; renderToggle(); restart(); });

    carousel.addEventListener('keydown', event => {
      if (event.target.closest('video, input, textarea')) return;
      if (event.key === 'ArrowLeft') { go(index - 1, true); event.preventDefault(); }
      if (event.key === 'ArrowRight') { go(index + 1, true); event.preventDefault(); }
    });

    // Rotation pauses while the pointer or keyboard focus is inside the carousel...
    carousel.addEventListener('mouseenter', () => { hovered = true; restart(); });
    carousel.addEventListener('mouseleave', () => { hovered = false; restart(); });
    carousel.addEventListener('focusin', () => { focused = true; restart(); });
    carousel.addEventListener('focusout', event => { if (!carousel.contains(event.relatedTarget)) { focused = false; restart(); } });
    document.addEventListener('visibilitychange', restart);
    // ...and while the figure viewer shows an enlarged image.
    document.addEventListener('figure-viewer:open', () => { viewerOpen = true; restart(); });
    document.addEventListener('figure-viewer:close', () => { viewerOpen = false; restart(); });

    // Swipe on touch screens.
    let startX = null;
    viewport.addEventListener('pointerdown', event => { if (event.pointerType !== 'mouse') startX = event.clientX; });
    viewport.addEventListener('pointerup', event => {
      if (startX === null) return;
      const dx = event.clientX - startX;
      startX = null;
      if (Math.abs(dx) > 40) go(index + (dx < 0 ? 1 : -1), true);
    });
    viewport.addEventListener('pointercancel', () => { startX = null; });

    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      syncVideos();
      restart();
    }, { threshold: 0.5 }).observe(viewport);

    reducedMotion.addEventListener('change', () => {
      if (reducedMotion.matches) playing = false;
      renderToggle();
      syncVideos();
      restart();
    });

    carousel.classList.add('is-ready');
    track.setAttribute('aria-live', 'polite');
    renderToggle();
    render();
  });
})();
