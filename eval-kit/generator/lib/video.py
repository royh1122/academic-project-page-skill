"""Videos and the GIF: numpy/Pillow frames piped to ffmpeg (libx264, yuv420p, faststart).

- results/loops/*.mp4       silent (no audio stream), SAR 1:1, seamless 4 s loops
- video/overview_explainer  captions burned in (libass + Latin Modern Sans), WebVTT and transcript
                            written separately, near-silent generated tone bed (no speech)
- media/tracking.gif        processed-output GIF (T10)
- media/field_demo_capture  stored 720x480 with SAR 32:27 on purpose (T11) and a code-drawn
                            fictional badge and plate (T12)
The fictional marker goes into the container `comment` tag only.
"""
import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from . import fields as F
from .common import ENV, FONT_DIR, GEN, MARK, NUM, P, font, save_gif, tool

V = NUM["videos"]
# filter_units drops SEI NAL units, so the x264 version/settings banner is not embedded in the stream
BITEXACT = ["-bsf:v", "filter_units=remove_types=6", "-fflags", "+bitexact", "-flags:v", "+bitexact", "-map_metadata", "-1", "-metadata", "comment=" + MARK]


def _pipe(frames, w, h, fps, out, vf, pre_inputs=(), post=(), cwd=None):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [tool("ffmpeg"), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-", *pre_inputs, *vf, *post, *BITEXACT, "-movflags", "+faststart", str(out.resolve())]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=ENV)
    try:
        for fr in frames:
            assert fr.shape == (h, w, 3), fr.shape
            p.stdin.write(np.ascontiguousarray(fr, np.uint8).tobytes())
        p.stdin.close()
    except BrokenPipeError:
        pass
    err = p.stderr.read().decode("utf-8", "replace")
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg failed for {out.name}: {err[-2000:]}")


def _label(img, xy, text, size=22, bold=True):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(size, bold)
    w = f.getlength(text)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + 20, y + size + 14], 6, fill=(0, 0, 0, 140))
    d.text((x + 10, y + 7), text, font=f, fill="white")


# ----------------------------------------------------------------- comparison loops (T5)
class CompareLoop:
    """Side-by-side moving field: linear interpolation of 8x8 sensors (left) vs Quillwave (right)."""

    def __init__(self, seed, pw=480, ph=360):
        self.seed, self.pw, self.ph = seed, pw, ph
        f0 = F.ripple(seed, pw, ph, 0.0, scale=pw / 256, drift=0.03)
        self.lo, self.hi = float(f0.min()), float(f0.max())
        self.xs, self.ys = F.sensor_grid(NUM["setup"]["sensor_grid"], pw, ph)

    def frame(self, t):
        gt = F.norm(F.ripple(self.seed, self.pw, self.ph, t, scale=self.pw / 256, drift=0.03), self.lo, self.hi)
        samples = gt[np.ix_(self.ys, self.xs)]
        lin = cv2.resize(samples, (self.pw, self.ph), interpolation=cv2.INTER_LINEAR)
        ours = cv2.GaussianBlur(gt, (0, 0), 1.0)
        left = F.cmap(lin)
        for yy in self.ys:
            for xx in self.xs:
                cv2.circle(left, (int(xx), int(yy)), 4, (245, 245, 245), -1, lineType=cv2.LINE_AA)
        frame = np.concatenate([left, np.full((self.ph, 0, 3), 255, np.uint8), F.cmap(ours)], 1)
        frame[:, self.pw - 1:self.pw + 1] = 255
        return frame


