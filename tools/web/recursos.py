"""Genera los recursos de site/: fotos en WebP sin metadatos, fuentes y favicon.

Uso (desde la raíz del repo):
    python3 -I tools/web/recursos.py --originales ../valle-petra-fotos-originales

Fuentes de las imágenes:
- Fotos reales: la carpeta de originales (ProRAW .DNG, .JPG, .PNG), fuera del repo.
  Se buscan por nombre de archivo en cualquier subcarpeta.
- Foto del encabezado, fotos provisorias y adornos diaguitas: salen del paquete
  design/claude-design/valle-petra-marca.html (van dentro como base64).

Proceso de cada foto:
1. sips (motor de imagen de macOS) decodifica, aplica la orientación, recorta/escala
   y convierte el color a sRGB. Convertir a sRGB ANTES de quitar metadatos evita que
   una foto en Display P3 o ECI-RGB se vea desaturada al perder su perfil de color.
2. cwebp -metadata none escribe el WebP sin EXIF, XMP, GPS ni perfil ICC.
3. Se verifica con webpinfo que el archivo no tenga bloques EXIF, XMP ni ICCP.

Requiere macOS (sips) y libwebp (brew install webp).
"""
import argparse
import base64
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
CALIDAD = "80"

# --- Fotos reales: archivo original -> nombre en site/img/ -------------------------
# Anku y Llu Llu comparten interior (son idénticos); Antay y Cachi también.
# Solo cambiará la foto del frontis de cada uno, que aún no está tomada.
REALES = {
    "alojamientos/domo-sala": "IMG_6242.DNG",
    "alojamientos/domo-dormitorio": "IMG_6243.DNG",
    "alojamientos/domo-cocina": "IMG_6237.DNG",
    "alojamientos/domo-bano": "IMG_6239.DNG",
    "alojamientos/chanar-living": "IMG_6259.JPG",
    "alojamientos/chanar-living-escalera": "IMG_6260.JPG",
    "alojamientos/chanar-cocina": "IMG_6249.DNG",
    "alojamientos/chanar-dormitorio-1": "IMG_6253.DNG",
    "alojamientos/chanar-dormitorio-1b": "IMG_6254.DNG",
    "alojamientos/chanar-dormitorio-2": "IMG_6263.JPG",
    "alojamientos/chanar-dormitorio-2b": "6536864D-4385-4BC1-9EE8-C5104E5DC3FB.png",
    "alojamientos/chanar-escalera": "IMG_6245.DNG",
    "alojamientos/chanar-bano": "IMG_6250.DNG",
    "alojamientos/cabana-terraza": "IMG_6265.JPG",
    "alojamientos/cabana-dormitorio": "4621E4C4-A8BB-4AB8-A845-5A02A09F5CD6.png",
    "alojamientos/cabana-comedor": "IMG_6225.DNG",
    "alojamientos/cabana-bano": "IMG_6228.DNG",
    "espacios/jardines-1": "IMG_6235.DNG",
}
ANCHOS_REALES = (800, 1200)  # tarjeta y visor de galería

# --- Imágenes que salen del paquete del diseño (uuid del manifiesto) -----------------
ENCABEZADO = "9903f11e-d6ae-4758-a0ee-3fc071e34478"  # foto propia del valle, 2560x1920

