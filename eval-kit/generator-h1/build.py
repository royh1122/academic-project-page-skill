"""Build the FICTIONAL held-out Paperwren kit (H1).

    python build.py              # clean build into ../kits-held-out/H1
    python build.py --out DIR    # kits root (default: ../kits-held-out)

Needs Python 3 with Pillow, and pdflatex (MiKTeX or TeX Live). Expected answers and the SHA-256 manifest go to
generator-h1/expected/H1.json, never into the kit. Held out: run it, never tune the skill to it.
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lib import content as C  # noqa: E402
from lib import figures as F  # noqa: E402
from lib import paper as L  # noqa: E402
from lib.common import FONT_DIR, NUM, P, compile_tex, sha256, write_json, write_text  # noqa: E402
from lib.traps import GRADE_BY_HAND, catalogue, must_not_contain  # noqa: E402

BUILD = HERE / "_build"
PROMPT = (f"Make a project page for our dataset paper \"{P['title']}\" from the materials in this folder, in docs/. "
          "Corresponding author: Oskar Esimerkki.")


def check_numbers():
    for rel in ("v1_0", "v1_1"):
        s = NUM["splits"][rel]
        assert s["train"] + s["val"] + s["test"] == s["total"], rel
    assert sum(c for _, c in NUM["families"]) == NUM["splits"]["v1_1"]["total"]
    assert NUM["splits"]["v1_0"]["test"] - NUM["splits"]["v1_1"]["test"] == NUM["splits"]["removed_near_duplicates"]


def build(kit):
    if kit.exists():
        shutil.rmtree(kit)
    write_text(kit / "FICTIONAL.md", C.fictional_md())
    write_text(kit / "LICENSE.md", C.license_md())
    write_text(kit / "LICENSE-FONTS.txt",
               "Latin Modern fonts (used for all rendered text in this folder) are distributed under the GUST "
               "Font License, reproduced verbatim below. No font files are included in this folder.\n\n"
               + (FONT_DIR / "GUST-FONT-LICENSE.txt").read_text(encoding="utf-8"))
    write_text(kit / "acceptance_email.txt", C.acceptance_email())
    write_json(kit / "links.json", C.links_json())
    write_text(kit / "press" / "blurb.md", C.press_blurb())
    write_text(kit / "access" / "ACCESS.md", C.access_md())
    write_text(kit / "access" / "DATA_TERMS_DRAFT.md", C.data_terms_draft())
    write_text(kit / "code" / "LICENSE", C.code_license())
    write_text(kit / "datasheet" / "DATASHEET.md", C.datasheet_md())
    write_text(kit / "datasheet" / "splits.csv", C.splits_csv())
    write_text(kit / "datasheet" / "layout_families.csv", C.families_csv())
    write_text(kit / "release" / "CHANGELOG.md", C.changelog())
    write_text(kit / "leaderboard" / "leaderboard.csv", C.leaderboard_csv())
    write_text(kit / "leaderboard" / "README.md", C.leaderboard_readme())
    write_text(kit / "data" / "README_DATA.md", C.readme_data())
    write_text(kit / "data" / "test_answers.jsonl", C.test_answers_jsonl())
    write_json(kit / "team" / "authors.json", C.authors_json())
    write_text(kit / "team" / "annotators.csv", C.annotators_csv())
    write_text(kit / "citation" / "paper.bib", C.paper_bib())
    write_text(kit / "citation" / "dataset.bib", C.dataset_bib())
    write_text(kit / "figures" / "CAPTIONS.md", C.captions_md())

    print("figures")
    fig = kit / "figures"
    samples = [kit / "data" / "samples" / f"sample_{i + 1:02d}.png" for i in range(len(F.SAMPLES))]
    for i, p in enumerate(samples):
        F.sample_form(i, p)
    F.sample_grid(samples, fig / "sample_forms.png")
    F.overview(fig / "overview.png")
    F.layout_gallery(fig / "layout_families.png")
    F.family_counts(fig / "family_counts.png")
    F.leaderboard_chart(fig / "leaderboard_v1_1.png")

    print("paper (pdflatex)")
    tdir = BUILD / "paper"
    (tdir / "figures").mkdir(parents=True, exist_ok=True)
    for f in ("overview.png", "sample_forms.png"):
        shutil.copyfile(fig / f, tdir / "figures" / f)
    write_text(tdir / "paper.tex", L.paper_tex())
    pdf = compile_tex(tdir / "paper.tex", tdir / "out")
    (kit / "paper").mkdir(exist_ok=True)
    shutil.copyfile(pdf, kit / "paper" / "paper.pdf")

    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in kit.iterdir())
    write_text(kit / "README.md", C.readme([(e, C.DESCR.get(e, "")) for e in entries]))


def write_expected(kit):
    files = sorted(p for p in kit.rglob("*") if p.is_file())
    manifest = {p.relative_to(kit).as_posix(): {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in files}
    exp = {
        "_comment": "FICTIONAL. Grading notes for the held-out kit; keep outside the kit so an agent under test "
                    "cannot read them. Held out: never tune the skill to this kit.",
        "variant": "H1", "name": "dataset-gated-benchmark",
        "description": "A gated dataset with a benchmark leaderboard, two releases and eight authors (Paperwren).",
        "prompt": PROMPT,
        "traps": catalogue(),
        "must_not_appear_on_page": must_not_contain(),
        "grade_by_hand": GRADE_BY_HAND,
        "final_numbers_source": "generator-h1/numbers.json",
        "total_bytes": sum(m["bytes"] for m in manifest.values()),
        "manifest": manifest,
    }
    write_json(HERE / "expected" / "H1.json", exp)
    return exp["total_bytes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parent / "kits-held-out"))
    out = Path(ap.parse_args().out).resolve()
    check_numbers()
    if BUILD.exists():
        shutil.rmtree(BUILD)
    build(out / "H1")
    tot = write_expected(out / "H1")
    print(f"done: H1 in {out}  total {tot / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
