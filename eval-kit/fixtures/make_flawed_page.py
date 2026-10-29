"""Build the flawed-page fixture for evals 4 (polish) and 5 (audit only).

    python make_flawed_page.py <clean docs/ folder built from kit V1> [--out flawed-v1]

Copies a clean, audited page and injects the known defects below, one edit each. The defect list is written
next to the fixture as <out>.defects.json and must stay out of the agent's working folder. Serve the fixture
under a repository subpath (preview_server.py --base quillwave) so the root-absolute path defect shows.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

# Content clean-up of the source page first, so the fixture's text is correct and only the defects differ.
CLEANUP = [
    (r" ?The gap between Quillwave and the baselines grows with fewer sensors\.", ""),
    (r"jittered 8&times;8 layout", "regular 8&times;8 grid"),
]

DEFECTS = [
    ("D1", "Font request loads Inter at 400 only, so headings, buttons and the title render synthesized bold",
     r"family=Inter:wght@400;500;600;700;800", "family=Inter:wght@400", "audit: synthesized bold"),
    ("D2", "Method paragraph indented 2.5rem under the full-width figure (two left edges)",
     r'<p class="measure">The 64 sensors sit', '<p class="measure" style="margin-left: 2.5rem">The 64 sensors sit',
     "audit: left edges"),
    ("D3", "Results panel image has square corners while other media are rounded",
     r'<img src="\./static/images/results_panels\.png"', '<img style="border-radius: 0" src="/static/images/results_panels.png"',
     "audit: corner radii"),
    ("D4", "Results panel image uses a root-absolute path (/static/...), which breaks under a repository subpath",
     None, None, "audit: missing resource (same edit as D3)"),
    ("D5", "Footer Nerfies link in a light blue that fails contrast",
     r'<a href="https://nerfies\.github\.io">', '<a href="https://nerfies.github.io" style="color: #9db4d6">',
     "audit: contrast"),
    ("D6", "Qualitative grid image has no alt text",
     r'(<img src="\./static/images/qualitative_grid\.jpg") alt="[^"]*"', r"\1", "audit: image without alt"),
    ("D7", "Teaser loop lost playsinline and its poster frame",
     r'<video autoplay muted loop playsinline controls preload="metadata"\s+width="960" height="360"\s+poster="[^"]+"',
     '<video autoplay muted loop controls preload="metadata"\n               width="960" height="360"',
     "audit: video warnings"),
    ("D8", "Placeholder Data button left from the template",
     r'(<span>Code</span>\s*</a>)',
     r'\1\n          <a href="[INSERT DATASET URL]" class="external-link button is-normal is-rounded is-dark">\n'
     r'            <span class="icon" aria-hidden="true"><i class="fas fa-database"></i></span>\n'
     r'            <span>Data</span>\n          </a>',
     "audit: placeholder"),
    ("D9", "The pipeline figure appears a second time in Comparison Clips",
     r'(<h2 class="title is-3">Comparison Clips</h2>)',
     r'\1\n      <figure class="figure-block"><img src="./static/images/overview.png" alt="Quillwave pipeline" '
     r'width="1564" height="488"></figure>',
     "audit: repeated image"),
    ("D10", "Limitations heading demoted to h4 (skips heading levels)",
     r'<h2 class="title is-3">Limitations</h2>', '<h4 class="title is-3">Limitations</h4>',
     "audit: heading order"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "flawed-v1"))
    args = ap.parse_args()
    src, out = Path(args.source).resolve(), Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out / "docs")
    page = out / "docs" / "index.html"
    html = page.read_text(encoding="utf-8")
    for pattern, repl in CLEANUP:
        html = re.sub(pattern, repl, html)
    for did, _, pattern, repl, _ in DEFECTS:
        if pattern is None:
            continue
        html, n = re.subn(pattern, repl, html, count=1)
        assert n == 1, f"{did}: pattern not found"
    page.write_text(html, encoding="utf-8")
    defects = [{"id": d, "defect": text, "detected_by": how} for d, text, _, _, how in DEFECTS]
    Path(str(out) + ".defects.json").write_text(json.dumps({
        "_comment": "FICTIONAL fixture. Grading notes for evals 4 and 5; keep outside the agent's working folder.",
        "serve": "preview_server.py --root docs --base quillwave",
        "defects": defects,
        "content_must_stay": ["Quillwave", "FCSV 2026", "29.46", "Limitations", "BibTeX"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"fixture: {out}  defects: {len(defects)}")


if __name__ == "__main__":
    main()
