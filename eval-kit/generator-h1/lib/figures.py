"""Figures and sample forms for the H1 kit, drawn with Pillow (draw at S x size, then downsample)."""
import random

from PIL import Image, ImageDraw

from .common import NUM, canvas, finish, font, save_png

S = 2
INK = (34, 58, 140)
FAM = NUM["families"]

# Field labels and synthetic values for the four sample forms (family index, fields).
SAMPLES = [
    (1, [("Card number", "LC-0417"), ("Reader", "M. Sampleton"), ("Branch", "North Annex"),
         ("Issued", "2026-03-02"), ("Expires", "2028-03-01"), ("Books allowed", "12")]),
    (2, [("Site", "Plot 7B"), ("Observer", "R. Testwood"), ("Date", "2026-04-18"), ("Weather", "light rain"),
         ("Birds counted", "23"), ("Water level (cm)", "41"), ("Notes", "fence broken near gate")]),
    (6, [("Visitor", "K. Mockridge"), ("Host", "Room 214"), ("Arrived", "09:40"), ("Left", "11:15"),
         ("Badge", "V-0093"), ("Purpose", "delivery")]),
    (11, [("Date", "2026-02-11"), ("Max temp", "7 C"), ("Min temp", "-2 C"), ("Rain (mm)", "3.5"),
          ("Wind", "NW, gusty"), ("Recorded by", "T. Fakely"), ("Checked", "yes")]),
]


