"""Build the fourth flawed-page fixture (flawed-v4): defects that live in the stylesheet and the script, not the HTML.

    python make_flawed_page_v4.py <clean page folder> [--out flawed-v4]

The clean page is the public "paper" demo (the gh-pages branch of this repository, folder paper/), built from kit V1.
In eval 14 a no-skill agent fixed every flawed-v3 defect by reading index.html. Here index.html is left byte for byte as
it was: every defect is an edit to static/css/index.css or static/js/index.js, made in place in an existing rule where
one exists, with no comment that announces it. (A first version added commented blocks; a no-skill agent fixed all of
them by reading the comments.) Finding them means looking at the rendered page, or reading every rule. Several
target audit checks that had no planted flaw before (focus-indicator, text-small, overflow, motion-carousel,
motion-endless). One defect has no audit id and is found only by looking at the screenshots.
The defect list is written next to the fixture as <out>.defects.json and must stay out of the agent's working folder.
Serve under a repository subpath (preview_server.py --root docs --base quillwave).
"""
import argparse
import json
import shutil
from pathlib import Path

# (id, defect, audit id or None, the clean fix)
DEFECTS = [
    ("X1", "index.js injects a fixed 56 px lab bar at the top of the screen and pads the body, so every Contents jump lands "
     "its heading under the bar", "anchor-covered",
     "Remove the injected bar, or add html { scroll-padding-top } equal to its height"),
    ("X2", "index.css folds the abstract into a box with max-height: 7.5rem and overflow: hidden, so most of it is cut off",
     "text-clipped", "Remove the max-height and overflow rule"),
    ("X3", "index.css's :focus-visible rule sets outline: none instead of the focus ring, so keyboard users cannot see "
     "where they are", "focus-indicator", "Restore outline: var(--focus-ring) in that rule"),
    ("X4", "index.css sets the author names to 11px", "text-small", "Remove the font-size override"),
    ("X5", "index.css sets the title to white-space: nowrap, so on a phone it runs off the screen and the page scrolls sideways",
     "overflow", "Remove the white-space rule"),
    ("X6", "index.js advances the carousel every 4 seconds by clicking Next, also for visitors who prefer reduced motion",
     "motion-carousel", "Remove the timer, or use the template's data-autoplay option, which respects the preference"),
    ("X7", "index.js pulses the venue pill with an endless Web Animations API animation, which the template's reduced-motion "
     "CSS cannot stop", "motion-endless",
     "Remove the animation, or start it only when prefers-reduced-motion is not set"),
    ("X8", "index.css gives the Results container margin-left: 3rem, so the section sits off-centre", "margin-uneven",
     "Remove the margin-left"),
    ("X9", "index.js hides Limitations until a scroll-reveal runs, and the reveal is skipped under reduced motion, so those "
     "visitors never see the limitations", "hidden-reduced-motion",
     "Show the section by default and fade it only under prefers-reduced-motion: no-preference, or remove the reveal"),
    ("X10", "index.css lightens figure captions to #a3acb9, below 4.5:1 contrast on white", "contrast",
     "Restore the caption colour token (or any colour with at least 4.5:1)"),
    ("X11", "index.css squashes the teaser video to height: 220px with object-fit: fill, so the ripple fields are distorted",
     "teaser-letterbox", "Remove the height and object-fit override so the video keeps its 960x360 aspect"),
    ("X12", "index.css turns the Results figures grey (filter: grayscale(1)), so the colour-coded methods in the panels can "
     "no longer be told apart", None, "Remove the filter"),
]

