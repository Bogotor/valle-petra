"""Valle Petra — construcción del logo (dirección C, Nouveau del Elqui).

Pipeline: Fraunces (OFL) instanciada -> layout con kerning HarfBuzz ->
ajustes manuales (tracking justificado, ligadura LL) -> deformación suave
"hecha a mano" -> unión booleana de contornos -> SVG vectorial limpio.

Uso:  python3 build.py        (genera el logo definitivo en tools/logo/out/)
Requiere: pip install fonttools uharfbuzz skia-pathops
"""
import math
import os
import random
import sys
import uharfbuzz as hb
import pathops
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.basePen import AbstractPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONT = os.path.join(HERE, "fonts", "Fraunces-VP.ttf")
if not os.path.exists(FONT):
    # instancia fija de Fraunces con los ejes del logo
    _vf = TTFont(os.path.join(HERE, "fonts", "Fraunces[SOFT,WONK,opsz,wght].ttf"))
    instancer.instantiateVariableFont(_vf, {"opsz": 144, "wght": 430, "SOFT": 100, "WONK": 1}).save(FONT)

# Paleta Valle Petra
TERRACOTA = "#AA4529"
CREMA = "#FDEEDD"
ORO_TIERRA = "#E0AF7F"
ADOBE = "#A03E25"
NAVY = "#111832"
MARFIL = "#EEEDF0"
ORO_NOCHE = "#E9CA94"

# Parámetros de oficio
WOBBLE_AMP = float(sys.argv[1]) if len(sys.argv) > 1 else 9.0   # unidades (cap = 1400); 9 = logo definitivo
WOBBLE_SEED = 7
LL_OVERLAP = 18     # las dos L se encajan (kerning óptico)
RA_FUSE = -46       # ligadura: R y A comparten un mismo remate
LINE_GAP = 210      # interlineado entre VALLE y PETRA
BASE_TRACK = 40     # tracking base

font = TTFont(FONT)
glyphset = font.getGlyphSet()
cmap = font.getBestCmap()
CAP = font["OS/2"].sCapHeight

blob = hb.Blob.from_file_path(FONT)
hbfont = hb.Font(hb.Face(blob))


class WarpPen(AbstractPen):
    """Aplica una función de deformación a todos los puntos (anclas y manijas)."""

    def __init__(self, out, fn):
        self.out, self.fn = out, fn

    def _m(self, pts):
        return [None if p is None else self.fn(p) for p in pts]

    def moveTo(self, p): self.out.moveTo(self.fn(p))
    def lineTo(self, p): self.out.lineTo(self.fn(p))
    def qCurveTo(self, *pts): self.out.qCurveTo(*self._m(pts))
    def curveTo(self, *pts): self.out.curveTo(*self._m(pts))
    def closePath(self): self.out.closePath()
    def endPath(self): self.out.endPath()
    def addComponent(self, g, t): raise NotImplementedError


def make_field(seed, amp):
    """Campo de desplazamiento suave (suma de senos): deforma el plano entero,
    así las curvas siguen siendo suaves pero pierden la perfección mecánica."""
    rnd = random.Random(seed)
    waves = []
    for _ in range(5):
        k = rnd.uniform(1 / 520, 1 / 180)
        ang = rnd.uniform(0, math.tau)
        ph = rnd.uniform(0, math.tau)
        waves.append((k * math.cos(ang), k * math.sin(ang), ph))

    def fn(p):
        x, y = p
        dx = sum(math.sin(math.tau * (kx * x + ky * y) + ph) for kx, ky, ph in waves)
        dy = sum(math.cos(math.tau * (ky * x - kx * y) + ph * 1.3) for kx, ky, ph in waves)
        s = amp / len(waves) * 1.6
        return (x + dx * s, y + dy * s)

    return fn


