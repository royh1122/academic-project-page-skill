# Quillwave kit generator (FICTIONAL synthetic test material)

Builds three self-contained materials folders for testing a project-page skill:
`../kits/V1` (accepted paper, all links), `../kits/V2` (research in preparation),
`../kits/V3` (final-year project with a verified award). Every number comes from `numbers.json`.
Trap answers and SHA-256 manifests go to `expected/` and never into a kit.

    python build.py            # clean build of V1, V2, V3 (about 90 s)
    python build.py --variant V1 --award --out ../kits-award   # V1 whose acceptance e-mail also announces a best paper award (eval 7); answers in expected/V1-award.json
    python verify.py           # ffprobe, pdftotext numbers, metadata, traps, links, name scan, sizes

Needs: Python 3 with numpy, Pillow, opencv-python; ffmpeg/ffprobe; pdflatex, pdftoppm (MiKTeX or
TeX Live); pdftotext/pdfinfo/pdffonts for verify.py. Layout: `lib/` (content, latex, images,
fields, plot, video, traps), `narration/script.json` (caption script, no speech),
`variants/V*/` (overlay.json, prompt.txt), `fonts/` (Latin Modern Sans + GUST Font License).

Licence: generated kits CC0 1.0; Latin Modern fonts under the GUST Font License
(`fonts/GUST-FONT-LICENSE.txt`, copyright notice in `fonts/README-Latin-Modern-excerpt.txt`).