# Exact (old, new) edits to static/css/index.css. Existing rules are changed in place where one exists; the three
# rules with no natural home are added without a comment, so nothing in the file announces a defect.
CSS = [
    ("""summary:focus-visible {
  outline: var(--focus-ring);""", """summary:focus-visible {
  outline: none;"""),  # X3
    ("""  font-weight: 800 !important;
  line-height: 1.1 !important;""", """  font-weight: 800 !important;
  line-height: 1.1 !important;
  white-space: nowrap !important;"""),  # X5
    (""".author-block {
  display: inline-block;
  margin-right: .35rem;""", """.author-block {
  display: inline-block;
  margin-right: .35rem;
  font-size: 11px;"""),  # X4
    (""".section.is-light + .section.is-light {""", """.has-text-justified {
  max-height: 7.5rem;
  overflow: hidden;
}

main > section:nth-of-type(6) > .container {
  margin-left: 3rem;
}

.section.is-light + .section.is-light {"""),  # X2, X8
    ("""  width: 100%;
  height: auto;
  box-shadow: var(--shadow-lg);""", """  width: 100%;
  height: 220px;
  object-fit: fill;
  box-shadow: var(--shadow-lg);"""),  # X11
    (""".teaser-caption {
  margin-top: 1.25rem;
  color: var(--text-secondary);""", """.teaser-caption {
  margin-top: 1.25rem;
  color: #a3acb9;"""),  # X10
    ("""  margin-top: .75rem;
  color: var(--text-secondary);
  font-size: .9375rem;""", """  margin-top: .75rem;
  color: #a3acb9;
  font-size: .9375rem;"""),  # X10
    ("""/* Bulma indents figures inside .content by 2em;""", """main > section:nth-of-type(6) figure img {
  filter: grayscale(1);
}

/* Bulma indents figures inside .content by 2em;"""),  # X12
]

# Exact (old, new) edit to static/js/index.js: plain code at the top of the template's own block, with no section comment.
JS = [
    ("""  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
""",
     """  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  const labBar = document.createElement('div');
  labBar.textContent = 'Imaginary Sciences Lab';
  labBar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:20;height:56px;display:flex;align-items:center;'
    + 'padding:0 1.5rem;background:#1e293b;color:#f8fafc;font-weight:600';
  document.body.prepend(labBar);
  document.body.style.paddingTop = '56px';

  const limits = document.querySelector('main > section:nth-of-type(9)');
  if (limits) {
    limits.style.opacity = '0';
    if (!reducedMotion.matches) {
      limits.style.transition = 'opacity .6s ease';
      new IntersectionObserver((entries, obs) => entries.forEach(e => {
        if (e.isIntersecting) { e.target.style.opacity = '1'; obs.disconnect(); }
      })).observe(limits);
    }
  }

  document.querySelector('.publication-venue')?.animate([{ opacity: 1 }, { opacity: .55 }, { opacity: 1 }],
    { duration: 2400, iterations: Infinity });
  setInterval(() => document.querySelector('.carousel-next')?.click(), 4000);
"""),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clean')
    ap.add_argument('--out', default=str(Path(__file__).resolve().parent / 'flawed-v4'))
    args = ap.parse_args()
    out = Path(args.out)
    docs = out / 'docs'
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(args.clean, docs)

    css_path = docs / 'static' / 'css' / 'index.css'
    css = css_path.read_text(encoding='utf-8')
    for old, new in CSS:
        assert css.count(old) == 1, old
        css = css.replace(old, new)
    css_path.write_bytes(css.encode('utf-8'))
    js_path = docs / 'static' / 'js' / 'index.js'
    js = js_path.read_text(encoding='utf-8')
    for old, new in JS:
        assert js.count(old) == 1, old
        js = js.replace(old, new)
    js_path.write_bytes(js.encode('utf-8'))

    spec = {
        "_comment": "FICTIONAL fixture. Defects planted in static/css/index.css and static/js/index.js only; index.html is "
                    "unchanged. evals/check_fixtures.py checks that the audit reports each audit_id (run in CI); eval 16 "
                    "(Polish) is graded against the fixes. Keep outside any agent's working folder.",
        "serve": "preview_server.py --root docs --base quillwave",
        "defects": [{"id": i, "defect": d, "detected_by": f"audit: [{a}]" if a else "looking at the screenshots",
                     **({"audit_id": a} if a else {}), "fix": f} for i, d, a, f in DEFECTS],
    }
    Path(str(out) + '.defects.json').write_bytes((json.dumps(spec, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    print(f'{out}: {len(DEFECTS)} defects in index.css and index.js; index.html unchanged')


if __name__ == '__main__':
    main()
