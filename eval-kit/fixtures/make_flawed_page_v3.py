"""Build the third flawed-page fixture (flawed-v3): layout, motion and serving defects for the audit checks added in 1.4.0.

    python make_flawed_page_v3.py <clean docs/ folder built from kit V1 with the 1.3.0+ template> [--out flawed-v3]

flawed-v1 holds mechanical defects, flawed-v2 visual and judgement defects. flawed-v3 holds defects that only show when the
page is scrolled, tabbed through, tapped, or viewed with reduced motion: a fixed header that hides headings after an
in-page jump, an abstract cut off by a fixed-height box, text a scroll-reveal never shows, keyboard focus under a fixed banner, tiny
crowded carousel dots, a blank band from an emptied video wrapper, an off-centre section, a dev-server script left in the
page, a doubled <body>, and a logo on top of a heading. Each edit is plausible for a real page and has a clear fix that leaves the content unchanged.
The defect list is written next to the fixture as <out>.defects.json (with the audit id that must report each defect) and
must stay out of the agent's working folder. Serve under a repository subpath (preview_server.py --root docs --base quillwave).
"""
import argparse
import json
import re
import shutil
from pathlib import Path

# (id, defect, audit id, the clean fix)
DEFECTS = [
    ("W1", "A fixed 56 px lab header bar was added with body padding but no scroll-padding-top, so every Contents jump lands its section heading under the bar",
     "anchor-covered", "Add html { scroll-padding-top: 56px } (or stop fixing the bar)"),
    ("W2", "The abstract was squeezed into a box with max-height: 180px and overflow: hidden (a read-more without the button), so most of it is cut off",
     "text-clipped", "Remove the max-height and overflow so the whole abstract shows"),
    ("W3", "Limitations fades in with a scroll-reveal whose script only runs when reduced motion is off, so reduced-motion visitors never see the limitations",
     "hidden-reduced-motion", "Show .reveal content by default and apply the fade only under prefers-reduced-motion: no-preference, or remove the reveal"),
    ("W4", "A fixed announcement banner at the bottom of the screen covers controls that keyboard focus scrolls to",
     "focus-covered", "Add html { scroll-padding-bottom } equal to the banner's height, or make the banner part of the page flow"),
    ("W5", "Carousel dots shrunk to 8 x 8 px with 4 px between them (a tweak to make them look smaller)",
     "target-small", "Restore the dots' 28 x 44 px hit area (keep a small visible dot inside it)"),
    ("W6", "An empty 16:9 video wrapper left after the YouTube iframe was removed leaves a blank band in Qualitative Results",
     "blank-band", "Delete the empty wrapper"),
    ("W7", "The Results section's container was given margin-left: 3rem, so the section sits off-centre",
     "margin-uneven", "Remove the margin-left so the container is centred like the others"),
    ("W8", "A Vite client script tag left from saving the page from a dev server (it also 404s under the repository subpath)",
     "dev-server", "Delete the script tag and audit the built page"),
    ("W10", "A lab logo placed with position: absolute at the top left of the Method section, on top of the Method heading",
     "text-covered", "Remove the logo or move it out of the heading's way (for example into the footer)"),
    ("W9", "The opening <body> and skip link appear twice (a doubled template block), so two 'Skip to main content' links exist",
     "malformed-source", "Delete the second <body> line and the second skip link"),
]

HEAD_EXTRA = """  <script type="module" src="/@vite/client"></script>
  <style>
    body { padding-top: 56px; }
    .lab-bar { position: fixed; top: 0; left: 0; right: 0; z-index: 20; height: 56px; display: flex; align-items: center;
      padding: 0 1.5rem; background: #1e293b; color: #f8fafc; font-weight: 600; }
    .announce { position: fixed; bottom: 0; left: 0; right: 0; z-index: 20; padding: .75rem 1.5rem; text-align: center;
      background: #fef3c7; color: #7c4a03; font-weight: 600; }
    .reveal { opacity: 0; transition: opacity .6s ease; }
    .reveal.is-visible { opacity: 1; }
    .carousel-dot { width: 8px; height: 8px; margin: 0 2px; }
    .carousel-dot::before { width: 8px; height: 8px; }
  </style>
</head>"""

