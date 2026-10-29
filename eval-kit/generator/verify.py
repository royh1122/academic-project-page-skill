"""Verify the generated kits: videos (ffprobe), PDFs (pdftotext numbers + marker), image metadata,
trap files, link domains, real-world-name scan, and per-kit file sizes.

    python verify.py [--kits DIR]
Exit code 1 if any check fails.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib.common import MARK, NUM  # noqa: E402
from PIL import Image  # noqa: E402

FAIL = []


def ok(cond, msg):
    print(("  ok    " if cond else "  FAIL  ") + msg)
    if not cond:
        FAIL.append(msg)


def sh(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout + r.stderr


def probe(f):
    out = sh(["ffprobe", "-v", "error", "-show_entries",
              "stream=codec_type,codec_name,width,height,sample_aspect_ratio,pix_fmt,channels:format=duration:format_tags=comment",
              "-of", "json", f])
    return json.loads(out)


def check_video(f, rel):
    info = probe(f)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    v = vs[0]
    dur = float(info["format"]["duration"])
    sar = v.get("sample_aspect_ratio", "1:1")
    comment = info["format"].get("tags", {}).get("comment", "")
    V = NUM["videos"]
    if "results/loops" in rel:
        want = dict(size=tuple(V["loop_size"]), sar="1:1", dur=V["loop_seconds"], audio=False)
    elif "overview_explainer" in rel:
        want = dict(size=tuple(V["explainer_size"]), sar="1:1", dur=V["explainer_seconds"], audio=True)
    else:
        want = dict(size=tuple(V["demo_stored_size"]), sar=V["demo_sar"], dur=V["demo_seconds"], audio=False)
    desc = (f"{rel}: {v['codec_name']} {v['pix_fmt']} {v['width']}x{v['height']} SAR {sar} {dur:.3f}s "
            f"audio={'+'.join(a['codec_name'] for a in au) or 'none'}")
    good = (v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p" and (v["width"], v["height"]) == want["size"]
            and sar == want["sar"] and abs(dur - want["dur"]) < 0.1 and bool(au) == want["audio"] and comment == MARK)
    if au:
        vol = sh(["ffmpeg", "-hide_banner", "-i", f, "-vn", "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"mean_volume: (-?[\d.]+) dB.*?max_volume: (-?[\d.]+) dB", vol, re.S)
        desc += f" (mean {m.group(1)} dB, max {m.group(2)} dB)"
    ok(good, desc + ("" if comment == MARK else " [comment tag missing]"))


def required_numbers(rel):
    r = NUM["main_table"]["rows"]
    d = NUM["derived"]
    s = NUM["setup"]
    nums = [f"{x[1]:.2f}" for x in r] + [f"{x[2]:.3f}" for x in r] + [f"{x[3]:.1f}" for x in r]
    nums += [f"{d['psnr_gain_over_best_baseline_db']:.2f}", f"{d['relative_mse_reduction_pct']:.1f}",
             f"{d['speedup_vs_rbf']:.2f}", str(s["sensors"]), str(s["field_size"])]
    name = rel.rsplit("/", 1)[-1]
    if name in ("paper.pdf", "summary.pdf", "FYP_Final_Report.pdf"):
        nums += [f"{v:.2f}" for row in NUM["sensor_sweep"]["psnr_rows"] for v in row[1:]]
        nums += [str(c) for c in NUM["sensor_sweep"]["sensor_counts"]]
        nums += [str(s["test_fields"])]
    if name in ("paper.pdf", "FYP_Final_Report.pdf", "short_paper.pdf"):
        nums += [str(s["test_fields"]), str(s["train_fields"]), str(s["training_runs"])]
    return nums


def check_pdf(f, rel):
    txt = sh(["pdftotext", "-layout", f, "-"])
    flat = re.sub(r"\s+", " ", txt)
    nums = required_numbers(rel)
    missing = [n for n in nums if n not in flat]
    stale = [n for n in (f"{NUM['stale_draft']['psnr']:.2f}", f"{NUM['stale_draft']['ssim']:.3f}") if n in flat]
    info = sh(["pdfinfo", f])
    fonts = sh(["pdffonts", f]).splitlines()[2:]
    non_lm = [l.split()[0] for l in fonts if l.strip() and not re.search(r"\+LM", l.split()[0])]
    pages = re.search(r"Pages:\s+(\d+)", info).group(1)
    ok(not missing and not stale and MARK in flat and "FICTIONAL" in info and not non_lm,
       f"{rel}: {pages} pages, {len(nums)} numbers from numbers.json found"
       + (f", MISSING {missing}" if missing else "") + (f", STALE {stale}" if stale else "")
       + (f", non-LM fonts {non_lm}" if non_lm else ", fonts all Latin Modern")
       + ("" if MARK in flat else ", footer marker missing"))
    return flat


def check_image(f, rel):
    im = Image.open(f)
    meta = str(im.info.get("Comment", "")) + str(im.info.get("comment", b""))
    ok("Synthetic test material" in meta, f"{rel}: {im.size[0]}x{im.size[1]} {im.format}, marker in metadata")


# real-world names that must not appear (institutions, venues, datasets, companies, services, people)
REAL = [r"\bMIT\b", "Stanford", "Berkeley", "Harvard", "Oxford", "Cambridge", "Tokyo", "ETH", "Zurich", "KAIST",
        "Tsinghua", "Peking", "HKUST", "Hong Kong", "Waterloo", "Toronto", "Princeton", "Carnegie", "Caltech",
        "Imperial College", "SIGGRAPH", "CVPR", "ICCV", "ECCV", "NeurIPS", "ICML", "ICLR", "MICCAI", "AAAI", "IEEE",
        r"\bACM\b", "arXiv", "YouTube", "GitHub", "Google", "Microsoft", "Apple", "Meta", "NVIDIA", "OpenAI",
        "Anthropic", "Zira", "ImageNet", "COCO", "KITTI", "ShapeNet", "Nerfies", "Knuth", "Jackowski", "Nowacki",
        "Lovelace", r"\bTUG\b", "Polish", "Claude"]


def scan_text(kit):
    """Text of every file: text files directly, PDFs via pdftotext, binaries via printable strings."""
    out = {}
    for f in sorted(kit.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(kit).as_posix()
        if f.suffix in (".md", ".txt", ".csv", ".bib", ".json", ".vtt", ".tex"):
            out[rel] = f.read_text(encoding="utf-8")
        elif f.suffix == ".pdf":
            info = sh(["pdfinfo", f])
            keep = ("Title", "Subject", "Keywords", "Author", "Creator", "Producer")
            meta = " | ".join(l for l in info.splitlines() if l.split(":")[0] in keep)
            out[rel] = sh(["pdftotext", f, "-"]) + " | " + meta
        else:
            data = f.read_bytes()
            if f.suffix == ".zip":
                import zipfile
                with zipfile.ZipFile(f) as z:
                    data = b"".join(z.read(n) for n in z.namelist()) + "".join(z.namelist()).encode()
            out[rel] = " ".join(m.decode("latin-1") for m in re.findall(rb"[\x20-\x7e]{6,}", data))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kits", default=str(HERE.parent / "kits"))
    kits = Path(ap.parse_args().kits)
    grand = 0
    for kit in sorted(p for p in kits.iterdir() if p.is_dir()):
        vid = kit.name
        print(f"\n=== {vid}")
        files = sorted(f for f in kit.rglob("*") if f.is_file())
        tot = sum(f.stat().st_size for f in files)
        grand += tot
        print(f"-- files ({len(files)}, {tot / 1e6:.2f} MB)")
        for f in files:
            print(f"  {f.stat().st_size:>9,}  {f.relative_to(kit).as_posix()}")
        print("-- videos")
        for f in files:
            if f.suffix == ".mp4":
                check_video(f, f.relative_to(kit).as_posix())
        print("-- PDFs")
        for f in files:
            if f.suffix == ".pdf":
                check_pdf(f, f.relative_to(kit).as_posix())
        print("-- image metadata")
        for f in files:
            if f.suffix in (".png", ".jpg", ".gif"):
                check_image(f, f.relative_to(kit).as_posix())
        print("-- traps (from generator/expected)")
        exp = json.loads((HERE / "expected" / f"{vid}.json").read_text(encoding="utf-8"))
        for t in exp["traps"]:
            miss = [p for p in t["files"] if not (kit / p).exists()]
            ok(not miss, f"{t['id']} {t['trap']}: {', '.join(t['files'])}")
        print("-- link domains and real-world names")
        texts = scan_text(kit)
        bad_urls = set()
        for rel, txt in texts.items():
            if rel == "LICENSE-FONTS.txt" or rel == "LICENSE.md":
                continue
            for u in re.findall(r"https?://[^\s)\"'>}]+", txt):
                if not re.match(r"https?://([a-z0-9-]+\.)*example\.org", u):
                    bad_urls.add((rel, u))
            for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", txt):
                if not (m.endswith(".invalid") or m.endswith("example.org")):
                    bad_urls.add((rel, m))
        ok(not bad_urls, "all URLs on example.org and all e-mails on .invalid/example.org (licence files excepted)"
           + (f": {sorted(bad_urls)[:8]}" if bad_urls else ""))
        hits = []
        for rel, txt in texts.items():
            for pat in REAL:
                for m in re.finditer(pat if pat.startswith(r"\b") else r"\b" + pat + r"\b", txt):
                    hits.append((rel, m.group(0), txt[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
        allowed = [h for h in hits if h[0] == "LICENSE-FONTS.txt"]
        other = [h for h in hits if h[0] != "LICENSE-FONTS.txt"]
        for h in allowed:
            print(f"  note  {h[0]}: '{h[1]}' (verbatim GUST Font License text) ...{h[2]}...")
        for h in other:
            print(f"  hit   {h[0]}: '{h[1]}' ...{h[2]}...")
        ok(not other, f"real-world name scan over {len(texts)} files ({len(REAL)} patterns)")
    print(f"\nTOTAL all kits: {grand / 1e6:.2f} MB (target 6-8 MB, cap 10 MB)")
    ok(grand <= 10e6, "under 10 MB hard cap")
    print(f"\n{'ALL CHECKS PASSED' if not FAIL else f'{len(FAIL)} FAILURES'}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