def shape(text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((font.getGlyphName(info.codepoint), pos.x_advance, pos.x_offset))
    return out


def ink_bounds(gname):
    p = pathops.Path()
    glyphset[gname].draw(p.getPen())
    return p.bounds  # xmin, ymin, xmax, ymax


def line_layout(text, track, extra=None):
    """Devuelve [(glyph, x)] usando kerning + tracking + ajustes por par."""
    extra = extra or {}
    glyphs = shape(text)
    xs, x = [], 0
    for i, (g, adv, off) in enumerate(glyphs):
        xs.append((g, x + off))
        x += adv + track
        if i + 1 < len(glyphs):
            x += extra.get(text[i:i + 2], 0)
    # ancho de tinta real
    first_g, first_x = xs[0]
    last_g, last_x = xs[-1]
    left = first_x + ink_bounds(first_g)[0]
    right = last_x + ink_bounds(last_g)[2]
    return xs, left, right


def solve_track(text, target_width, extra):
    lo, hi = -100, 600
    for _ in range(40):
        mid = (lo + hi) / 2
        _, l, r = line_layout(text, mid, extra)
        if r - l < target_width:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ll_extra():
    """Calcula el kerning para que el brazo de la 1ª L toque el pie de la 2ª."""
    g = cmap[ord("L")]
    xmin, _, xmax, _ = ink_bounds(g)
    adv = font["hmtx"][g][0]
    # distancia natural entre tinta de L y tinta de la siguiente L
    gap = (adv - xmax) + xmin
    return -(gap + BASE_TRACK) - LL_OVERLAP


def star_path(cx, cy, r, waist=0.2):
    """Estrella de 4 puntas con lados cóncavos (destello del cielo del Elqui)."""
    p = pathops.Path()
    pen = p.getPen()
    pts = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
    pen.moveTo(pts[0])
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        # control hacia el centro: lados cóncavos
        c = (cx + (a[0] + b[0] - 2 * cx) * waist, cy + (a[1] + b[1] - 2 * cy) * waist)
        pen.qCurveTo(c, b)
    pen.closePath()
    return p


def build(mode="stacked"):
    warp = make_field(WOBBLE_SEED, WOBBLE_AMP)
    letters = pathops.Path()
    pen = letters.getPen()

    extra_valle = {"LL": ll_extra()}
    if mode == "stacked":
        xs1, l1, r1 = line_layout("VALLE", BASE_TRACK, extra_valle)
        w1 = r1 - l1
        # PETRA se justifica al mismo ancho de tinta que VALLE
        t2 = solve_track("PETRA", w1, {"RA": RA_FUSE})
        xs2, l2, r2 = line_layout("PETRA", t2, {"RA": RA_FUSE})
        lines = [(xs1, l1, CAP + LINE_GAP), (xs2, l2, 0)]
        width = w1
    else:  # horizontal: VALLE ✦ PETRA
        xs1, l1, r1 = line_layout("VALLE", BASE_TRACK, extra_valle)
        xs2, l2, r2 = line_layout("PETRA", BASE_TRACK, {"RA": RA_FUSE - 30})
        gap = CAP * 0.95
        off2 = (r1 - l1) + gap - l2 + l1
        lines = [(xs1, l1, 0), ([(g, x + off2) for g, x in xs2], l1, 0)]
        width = (r1 - l1) + gap + (r2 - l2)

    for xs, left, base in lines:
        for g, x in xs:
            tp = TransformPen(WarpPen(pen, warp), (1, 0, 0, 1, x - left, base))
            glyphset[g].draw(tp)

    clean = pathops.simplify(letters, clockwise=False)

    # Estrella
    if mode == "stacked":
        r = CAP * 0.17
        star = star_path(width / 2, CAP * 2 + LINE_GAP + r + CAP * 0.2, r)
    else:
        r = CAP * 0.2
        star = star_path((r1 - l1) + (CAP * 0.95) / 2, CAP / 2, r)
    return clean, star, width


def to_d(path, height, pad):
    svgpen = SVGPathPen(None, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    # voltear eje Y (fuente: y hacia arriba; SVG: y hacia abajo)
    path.draw(TransformPen(svgpen, (1, 0, 0, -1, pad, height + pad)))
    return svgpen.getCommands()


def write_svg(name, letters, star, width, top, fg, star_fg, bg=None, pad=None, square=False):
    pad = pad if pad is not None else CAP * 0.42
    height = top
    W, H = width + 2 * pad, height + 2 * pad
    dx = dy = 0
    if square:
        S = max(W, H) * 1.1
        dx, dy = (S - W) / 2, (S - H) / 2
        W = H = S
    d_letters = to_d(letters, height, pad)
    d_star = to_d(star, height, pad)
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'role="img" aria-label="Valle Petra">'
        f"<title>Valle Petra</title>{bg_rect}"
        f'<g transform="translate({dx:.1f} {dy:.1f})">'
        f'<path fill="{fg}" d="{d_letters}"/>'
        f'<path fill="{star_fg}" d="{d_star}"/></g></svg>'
    )
    with open(f"{OUT}/{name}.svg", "w") as fh:
        fh.write(svg)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    L, S, w = build("stacked")
    top = S.bounds[3]
    write_svg("vp-apilado-claro", L, S, w, top, TERRACOTA, ORO_TIERRA)
    write_svg("vp-apilado-terracota", L, S, w, top, CREMA, ORO_NOCHE)
    write_svg("vp-apilado-oscuro", L, S, w, top, MARFIL, ORO_NOCHE)
    write_svg("vp-apilado-currentcolor", L, S, w, top, "currentColor", "currentColor")
    write_svg("_prev-apilado-claro", L, S, w, top, TERRACOTA, ORO_TIERRA, bg=CREMA)
    write_svg("_prev-apilado-terracota", L, S, w, top, CREMA, ORO_NOCHE, bg=TERRACOTA)
    write_svg("_prev-apilado-oscuro", L, S, w, top, MARFIL, ORO_NOCHE, bg=NAVY)
    write_svg("vp-avatar-instagram", L, S, w, top, CREMA, ORO_NOCHE, bg=TERRACOTA, square=True)
    write_svg("vp-avatar-instagram-oscuro", L, S, w, top, MARFIL, ORO_NOCHE, bg=NAVY, square=True)

    Lh, Sh, wh = build("horizontal")
    toph = CAP
    write_svg("vp-horizontal-claro", Lh, Sh, wh, toph, TERRACOTA, ORO_TIERRA)
    write_svg("vp-horizontal-oscuro", Lh, Sh, wh, toph, MARFIL, ORO_NOCHE)
    write_svg("vp-horizontal-currentcolor", Lh, Sh, wh, toph, "currentColor", "currentColor")
    write_svg("_prev-horizontal-claro", Lh, Sh, wh, toph, TERRACOTA, ORO_TIERRA, bg=CREMA)
    write_svg("_prev-horizontal-oscuro", Lh, Sh, wh, toph, MARFIL, ORO_NOCHE, bg=NAVY)
    print("ok", round(w), round(top), "track LL", round(ll_extra()))
