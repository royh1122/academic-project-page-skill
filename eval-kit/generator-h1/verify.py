"""Verify the held-out H1 kit: PDF numbers and marker, image metadata, the planted count disagreements,
trap files, link domains, a real-world-name scan and the size budget.

    python verify.py [--kit DIR]
Exit code 1 if any check fails.
"""
import argparse
import ast
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib.common import MARK, NUM, fmt  # noqa: E402
from PIL import Image  # noqa: E402

FAIL = []
V10, V11 = NUM["splits"]["v1_0"], NUM["splits"]["v1_1"]
# Files where the v1.0 counts are allowed, because they are labelled as v1.0 there (trap C).
V10_ALLOWED = {"paper/paper.pdf", "release/CHANGELOG.md", "README.md"}


def ok(cond, msg):
    print(("  ok    " if cond else "  FAIL  ") + msg)
    if not cond:
        FAIL.append(msg)


def sh(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True)
    return (r.stdout + r.stderr).decode("utf-8", errors="replace")


def real_names():
    """The real-world name patterns of the Quillwave verify.py, read without importing it."""
    src = (HERE.parent / "generator" / "verify.py").read_text(encoding="utf-8")
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "REAL":
            return ast.literal_eval(node.value)
    raise SystemExit("REAL list not found in generator/verify.py")


def texts(kit):
    out = {}
    for f in sorted(kit.rglob("*")):
        rel = f.relative_to(kit).as_posix()
        if f.suffix == ".pdf":
            out[rel] = sh(["pdftotext", "-enc", "UTF-8", "-layout", f, "-"])
        elif f.is_file() and f.suffix not in (".png",):
            out[rel] = f.read_text(encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", default=str(HERE.parent / "kits-held-out" / "H1"))
    kit = Path(ap.parse_args().kit)
    files = sorted(f for f in kit.rglob("*") if f.is_file())
    tot = sum(f.stat().st_size for f in files)
    print(f"=== H1: {len(files)} files, {tot / 1e6:.2f} MB")
    T = texts(kit)

    print("-- paper")
    pdf = T["paper/paper.pdf"]
    flat = re.sub(r"\s+", " ", pdf)
    want = [fmt(V10[k]) for k in ("train", "val", "test", "total")] + ["84.6", "71.9", str(NUM["annotators"]["count"])]
    want += [p["name"] for p in NUM["people"]]
    missing = [w for w in want if w not in flat]
    fonts = sh(["pdffonts", kit / "paper/paper.pdf"]).splitlines()[2:]
    non_lm = [l.split()[0] for l in fonts if l.strip() and "+LM" not in l.split()[0]]
    info = sh(["pdfinfo", kit / "paper/paper.pdf"])
    ok(not missing and MARK in flat and "FICTIONAL" in info and not non_lm,
       f"paper.pdf: v1.0 counts, results and all 8 author names present; marker, metadata, Latin Modern only"
       + (f"; MISSING {missing}" if missing else "") + (f"; non-LM {non_lm}" if non_lm else ""))

    print("-- image metadata")
    for f in files:
        if f.suffix == ".png":
            ok(Image.open(f).info.get("Comment") == MARK, f"{f.relative_to(kit).as_posix()}: fictional marker")

    print("-- counts (trap C and D are the only disagreements)")
    splits = {r["split"]: int(r["forms"]) for r in csv.DictReader(open(kit / "datasheet/splits.csv", encoding="utf-8"))}
    ok(sum(splits.values()) == V11["total"], f"splits.csv sums to the v1.1 total {fmt(V11['total'])}")
    fam = [int(r["forms_v1.1"]) for r in csv.DictReader(open(kit / "datasheet/layout_families.csv", encoding="utf-8"))]
    ok(sum(fam) == V11["total"], "layout_families.csv sums to the v1.1 total")
    stray = [(rel, n) for rel, t in T.items() for n in (fmt(V10["total"]), fmt(V10["test"]))
             if n in t and rel not in V10_ALLOWED]
    ok(not stray, f"v1.0 counts appear only in {sorted(V10_ALLOWED)}" + (f": {stray}" if stray else ""))
    lines = [l for l in T["leaderboard/leaderboard.csv"].splitlines() if l and not l.startswith("#")]
    rows = list(csv.DictReader(lines))
    ok([[r["model"], r["test_split"], float(r["f1"]), r["submitted"]] for r in rows] == NUM["leaderboard"]["rows"],
       "leaderboard.csv matches numbers.json")
    b10 = max(float(r["f1"]) for r in rows if r["test_split"] == "v1.0")
    b11 = max(float(r["f1"]) for r in rows if r["test_split"] == "v1.1")
    ok(b10 > b11, f"best v1.0 row ({b10}) beats best v1.1 row ({b11}), so trap D can catch a ranking claim")

    print("-- traps (from expected/H1.json)")
    exp = json.loads((HERE / "expected" / "H1.json").read_text(encoding="utf-8"))
    for t in exp["traps"]:
        miss = [p for p in t["files"] if not (kit / p).exists()]
        ok(not miss, f"{t['id']} {t['trap']}: {', '.join(t['files'])}")
    man = {f.relative_to(kit).as_posix() for f in files}
    ok(man == set(exp["manifest"]), "expected/H1.json manifest lists exactly the kit's files")

    print("-- link domains and real-world names")
    bad = set()
    for rel, t in T.items():
        if rel in ("LICENSE.md", "LICENSE-FONTS.txt"):
            continue
        for u in re.findall(r"https?://[^\s)\"'>}]+", t):
            if not re.match(r"https?://([a-z0-9-]+\.)*example\.org", u):
                bad.add((rel, u))
        for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", t):
            if not (m.endswith(".invalid") or m.endswith("example.org")):
                bad.add((rel, m))
    ok(not bad, "all URLs on example.org, all e-mails on .invalid or example.org" + (f": {sorted(bad)[:8]}" if bad else ""))
    hits = []
    for rel, t in T.items():
        if rel == "LICENSE-FONTS.txt":
            continue
        for pat in real_names():
            for m in re.finditer(pat if pat.startswith(r"\b") else r"\b" + pat + r"\b", t):
                # MIT is the code licence's name, not the institute.
                if m.group(0) == "MIT" and rel in ("code/LICENSE", "README.md"):
                    continue
                hits.append((rel, m.group(0), t[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
    for h in hits:
        print(f"  hit   {h[0]}: '{h[1]}' ...{h[2]}...")
    ok(not hits, "real-world name scan")

    ok(tot <= 2e6, f"kit size {tot / 1e6:.2f} MB within the 2 MB budget")
    print(f"\n{'ALL CHECKS PASSED' if not FAIL else f'{len(FAIL)} FAILURES'}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
