"""Raster figures: results panels, qualitative grid and tiles, dashboard screenshots."""
import numpy as np
from PIL import Image, ImageDraw

from . import fields as F
from .common import NUM, font, save_jpg, save_png
from .plot import COLORS, SHORT, Axes, canvas, finish

MT = NUM["main_table"]
SW = NUM["sensor_sweep"]
SEED = NUM["seeds"]
SCENE_SEEDS = [SEED["fields"] + i for i in range(4)]


def results_panels(path):
    W, H, S = 2400, 1400, 2
    img = canvas(W, H, S)
    sc = SW["sensor_counts"]
    pw, ph = 600, 400
    xs0 = [150, 950, 1750]
    ys0 = [110, 820]
    fs = 22
    # (a) PSNR vs sensors
    ax = Axes(img, (xs0[0], ys0[0], xs0[0] + pw, ys0[0] + ph), (12, 160), (14, 34), S, fs, xlog2=True)
    ax.frame(sc, range(14, 35, 4), xlabel="Number of sensors", ylabel="PSNR (dB)", title="(a) PSNR vs. sensors")
    for r in SW["psnr_rows"]:
        ax.line(sc, r[1:], COLORS[r[0]], 4 if "ours" in r[0] else 3)
    ax.legend([(SHORT[r[0]], COLORS[r[0]]) for r in reversed(SW["psnr_rows"])], (xs0[0] + 20, ys0[0] + 20), size=18)
    # (b) SSIM vs sensors
    ax = Axes(img, (xs0[1], ys0[0], xs0[1] + pw, ys0[0] + ph), (12, 160), (0.35, 1.0), S, fs, xlog2=True)
    ax.frame(sc, [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], yfmt="{:.1f}", xlabel="Number of sensors", ylabel="SSIM",
             title="(b) SSIM vs. sensors")
    for r in SW["ssim_rows"]:
        ax.line(sc, r[1:], COLORS[r[0]], 4 if "ours" in r[0] else 3)
    # (c) runtime bars
    ax = Axes(img, (xs0[2], ys0[0], xs0[2] + pw, ys0[0] + ph), (-0.6, 3.6), (0, 8), S, fs)
    ax.frame([], range(0, 9, 2), ylabel="Runtime (ms)", title="(c) Runtime per field")
    for i, (n, p, s, m) in enumerate(MT["rows"]):
        ax.bar(i, m, 0.6, COLORS[n], f"{m:.1f}", bold="ours" in n)
        ax.text((ax._tx(i), ax.y1 + 10 * S), SHORT[n].replace(" (ours)", "\n(ours)"), size=17, fill="#444", anchor="ma")
    # (d) error histogram (illustrative, seeded)
    rng = np.random.default_rng(SEED["panels"])
    e_ours = np.abs(rng.normal(0, 0.035, 20000))
    e_rbf = np.abs(rng.normal(0, 0.065, 20000))
    bins = np.linspace(0, 0.2, 21)
    ho, _ = np.histogram(e_ours, bins)
    hr, _ = np.histogram(e_rbf, bins)
    ho, hr = ho / ho.sum() * 100, hr / hr.sum() * 100
    ax = Axes(img, (xs0[0], ys0[1], xs0[0] + pw, ys0[1] + ph), (0, 0.2), (0, 40), S, fs)
    ax.frame([0, 0.05, 0.1, 0.15, 0.2], range(0, 41, 10), xfmt="{:.2f}", xlabel="Absolute error",
             ylabel="Pixels (%)", title="(d) Error histogram")
    for i in range(len(bins) - 1):
        c = (bins[i] + bins[i + 1]) / 2
        ax.bar(c - 0.0024, hr[i], 0.0044, COLORS["Radial-basis interpolation"])
        ax.bar(c + 0.0024, ho[i], 0.0044, COLORS["Quillwave (ours)"])
    ax.legend([("Quillwave (ours)", COLORS["Quillwave (ours)"]), ("RBF", COLORS["Radial-basis interpolation"])],
              (xs0[0] + 330, ys0[1] + 30), size=18)
    # (e) per-scene scatter (illustrative, seeded around the table means)
    rbf_m, ours_m = MT["rows"][1][1], MT["rows"][3][1]
    xr = rng.normal(rbf_m, 1.6, 120)
    yo = ours_m + (xr - rbf_m) * 0.7 + rng.normal(0, 0.9, 120)
    ax = Axes(img, (xs0[1], ys0[1], xs0[1] + pw, ys0[1] + ph), (18, 34), (18, 34), S, fs)
    ax.frame(range(18, 35, 4), range(18, 35, 4), xlabel="RBF PSNR (dB)", ylabel="Quillwave PSNR (dB)",
             title="(e) Per-scene PSNR")
    ax.line([18, 34], [18, 34], "#bbbbbb", 2, marker=0)
    ax.scatter(xr, yo, COLORS["Quillwave (ours)"], 4)
    # (f) training curve (illustrative, seeded, converges to the table value)
    ep = np.arange(0, NUM["setup"]["epochs"] + 1, 4)
    curve = ours_m - 9.5 * np.exp(-ep / 35) + rng.normal(0, 0.18, ep.size) * np.exp(-ep / 120)
    curve[-1] = ours_m
    ax = Axes(img, (xs0[2], ys0[1], xs0[2] + pw, ys0[1] + ph), (0, NUM["setup"]["epochs"]), (18, 32), S, fs)
    ax.frame(range(0, NUM["setup"]["epochs"] + 1, 50), range(18, 33, 2), xlabel="Epoch",
             ylabel="Validation PSNR (dB)", title="(f) Training curve")
    ax.line(ep, curve, COLORS["Quillwave (ours)"], 3, marker=0)
    save_png(finish(img, W, H), path, colors=96)


