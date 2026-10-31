# Paperwren kit generator (H1, held out; FICTIONAL synthetic test material)

Builds `../kits-held-out/H1`, a materials folder for a gated dataset with a benchmark leaderboard: two releases (v1.0 and v1.1), eight authors at four institutions, a paper, a datasheet, a leaderboard export, sample forms, and access and licence notes. Every number comes from `numbers.json`. Trap answers and the SHA-256 manifest go to `expected/H1.json` and never into the kit.

    python build.py     # clean build (a few seconds); output is byte-identical on the same toolchain
    python verify.py    # PDF numbers and marker, image metadata, planted count disagreements, traps, links, name scan, size

Needs Python 3 with Pillow, and pdflatex, pdftotext, pdffonts and pdfinfo (MiKTeX or TeX Live, Poppler).

**Held out.** This kit checks that the skill generalises beyond the Quillwave kits. Run eval 15 once per behaviour release, with and without the skill. Never tune the skill to it: a failure here is fixed with a general rule, which is then confirmed on the core evals.

Kept separate from `../generator/` on purpose, so the Quillwave kits stay byte-identical. `lib/common.py` copies the few helpers it needs instead of importing them, because the Quillwave modules load Quillwave's numbers and stamp its metadata. The Latin Modern fonts are read from `../generator/fonts/`.

Licence: generated kit CC0 1.0; Latin Modern fonts under the GUST Font License.
