"""Procedural ripple fields, sensors and stand-in reconstructions (numpy + cv2).

Nothing here is real data: fields are sums of damped circular waves from seeded
random sources. "Ours" is the ground truth with a little blur and structured noise;
the baselines are the 8x8 sensor samples upsampled with linear / cubic resizing.
"""
import cv2
import numpy as np

# dark navy -> teal -> pale yellow (custom map, no third-party colormap)
_ANCH = np.array([[18, 24, 56], [28, 78, 128], [32, 142, 150], [120, 196, 140], [246, 236, 170]], np.float32)


def cmap(f):
    f = np.clip(f, 0, 1) * (len(_ANCH) - 1)
    i = np.minimum(f.astype(np.int32), len(_ANCH) - 2)
    t = (f - i)[..., None]
    return (_ANCH[i] * (1 - t) + _ANCH[i + 1] * t).astype(np.uint8)


def sources(seed, w, h, n=4):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        out.append((rng.uniform(0.1, 0.9) * w, rng.uniform(0.1, 0.9) * h,
                    rng.uniform(0.06, 0.13),
                    rng.uniform(0, 2 * np.pi), rng.uniform(0.6, 1.0)))
    return out


def ripple(seed, w, h, t=0.0, scale=1.0, drift=0.0):
    """Field in [0,1]. t in [0,1) gives a seamless loop (phase advances one period).
    drift moves the sources on a closed circle so loops stay seamless."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    f = np.zeros((h, w), np.float32)
    for j, (cx, cy, k, ph, a) in enumerate(sources(seed, w, h)):
        ang = 2 * np.pi * t + j
        cx2, cy2 = cx + drift * w * np.cos(ang), cy + drift * h * np.sin(ang)
        r = np.hypot(x - cx2, y - cy2)
        f += a * np.sin(k / scale * r - 2 * np.pi * t + ph) / (1 + r / (90 * scale))
    return f


def norm(f, lo=None, hi=None):
    lo = f.min() if lo is None else lo
    hi = f.max() if hi is None else hi
    return np.clip((f - lo) / (hi - lo + 1e-6), 0, 1)


def sensor_grid(n_side, w, h):
    xs = ((np.arange(n_side) + 0.5) * w / n_side).astype(int)
    ys = ((np.arange(n_side) + 0.5) * h / n_side).astype(int)
    return xs, ys


def reconstructions(gt, seed, n_side=8):
    """Return dict of [0,1] fields: sensors (sparse samples), linear, rbf, ours."""
    h, w = gt.shape
    xs, ys = sensor_grid(n_side, w, h)
    samples = gt[np.ix_(ys, xs)].astype(np.float32)
    lin = cv2.resize(samples, (w, h), interpolation=cv2.INTER_LINEAR)
    rbf = cv2.resize(samples, (w, h), interpolation=cv2.INTER_CUBIC)
    rbf = cv2.GaussianBlur(rbf, (0, 0), 3)
    rng = np.random.default_rng(seed + 1000)
    noise = cv2.resize(rng.normal(0, 1, (16, 16)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    ours = cv2.GaussianBlur(gt, (0, 0), 1.2) + 0.04 * noise
    return dict(samples=samples, xs=xs, ys=ys, linear=np.clip(lin, 0, 1),
                rbf=np.clip(rbf, 0, 1), ours=np.clip(ours, 0, 1))


def sensor_map(gt, xs, ys, dot=5):
    """RGB image: dark background with coloured sensor dots."""
    h, w = gt.shape
    img = np.full((h, w, 3), 236, np.uint8)
    cols = cmap(gt[np.ix_(ys, xs)])
    for j, yy in enumerate(ys):
        for i, xx in enumerate(xs):
            c = tuple(int(v) for v in cols[j, i])
            cv2.circle(img, (int(xx), int(yy)), dot + 2, (40, 40, 40), -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (int(xx), int(yy)), dot, c, -1, lineType=cv2.LINE_AA)
    return img


def scene(seed, size=256):
    return norm(ripple(seed, size, size))