# ----------------------------------------------------------------- qualitative
def scene_panels(seed, size=256):
    gt = F.scene(seed, size)
    rec = F.reconstructions(gt, seed, NUM["setup"]["sensor_grid"])
    sens = F.sensor_map(gt, rec["xs"], rec["ys"])
    return dict(sensors=sens, linear=F.cmap(rec["linear"]), rbf=F.cmap(rec["rbf"]),
                ours=F.cmap(rec["ours"]), gt=F.cmap(gt))


def qualitative_grid(path):
    tile, gap, left, top = 300, 10, 90, 64
    cols = [("sensors", "Sensors (64)"), ("linear", "Linear"), ("rbf", "RBF"), ("ours", "Quillwave (ours)"),
            ("gt", "Ground truth")]
    W = left + 5 * tile + 4 * gap + 10
    H = top + 4 * tile + 3 * gap + 10
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    for c, (_, label) in enumerate(cols):
        d.text((left + c * (tile + gap) + tile / 2, top - 16), label, font=font(30, c == 3), fill="#222", anchor="ms")
    for r, seed in enumerate(SCENE_SEEDS):
        p = scene_panels(seed)
        y = top + r * (tile + gap)
        txt = Image.new("RGBA", (tile, 60), (255, 255, 255, 0))
        ImageDraw.Draw(txt).text((tile / 2, 30), f"Scene {r + 1}", font=font(28), fill="#222", anchor="mm")
        txt = txt.rotate(90, expand=True)
        img.paste(txt, (left - 70, y), txt)
        for c, (key, _) in enumerate(cols):
            im = Image.fromarray(p[key]).resize((tile, tile), Image.BICUBIC)
            img.paste(im, (left + c * (tile + gap), y))
    save_jpg(img, path, 80)
    return img.size


def scene_tiles(folder):
    tile, gap, top = 256, 8, 46
    for r, seed in enumerate(SCENE_SEEDS):
        p = scene_panels(seed)
        img = Image.new("RGB", (3 * tile + 2 * gap, top + tile), "white")
        d = ImageDraw.Draw(img)
        for c, (key, label) in enumerate([("sensors", "Input: 64 sensors"), ("ours", "Quillwave"), ("gt", "Ground truth")]):
            d.text((c * (tile + gap) + tile / 2, top - 12), label, font=font(22, c == 1), fill="#222", anchor="ms")
            img.paste(Image.fromarray(p[key]), (c * (tile + gap), top))
        save_jpg(img, folder / f"scene_{r + 1:02d}.jpg", 85)


# ----------------------------------------------------------------- dashboard screenshots (V3)
def _chrome(d, W, title, active):
    d.rectangle([0, 0, W, 56], fill="#1f2a44")
    d.text((24, 28), "Quillwave dashboard", font=font(24, True), fill="white", anchor="lm")
    tabs = ["Live", "Sensors", "Metrics", "Settings"]
    x = 360
    for t in tabs:
        f = font(20, t == active)
        w = f.getlength(t)
        if t == active:
            d.rectangle([x - 12, 10, x + w + 12, 46], fill="#33436b")
        d.text((x, 28), t, font=f, fill="white", anchor="lm")
        x += w + 48
    d.text((W - 24, 28), "simulated sensor array", font=font(18), fill="#b8c2dc", anchor="rm")
    d.text((24, 84), title, font=font(26, True), fill="#1f2a44", anchor="lm")


