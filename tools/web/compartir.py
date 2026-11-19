"""Imagen para compartir el enlace (Open Graph): logo apilado sobre terracota, 1200 x 630.

Uso: python3 tools/web/compartir.py

Es la imagen que muestran WhatsApp, iMessage, Instagram y otros al pegar el enlace
del sitio. Usa el logo de brand/png/ (trazos vectoriales ya rasterizados, nunca la
fuente) en la combinación principal de la marca: fondo terracota #AA4529, letras
crema y estrella oro.

Requiere macOS (sips, para achicar el logo con buena calidad). El resto es Python
sin dependencias: compone sobre el fondo y escribe un PNG solo con IHDR, IDAT e
IEND, es decir, sin metadatos.
"""
import os
import struct
import subprocess
import sys
import tempfile
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO = os.path.join(RAIZ, "brand/png/vp-apilado-terracota.png")  # crema y oro, fondo transparente
SALIDA = os.path.join(RAIZ, "site/img/compartir.png")
ANCHO, ALTO = 1200, 630
ALTO_LOGO = 380  # deja el logo completo aunque la app recorte la imagen a un cuadrado
FONDO = (0xAA, 0x45, 0x29)  # terracota


def leer_png(ruta):
    """Devuelve (ancho, alto, filas RGBA) de un PNG de 8 bits RGBA sin entrelazar."""
    datos = open(ruta, "rb").read()
    pos, idat, cabecera = 8, b"", None
    while pos < len(datos):
        largo, tipo = struct.unpack(">I4s", datos[pos:pos + 8])
        cuerpo = datos[pos + 8:pos + 8 + largo]
        if tipo == b"IHDR":
            cabecera = struct.unpack(">IIBBBBB", cuerpo)
        elif tipo == b"IDAT":
            idat += cuerpo
        pos += 12 + largo
    ancho, alto, profundidad, color, _, _, entrelazado = cabecera
    if (profundidad, color, entrelazado) != (8, 6, 0):
        sys.exit(f"PNG no soportado: profundidad {profundidad}, color {color}, entrelazado {entrelazado}")
    crudo = zlib.decompress(idat)
    bpp, paso = 4, ancho * 4
    filas, anterior, i = [], bytearray(paso), 0
    for _ in range(alto):
        filtro, fila = crudo[i], bytearray(crudo[i + 1:i + 1 + paso])
        i += 1 + paso
        for x in range(paso):
            a = fila[x - bpp] if x >= bpp else 0
            b = anterior[x]
            c = anterior[x - bpp] if x >= bpp else 0
            if filtro == 1:
                fila[x] = (fila[x] + a) & 255
            elif filtro == 2:
                fila[x] = (fila[x] + b) & 255
            elif filtro == 3:
                fila[x] = (fila[x] + (a + b) // 2) & 255
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                fila[x] = (fila[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        filas.append(fila)
        anterior = fila
    return ancho, alto, filas


def escribir_png(ruta, ancho, alto, filas_rgb):
    def bloque(tipo, cuerpo):
        return struct.pack(">I", len(cuerpo)) + tipo + cuerpo + struct.pack(">I", zlib.crc32(tipo + cuerpo))
    crudo = b"".join(b"\x00" + bytes(f) for f in filas_rgb)
    with open(ruta, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(bloque(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)))
        fh.write(bloque(b"IDAT", zlib.compress(crudo, 9)))
        fh.write(bloque(b"IEND", b""))


def main():
    with tempfile.TemporaryDirectory(prefix="vp-compartir-") as tmp:
        chico = os.path.join(tmp, "logo.png")
        r = subprocess.run(["sips", "--resampleHeight", str(ALTO_LOGO), LOGO, "--out", chico],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(r.stderr)
        w, h, logo = leer_png(chico)

    lienzo = [bytearray(bytes(FONDO) * ANCHO) for _ in range(ALTO)]
    x0, y0 = (ANCHO - w) // 2, (ALTO - h) // 2
    for y, fila in enumerate(logo):
        destino = lienzo[y0 + y]
        for x in range(w):
            r_, g, b, a = fila[x * 4:x * 4 + 4]
            if a:
                k = (x0 + x) * 3
                for canal, valor in enumerate((r_, g, b)):
                    destino[k + canal] = (valor * a + FONDO[canal] * (255 - a) + 127) // 255
    escribir_png(SALIDA, ANCHO, ALTO, lienzo)
    print(f"{os.path.relpath(SALIDA, RAIZ)}: {ANCHO}x{ALTO}, logo {w}x{h}, {os.path.getsize(SALIDA) // 1024} KB")


if __name__ == "__main__":
    main()