# Provisorias: fotos de stock del diseño, NO son de Valle Petra.
# Reemplazarlas por fotos reales en cuanto existan (mismo nombre de archivo).
PROVISORIAS = {
    "frontis-anku": "2a0a052d-c0df-46d4-8996-f455aefadf09",
    "frontis-llullu": "107b5c19-a3c5-45e2-81c0-1029cf39264f",
    "frontis-chanar": "e08c5042-7541-4960-9825-c8463697b078",
    "frontis-antay": "4eb3c355-d9c5-4c8a-9334-d463a82f1616",
    "frontis-cachi": "a55544c9-bf0f-4169-8c1a-b6d183bc28bf",
    "piscina-1": "9a600537-0f45-41d3-98d2-e2cc11ee5996",
    "piscina-2": "c21e9b3f-ff63-414c-ac02-d7b49354981a",
    "piscina-3": "18c84129-a6c5-47db-a816-23dc6233de18",
    "piscina-4": "c9181358-be23-45d7-a057-940b281549c9",
    "piscina-5": "a92126fc-5982-4df2-8be4-956b9cffe2f0",
    "piscina-6": "5abfd7cd-a793-4719-bb51-9663d3876ab1",
    "quincho-1": "4f9496cd-f1cb-4ea5-94c8-d7994c6e4481",
    "quincho-2": "4d9fa1c2-bd0d-43d9-b2be-7afd228db8c1",
    "quincho-3": "a1dfd772-2021-4b40-8065-56558b727ff0",
    "quincho-4": "885a6123-f101-425e-b100-cf6dd0dea134",
    "quincho-5": "ec49ffca-ccc3-44a4-ada9-b2b1b3204f03",
    "fogon-1": "ddf30441-1097-4239-b2dd-0781d2e8b8d6",
    "fogon-2": "04d020ca-5615-4c82-bc01-59e21e57ed51",
    "fogon-3": "9f267ce8-c43b-4e7c-9883-e734ae2c77c9",
    "tinas-1": "80e6aad5-54f0-4316-a43c-86c157c4f5f8",
    "tinas-2": "00d3d406-629b-47d2-ae46-6a52c5a719a8",
    "tinas-3": "68fad506-8773-45c7-a573-c0b1b2cf8443",
    "tinas-4": "de46c767-6636-4a1e-8a8b-b0674a3c3b6d",
    "jardines-2": "f210a61c-a6c7-4d16-8600-cc1b8747250c",
    "jardines-3": "ac94ea52-518e-4a38-87c7-cb62372353da",
    "jardines-4": "7439e3ac-e111-49e7-81f3-9a65e4c3df11",
    "jardines-5": "c6ed2506-d3af-4723-abac-22dd885ea80b",
}

# Iconografía diaguita (PNG con transparencia). Se muestra a <= 300 px.
DECO = {
    "experiencia-ave": "3403b45d-4dc4-40da-9e01-da087be7497c",
    "experiencia-diamante": "b94ab7ec-a726-42b0-8b54-e0efe71d5159",
    "experiencia-espiral": "522d556a-0894-42a2-a267-ccf2b0460b26",
    "espacios-ave": "e4fd0dcc-128c-46eb-9cda-282ad5abedd2",
    "ave-cruz": "0075f897-a6dd-4199-80f9-c26c9400b959",
    "espacios-diamante": "5bd98034-2735-47e8-9b8c-d96fd89ebcb2",
    "reservas-ave-espiral": "af50d1a1-b461-449a-956b-e62331ad0980",
    "reservas-ave-anillada": "04634286-0e5d-465c-97f2-0963302040ee",
}

# Figtree (texto) vive en tools/web/, descargada de Google Fonts (variable 300–700, OFL)
FUENTES = ("figtree-latin.woff2", "figtree-latin-ext.woff2")


def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"falló: {' '.join(cmd)}\n{r.stderr}")
    return r.stdout


def leer_manifiesto(ruta):
    lineas = open(ruta, encoding="utf-8").read().split("\n")
    for i, ln in enumerate(lineas):
        if ln.strip() == '<script type="__bundler/manifest">':
            return json.loads(lineas[i + 1])
    sys.exit("no encontré el manifiesto del paquete")


def dimensiones(ruta):
    """Ancho y alto de los píxeles guardados (sin aplicar la orientación)."""
    out = run("sips", "-g", "pixelWidth", "-g", "pixelHeight", ruta)
    vals = [int(l.split(":")[1]) for l in out.splitlines() if "pixel" in l]
    return vals[0], vals[1]