def _hand(img, xy, text, size, seed):
    """Paste text as 'handwriting': ink colour, a small random tilt and baseline jitter."""
    rng = random.Random(seed)
    f = font(size)
    w = int(f.getlength(text)) + 20 * S
    h = int(size * 1.6)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((10 * S, h // 2), text, font=f, fill=INK + (235,), anchor="lm")
    layer = layer.rotate(rng.uniform(-3.5, 3.5), resample=Image.BICUBIC, expand=True)
    img.paste(layer, (xy[0], xy[1] - layer.height // 2 + rng.randint(-3, 3) * S), layer)


def sample_form(idx, path):
    fam_i, fields = SAMPLES[idx]
    W, H = 900, 1150
    img = canvas(W, H, S, "#d9dbe0")
    d = ImageDraw.Draw(img)
    # Scanned sheet, slightly off-square, on a grey scanner bed.
    d.rectangle([40 * S, 30 * S, (W - 40) * S, (H - 30) * S], fill="#fbfaf6", outline="#c9c6bd", width=2 * S)
    d.rectangle([40 * S, 30 * S, (W - 40) * S, 130 * S], fill="#2f3b52")
    d.text((70 * S, 80 * S), FAM[fam_i][0].upper(), font=font(34 * S, True), fill="white", anchor="lm")
    d.text(((W - 70) * S, 80 * S), f"Form {fam_i + 1:02d}", font=font(22 * S), fill="#c8d0e0", anchor="rm")
    y = 190
    for j, (label, value) in enumerate(fields):
        d.text((80 * S, y * S), label, font=font(22 * S, True), fill="#38404d", anchor="lm")
        d.line([(330 * S, (y + 22) * S), ((W - 80) * S, (y + 22) * S)], fill="#8f96a3", width=2 * S)
        _hand(img, (340 * S, y * S), value, 34 * S, seed=idx * 100 + j)
        y += 118
    d.text((80 * S, (H - 70) * S), "Synthetic form. Values are invented.", font=font(18 * S), fill="#8f96a3",
           anchor="lm")
    save_png(finish(img, W, H), path, colors=48)


def sample_grid(paths, out):
    tiles = [Image.open(p).convert("RGB").resize((450, 575), Image.LANCZOS) for p in paths]
    img = Image.new("RGB", (450 * 4 + 50, 575 + 20), "white")
    for i, t in enumerate(tiles):
        img.paste(t, (10 + i * 460, 10))
    save_png(img, out, colors=64)


def overview(path):
    W, H = 1600, 420
    img = canvas(W, H, S)
    d = ImageDraw.Draw(img)
    steps = ["Generate layout\nand values", "Fill in\nby hand", "Scan", "Label twice\nand check",
             "Split into train,\nvalidation, test"]
    bw, gap, top = 250, 62, 110
    x = 40
    for i, s in enumerate(steps):
        fill = "#e8eefb" if i < 4 else "#2f3b52"
        txt = "#1d2738" if i < 4 else "white"
        d.rounded_rectangle([x * S, top * S, (x + bw) * S, (top + 200) * S], radius=18 * S, fill=fill,
                            outline="#2f3b52", width=3 * S)
        d.multiline_text(((x + bw / 2) * S, (top + 100) * S), s, font=font(26 * S, True), fill=txt,
                         anchor="mm", align="center", spacing=8 * S)
        if i < len(steps) - 1:
            ax = x + bw + 8
            d.line([(ax * S, (top + 100) * S), ((ax + gap - 22) * S, (top + 100) * S)], fill="#2f3b52",
                   width=5 * S)
            d.polygon([((ax + gap - 10) * S, (top + 100) * S), ((ax + gap - 26) * S, (top + 88) * S),
                       ((ax + gap - 26) * S, (top + 112) * S)], fill="#2f3b52")
        x += bw + gap
    d.text((40 * S, 50 * S), "Paperwren pipeline", font=font(30 * S, True), fill="#1d2738", anchor="lm")
    save_png(finish(img, W, H), path, colors=48)


def _thumb(d, x, y, w, h, kind):
    """A tiny schematic of a layout family: varies rows, columns and boxes by kind."""
    d.rectangle([x, y, x + w, y + h], fill="#e9ecf2")
    d.rectangle([x, y, x + w, y + 22 * S], fill="#6f86c6")
    rng = random.Random(kind)
    cols = 1 + kind % 3
    rows = 4 + kind % 4
    cw = (w - 20 * S) / cols
    for c in range(cols):
        for r in range(rows):
            yy = y + 36 * S + r * (h - 50 * S) / rows
            xx = x + 10 * S + c * cw
            ln = cw * rng.uniform(0.55, 0.9)
            d.line([(xx, yy), (xx + ln, yy)], fill="#9aa3b5", width=3 * S)
    if kind % 4 == 0:
        d.rectangle([x + 10 * S, y + h - 46 * S, x + w - 10 * S, y + h - 10 * S], outline="#6f86c6", width=2 * S)


def layout_gallery(path):
    """Dark-background gallery of the twelve families (a dark figure on purpose)."""
    W, H = 1600, 1000
    img = canvas(W, H, S, "#14161c")
    d = ImageDraw.Draw(img)
    tw, th = 330, 230
    for i, (name, _) in enumerate(FAM):
        r, c = divmod(i, 4)
        x = 60 + c * (tw + 50)
        y = 50 + r * (th + 85)
        _thumb(d, x * S, y * S, tw * S, th * S, i)
        d.text(((x + tw / 2) * S, (y + th + 30) * S), name, font=font(24 * S, True), fill="#dfe4ee", anchor="mm")
    save_png(finish(img, W, H), path, colors=48)


def _hbars(path, title, items, unit_fmt, color, W=1400, xmax=None):
    H = 120 + 52 * len(items)
    img = canvas(W, H, S)
    d = ImageDraw.Draw(img)
    d.text((40 * S, 45 * S), title, font=font(28 * S, True), fill="#1d2738", anchor="lm")
    left, right = 380, W - 140
    xmax = xmax or max(v for _, v in items)
    for i, (label, v) in enumerate(items):
        y = 100 + i * 52
        d.text(((left - 16) * S, (y + 18) * S), label, font=font(22 * S), fill="#333", anchor="rm")
        x1 = left + (right - left) * v / xmax
        d.rectangle([left * S, (y + 4) * S, x1 * S, (y + 32) * S], fill=color)
        d.text(((x1 + 10) * S, (y + 18) * S), unit_fmt(v), font=font(22 * S, True), fill="#1d2738", anchor="lm")
    save_png(finish(img, W, H), path, colors=48)


def family_counts(path):
    _hbars(path, "Forms per layout family (v1.1)", [(n, c) for n, c in FAM], lambda v: f"{v:,}", "#5574c4")


def leaderboard_chart(path):
    rows = [(m, f) for m, v, f, _ in NUM["leaderboard"]["rows"] if v == "v1.1"]
    _hbars(path, "Field-level F1 (%) on the v1.1 test split", rows, lambda v: f"{v:.1f}", "#2f8f7a", xmax=100)
