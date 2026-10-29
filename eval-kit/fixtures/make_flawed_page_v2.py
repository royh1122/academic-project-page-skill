"""Build the second flawed-page fixture (flawed-v2) for evals 9 (polish) and 10 (audit only).

    python make_flawed_page_v2.py <clean docs/ folder built from kit V1> [--out flawed-v2]

flawed-v1 holds mechanical defects the bundled audit catches. flawed-v2 holds visual and judgement defects that
show only when the rendered page is looked at (the audit's screenshots at 375, 768 and 1440 px). Each edit is
plausible for a real page and has a clear fix that leaves the content unchanged. The defect list is written
next to the fixture as <out>.defects.json and must stay out of the agent's working folder. Serve under a
repository subpath (preview_server.py --root docs --base quillwave).
"""
import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image

CLEANUP = [
    (r" ?The gap between Quillwave and the baselines grows with fewer sensors\.", ""),
    (r"jittered 8&times;8 layout", "regular 8&times;8 grid"),
]

# (id, defect, how it is detected, the clean fix)
DEFECTS = [
    ("V1", "Teaser image sits centred in a fixed 560 px tall grey box (max-height 100%, auto width), so empty bars show around the diagram (a large empty area around the diagram, worst at 375 px)",
     "audit: warning 'Teaser media letterboxed' at 375, 1024 and 1440 px; also visible in the screenshots (375 px worst)",
     "Remove the wrapper box and the inline sizing so the teaser fills the content width at its natural aspect ratio"),
    ("V2", "The dense six-panel results figure (with its caption) was made the teaser and the clear pipeline diagram was moved into the Method section; the Method text no longer says 'at the top'",
     "looking: 375 px, the first screen is unreadable panels; the audit does not flag it",
     "Put the results figure back in Results (zoomable) and open with a legible teaser that shows the main result (here a comparison clip or a clear result image), or the pipeline diagram"),
    ("V3", "A hand-inserted <br> in the title before the last word, so the title wraps with the single word 'Fields' alone on the last line (and a short line above it)",
     "looking: 1440 px, header",
     "Remove the <br> so the title wraps freely and balances"),
    ("V4", "Two tinted bands in a row (Abstract and Video) after a reorder; Method lost its tint, so the alternation is broken and the two bands read as one tall block",
     "looking: 1440 and 768 px, sections 2-3",
     "Make Video a plain section and Method a tinted one again, restoring alternation"),
    ("V5", "Third carousel clip given a square box (aspect-ratio 1/1, contain), so the carousel is as tall as the square and clips 1 and 2 leave a large blank gap under their captions, while clip 3 shows black side bars",
     "looking: 1440 px, Qualitative Results",
     "Remove the aspect-ratio and object-fit on clip 3 so all slides share the 8:3 shape and the carousel height fits"),
    ("V6", "Table 2 stretched to the full column width with numeric columns left-aligned (is-numeric removed), so numbers sit far from their headers and decimals do not line up",
     "looking: 1440 px, Results",
     "Let the table take its natural width and restore the is-numeric class so number columns are right-aligned"),
    ("V7", "Figure 2 caption lists the columns in the wrong order (linear and radial-basis swapped), so it no longer matches the figure",
     "looking: compare Figure 2 with its caption (1440 px)",
     "Restore the order in the figure: sensor map, linear interpolation, radial-basis interpolation, Quillwave, ground truth"),
    ("V8", "The explainer video's poster is a black frame, so the Video section shows a black rectangle before play",
     "looking: 1440 px and 375 px, Video",
     "Extract a representative frame from the MP4 (for example at 0:20, when the decoder is explained) and use it as the poster"),
    ("V9", "The Limitations section has doubled vertical padding (8 rem instead of 4 rem), an uneven rhythm",
     "looking: 1440 px, gap around Limitations",
     "Remove the inline padding so it matches the other sections"),
    ("V10", "Figure 2 uses a soft, upscaled copy of the figure (an old low-resolution export re-saved at 1640 px), so it is blurry at full width and in the zoom viewer; the sharp original sits unused beside it",
     "looking: 1440 px, Figure 2",
     "Point the image at the sharp qualitative_grid.jpg and delete the soft copy"),
]


