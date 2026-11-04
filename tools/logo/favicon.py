"""Valle Petra — set de favicon a partir de la estrella del logo."""
import os
import subprocess
import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TERRACOTA = "#AA4529"
ORO_NOCHE = "#E9CA94"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "favicon")


def star_path(cx, cy, r, waist):
    """Misma estrella del logo: 4 puntas, lados cóncavos."""
    p = pathops.Path()
    pen = p.getPen()
    pts = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
    pen.moveTo(pts[0])
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        c = (cx + (a[0] + b[0] - 2 * cx) * waist, cy + (a[1] + b[1] - 2 * cy) * waist)
        pen.qCurveTo(c, b)
    pen.closePath()
    return p


def d(path):
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    path.draw(pen)
    return pen.getCommands()


# En tamaños chicos la estrella se engrosa un poco (waist 0.28 vs 0.2 del logo)
# para que las puntas no desaparezcan.
STAR_SOLO = d(star_path(32, 32, 30, 0.28))
STAR_TILE = d(star_path(32, 32, 22, 0.28))


def svg_adaptativo():
    """Favicon SVG: estrella sola; terracota en pestañas claras, oro en oscuras."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f"<style>path{{fill:{TERRACOTA}}}"
        f"@media (prefers-color-scheme:dark){{path{{fill:{ORO_NOCHE}}}}}</style>"
        f'<path d="{STAR_SOLO}"/></svg>'
    )


def svg_tile(radius):
    """Estrella oro sobre fondo terracota (ico, Apple, Android)."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="{radius}" fill="{TERRACOTA}"/>'
        f'<path fill="{ORO_NOCHE}" d="{STAR_TILE}"/></svg>'
    )


def png(svg_file, size, out):
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), svg_file, "-o", out], check=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/favicon.svg", "w") as f:
        f.write(svg_adaptativo())
    with open(f"{OUT}/_tile-redondeado.svg", "w") as f:
        f.write(svg_tile(14))
    with open(f"{OUT}/_tile-cuadrado.svg", "w") as f:
        f.write(svg_tile(0))  # iOS y Android aplican su propia máscara

    for s in (16, 32, 48):
        png(f"{OUT}/_tile-redondeado.svg", s, f"{OUT}/_ico-{s}.png")
    subprocess.run(["convert", f"{OUT}/_ico-16.png", f"{OUT}/_ico-32.png", f"{OUT}/_ico-48.png",
                    f"{OUT}/favicon.ico"], check=True)

    png(f"{OUT}/_tile-cuadrado.svg", 180, f"{OUT}/apple-touch-icon.png")
    png(f"{OUT}/_tile-cuadrado.svg", 192, f"{OUT}/icon-192.png")
    png(f"{OUT}/_tile-cuadrado.svg", 512, f"{OUT}/icon-512.png")

    with open(f"{OUT}/site.webmanifest", "w") as f:
        f.write(
            '{\n  "name": "Valle Petra",\n  "short_name": "Valle Petra",\n'
            '  "icons": [\n'
            '    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},\n'
            '    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}\n'
            "  ],\n"
            f'  "theme_color": "{TERRACOTA}",\n  "background_color": "#FDEEDD",\n'
            '  "display": "standalone"\n}\n'
        )

    with open(f"{OUT}/head.html", "w") as f:
        f.write(
            "<!-- Pegar dentro de <head>. Archivos en la raíz del sitio. -->\n"
            '<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
            '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
            '<link rel="manifest" href="/site.webmanifest">\n'
            f'<meta name="theme-color" content="{TERRACOTA}">\n'
        )

    for tmp in ("_ico-16.png", "_ico-32.png", "_ico-48.png", "_tile-redondeado.svg", "_tile-cuadrado.svg"):
        os.remove(f"{OUT}/{tmp}")
    print("ok", sorted(os.listdir(OUT)))
