"""Shared paths, numbers, fonts, subprocess, file-writing and LaTeX helpers for the H1 kit.

Copied from ../generator/lib (common.py, plot.py, latex.py) rather than imported: those modules load the
Quillwave numbers at import and stamp Quillwave metadata into images. Fonts are read from ../generator/fonts.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageFont, PngImagePlugin

GEN = Path(__file__).resolve().parent.parent
EVAL_KIT = GEN.parent
NUM = json.loads((GEN / "numbers.json").read_text(encoding="utf-8"))
P = NUM["project"]
MARK = P["fictional_marker"]
FONT_DIR = EVAL_KIT / "generator" / "fonts"
FONT_REG = FONT_DIR / "lmsans10-regular.otf"
FONT_BOLD = FONT_DIR / "lmsans10-bold.otf"
PEOPLE = {p["key"]: p for p in NUM["people"]}
INST = NUM["institutions"]

# Fixed timestamp for byte-stable PDFs (2026-10-01T00:00:00Z), as in the Quillwave generator.
EPOCH = 1790812800
ENV = dict(os.environ, SOURCE_DATE_EPOCH=str(EPOCH), FORCE_SOURCE_DATE="1")

_font_cache = {}


def font(size, bold=False):
    key = (int(size), bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), int(size))
    return _font_cache[key]


def tool(name):
    p = shutil.which(name)
    if not p:
        raise SystemExit(f"required tool not found on PATH: {name}")
    return p


def run(cmd, cwd=None, what=None):
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, env=ENV,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print((r.stdout or "")[-3000:])
        print((r.stderr or "")[-3000:])
        raise SystemExit(f"command failed: {what or cmd[0]}")
    return r.stdout


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=2, ensure_ascii=False))


# The fictional marker goes into metadata only, as in the Quillwave kits.
def save_png(img, path, colors=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if colors:
        img = img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                          dither=Image.Dither.NONE)
    info = PngImagePlugin.PngInfo()
    info.add_text("Comment", MARK)
    info.add_text("Description", "FICTIONAL synthetic test material (Paperwren kit, H1)")
    info.add_text("Copyright", "CC0 1.0 Universal")
    img.save(path, pnginfo=info, optimize=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def canvas(w, h, S=2, bg="white"):
    return Image.new("RGB", (w * S, h * S), bg)


def finish(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def compile_tex(tex_path, outdir, runs=2):
    """Compile tex_path (cwd = its folder, so relative \\graphicspath works); PDF lands in outdir."""
    tex_path = Path(tex_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pdflatex = tool("pdflatex")
    for _ in range(runs):
        run([pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={outdir}", tex_path.name],
            cwd=tex_path.parent, what=f"pdflatex {tex_path.name}")
    return outdir / (tex_path.stem + ".pdf")


def fmt(n):
    """12384 -> '12,384'."""
    return f"{n:,}"