def orientacion(ruta):
    """Etiqueta Orientation (0x0112) de un DNG/TIFF, del EXIF de un JPEG o del eXIf de un PNG."""
    with open(ruta, "rb") as fh:
        d = fh.read(512 * 1024)
    if d[:2] in (b"II", b"MM"):
        tiff = d
    elif d[:4] == b"\x89PNG":
        i = d.find(b"eXIf")
        if i < 0:
            return 1
        tiff = d[i + 4:]
    else:
        i = d.find(b"Exif\x00\x00")
        if i < 0:
            return 1
        tiff = d[i + 6:]
    e = "<" if tiff[:2] == b"II" else ">"
    ifd = struct.unpack(e + "I", tiff[4:8])[0]
    n = struct.unpack(e + "H", tiff[ifd:ifd + 2])[0]
    for k in range(n):
        ent = tiff[ifd + 2 + 12 * k: ifd + 14 + 12 * k]
        if struct.unpack(e + "H", ent[:2])[0] == 0x0112:
            return struct.unpack(e + "H", ent[8:10])[0]
    return 1


GIRO = {3: 180, 6: 90, 8: 270}  # orientación EXIF -> grados en sentido horario


def a_png_srgb(origen, destino, ancho=None, recorte=None):
    """sips -> PNG temporal en sRGB, derecho, con recorte centrado (alto, ancho) o escalado a `ancho`.

    sips no aplica la orientación EXIF por sí solo (el ProRAW del iPhone viene con
    orientación 6), así que se gira explícitamente. sips escala ANTES de girar, por eso
    en fotos giradas 90/270 el ancho final se pide como alto.
    """
    o = orientacion(origen)
    w, h = dimensiones(origen)
    girada = o in (6, 8)
    ancho_final = h if girada else w
    cmd = ["sips", "-s", "format", "png", "--matchTo", SRGB]
    if recorte:
        if o != 1:
            sys.exit(f"recorte no soportado con orientación {o}: {origen}")
        cmd += ["--cropToHeightWidth", str(recorte[0]), str(recorte[1])]
    if ancho and ancho < ancho_final:  # nunca agrandar
        cmd += ["--resampleHeight" if girada else "--resampleWidth", str(ancho)]
    if o in GIRO:
        cmd += ["-r", str(GIRO[o])]
    run(*cmd, origen, "--out", destino)
    return destino


def a_webp(png, destino, alfa=False):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    cmd = ["cwebp", "-quiet", "-metadata", "none", "-q", CALIDAD, "-m", "6", "-sharp_yuv"]
    if alfa:
        cmd += ["-alpha_q", "100", "-exact"]
    run(*cmd, png, "-o", destino)
    verificar(destino)


