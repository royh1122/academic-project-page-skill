"""Shared paths, numbers, fonts, subprocess and file-writing helpers.

Windows notes (from the prototype): always decode subprocess output as UTF-8
explicitly (the console code page may be cp950); MiKTeX prints an update nag on
stderr, so only the return code decides success.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageFont, PngImagePlugin

GEN = Path(__file__).resolve().parent.parent
SYN = GEN.parent
NUM = json.loads((GEN / "numbers.json").read_text(encoding="utf-8"))
P = NUM["project"]
MARK = P["fictional_marker"]
FONT_DIR = GEN / "fonts"
FONT_REG = FONT_DIR / "lmsans10-regular.otf"
FONT_BOLD = FONT_DIR / "lmsans10-bold.otf"

# Fixed timestamp for byte-stable PDFs and zip entries (2026-10-01T00:00:00Z).
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


# ------------------------------------------------------------- image savers
# The fictional marker goes into metadata only (owner decision: no visible corner text).
def save_png(img, path, colors=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if colors:
        img = img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                          dither=Image.Dither.NONE)
    info = PngImagePlugin.PngInfo()
    info.add_text("Comment", MARK)
    info.add_text("Description", "FICTIONAL synthetic test material (Quillwave kit)")
    info.add_text("Copyright", "CC0 1.0 Universal")
    img.save(path, pnginfo=info, optimize=True)


def save_jpg(img, path, quality=85):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exif = Image.Exif()
    exif[0x010E] = MARK              # ImageDescription
    exif[0x8298] = "CC0 1.0 Universal"  # Copyright
    img.convert("RGB").save(path, quality=quality, optimize=True, comment=MARK,
                            exif=exif.tobytes(), subsampling="4:2:0")


def save_gif(frames, path, fps):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pal = [f.convert("RGB").quantize(colors=48, method=Image.Quantize.MEDIANCUT,
                                     dither=Image.Dither.NONE) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=int(1000 / fps),
                loop=0, optimize=True, comment=MARK, disposal=1)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
