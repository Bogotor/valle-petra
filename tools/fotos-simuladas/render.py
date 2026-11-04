"""Fotos simuladas para los prototipos de Valle Petra (renders procedurales)."""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, gaussian_filter1d, zoom

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def C(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32) / 255.0


def smooth(t):
    return t * t * (3 - 2 * t)


def gradient(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        f = smooth((t[m] - p0) / max(p1 - p0, 1e-6))[:, None]
        out[m] = C(c0) * (1 - f) + C(c1) * f
    return out


def fbm(H, W, rng, scales=(256, 128, 64, 32, 16, 8), gain=0.55):
    out = np.zeros((H, W), np.float32)
    amp, tot = 1.0, 0.0
    for s in scales:
        g = rng.random((H // s + 3, W // s + 3)).astype(np.float32)
        up = zoom(g, s, order=3)[:H, :W]
        out += amp * up
        tot += amp
        amp *= gain
    return out / tot


def noise1d(W, rng, octaves=7, base=3, rough=0.52):
    y = np.zeros(W)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        pts = rng.random(n + 2)
        xs = np.linspace(0, n, W)
        i = np.minimum(np.floor(xs).astype(int), n)
        f = (1 - np.cos((xs - i) * np.pi)) / 2
        y += amp * (pts[i] * (1 - f) + pts[i + 1] * f)
        tot += amp
        amp *= rough
    return y / tot


class Scene:
    def __init__(self, W, H, seed, horizon):
        self.W, self.H = W, H
        self.rng = np.random.default_rng(seed)
        self.horizon = horizon
        self.img = np.zeros((H, W, 3), np.float32)
        self.glow = np.zeros((H, W, 3), np.float32)
        self.Y, self.X = np.mgrid[0:H, 0:W].astype(np.float32)

    # ---------- cielo ----------
    def sky(self, stops, sun=None):
        t = self.Y / self.horizon
        self.img[:] = gradient(t, stops)
        if sun:
            sx, sy, rad, col, k = sun
            d = np.sqrt((self.X - sx) ** 2 + ((self.Y - sy) * 1.6) ** 2)
            self.img += C(col) * (np.exp(-(d / rad) ** 2) * k)[..., None]

    def stars(self, n, bright=1.0, fade=0.35):
        H, W, rng = self.H, self.W, self.rng
        layer = np.zeros((H, W), np.float32)
        big = np.zeros((H, W), np.float32)
        xs = rng.integers(0, W, n)
        ys = rng.integers(0, int(self.horizon), n)
        b = np.clip(rng.pareto(2.6, n) * 0.18 + 0.04, 0, 2.0)
        np.add.at(layer, (ys, xs), b)
        sel = b > 0.55
        np.add.at(big, (ys[sel], xs[sel]), b[sel])
        tot = gaussian_filter(layer, 0.6) * 5 + gaussian_filter(big, 1.8) * 22
        f = np.clip((self.horizon - self.Y) / (fade * self.horizon), 0, 1)
        self.img += (tot * f * bright)[..., None] * np.array([0.93, 0.96, 1.0], np.float32)

    def milky_way(self, cx, cy, angle, width, strength=0.55):
        H, W, rng = self.H, self.W, self.rng
        a = math.radians(angle)
        d = -(self.X - cx) * math.sin(a) + (self.Y - cy) * math.cos(a)
        band = np.exp(-(d / width) ** 2)
        n1 = fbm(H, W, rng, (192, 96, 48, 24, 12, 6))
        n2 = fbm(H, W, rng, (128, 64, 32, 16, 8))
        core = band * (0.25 + 1.1 * n1 ** 2) - 1.4 * band ** 1.3 * np.clip(n2 - 0.5, 0, 1)
        core = np.clip(core, 0, None)
        warm = C("#F2D3B0")
        cool = C("#8C97D6")
        col = cool[None, None] * (1 - band[..., None] ** 2) + warm[None, None] * band[..., None] ** 2
        f = np.clip((self.horizon - self.Y) / (0.25 * self.horizon), 0, 1)
        self.img += core[..., None] * col * strength * f[..., None]
        # estrellas extra dentro de la banda
        cand = 14000
        xs = rng.integers(0, W, cand)
        ys = rng.integers(0, int(self.horizon), cand)
        keep = rng.random(cand) < band[ys, xs] * (0.4 + n1[ys, xs])
        layer = np.zeros((H, W), np.float32)
        np.add.at(layer, (ys[keep], xs[keep]), rng.random(keep.sum()) * 0.35 + 0.05)
        self.img += (gaussian_filter(layer, 0.6) * 4 * f)[..., None]

    # ---------- cerros ----------
    def mountains(self, base, amp, top, bot, haze_col=None, haze=0.0, sharp=0.5,
                  base_freq=3, rough=0.52, rim=None, tex=0.08):
        H, W, rng = self.H, self.W, self.rng
        r1 = noise1d(W, rng, 7, base_freq, rough)
        r2 = 1 - np.abs(2 * noise1d(W, rng, 6, base_freq + 1, rough) - 1)
        prof = (1 - sharp) * r1 + sharp * r2
        prof = (prof - prof.min()) / (np.ptp(prof) + 1e-6)
        ry = base - amp * prof
        m = np.clip(self.Y - ry[None, :] + 0.5, 0, 1)
        ry_s = gaussian_filter1d(ry, W * 0.06)
        depth = np.clip((self.Y - ry_s[None, :]) / (H - ry_s.min() + 1), 0, 1) ** 0.7
        col = C(top)[None, None] * (1 - depth[..., None]) + C(bot)[None, None] * depth[..., None]
        t = fbm(H, W, rng, (64, 32, 16, 8, 4))
        col *= (1 - tex + 2 * tex * t)[..., None]
        if rim:
            rc, rw, side = rim
            slope = np.gradient(gaussian_filter1d(ry, 4))
            facing = np.clip(-slope * side * 0.8, 0, 1)
            rimmask = np.exp(-np.clip(self.Y - ry[None, :], 0, None) / rw) * facing[None, :]
            col += C(rc)[None, None] * rimmask[..., None] * 0.55
        if haze_col is not None and haze > 0:
            col = col * (1 - haze) + C(haze_col) * haze
        self.img = self.img * (1 - m[..., None]) + col * m[..., None]
        return ry

    def ground(self, y0, top, bot, tex=0.12, wav=30):
        H, W, rng = self.H, self.W, self.rng
        ry = y0 - wav * noise1d(W, rng, 6, 3, 0.5)
        m = np.clip(self.Y - ry[None, :] + 0.5, 0, 1)
        depth = np.clip((self.Y - ry[None, :]) / (H - ry.min() + 1), 0, 1)
        col = C(top)[None, None] * (1 - depth[..., None]) + C(bot)[None, None] * depth[..., None]
        t = fbm(H, W, rng, (32, 16, 8, 4, 2))
        col *= (1 - tex + 2 * tex * t)[..., None]
        self.img = self.img * (1 - m[..., None]) + col * m[..., None]
        return ry

    # ---------- capa vectorial antialias ----------
    def layer(self):
        ss = 2
        im = Image.new("RGBA", (self.W * ss, self.H * ss), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im), ss

    def composite(self, im, glow=0.0, sigma=18):
        im = im.resize((self.W, self.H), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255.0
        rgb, al = a[..., :3], a[..., 3:4]
        self.img = self.img * (1 - al) + rgb * al
        if glow:
            self.glow += gaussian_filter(rgb * al, (sigma, sigma, 0)) * glow

    def light(self, x, y, r, col, k=1.0):
        d = np.sqrt((self.X - x) ** 2 + (self.Y - y) ** 2)
        self.glow += C(col) * (np.exp(-(d / r) ** 2) * k)[..., None]

    # ---------- objetos ----------
    def dome(self, cx, base, r, body, lit=True, lightdir=(-0.5, 0.6, 0.62), win="#FFC27A",
             facet=0.22, amb=0.35):
        dx = (self.X - cx) / r
        dy = (base - self.Y) / r
        inside = (dx ** 2 + dy ** 2 <= 1) & (dy >= 0)
        nz = np.sqrt(np.clip(1 - dx ** 2 - dy ** 2, 0, 1))
        L = np.array(lightdir) / np.linalg.norm(lightdir)
        lam = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
        shade = amb + (1 - amb) * lam
        col = C(body)[None, None] * shade[..., None]
        if lit:
            wy = base - 0.5 * r
            d = np.sqrt((self.X - (cx + 0.18 * r)) ** 2 + (self.Y - wy) ** 2) / r
            col += C(win) * (np.exp(-(d / 0.75) ** 2) * 0.28)[..., None]
        edge = np.clip((1 - np.sqrt(dx ** 2 + dy ** 2)) * r * 0.9, 0, 1) * np.clip(dy * r, 0, 1)
        m = (inside * edge)[..., None]
        self.img = self.img * (1 - m) + col * m
        # facetas geodésicas
        im, dr, ss = self.layer()
        lc = (20, 22, 34, int(255 * facet))
        for k in range(1, 5):
            h = k / 5
            hw = math.sqrt(1 - h * h) * r
            yy = base - h * r
            dr.arc([(cx - hw) * ss, (yy - hw * 0.16) * ss, (cx + hw) * ss, (yy + hw * 0.16) * ss],
                   0, 180, fill=lc, width=2 * ss // 2 + 1)
        for th in (-70, -45, -20, 5, 30, 55, 78):
            pts = []
            for ph in range(0, 91, 6):
                p = math.radians(ph)
                x = cx + r * math.cos(p) * math.sin(math.radians(th))
                y = base - r * math.sin(p)
                pts.append((x * ss, y * ss))
            dr.line(pts, fill=lc, width=2 * ss // 2 + 1)
        # base / deck
        dr.rectangle([(cx - r * 1.25) * ss, (base - 2) * ss, (cx + r * 1.25) * ss, (base + r * 0.08) * ss],
                     fill=(58, 42, 34, 255))
        if lit:
            wx, wy, wr = cx + 0.2 * r, base - 0.5 * r, 0.26 * r
            dr.ellipse([(wx - wr) * ss, (wy - wr * 0.92) * ss, (wx + wr) * ss, (wy + wr * 0.92) * ss],
                       fill=C255(win))
            dr.line([(wx - wr) * ss, wy * ss, (wx + wr) * ss, wy * ss], fill=(60, 40, 30, 200), width=3 * ss)
            dr.line([wx * ss, (wy - wr) * ss, wx * ss, (wy + wr) * ss], fill=(60, 40, 30, 200), width=3 * ss)
            ddx = cx - 0.32 * r
            dr.rounded_rectangle([(ddx - 0.12 * r) * ss, (base - 0.46 * r) * ss, (ddx + 0.12 * r) * ss, base * ss],
                                 radius=int(0.1 * r * ss), fill=C255("#FFB466"))
        self.composite(im, glow=0.9 if lit else 0, sigma=r * 0.35)
        if lit:
            self.light(cx + 0.2 * r, base - 0.5 * r, r * 0.9, "#FFB060", 0.32)
            self.light(cx, base + 0.05 * r, r * 1.3, "#FF9E50", 0.12)

    def cabin(self, x, base, w, h, wall="#5A3E30", side="#3E2A22", roof="#22252E", lit=True,
              win="#FFC27A", depth=0.38):
        im, dr, ss = self.layer()
        s = lambda pts: [(px * ss, py * ss) for px, py in pts]
        dw = w * depth
        # cara lateral
        dr.polygon(s([(x + w, base), (x + w + dw, base - h * 0.18), (x + w + dw, base - h * 1.05),
                      (x + w, base - h * 0.9)]), fill=C255(side))
        # fachada
        dr.polygon(s([(x, base), (x + w, base), (x + w, base - h * 0.9), (x, base - h * 1.15)]), fill=C255(wall))
        # techo de una agua
        dr.polygon(s([(x - w * 0.06, base - h * 1.18), (x + w * 1.04, base - h * 0.86),
                      (x + w + dw + w * 0.04, base - h * 1.02), (x + dw * 0.9, base - h * 1.38)]), fill=C255(roof))
        # ventanales
        if lit:
            wc = C255(win)
            dr.polygon(s([(x + w * 0.08, base - h * 0.06), (x + w * 0.62, base - h * 0.06),
                          (x + w * 0.62, base - h * 0.98), (x + w * 0.08, base - h * 1.08)]), fill=wc)
            for k in (0.26, 0.44):
                dr.line(s([(x + w * k, base - h * 0.06), (x + w * k, base - h * (1.1 - k * 0.24))]),
                        fill=(70, 46, 34, 230), width=3 * ss)
            dr.rectangle(s([(x + w * 0.72, base - h * 0.62), (x + w * 0.9, base - h * 0.06)]), fill=C255("#FFB466"))
        else:
            dr.polygon(s([(x + w * 0.08, base - h * 0.06), (x + w * 0.62, base - h * 0.06),
                          (x + w * 0.62, base - h * 0.98), (x + w * 0.08, base - h * 1.08)]), fill=C255("#7C8DA6"))
        # deck
        dr.polygon(s([(x - w * 0.12, base), (x + w * 1.1, base), (x + w * 1.1 + dw, base - h * 0.16),
                      (x - w * 0.02 + dw, base - h * 0.16)]), fill=(70, 50, 38, 255))
        dr.rectangle(s([(x - w * 0.12, base), (x + w * 1.1, base + h * 0.06)]), fill=(46, 32, 24, 255))
        self.composite(im, glow=0.8 if lit else 0, sigma=w * 0.12)
        if lit:
            self.light(x + w * 0.4, base - h * 0.5, w * 0.9, "#FFB060", 0.28)

    def pool(self, y0, y1, x0=0, x1=None, tint="#1E3A5A", k=0.78, coping="#CDB79E"):
        x1 = self.W if x1 is None else x1
        H, W = self.H, self.W
        y0, y1, x0, x1 = int(y0), int(y1), int(x0), int(x1)
        src = self.img.copy()
        rows = np.arange(y0, y1)
        mir = np.clip(2 * y0 - rows - 2, 0, H - 1).astype(int)
        refl = src[mir][:, x0:x1]
        ripple = np.sin(np.arange(x1 - x0)[None, :] * 0.045 + rows[:, None] * 0.9) * 0.5 + 0.5
        refl = refl * (k - 0.08 * ripple[..., None]) + C(tint) * 0.22
        self.img[y0:y1, x0:x1] = refl
        # borde de piedra delantero
        self.img[y1:y1 + max(3, (y1 - y0) // 7), x0:x1] = C(coping)

    def tub(self, cx, cy, rx, ry, wood="#4A3226", water="#2A4A66", lit=True):
        im, dr, ss = self.layer()
        dr.ellipse([(cx - rx) * ss, (cy - ry) * ss, (cx + rx) * ss, (cy + ry * 2.6) * ss], fill=C255(wood))
        dr.rectangle([(cx - rx) * ss, cy * ss, (cx + rx) * ss, (cy + ry * 1.8) * ss], fill=C255(wood))
        dr.ellipse([(cx - rx) * ss, (cy - ry) * ss, (cx + rx) * ss, (cy + ry) * ss], fill=C255("#6A4836"))
        dr.ellipse([(cx - rx * 0.88) * ss, (cy - ry * 0.8) * ss, (cx + rx * 0.88) * ss, (cy + ry * 0.8) * ss],
                   fill=C255(water))
        for k in range(-3, 4):
            xx = cx + k * rx * 0.28
            dr.line([(xx * ss, (cy + ry * 0.95) * ss), (xx * ss, (cy + ry * 2.4) * ss)], fill=(34, 22, 16, 160),
                    width=2 * ss)
        self.composite(im)
        if lit:
            self.light(cx, cy, rx * 0.9, "#FFC27A", 0.18)
        # vapor
        rng = self.rng
        st = np.zeros((self.H, self.W), np.float32)
        for _ in range(40):
            sx = cx + rng.normal(0, rx * 0.4)
            sy = cy - rng.uniform(0, rx * 1.6)
            rr = rng.uniform(rx * 0.12, rx * 0.3)
            d = np.sqrt((self.X - sx) ** 2 + ((self.Y - sy) * 0.8) ** 2)
            st += np.exp(-(d / rr) ** 2) * 0.05
        st = gaussian_filter(st, rx * 0.08)
        self.img = self.img * (1 - np.clip(st, 0, 0.5)[..., None]) + C("#E8E6F0") * np.clip(st, 0, 0.5)[..., None]

    def fire(self, cx, cy, r):
        im, dr, ss = self.layer()
        rng = self.rng
        for i in range(14):
            a = i / 14 * math.tau
            sx, sy = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.35
            sr = r * rng.uniform(0.2, 0.28)
            g = int(rng.uniform(70, 110))
            dr.ellipse([(sx - sr) * ss, (sy - sr * 0.7) * ss, (sx + sr) * ss, (sy + sr * 0.7) * ss],
                       fill=(g, g - 8, g - 16, 255))
        for i in range(9):
            fx = cx + rng.normal(0, r * 0.25)
            fh = r * rng.uniform(0.6, 1.4)
            fw = r * rng.uniform(0.14, 0.24)
            col = [(255, 200, 110, 235), (255, 150, 60, 230), (255, 110, 40, 220)][i % 3]
            dr.polygon([((fx - fw) * ss, cy * ss), ((fx + fw) * ss, cy * ss),
                        ((fx + rng.normal(0, fw * 0.6)) * ss, (cy - fh) * ss)], fill=col)
        self.composite(im, glow=1.4, sigma=r * 0.5)
        self.light(cx, cy - r * 0.4, r * 4, "#FF9040", 0.55)
        for _ in range(26):
            px = int(cx + rng.normal(0, r * 0.8))
            py = int(cy - abs(rng.normal(r * 1.6, r * 1.2)))
            if 0 <= px < self.W and 0 <= py < self.H:
                self.glow[py, px] += C("#FFC070") * 3

    def cactus(self, x, base, h, w, col="#2E3B2C", rim=None, arms=2):
        im, dr, ss = self.layer()
        rng = self.rng
        c = C255(col)
        rad = int(w * ss / 2)
        dr.rounded_rectangle([(x - w / 2) * ss, (base - h) * ss, (x + w / 2) * ss, base * ss], radius=rad, fill=c)
        for k in range(arms):
            side = -1 if k % 2 == 0 else 1
            ay = base - h * rng.uniform(0.35, 0.6)
            ah = h * rng.uniform(0.25, 0.45)
            ax = x + side * w * 1.1
            dr.rounded_rectangle([min(x, ax) * ss, (ay - w * 0.35) * ss, max(x, ax) * ss, (ay + w * 0.35) * ss],
                                 radius=int(w * 0.35 * ss), fill=c)
            dr.rounded_rectangle([(ax - w * 0.38) * ss, (ay - ah) * ss, (ax + w * 0.38) * ss, (ay + w * 0.3) * ss],
                                 radius=int(w * 0.38 * ss), fill=c)
        if rim:
            dr.rounded_rectangle([(x - w / 2 + w * 0.06) * ss, (base - h + w * 0.2) * ss, (x - w / 2 + w * 0.2) * ss,
                                  (base - w * 0.2) * ss], radius=int(w * 0.07 * ss), fill=C255(rim, 55))
        self.composite(im)

    def stones(self, cx, base, n, size, col="#7A6656", hi="#A88E78", spread=1.0, stack=False):
        im, dr, ss = self.layer()
        rng = self.rng
        y = base
        for i in range(n):
            if stack:
                rw = size * (1 - i * 0.17)
                rh = rw * 0.42
                sx = cx + rng.normal(0, size * 0.04)
                sy = y - rh
                y = sy - rh * 0.05
            else:
                rw = size * rng.uniform(0.5, 1.0)
                rh = rw * rng.uniform(0.45, 0.65)
                sx = cx + rng.normal(0, size * 2.2 * spread)
                sy = base - rh + rng.normal(0, size * 0.2)
            dr.ellipse([(sx - rw) * ss, (sy - rh) * ss, (sx + rw) * ss, (sy + rh) * ss], fill=C255(col))
            dr.ellipse([(sx - rw * 0.8) * ss, (sy - rh * 0.95) * ss, (sx + rw * 0.4) * ss, (sy + rh * 0.1) * ss],
                       fill=C255(hi, 90))
        self.composite(im)

    def vineyard(self, vx, vy, top="#5A6A2E", soil="#B98A5C", density=26, cover=0.58):
        H = self.H
        below = self.Y > vy + 2
        dy = np.clip(self.Y - vy, 1, None)
        u = (self.X - vx) / dy * density / 10
        frac = u - np.floor(u)
        row = (frac < cover) & below
        t = fbm(self.H, self.W, self.rng, (16, 8, 4, 2))
        persp = np.clip((self.Y - vy) / (H - vy), 0, 1)
        leaf = C(top)[None, None] * (0.7 + 0.6 * t[..., None]) * (0.75 + 0.35 * persp[..., None])
        dirt = C(soil)[None, None] * (0.85 + 0.25 * t[..., None])
        col = np.where(row[..., None], leaf, dirt)
        m = np.clip((self.Y - vy) / 3, 0, 1)[..., None] * below[..., None]
        self.img = self.img * (1 - m) + col * m

    def trail(self, x_bottom, y_top, w_bottom, col="#D8B98E"):
        H, W = self.H, self.W
        im, dr, ss = self.layer()
        pts_l, pts_r = [], []
        for i in range(60):
            t = i / 59
            y = H - t * (H - y_top)
            cx = x_bottom + math.sin(t * 5.2) * W * 0.12 * (1 - t) + (W * 0.55 - x_bottom) * t
            hw = w_bottom * (1 - t) ** 1.6 + 1.5
            pts_l.append(((cx - hw) * ss, y * ss))
            pts_r.append(((cx + hw) * ss, y * ss))
        dr.polygon(pts_l + pts_r[::-1], fill=C255(col))
        self.composite(im)

    def scrub(self, n, y0, y1, col="#3E4A2E", size=(3, 9)):
        im, dr, ss = self.layer()
        rng = self.rng
        for _ in range(n):
            x = rng.uniform(0, self.W)
            y = rng.uniform(y0, y1)
            s = rng.uniform(*size) * (0.5 + (y - y0) / max(y1 - y0, 1))
            dr.ellipse([(x - s) * ss, (y - s * 0.6) * ss, (x + s) * ss, (y + s * 0.6) * ss], fill=C255(col, 230))
        self.composite(im)

    # ---------- revelado ----------
    def finish(self, name, exposure=1.0, bloom=0.5, vignette=0.32, grain=0.014, grade=None, q=84):
        img = self.img + self.glow
        bright = np.clip(img - 0.7, 0, None)
        img += gaussian_filter(bright, (self.H * 0.012, self.H * 0.012, 0)) * bloom
        img = 1 - np.exp(-img * exposure * 1.25)
        r2 = ((self.X / self.W - 0.5) ** 2 + (self.Y / self.H - 0.5) ** 2) / 0.5
        img *= (1 - vignette * r2)[..., None]
        if grade:
            sh, hi = C(grade[0]), C(grade[1])
            lum = img.mean(axis=2, keepdims=True)
            img = img + (sh - 0.5) * 0.12 * (1 - lum) + (hi - 0.5) * 0.08 * lum
        img += self.rng.normal(0, grain, img.shape).astype(np.float32)
        img = np.clip(img, 0, 1)
        Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".jpg"), quality=q,
                                                          optimize=True, progressive=True)
        print("ok", name, self.W, self.H)


def C255(h, a=255):
    c = (C(h) * 255).astype(int)
    return (int(c[0]), int(c[1]), int(c[2]), a)


NIGHT = [(0, "#04071A"), (0.5, "#0C1332"), (0.82, "#18204A"), (0.95, "#2E2E55"), (1.0, "#4A3A58")]
BLUE = [(0, "#0A0F2E"), (0.45, "#1B2452"), (0.75, "#41406E"), (0.9, "#9A6362"), (1.0, "#E39466")]
DUSK = [(0, "#28305F"), (0.42, "#6E5585"), (0.72, "#D9846A"), (0.9, "#F2AE78"), (1.0, "#F8CC92")]
GOLD = [(0, "#5B84B6"), (0.5, "#A7B8C9"), (0.82, "#EBC8A0"), (1.0, "#F6D3A0")]
DAY = [(0, "#3A70AE"), (0.6, "#88AFD4"), (1.0, "#D9E4EC")]


def night_base(s, mw=True, mw_angle=-28, mw_cx=None, mw_cy=None, stars=2600):
    s.sky(NIGHT)
    s.stars(stars)
    if mw:
        s.milky_way(mw_cx if mw_cx is not None else s.W * 0.55, mw_cy if mw_cy is not None else s.horizon * 0.45,
                    mw_angle, s.H * 0.13)
    hz = s.horizon
    s.mountains(hz + 4, s.H * 0.16, "#151B3D", "#111735", "#1E2348", 0.2, sharp=0.6, rough=0.56)
    s.mountains(hz + s.H * 0.07, s.H * 0.13, "#0C1129", "#090D21", sharp=0.4, base_freq=2, rough=0.56)


def dusk_base(s, sunx=None):
    s.sky(DUSK, sun=(sunx if sunx is not None else s.W * 0.62, s.horizon, s.W * 0.22, "#FFD9A0", 0.55))
    s.stars(400, bright=0.35, fade=0.7)
    hz = s.horizon
    s.mountains(hz + 4, s.H * 0.15, "#9A6878", "#82586C", "#C98A7A", 0.25, sharp=0.6)
    s.mountains(hz + s.H * 0.07, s.H * 0.12, "#5C3E5A", "#46304A", sharp=0.45, base_freq=2)


def gold_base(s, sunx=None):
    s.sky(GOLD, sun=(sunx if sunx is not None else s.W * 0.15, s.horizon * 0.9, s.W * 0.25, "#FFE3B0", 0.45))
    hz = s.horizon
    s.mountains(hz + 4, s.H * 0.16, "#C89C8A", "#B48A7E", "#D9BBA8", 0.35, sharp=0.6)
    s.mountains(hz + s.H * 0.07, s.H * 0.14, "#C27A52", "#8F5036", sharp=0.5, base_freq=2)


# ------------------------- escenas -------------------------

def hero_a():
    s = Scene(1920, 1150, 11, 640)
    night_base(s, mw_cx=1200, mw_cy=320, mw_angle=-32)
    g = s.ground(s.horizon + 190, "#0B0F26", "#05070F", wav=26)
    s.stones(1560, s.horizon + 345, 5, 20, col="#161827", hi="#2A2D40", spread=1.5)
    s.cactus(1660, s.horizon + 340, 190, 32, col="#05070F", arms=2)
    s.dome(1340, s.horizon + 300, 190, "#3A3F58", lit=True, lightdir=(0.3, 0.5, 0.8))
    s.finish("a-hero-domo-noche", exposure=1.0, bloom=0.7)


def milky():
    s = Scene(1920, 960, 12, 700)
    night_base(s, mw_cx=1150, mw_cy=300, mw_angle=-38, stars=3400)
    s.ground(s.horizon + 120, "#0A0E24", "#04060E", wav=20)
    s.finish("cielo-via-lactea", exposure=1.05, bloom=0.6)


def card(name, seed, mode, obj):
    s = Scene(900, 1200, seed, 690)
    if mode == "night":
        night_base(s, mw_cx=450, mw_cy=260, mw_angle=-60, stars=1600)
        gt, gb = "#0D1128", "#05070F"
    elif mode == "dusk":
        dusk_base(s, sunx=620)
        gt, gb = "#3A2834", "#1A1218"
    else:
        gold_base(s, sunx=140)
        gt, gb = "#8A5A3E", "#4A2E20"
    s.ground(s.horizon + 150, gt, gb, wav=18)
    base = s.horizon + 300
    if mode == "gold":
        s.cactus(120, base + 120, 260, 40, col="#3B4A30", rim="#E9C08A", arms=2)
    else:
        s.cactus(110, base + 110, 230, 36, col="#0E1224" if mode == "night" else "#241A22", arms=2)
    if obj == "dome":
        s.dome(470, base, 200, "#E4D6C2" if mode != "night" else "#3A3F58",
               lightdir=(-0.55, 0.5, 0.65) if mode == "dusk" else (0.3, 0.5, 0.8), amb=0.3)
    else:
        s.cabin(270, base, 400, 230,
                wall="#7A5240" if mode == "gold" else ("#4A3428" if mode == "dusk" else "#2E2420"),
                side="#4E3428" if mode == "gold" else "#2A1E1A",
                roof="#2A2A30", lit=True, win="#F6D6A8" if mode == "gold" else "#FFC27A")
    s.stones(650, base + 140, 6, 26, col="#5A4A44" if mode != "night" else "#24263A",
             hi="#8A7464" if mode != "night" else "#343852", spread=1.2)
    s.finish(name, exposure=1.0 if mode == "night" else 0.95, bloom=0.6)


def quincho():
    s = Scene(1400, 875, 21, 470)
    dusk_base(s, sunx=980)
    s.ground(s.horizon + 120, "#3A2632", "#160E14", wav=14)
    im, dr, ss = s.layer()
    col = (40, 28, 26, 255)
    for (bx, by, bw) in ((700, 760, 190), (1180, 770, 180)):
        dr.rounded_rectangle([bx * ss, by * ss, (bx + bw) * ss, (by + 26) * ss], radius=10 * ss, fill=col)
        dr.rectangle([(bx + 18) * ss, (by + 20) * ss, (bx + 34) * ss, (by + 60) * ss], fill=col)
        dr.rectangle([(bx + bw - 34) * ss, (by + 20) * ss, (bx + bw - 18) * ss, (by + 60) * ss], fill=col)
    s.composite(im)
    s.fire(1010, 735, 70)
    s.stones(1010, 800, 10, 30, col="#3A2C2C", hi="#6A5048", spread=1.6)
    s.finish("fogon-atardecer", exposure=1.0, bloom=0.7)


def tinaja():
    s = Scene(1400, 875, 22, 520)
    night_base(s, mw_cx=700, mw_cy=180, mw_angle=-20, stars=2400)
    s.ground(s.horizon + 110, "#0C1027", "#05070F", wav=14)
    s.tub(760, 640, 230, 52)
    s.stones(330, 800, 8, 26, col="#22253A", hi="#33384F", spread=2.5)
    s.finish("tinaja-estrellas", exposure=1.0, bloom=0.7)


def hero_c():
    s = Scene(1920, 1015, 31, 600)
    s.sky(BLUE)
    s.stars(1800, bright=0.8, fade=0.6)
    s.milky_way(1300, 230, -24, s.H * 0.11, strength=0.32)
    hz = s.horizon
    s.mountains(hz + 4, s.H * 0.17, "#3B3762", "#322F58", "#6A5272", 0.3, sharp=0.6)
    s.mountains(hz + 70, s.H * 0.12, "#262A52", "#1C2044", sharp=0.4, base_freq=2)
    s.ground(hz + 170, "#141834", "#080A18", wav=20)
    s.dome(980, hz + 300, 170, "#3E4260", lightdir=(0.2, 0.6, 0.75))
    s.cabin(1250, hz + 270, 210, 130, wall="#2E2420", side="#221A18", roof="#1A1C26")
    s.cactus(560, hz + 340, 170, 28, col="#0B0E20", arms=2)
    s.finish("c-hero-hora-azul", exposure=1.0, bloom=0.7)


def jardin():
    s = Scene(1300, 1040, 32, 470)
    gold_base(s, sunx=200)
    s.ground(s.horizon + 120, "#A06A44", "#5A3826", wav=16)
    s.cactus(300, 930, 520, 70, col="#37422E", rim="#EFC88E", arms=2)
    s.cactus(820, 900, 380, 58, col="#323D2A", rim="#EFC88E", arms=2)
    s.cactus(1080, 880, 260, 46, col="#3A482E", rim="#EFC88E", arms=1)
    s.stones(560, 990, 5, 80, col="#8A6E5A", hi="#C8A888", stack=True)
    s.stones(950, 1000, 9, 40, col="#7A6250", hi="#B89A7E", spread=1.4)
    s.finish("jardin-piedra-cactus", exposure=0.95, bloom=0.4, grade=("#3A2A40", "#FFD8A8"))


def comfort():
    s = Scene(1920, 770, 33, 380)
    dusk_base(s, sunx=1500)
    s.ground(s.horizon + 110, "#3A2834", "#170F15", wav=14)
    s.cabin(1250, 640, 300, 170, wall="#4A3428", side="#2E201A", roof="#22222A")
    s.dome(1700, 640, 140, "#D8C8B4", lightdir=(-0.6, 0.45, 0.6))
    s.finish("domo-cabana-atardecer", exposure=0.95, bloom=0.6)


def parrales():
    s = Scene(1400, 1050, 41, 470)
    gold_base(s, sunx=1100)
    s.vineyard(760, s.horizon + 60, density=24)
    s.finish("parrales-atardecer", exposure=0.95, bloom=0.4, grade=("#3A2A40", "#FFD8A8"))


def sendero():
    s = Scene(1400, 1050, 42, 430)
    s.sky(DAY)
    hz = s.horizon
    s.mountains(hz + 4, s.H * 0.15, "#9EAABA", "#93A0B2", "#C9D4DE", 0.3, sharp=0.65)
    s.mountains(hz + 90, s.H * 0.17, "#B88C66", "#8E6446", sharp=0.55, base_freq=2)
    s.ground(hz + 250, "#C29C72", "#8E6A48", wav=24)
    s.trail(560, hz + 260, 120)
    s.scrub(160, hz + 260, s.H, col="#55603A", size=(4, 14))
    s.finish("sendero-cerros", exposure=0.92, bloom=0.3)


def piscina():
    s = Scene(1200, 1200, 51, 560)
    dusk_base(s, sunx=760)
    s.pool(s.horizon + 150, 1010)
    s.ground(1040, "#D6C2A6", "#A89078", tex=0.06, wav=0)
    s.finish("piscina-infinity", exposure=0.95, bloom=0.6)


SCENES = {
    "a-hero": hero_a, "milky": milky, "quincho": quincho, "tinaja": tinaja, "c-hero": hero_c,
    "jardin": jardin, "comfort": comfort, "parrales": parrales, "sendero": sendero, "piscina": piscina,
    "cards": lambda: [card("domo-anku", 61, "dusk", "dome"), card("domo-llullu", 62, "night", "dome"),
                      card("cabana-chanar", 63, "gold", "cabin"), card("cabana-antay", 64, "night", "cabin"),
                      card("cabana-cachi", 65, "dusk", "cabin")],
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        SCENES[n]()
