// Honour prefers-reduced-motion for motion the page starts by itself:
// - pauses <video autoplay> loops and shows their controls;
// - pauses videos that page scripts start with play() (for example on scroll), while still allowing
//   a play the visitor starts themselves (detected through user activation);
// - sets data-reduced-motion on <html> and dispatches a "reducedmotionchange" event, so page scripts
//   such as carousels can stop autoplay.
// Keep this file whenever the page has autoplaying video or carousels; remove it otherwise.
(() => {
  const query = window.matchMedia('(prefers-reduced-motion: reduce)');

  const apply = () => {
    document.documentElement.toggleAttribute('data-reduced-motion', query.matches);
    document.querySelectorAll('video[autoplay]').forEach(video => {
      if (query.matches) {
        video.pause();
        video.controls = true;
      } else if (video.paused) {
        video.play().catch(() => {});
      }
    });
    document.dispatchEvent(new CustomEvent('reducedmotionchange', { detail: { reduce: query.matches } }));
  };

  // A play() without a recent user gesture comes from a script, not the visitor.
  document.addEventListener('play', event => {
    if (query.matches && !(navigator.userActivation && navigator.userActivation.isActive)) event.target.pause();
  }, true);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
  query.addEventListener('change', apply);
})();