def compare_loop(seed, out):
    w, h = V["loop_size"]
    fps, n = V["loop_fps"], V["loop_seconds"] * V["loop_fps"]
    cl = CompareLoop(seed, w // 2, h)
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _label(ov, (12, 12), "Input: linear, 64 sensors")
    _label(ov, (w // 2 + 12, 12), "Quillwave")
    ov = np.asarray(ov).astype(np.float32)
    a = ov[..., 3:4] / 255.0

    def frames():
        for i in range(n):
            fr = cl.frame(i / n).astype(np.float32)
            yield (fr * (1 - a) + ov[..., :3] * a).astype(np.uint8)

    _pipe(frames(), w, h, fps, out, ["-vf", "setsar=1"],
          post=["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p"])


# ----------------------------------------------------------------- explainer (T4)
def load_script():
    sc = json.loads((GEN / "narration" / "script.json").read_text(encoding="utf-8"))
    S, D = NUM["setup"], NUM["derived"]
    vals = dict(field_size=S["field_size"], sensors=S["sensors"], psnr=f"{NUM['main_table']['rows'][3][1]:.2f}",
                gain=f"{D['psnr_gain_over_best_baseline_db']:.2f}")
    sc["cues"] = [[a, b, t.format(**vals)] for a, b, t in sc["cues"]]
    return sc


def _ts(t, sep="."):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def vtt_text(sc):
    out = ["WEBVTT", "", "NOTE " + MARK, ""]
    for i, (a, b, t) in enumerate(sc["cues"], 1):
        out += [str(i), f"{_ts(a)} --> {_ts(b)}", t, ""]
    return "\n".join(out)


def srt_text(sc):
    out = []
    for i, (a, b, t) in enumerate(sc["cues"], 1):
        out += [str(i), f"{_ts(a, ',')} --> {_ts(b, ',')}", t, ""]
    return "\n".join(out)


def transcript_md(sc):
    out = ["# Transcript: Quillwave explainer video", "",
           f"The video has no speech. These are its on-screen captions, also provided as "
           f"`overview_explainer.en.vtt`. {MARK}", ""]
    for a, b, t in sc["cues"]:
        out.append(f"[{_ts(a)[3:8]}] {t}")
        out.append("")
    return "\n".join(out)


def _card(W, H, bg="#10182c"):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def explainer(out, overview_png, authors, workdir):
    W, H = V["explainer_size"]
    fps, total = 24, V["explainer_seconds"]
    sc = load_script()
    S, MT = NUM["setup"], NUM["main_table"]
    capbar = 86  # bottom strip reserved for captions

    # static cards
    title, d = _card(W, H)
    d.text((W / 2, 150), "Quillwave", font=font(64, True), fill="white", anchor="mm")
    d.text((W / 2, 215), "Sparse-Sensor Reconstruction of Synthetic Ripple Fields", font=font(26), fill="#c8d2ea", anchor="mm")
    d.text((W / 2, 285), authors, font=font(22), fill="#e8ecf6", anchor="mm")
    d.text((W / 2, 318), P["affiliation"], font=font(18), fill="#9aa6c4", anchor="mm")

    gt = F.scene(NUM["seeds"]["fields"] + 2, 256)
    rec = F.reconstructions(gt, 9, S["sensor_grid"])
    problem, d = _card(W, H, "#f4f6fa")
    d.text((W / 2, 40), f"{S['sensors']} sensors in, {S['field_size']}x{S['field_size']} field out",
           font=font(30, True), fill="#1f2a44", anchor="mm")
    for i, (im, lab) in enumerate([(F.sensor_map(gt, rec["xs"], rec["ys"]), "Sensors"),
                                   (F.cmap(rec["linear"]), "Linear interpolation"), (F.cmap(gt), "Ground truth")]):
        x = 37 + i * 270
        problem.paste(Image.fromarray(im).resize((240, 240), Image.BICUBIC), (x, 80))
        d.text((x + 120, 340), lab, font=font(20), fill="#333", anchor="mm")

    ovn = np.asarray(Image.open(overview_png).convert("RGB"))
    oh = 320  # displayed diagram height; slow zoom from the full diagram onto encoder/decoder
    pan_bg, d = _card(W, H, "white")
    d.text((W / 2, 36), "Method", font=font(30, True), fill="#1f2a44", anchor="mm")
    pan_bg = np.asarray(pan_bg).copy()

    table, d = _card(W, H, "#f4f6fa")
    d.text((W / 2, 40), "Results on RippleBench-Synthetic (64 sensors)", font=font(28, True), fill="#1f2a44", anchor="mm")
    cols = [60, 500, 610, 794]  # left edge of the name column, right edges of the numeric columns
    for j, c in enumerate(MT["columns"]):
        d.text((cols[j], 100), c, font=font(20, True), fill="#333", anchor="la" if j == 0 else "ra")
    d.line([(60, 130), (W - 60, 130)], fill="#333", width=2)
    for i, (n, p, s, m) in enumerate(MT["rows"]):
        y = 160 + i * 46
        b = "ours" in n
        for j, v in enumerate([n, f"{p:.2f}", f"{s:.3f}", f"{m:.1f}"]):
            d.text((cols[j], y), v, font=font(22, b), fill="#111", anchor="lm" if j == 0 else "rm")
    d.line([(60, 160 + 4 * 46 - 20), (W - 60, 160 + 4 * 46 - 20)], fill="#333", width=2)

    lim, d = _card(W, H)
    d.text((60, 60), "Limitations", font=font(34, True), fill="white", anchor="lm")
    from .content import LIMITATIONS
    for i, (t, desc) in enumerate(LIMITATIONS):
        d.text((60, 130 + i * 70), "- " + t, font=font(26, True), fill="#e8ecf6", anchor="lm")

    loop = CompareLoop(NUM["seeds"]["fields"], 480, 360)
    lbl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _label(lbl, (16, 14), "Linear interpolation", 20)
    _label(lbl, (W // 2 + 16, 14), "Quillwave", 20)
    lbl = np.asarray(lbl).astype(np.float32)
    la = lbl[..., 3:4] / 255.0

    statics = {k: np.asarray(v) for k, v in dict(title=title, problem=problem, table=table, limitations=lim).items()}

    def scene_at(t):
        for s in sc["scenes"]:
            if s["start"] <= t < s["end"]:
                return s
        return sc["scenes"][-1]

    def frames():
        for i in range(total * fps):
            t = i / fps
            s = scene_at(t)
            if s["id"] in statics:
                yield statics[s["id"]]
            elif s["id"] == "method":
                u = (t - s["start"]) / (s["end"] - s["start"])
                u = u * u * (3 - 2 * u)
                Hs, Ws = ovn.shape[:2]
                ww = Ws - u * (Ws - 0.62 * Ws)
                wh = ww * oh / W
                cx = Ws / 2 + u * 0.1 * Ws
                cy = Hs / 2
                x0 = int(np.clip(cx - ww / 2, 0, Ws - ww))
                y0 = int(np.clip(cy - wh / 2, 0, Hs - wh))
                crop = ovn[y0:y0 + int(wh), x0:x0 + int(ww)]
                fr = pan_bg.copy()
                fr[64:64 + oh] = cv2.resize(crop, (W, oh), interpolation=cv2.INTER_AREA)
                yield fr
            else:
                lt = ((t - s["start"]) / V["loop_seconds"]) % 1.0
                fr = loop.frame(lt)
                fr = cv2.resize(fr, (W, int(360 * W / 960)), interpolation=cv2.INTER_AREA)
                canvas = np.full((H, W, 3), 16, np.uint8)
                canvas[40:40 + fr.shape[0]] = fr
                canvas = (canvas.astype(np.float32) * (1 - la) + lbl[..., :3] * la).astype(np.uint8)
                yield canvas

    # captions are burned with libass from an SRT; fonts dir holds only Latin Modern Sans
    work = Path(workdir)
    (work / "fonts").mkdir(parents=True, exist_ok=True)
    for f in FONT_DIR.glob("*.otf"):
        shutil.copy(f, work / "fonts" / f.name)
    (work / "captions.srt").write_text(srt_text(sc), encoding="utf-8", newline="\n")
    style = ("FontName=LM Sans 10,FontSize=17,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,"
             "OutlineColour=&H99000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=12")
    # near-silent tone bed (about -34 dBFS peak) so the file carries an audio track: no speech, no TTS
    tone = (f"aevalsrc=0.012*sin(2*PI*110*t)+0.008*sin(2*PI*164.81*t):s=44100:d={total}")
    _pipe(frames(), W, H, fps, out,
          ["-filter_complex",
           f"[0:v]subtitles=captions.srt:fontsdir=fonts:force_style='{style}',setsar=1[v];"
           f"[1:a]afade=t=in:d=2,afade=t=out:st={total - 2}:d=2[a]",
           "-map", "[v]", "-map", "[a]"],
          pre_inputs=["-f", "lavfi", "-i", tone],
          post=["-c:v", "libx264", "-preset", "slow", "-crf", "32", "-pix_fmt", "yuv420p", "-g", "96",
                "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-shortest"],
          cwd=work)
    return sc


def poster_frame(video, out_jpg, t=0.5):
    from .common import run
    from PIL import Image as _I
    tmp = Path(out_jpg).with_suffix(".tmp.png")
    run([tool("ffmpeg"), "-y", "-loglevel", "error", "-ss", str(t), "-i", video, "-frames:v", "1", tmp], what="poster frame")
    from .common import save_jpg
    save_jpg(_I.open(tmp), out_jpg, 85)
    tmp.unlink()


# ----------------------------------------------------------------- GIF (T10)
def tracking_gif(out):
    w, h = V["gif_size"]
    fps, n = V["gif_fps"], V["gif_seconds"] * V["gif_fps"]
    seed = NUM["seeds"]["fields"] + 5
    f0 = F.ripple(seed, w, h, 0, scale=0.9)
    lo, hi = float(f0.min()), float(f0.max())
    frames = []
    for i in range(n):
        t = i / n
        fld = F.norm(F.ripple(seed, w, h, t, scale=0.9), lo, hi)
        img = Image.fromarray(F.cmap(np.round(fld * 9) / 9))  # 10 flat bands keep the GIF small
        d = ImageDraw.Draw(img)
        bx = w / 2 + 90 * np.cos(2 * np.pi * t)
        by = h / 2 + 45 * np.sin(2 * np.pi * t)
        d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill="#f26b1d", outline="white", width=2)
        d.rectangle([bx - 16, by - 16, bx + 16, by + 16], outline="#ffe14d", width=2)
        d.text((bx - 16, by - 20), "buoy 1", font=font(13, True), fill="#ffe14d", anchor="ls")
        frames.append(img)
    save_gif(frames, out, fps)


# ----------------------------------------------------------------- anamorphic demo capture (T11, T12)
def demo_capture(out):
    sw, sh = V["demo_stored_size"]          # stored 720x480
    dw = int(round(sw * 32 / 27))           # 853 display width for SAR 32:27
    fps, n = 24, V["demo_seconds"] * 24
    seed = NUM["seeds"]["demo"]
    f0 = F.ripple(seed, 300, 300, 0, scale=1.2)
    lo, hi = float(f0.min()), float(f0.max())
    base = Image.new("RGB", (dw, sh), "#eef1f6")
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, dw, 44], fill="#1f2a44")
    d.text((16, 22), "Quillwave dashboard - field demo", font=font(20, True), fill="white", anchor="lm")
    d.text((dw - 16, 22), "REC", font=font(18, True), fill="#ff6b6b", anchor="rm")
    d.rounded_rectangle([12, 56, 340, 404], 8, fill="white", outline="#cfd5e2")
    d.text((26, 74), "Live field", font=font(18, True), fill="#333", anchor="lm")
    # camera panel with a code-drawn toy vehicle and fictional plate
    d.rounded_rectangle([356, 56, dw - 12, 300], 8, fill="#cdd6e4", outline="#cfd5e2")
    d.text((370, 74), "Camera feed (simulated)", font=font(18, True), fill="#333", anchor="lm")
    d.rectangle([356, 230, dw - 12, 300], fill="#8c96a6")
    d.rounded_rectangle([470, 140, 740, 250], 18, fill="#3d6fb6", outline="#24406a", width=3)
    d.rounded_rectangle([520, 110, 690, 160], 12, fill="#5d8bd0", outline="#24406a", width=3)
    for cx in (520, 690):
        d.ellipse([cx - 26, 228, cx + 26, 280], fill="#222")
    d.rectangle([560, 200, 650, 232], fill="#f7f7f2", outline="#222", width=2)
    d.text((605, 216), "EX 0000", font=font(20, True), fill="#111", anchor="mm")
    # operator badge with a fictional name and ID in the 555-01xx fiction range
    d.rounded_rectangle([356, 316, dw - 12, 404], 8, fill="white", outline="#cfd5e2")
    d.rounded_rectangle([372, 328, 432, 392], 6, fill="#c9d3e6")
    d.ellipse([388, 334, 416, 362], fill="#8a99b8")
    d.text((448, 346), "Operator: Cleo Sample", font=font(22, True), fill="#111", anchor="lm")
    d.text((448, 376), "ID 555-0142", font=font(20), fill="#333", anchor="lm")
    d.rounded_rectangle([12, 416, dw - 12, sh - 10], 8, fill="white", outline="#cfd5e2")
    base_np = np.asarray(base).copy()

    def frames():
        for i in range(n):
            t = (i / n * 1.5) % 1.0
            fr = base_np.copy()
            fld = F.cmap(F.norm(F.ripple(seed, 300, 300, t, scale=1.2), lo, hi))
            fr[94:394, 26:326] = fld
            w = int((i + 1) / n * (dw - 60))
            fr[440:452, 30:30 + w] = (36, 87, 197)
            yield cv2.resize(fr, (sw, sh), interpolation=cv2.INTER_AREA)

    _pipe(frames(), sw, sh, fps, out, ["-vf", "setsar=32/27"],
          post=["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-pix_fmt", "yuv420p"])