def verificar(ruta):
    """Falla si el WebP conserva bloques de metadatos."""
    info = run("webpinfo", ruta)
    for bloque in ("EXIF", "XMP", "ICCP"):
        if f"Chunk {bloque}" in info:
            sys.exit(f"{ruta} conserva el bloque {bloque}")
    datos = open(ruta, "rb").read()
    for marca in (b"Exif", b"GPS", b"<x:xmpmeta"):
        if marca in datos:
            sys.exit(f"{ruta} contiene '{marca.decode()}'")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--originales", required=True, help="carpeta con las fotos originales")
    p.add_argument("--diseno", default=os.path.join(RAIZ, "design/claude-design/valle-petra-marca.html"))
    p.add_argument("--salida", default=os.path.join(RAIZ, "site"))
    a = p.parse_args()

    img = os.path.join(a.salida, "img")
    tmp = tempfile.mkdtemp(prefix="vp-recursos-")
    manifiesto = leer_manifiesto(a.diseno)
    hechos = []

    def del_paquete(uuid, ext):
        ruta = os.path.join(tmp, f"{uuid}.{ext}")
        if not os.path.exists(ruta):
            open(ruta, "wb").write(base64.b64decode(manifiesto[uuid]["data"]))
        return ruta

    # Índice de originales por nombre de archivo
    originales = {}
    for base, _, archivos in os.walk(a.originales):
        for f in archivos:
            originales.setdefault(f, os.path.join(base, f))

    try:
        # 1. Fotos reales en dos anchos (sin agrandar las que son más chicas)
        for nombre, archivo in REALES.items():
            if archivo not in originales:
                sys.exit(f"no encontré {archivo} en {a.originales}")
            fuente = originales[archivo]
            for ancho, sufijo in zip(ANCHOS_REALES, ("-sm", "")):
                png = a_png_srgb(fuente, os.path.join(tmp, f"r-{os.path.basename(nombre)}{sufijo}.png"), ancho)
                a_webp(png, os.path.join(img, f"{nombre}{sufijo}.webp"))
            hechos.append(nombre)

        # 2. Encabezado: recorte ancho (escritorio) y vertical 9:16 centrado (celular)
        enc = del_paquete(ENCABEZADO, "jpg")
        png = a_png_srgb(enc, os.path.join(tmp, "enc-escritorio.png"), 2400)
        a_webp(png, os.path.join(img, "encabezado/valle-escritorio.webp"))
        png = a_png_srgb(enc, os.path.join(tmp, "enc-celular.png"), recorte=(1920, 1080))
        a_webp(png, os.path.join(img, "encabezado/valle-celular.webp"))
        hechos.append("encabezado (2)")

        # 3. Provisorias, a su tamaño original (<= 1100 px)
        for nombre, uuid in PROVISORIAS.items():
            png = a_png_srgb(del_paquete(uuid, "jpg"), os.path.join(tmp, f"p-{nombre}.png"))
            a_webp(png, os.path.join(img, f"provisorias/{nombre}.webp"))
        hechos.append(f"provisorias ({len(PROVISORIAS)})")

        # 4. Adornos diaguitas a 600 px (2x de su tamaño en pantalla), con transparencia
        for nombre, uuid in DECO.items():
            png = a_png_srgb(del_paquete(uuid, "png"), os.path.join(tmp, f"d-{nombre}.png"), 600)
            a_webp(png, os.path.join(img, f"deco/{nombre}.webp"), alfa=True)
        hechos.append(f"adornos ({len(DECO)})")

        # 5. Fuentes desde tools/web: Fraunces completa (SOFT/WONK) y Figtree
        fuentes = os.path.join(a.salida, "fonts")
        os.makedirs(fuentes, exist_ok=True)
        shutil.copyfile(os.path.join(RAIZ, "tools/web/Fraunces-vp.woff2"), os.path.join(fuentes, "fraunces.woff2"))
        shutil.copyfile(os.path.join(RAIZ, "tools/web/Fraunces-Italic-vp.woff2"), os.path.join(fuentes, "fraunces-italic.woff2"))
        for nombre in FUENTES:
            shutil.copyfile(os.path.join(RAIZ, "tools/web", nombre), os.path.join(fuentes, nombre))
        hechos.append("fuentes (4)")

        # 6. Favicon (estrella) con rutas relativas, para que funcione en GitHub Pages
        fav = os.path.join(RAIZ, "brand/favicon")
        for f in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "icon-192.png", "icon-512.png"):
            shutil.copyfile(os.path.join(fav, f), os.path.join(a.salida, f))
        manifest = json.load(open(os.path.join(fav, "site.webmanifest")))
        for icono in manifest["icons"]:
            icono["src"] = icono["src"].lstrip("/")
        manifest["start_url"] = "./"
        with open(os.path.join(a.salida, "site.webmanifest"), "w") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        hechos.append("favicon")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("listo:", ", ".join(hechos[-6:]), f"+ {len(REALES)} fotos reales")


if __name__ == "__main__":
    main()
