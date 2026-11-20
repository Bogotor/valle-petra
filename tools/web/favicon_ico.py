"""favicon.ico sin fondo: la estrella terracota sola, sin borde.

Uso: python3 tools/web/favicon_ico.py

Safari no lee favicons SVG y usa favicon.ico, que antes era la estrella sobre un
cuadrado terracota. Este .ico lleva solo la estrella terracota (fondo transparente),
igual que favicon.svg en modo claro. El .ico no cambia de color según el modo del
navegador (el SVG sí); el terracota se distingue en pestañas claras y oscuras.

Python puro, sin dependencias: dibuja la misma estrella de tools/logo/favicon.py
(4 puntas, lados cóncavos) con antialiasing por supermuestreo y guarda un .ico con
PNG de 16, 32 y 48 px, solo con IHDR, IDAT e IEND (sin metadatos).
Los íconos de Apple y Android siguen con fondo: iOS pinta de negro lo transparente.
"""
import os
import struct
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDAS = [os.path.join(RAIZ, "site/favicon.ico"), os.path.join(RAIZ, "brand/favicon/favicon.ico")]
TAMANOS = (16, 32, 48)
TERRACOTA = (0xAA, 0x45, 0x29)
CINTURA = 0.28        # igual que el favicon SVG: puntas algo más gruesas para tamaños chicos
R_ESTRELLA = 30       # en una grilla de 64, como favicon.svg (puntas en 2 y 62)
MUESTRAS = 4          # supermuestreo 4x4 por píxel


def estrella(r, c=32.0, pasos=24):
    """Polígono de la estrella (curvas cuadráticas aplanadas) en la grilla de 64."""
    puntas = [(c, c + r), (c + r, c), (c, c - r), (c - r, c)]
    pts = []
    for i in range(4):
        a, b = puntas[i], puntas[(i + 1) % 4]
        ctrl = (c + (a[0] + b[0] - 2 * c) * CINTURA, c + (a[1] + b[1] - 2 * c) * CINTURA)
        for k in range(pasos):
            t = k / pasos
            pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * ctrl[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * ctrl[1] + t * t * b[1]))
    return pts


def dentro(x, y, pol):
    res, j = False, len(pol) - 1
    for i in range(len(pol)):
        xi, yi = pol[i]
        xj, yj = pol[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            res = not res
        j = i
    return res


def cobertura(n, pol):
    """Fracción de cada píxel (n x n) cubierta por el polígono."""
    esc = 64 / n
    filas = []
    for py in range(n):
        fila = []
        for px in range(n):
            hits = 0
            for sy in range(MUESTRAS):
                for sx in range(MUESTRAS):
                    x = (px + (sx + 0.5) / MUESTRAS) * esc
                    y = (py + (sy + 0.5) / MUESTRAS) * esc
                    hits += dentro(x, y, pol)
            fila.append(hits / MUESTRAS ** 2)
        filas.append(fila)
    return filas


def png_rgba(n, filas):
    def bloque(tipo, cuerpo):
        return struct.pack(">I", len(cuerpo)) + tipo + cuerpo + struct.pack(">I", zlib.crc32(tipo + cuerpo))
    crudo = b"".join(b"\x00" + bytes(f) for f in filas)
    return (b"\x89PNG\r\n\x1a\n" + bloque(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0))
            + bloque(b"IDAT", zlib.compress(crudo, 9)) + bloque(b"IEND", b""))


def icono(n):
    # color terracota en todo el cuadro; la silueta de la estrella da la transparencia
    filas = [bytearray(b"".join(bytes(TERRACOTA) + bytes([round(a * 255)]) for a in fila))
             for fila in cobertura(n, estrella(R_ESTRELLA))]
    return png_rgba(n, filas)


def main():
    imgs = [icono(n) for n in TAMANOS]
    cabecera = struct.pack("<HHH", 0, 1, len(imgs))
    pos = 6 + 16 * len(imgs)
    entradas, datos = b"", b""
    for n, img in zip(TAMANOS, imgs):
        entradas += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(img), pos)
        pos += len(img)
        datos += img
    for ruta in SALIDAS:
        with open(ruta, "wb") as fh:
            fh.write(cabecera + entradas + datos)
        print(f"{os.path.relpath(ruta, RAIZ)}: {', '.join(f'{n}px' for n in TAMANOS)}, {os.path.getsize(ruta)} bytes")


if __name__ == "__main__":
    main()