BODY_START = """<body>

<a class="skip-link" href="#main-content">Skip to main content</a>
"""

REVEAL_SCRIPT = """<script>
  // Fade sections in as they scroll into view.
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver(entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('is-visible'); }));
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  }
</script>
</body>"""


def replace_once(text, old, new, what):
    if text.count(old) != 1:
        raise SystemExit(f'{what}: expected the anchor text exactly once, found {text.count(old)}: {old[:60]!r}')
    return text.replace(old, new)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('clean', type=Path)
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('flawed-v3'))
    args = parser.parse_args()

    if args.out.exists():
        shutil.rmtree(args.out)
    shutil.copytree(args.clean, args.out / 'docs')
    page = args.out / 'docs' / 'index.html'
    html = page.read_text(encoding='utf-8')

    html = replace_once(html, '</head>', HEAD_EXTRA, 'W8 and styles')
    html = replace_once(html, BODY_START, BODY_START + '\n<header class="lab-bar">Example University (fictional) · Imaginary Sciences Lab</header>\n'
                        + '<div class="announce">Accepted at FCSV 2026 (fictional).</div>\n\n' + BODY_START, 'W1, W4, W9')
    # W2: the abstract cut down to a fixed-height box with no way to expand it.
    abstract = html.index('<h2 class="title is-3">Abstract</h2>')
    html = html[:abstract] + replace_once(html[abstract:], '<div class="content has-text-justified">',
                                          '<div class="content has-text-justified" style="max-height: 180px; overflow: hidden">', 'W2')
    # W3: Limitations behind a scroll-reveal.
    limitations = html.index('<h2 class="title is-3">Limitations</h2>')
    html = html[:limitations] + replace_once(html[limitations:], '<div class="content">', '<div class="content reveal">', 'W3')
    html = replace_once(html, '</body>', REVEAL_SCRIPT, 'W3 script')
    # W6: an emptied video wrapper at the end of Qualitative Results.
    qualitative = re.search(r'<h2 class="title is-3">Qualitative[^<]*</h2>', html).start()
    end = html.index('</section>', qualitative)
    close = html.rindex('  </div>\n', qualitative, end)
    html = html[:close] + '    <div class="video-wrapper" style="position: relative; padding-top: 56.25%"></div>\n' + html[close:]
    # W10: a logo positioned over the Method heading.
    method = html.index('<h2 class="title is-3">Method</h2>')
    start = html.rindex('<div class="container is-max-desktop">', 0, method)
    html = (html[:start] + '<div class="container is-max-desktop" style="position: relative">\n'
            + '    <img class="lab-logo" src="./static/images/favicon.svg" alt="" width="72" height="72" '
            + 'style="position: absolute; top: 0; left: 0; z-index: 2; background: #fff; border-radius: 12px">'
            + html[start + len('<div class="container is-max-desktop">'):])
    # W7: the Results container pushed right.
    results = html.index('<h2 class="title is-3">Results</h2>')
    start = html.rindex('<div class="container is-max-desktop">', 0, results)
    html = html[:start] + '<div class="container is-max-desktop" style="margin-left: 3rem">' + html[start + len('<div class="container is-max-desktop">'):]

    page.write_text(html, encoding='utf-8', newline='\n')
    spec = {
        '_comment': 'FICTIONAL fixture. Planted flaws for the 1.4.0 audit checks: evals/check_fixtures.py checks that the audit reports each audit_id (run in CI); eval 14 (Polish) is graded against the fixes. Keep outside any agent\'s working folder.',
        'serve': 'preview_server.py --root docs --base quillwave',
        'defects': [{'id': i, 'defect': d, 'detected_by': f'audit: [{a}]', 'audit_id': a, 'fix': f} for i, d, a, f in DEFECTS],
        'content_must_stay': ['Quillwave: Sparse-Sensor Reconstruction of Synthetic Ripple Fields', 'Limitations', 'Figure 2.'],
    }
    args.out.with_name(args.out.name + '.defects.json').write_bytes((json.dumps(spec, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    print(f'wrote {args.out} and {args.out.name}.defects.json ({len(DEFECTS)} defects)')


if __name__ == '__main__':
    main()