def dashboards(folder):
    W, H = 1280, 760
    seed = SCENE_SEEDS[1]
    p = scene_panels(seed)
    MTr = NUM["main_table"]["rows"]
    out = []
    # 1 live
    img = Image.new("RGB", (W, H), "#f4f6fa")
    d = ImageDraw.Draw(img)
    _chrome(d, W, "Live reconstruction", "Live")
    for i, (key, lab) in enumerate([("sensors", "Sensor layout"), ("ours", "Reconstruction"), ("gt", "Ground truth")]):
        x = 24 + i * 410
        d.rounded_rectangle([x, 120, x + 390, 560], 10, fill="white", outline="#d5dae5")
        d.text((x + 16, 142), lab, font=font(20, True), fill="#333", anchor="lm")
        img.paste(Image.fromarray(p[key]).resize((350, 350), Image.BICUBIC), (x + 20, 175))
    d.rounded_rectangle([24, 580, W - 24, H - 24], 10, fill="white", outline="#d5dae5")
    d.text((44, 610), f"Streaming   |   {NUM['setup']['sensors']} sensors   |   decoder: Quillwave   |   "
           f"latency {MTr[3][3]:.1f} ms", font=font(20), fill="#333", anchor="lm")
    out.append(img)
    # 2 sensors: sparkline grid
    img = Image.new("RGB", (W, H), "#f4f6fa")
    d = ImageDraw.Draw(img)
    _chrome(d, W, "Sensor readings", "Sensors")
    rng = np.random.default_rng(SEED["demo"])
    for k in range(16):
        x, y = 24 + (k % 4) * 310, 120 + (k // 4) * 156
        d.rounded_rectangle([x, y, x + 292, y + 140], 8, fill="white", outline="#d5dae5")
        d.text((x + 12, y + 18), f"Sensor {k + 1:02d}", font=font(18, True), fill="#333", anchor="lm")
        ph, fr = rng.uniform(0, 6.28), rng.uniform(0.8, 1.6)
        pts = [(x + 12 + t * 2.68, y + 88 - 34 * np.sin(fr * t / 12 + ph)) for t in range(100)]
        d.line(pts, fill="#2457c5", width=2)
    out.append(img)
    # 3 metrics: bars from the main table
    img = Image.new("RGB", (W, H), "#f4f6fa")
    d = ImageDraw.Draw(img)
    _chrome(d, W, "Reconstruction metrics (RippleBench-Synthetic)", "Metrics")
    d.rounded_rectangle([24, 120, W - 24, H - 24], 10, fill="white", outline="#d5dae5")
    from .plot import COLORS as C
    for i, (n, ps, ss, m) in enumerate(MTr):
        y = 180 + i * 130
        d.text((60, y), n, font=font(22, "ours" in n), fill="#333", anchor="lm")
        bw = (ps - 18) / (32 - 18) * 700
        d.rectangle([420, y - 22, 420 + bw, y + 22], fill=C[n])
        d.text((430 + bw, y), f"{ps:.2f} dB   SSIM {ss:.3f}", font=font(20), fill="#333", anchor="lm")
    out.append(img)
    # 4 settings form
    img = Image.new("RGB", (W, H), "#f4f6fa")
    d = ImageDraw.Draw(img)
    _chrome(d, W, "Settings", "Settings")
    d.rounded_rectangle([24, 120, 760, H - 24], 10, fill="white", outline="#d5dae5")
    rows = [("Sensor count", str(NUM["setup"]["sensors"])), ("Field size", f"{NUM['setup']['field_size']} x {NUM['setup']['field_size']}"),
            ("Decoder", "Quillwave"), ("Show confidence map", "on"), ("Refresh", "every frame")]
    for i, (k, v) in enumerate(rows):
        y = 180 + i * 90
        d.text((60, y), k, font=font(22), fill="#333", anchor="lm")
        d.rounded_rectangle([380, y - 26, 720, y + 26], 6, fill="#f4f6fa", outline="#c4cad8")
        d.text((396, y), v, font=font(22), fill="#111", anchor="lm")
    d.rounded_rectangle([800, 120, W - 24, 460], 10, fill="white", outline="#d5dae5")
    d.text((820, 150), "Preview", font=font(20, True), fill="#333", anchor="lm")
    img.paste(Image.fromarray(p["ours"]).resize((256, 256), Image.BICUBIC), (840, 180))
    out.append(img)
    paths = []
    for i, im in enumerate(out):
        pth = folder / f"dashboard_{i + 1:02d}.png"
        save_png(im, pth, colors=64)
        paths.append(pth)
    return paths