def sub(html, pattern, repl, did, flags=0):
    html, n = re.subn(pattern, repl, html, count=1, flags=flags)
    assert n == 1, f"{did}: pattern not found"
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "flawed-v2"))
    args = ap.parse_args()
    src, out = Path(args.source).resolve(), Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out / "docs")
    docs = out / "docs"
    page = docs / "index.html"
    html = page.read_text(encoding="utf-8")
    for pattern, repl in CLEANUP:
        html = re.sub(pattern, repl, html)

    # V2 first (it moves the figures); V1 then acts on whatever sits in the teaser.
    teaser = re.search(r'<section class="hero teaser">.*?</section>', html, re.S).group(0)
    t_img = re.search(r"<img .*?>", teaser, re.S).group(0)
    t_cap = re.search(r'<figcaption class="teaser-caption">(.*?)</figcaption>', teaser, re.S).group(1)
    res = re.search(r'\n    <div class="content" data-zoom-context>\s*<figure class="figure-block">\s*'
                    r'(<img src="\./static/images/results_panels\.png".*?>)\s*<figcaption>(.*?)</figcaption>\s*</figure>\s*</div>',
                    html, re.S)
    r_img, r_cap = res.group(1).replace(' loading="lazy"', ""), res.group(2)
    html = html.replace(res.group(0), "")
    html = html.replace(teaser, teaser.replace(t_img, r_img).replace(t_cap, r_cap))
    method_fig = ('\n    <div class="content" data-zoom-context>\n      <figure class="figure-block">\n        '
                  + t_img + f'\n        <figcaption>{t_cap}</figcaption>\n      </figure>\n    </div>')
    html = sub(html, r'(<h2 class="title is-3">Method</h2>\s*<div class="content">\s*<p class="measure">.*?</p>\s*</div>)',
               lambda m: m.group(1) + method_fig, "V2", re.S)
    html = sub(html, r"As the pipeline diagram at the top shows,", "As the pipeline diagram shows,", "V2")

    # V1: letterboxed teaser.
    html = sub(html, r'(<section class="hero teaser">.*?<img )', r'\1style="height: 420px; object-fit: contain" ', "V1", re.S)

    # V3: hard line break in the title leaves one word alone on the last line.
    html = sub(html, r"Synthetic Ripple Fields</h1>", "Synthetic Ripple<br>Fields</h1>", "V3")

    # V4: two tinted bands in a row.
    html = sub(html, r'<section class="section">(\s*<div class="container is-max-desktop">\s*<div class="columns is-centered has-text-centered">\s*<div class="column is-four-fifths">\s*<h2 class="title is-3">Video)',
               r'<section class="section is-light">\1', "V4")
    html = sub(html, r'<section class="section is-light">(\s*<div class="container is-max-desktop">\s*<h2 class="title is-3">Method)',
               r'<section class="section">\1', "V4")

    # V5: a clip with another aspect ratio.
    html = sub(html, r'(<video muted loop playsinline controls preload="metadata" width="960" height="360")(\s*poster="\./static/images/loop3-poster\.jpg")',
               r'\1 style="aspect-ratio: 1 / 1; object-fit: contain; background: #000"\2', "V5")

    # V6: stretched table, left-aligned numbers (Table 2).
    html = sub(html, r'(<p class="table-caption" id="table-2-caption">.*?<table class=")table is-narrow is-numeric(">)',
               r'\1table is-narrow" style="width: 100%\2', "V6", re.S)

    # V7: caption names the wrong column order.
    html = sub(html, r"sensor map, linear interpolation, radial-basis interpolation, Quillwave \(ours\), ground truth\.</figcaption>",
               "sensor map, radial-basis interpolation, linear interpolation, Quillwave (ours), ground truth.</figcaption>", "V7")

    # V8: black poster frame for the explainer.
    Image.new("RGB", (854, 480), (6, 6, 8)).save(docs / "static/images/overview-poster.jpg", quality=80)

    # V9: doubled section padding.
    html = sub(html, r'<section class="section">(\s*<div class="container is-max-desktop">\s*<h2 class="title is-3">Limitations)',
               r'<section class="section" style="padding-top: 8rem; padding-bottom: 8rem">\1', "V9")

    # V10: soft upscaled copy shown in place of the sharp original, the full-resolution file left unused beside it.
    full = Image.open(docs / "static/images/qualitative_grid.jpg")
    small = full.resize((full.width // 4, full.height // 4), Image.LANCZOS)
    small.resize(full.size, Image.BICUBIC).save(docs / "static/images/qualitative_grid_v1.jpg", quality=85)
    html = sub(html, r'src="\./static/images/qualitative_grid\.jpg"', 'src="./static/images/qualitative_grid_v1.jpg"', "V10")

    page.write_text(html, encoding="utf-8")
    Path(str(out) + ".defects.json").write_text(json.dumps({
        "_comment": "FICTIONAL fixture. Grading notes for evals 9 and 10; keep outside the agent's working folder. "
                    "Defects are visual or judgement defects; the bundled audit is expected to pass or only warn.",
        "serve": "preview_server.py --root docs --base quillwave",
        "defects": [{"id": d, "defect": t, "detected_by": h, "fix": f} for d, t, h, f in DEFECTS],
        "content_must_stay": ["Quillwave", "FCSV 2026", "29.46", "Limitations", "BibTeX"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"fixture: {out}  defects: {len(DEFECTS)}")


if __name__ == "__main__":
    main()
