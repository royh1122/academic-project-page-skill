"""Tiny numpy + Pillow plotting helpers (matplotlib is not installed here).

Draw on a canvas S times larger than the target, then downsample for antialiasing.
"""
import math

from PIL import Image, ImageDraw

from .common import font

COLORS = {
    "Linear interpolation": "#8a94a0",
    "Radial-basis interpolation": "#c4862f",
    "Quillwave-Lite (ablation)": "#5fa8a0",
    "Quillwave (ours)": "#2457c5",
}
SHORT = {
    "Linear interpolation": "Linear",
    "Radial-basis interpolation": "RBF",
    "Quillwave-Lite (ablation)": "Quillwave-Lite",
    "Quillwave (ours)": "Quillwave (ours)",
}


class Axes:
    def __init__(self, img, box, xlim, ylim, S=2, fs=22, xlog2=False):
        self.img, self.d = img, ImageDraw.Draw(img)
        self.S, self.fs, self.xlog2 = S, fs, xlog2
        self.x0, self.y0, self.x1, self.y1 = [v * S for v in box]
        self.xlim, self.ylim = xlim, ylim

    def _tx(self, x):
        if self.xlog2:
            x, lo, hi = math.log2(x), math.log2(self.xlim[0]), math.log2(self.xlim[1])
        else:
            lo, hi = self.xlim
        return self.x0 + (x - lo) / (hi - lo) * (self.x1 - self.x0)

    def _ty(self, y):
        lo, hi = self.ylim
        return self.y1 - (y - lo) / (hi - lo) * (self.y1 - self.y0)

    def text(self, xy, s, size=None, bold=False, fill="#222", anchor="la"):
        self.d.text(xy, s, font=font((size or self.fs) * self.S, bold), fill=fill, anchor=anchor)

    def frame(self, xticks, yticks, xfmt="{:g}", yfmt="{:g}", xlabel="", ylabel="", title="", grid=True):
        S, d = self.S, self.d
        for v in yticks:
            y = self._ty(v)
            if grid:
                d.line([(self.x0, y), (self.x1, y)], fill="#e6e6e6", width=S)
            self.text((self.x0 - 8 * S, y), yfmt.format(v), fill="#444", anchor="rm")
        for v in xticks:
            x = self._tx(v)
            d.line([(x, self.y1), (x, self.y1 + 6 * S)], fill="#777", width=S)
            self.text((x, self.y1 + 9 * S), xfmt.format(v), fill="#444", anchor="ma")
        d.line([(self.x0, self.y0), (self.x0, self.y1)], fill="#777", width=2 * S)
        d.line([(self.x0, self.y1), (self.x1, self.y1)], fill="#777", width=2 * S)
        if xlabel:
            self.text(((self.x0 + self.x1) / 2, self.y1 + 40 * S), xlabel, fill="#333", anchor="ma")
        if ylabel:
            f = font(self.fs * S)
            bb = f.getbbox(ylabel)
            t = Image.new("RGBA", (bb[2] + 4, bb[3] + 8), (255, 255, 255, 0))
            ImageDraw.Draw(t).text((2, 2), ylabel, font=f, fill="#333")
            t = t.rotate(90, expand=True)
            self.img.paste(t, (int(self.x0 - 78 * S - t.width / 2), int((self.y0 + self.y1) / 2 - t.height / 2)), t)
        if title:
            self.text((self.x0, self.y0 - 34 * S), title, size=self.fs + 3, bold=True, anchor="ls")

    def line(self, xs, ys, color, width=3, marker=6):
        pts = [(self._tx(x), self._ty(y)) for x, y in zip(xs, ys)]
        self.d.line(pts, fill=color, width=width * self.S, joint="curve")
        if marker:
            r = marker * self.S
            for x, y in pts:
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline="white", width=self.S)

    def scatter(self, xs, ys, color, r=4):
        r *= self.S
        for x, y in zip(xs, ys):
            X, Y = self._tx(x), self._ty(y)
            self.d.ellipse([X - r, Y - r, X + r, Y + r], fill=color)

    def bar(self, x, h, w, color, label=None, bold=False):
        X0, X1 = self._tx(x - w / 2), self._tx(x + w / 2)
        self.d.rectangle([X0, self._ty(h), X1, self._ty(self.ylim[0])], fill=color)
        if label:
            self.text(((X0 + X1) / 2, self._ty(h) - 6 * self.S), label, bold=bold, anchor="mb")

    def legend(self, items, xy, size=None):
        S = self.S
        x, y = xy[0] * S, xy[1] * S
        for name, color in items:
            self.d.line([(x, y), (x + 30 * S, y)], fill=color, width=4 * S)
            self.text((x + 38 * S, y), name, size=size, fill="#333", anchor="lm")
            y += ((size or self.fs) + 10) * S


def canvas(w, h, S=2):
    return Image.new("RGB", (w * S, h * S), "white")


def finish(img, w, h):
    return img.resize((w, h), Image.LANCZOS)
