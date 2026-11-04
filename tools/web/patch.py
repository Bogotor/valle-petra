"""Aplica la identidad Valle Petra (logo, Fraunces completa, favicon) al standalone,
sin tocar fotos, textos ni estructura.

Uso: python3 -I patch.py <export-original-de-claude-design.html> <salida.html>

La entrada es el "Standalone" exportado desde el proyecto de Claude Design
(no está en el repo). El resultado está en design/claude-design/valle-petra-marca.html.
logos.json sale de brand/ (trazos del logo sin márgenes) y los .woff2 son
Fraunces completa (SOFT/WONK) recortada a latín.
"""
import base64
import json
import re
import sys
import urllib.parse
import os
import uuid

SRC, DST = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "..", "..", "brand")

raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

# Localizar las islas del bundle por su etiqueta, no por número de línea
def island(kind):
    for i, ln in enumerate(lines):
        if ln.strip() == f'<script type="__bundler/{kind}">':
            return i + 1
    raise SystemExit(f"no encontré {kind}")

i_man, i_tpl = island("manifest"), island("template")
manifest = json.loads(lines[i_man])
template = json.loads(lines[i_tpl])

changes = []


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"[{label}] se esperaba 1 coincidencia, hay {n}")
    changes.append(label)
    return text.replace(old, new)


# ---------- 1. Fraunces completa (opsz, wght, SOFT, WONK) ----------
old_faces = re.findall(r"(?:/\* [a-z-]+ \*/\n)?@font-face \{[^}]*font-family: 'Fraunces';[^}]*\}\n?", template)
old_uuids = set(re.findall(r'url\("([0-9a-f-]{36})"\)', "".join(old_faces)))
assert len(old_faces) == 12, len(old_faces)
for f in old_faces:
    template = template.replace(f, "", 1)
changes.append(f"quitadas {len(old_faces)} caras Fraunces sin SOFT/WONK")

UR = ("U+0000-00FF, U+0100-017F, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, "
      "U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")
new_faces = ""
for style, fname in (("normal", "Fraunces-vp.woff2"), ("italic", "Fraunces-Italic-vp.woff2")):
    u = str(uuid.uuid4())
    manifest[u] = {"mime": "font/woff2", "compressed": False,
                   "data": base64.b64encode(open(f"{HERE}/{fname}", "rb").read()).decode()}
    new_faces += ("@font-face {\n  font-family: 'Fraunces';\n  font-style: %s;\n  font-weight: 100 900;\n"
                  "  font-display: swap;\n  src: url(\"%s\") format('woff2');\n  unicode-range: %s;\n}\n"
                  % (style, u, UR))
# quitar del manifest las fuentes viejas que ya nadie usa
for u in old_uuids:
    if template.count(u) == 0:
        manifest.pop(u, None)
first = template.index("<style>")
template = template[:first + 7] + new_faces + template[first + 7:]
changes.append("fuentes Fraunces nuevas (normal + cursiva)")

# ---------- 2. Logos ----------
logos = json.load(open(f"{HERE}/logos.json"))


def logo_svg(kind, label=None):
    L = logos[kind]
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    return (f'<svg class="vp-logo vp-logo--{kind}" viewBox="0 0 {L["w"]} {L["h"]}" {a11y} '
            f'xmlns="http://www.w3.org/2000/svg"><path class="vp-logo-ink" d="{L["ink"]}"></path>'
            f'<path class="vp-logo-star" d="{L["star"]}"></path></svg>')


template = once(
    template,
    '<span class="brand-mark">Valle Petra</span>\n      <span class="brand-dot" aria-hidden="true"></span>',
    logo_svg("horizontal"),
    "logo en el menú",
)
template = once(
    template,
    '<h1 class="title-rise" id="heroTitle">\n      <span><span class="inner">Valle</span></span>\n'
    '      <span><span class="inner delay-2">Petra</span></span>\n    </h1>',
    '<h1 class="title-rise hero-logo" id="heroTitle">\n      <span><span class="inner">'
    + logo_svg("apilado") + '</span></span><span class="vp-sr">Valle Petra</span>\n    </h1>',
    "logo apilado en el encabezado",
)
template = once(
    template,
    '<div class="foot-mark">Valle Petra<span>.</span></div>',
    '<div class="foot-mark">' + logo_svg("horizontal", "Valle Petra") + "</div>",
    "logo en el pie",
)

template = once(
    template,
    '<p class="eyebrow hero-eyebrow reveal">Vicuña · Valle del Elqui · Chile</p>',
    '<p class="eyebrow hero-eyebrow reveal">Vicuña · Chile</p>',
    "texto de ubicación del encabezado",
)

BRAND_CSS = """
  /* ---------- Marca Valle Petra (logo definitivo + Fraunces con SOFT/WONK) ---------- */
  :root { --logo-ink: #AA4529; --logo-star: #E0AF7F; }
  html[data-theme="dark"] { --logo-ink: #EEEDF0; --logo-star: #E9CA94; }
  h1, h2, h3, h4, .serif, .hero-quote, .foot-mark {
    font-variation-settings: 'SOFT' 100, 'WONK' 1;
    font-optical-sizing: auto;
  }
  .vp-logo { display: block; }
  .vp-logo .vp-logo-ink { fill: currentColor; }
  .vp-logo .vp-logo-star { fill: var(--logo-star); }
  .brand { align-items: center; }
  .brand .vp-logo { height: 24px; width: auto; }
  @media (max-width: 480px) { .brand .vp-logo { height: 20px; } }
  header.site .brand { color: #FDEEDD; }
  header.site .brand .vp-logo-star { fill: #E9CA94; }
  header.site.scrolled .brand { color: var(--logo-ink); }
  header.site.scrolled .brand .vp-logo-star { fill: var(--logo-star); }
  .hero h1.hero-logo { line-height: 0; }
  .hero h1.hero-logo .vp-logo {
    width: clamp(210px, 28vw, 400px); height: auto; color: #FDEEDD;
    filter: drop-shadow(0 2px 18px rgba(20,12,8,.5));
  }
  .hero h1.hero-logo .vp-logo-star { fill: #E9CA94; }
  .foot .foot-mark .vp-logo { height: 20px; width: auto; color: var(--logo-ink); }
  .vp-sr {
    position: absolute !important; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
  }
"""
template = once(template, "\n  /* ---------- Reset ---------- */", BRAND_CSS + "\n  /* ---------- Reset ---------- */",
                "estilos de marca")

# ---------- 2b. Estabilidad de render (va al final para ganar a las reglas originales) ----------
RENDER_CSS = """<style>
  /* Sin desenfoque de fondo (backdrop-filter) en zonas que se repintan al bajar o pasar el mouse:
     en Mac (Chrome y Safari) obliga a re-desenfocar en cada cuadro y produce parpadeos.
     Se compensa con fondos un poco más opacos para mantener el mismo aspecto. */
  html[data-theme="dark"] #alojamientos,
  html[data-theme="dark"] #entorno {
    -webkit-backdrop-filter: none; backdrop-filter: none;
    background: rgba(22, 30, 59, 0.86) !important;
  }
  html[data-theme="dark"] .contact {
    -webkit-backdrop-filter: none; backdrop-filter: none;
    background: rgba(22, 30, 59, 0.86);
  }
  html[data-theme="dark"] footer.site {
    -webkit-backdrop-filter: none; backdrop-filter: none;
    background: rgba(17, 24, 50, 0.94);
  }
  header.site.scrolled { -webkit-backdrop-filter: none; backdrop-filter: none; background: rgba(253, 238, 221, 0.96); }
  html[data-theme="dark"] header.site.scrolled { background: rgba(17, 24, 50, 0.96); }
  .hero .btn-outline { -webkit-backdrop-filter: none; backdrop-filter: none; background: rgba(20, 12, 8, 0.34); }
  .lodge-nav { -webkit-backdrop-filter: none; backdrop-filter: none; background: rgba(20, 12, 8, 0.55); }
  .lodge-nav:hover { background: rgba(20, 12, 8, 0.75); }
  .lodge-tag { -webkit-backdrop-filter: none; backdrop-filter: none; background: rgba(20, 12, 8, 0.66); }
  .m-badge { -webkit-backdrop-filter: none; backdrop-filter: none; background: rgba(20, 12, 8, 0.66); }
  /* El visor de galería cerrado cubría toda la pantalla con un desenfoque de 0px siempre activo */
  .lightbox {
    -webkit-backdrop-filter: none; backdrop-filter: none;
    visibility: hidden;
    transition: opacity .25s ease, background-color .25s ease, visibility 0s linear .25s;
  }
  .lightbox[aria-hidden="false"] {
    visibility: visible;
    transition: opacity .25s ease, background-color .25s ease, visibility 0s;
  }
  /* Las tarjetas mantienen su capa: sin promover/degradar la foto al entrar y salir el mouse */
  .lodge, .m-block, .resv-card { will-change: transform; }
  .lodge-img, .m-block { isolation: isolate; }
  /* Liberar memoria de GPU una vez que terminó la animación de entrada */
  .reveal.in, .stagger.in > * { will-change: auto; }
</style>
"""
template = once(template, "</head>", RENDER_CSS + "</head>", "estabilidad de render")

HERO_CSS = """<style>
  /* ---------- Encabezado centrado sobre la foto principal ---------- */
  .hero { align-items: center; padding-block: 110px 200px; }
  .hero .wrap { display: flex; flex-direction: column; align-items: center; text-align: center; }
  .hero-eyebrow { margin-bottom: 28px; }
  .hero h1.hero-logo { display: flex; justify-content: center; }
  /* margen interno para que la sombra del logo no quede recortada por la máscara de la animación */
  .hero h1.hero-logo > span:first-child { padding: 24px; margin: -24px; }
  .hero h1.hero-logo .vp-logo {
    width: clamp(230px, 30vw, 440px);
    filter: drop-shadow(0 2px 12px rgba(20,12,8,.45));
  }
  .hero-sub, .hero-quote { margin-left: auto; margin-right: auto; }
  .hero-ctas { justify-content: center; }
  .hero-cta-hint { flex-basis: 100%; margin-left: 0; }
  /* modo claro: el aviso en el café oscuro de la página (sin la sombra oscura, que lo ensuciaría) */
  html[data-theme="light"] .hero-cta-hint { color: #2A1F1A; text-shadow: none; }
  /* el oscurecimiento que da contraste al texto ahora también va al centro */
  .hero-bg::after {
    background:
      radial-gradient(ellipse 62% 70% at 50% 52%, rgba(20,12,8,.5) 0%, rgba(20,12,8,.14) 60%, rgba(20,12,8,0) 100%),
      linear-gradient(180deg, rgba(20,12,8,.35) 0%, rgba(20,12,8,.10) 35%, rgba(20,12,8,.65) 100%);
  }
  html[data-theme="dark"] .hero-bg::after {
    background:
      radial-gradient(ellipse 62% 70% at 50% 52%, rgba(8,10,22,.66) 0%, rgba(8,10,22,.24) 60%, rgba(8,10,22,0) 100%),
      linear-gradient(180deg, rgba(8,10,22,.55) 0%, rgba(8,10,22,.15) 35%, rgba(8,10,22,.8) 100%);
  }
</style>
"""
template = once(template, "</head>", HERO_CSS + "</head>", "encabezado centrado")

# ---------- 3. Favicon (estrella) y color de tema ----------
fav_svg = open(f"{KIT}/favicon/favicon.svg").read()
fav_uri = "data:image/svg+xml," + urllib.parse.quote(fav_svg, safe=" :/=#;,()'")
touch = base64.b64encode(open(f"{KIT}/favicon/apple-touch-icon.png", "rb").read()).decode()
HEAD = (f'\n<link rel="icon" type="image/svg+xml" href="{fav_uri}">'
        f'\n<link rel="apple-touch-icon" href="data:image/png;base64,{touch}">'
        '\n<meta name="theme-color" content="#AA4529" media="(prefers-color-scheme: light)">'
        '\n<meta name="theme-color" content="#111832" media="(prefers-color-scheme: dark)">')
m = re.search(r'<meta name="description"[^>]*>', template)
template = template[:m.end()] + HEAD + template[m.end():]
changes.append("favicon + color de tema")

# ---------- 4. Reempaquetar ----------
lines[i_man] = json.dumps(manifest, separators=(",", ":"))
lines[i_tpl] = json.dumps(template, ensure_ascii=False).replace("</", "<\\u002F")

out = "\n".join(lines)
# vista previa mientras desempaqueta: logo apilado en vez de montañas con sol
thumb_old = re.search(r'<div id="__bundler_thumbnail">.*?</div>', out, re.S).group(0)
L = logos["apilado"]
thumb_new = ('<div id="__bundler_thumbnail"><svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
             'style="width:min(320px,60vw);height:auto"><path fill="#AA4529" d="%s"></path>'
             '<path fill="#E0AF7F" d="%s"></path></svg></div>' % (L["w"], L["h"], L["ink"], L["star"]))
out = out.replace(thumb_old, thumb_new, 1)
out = out.replace("<title>Valle Petra — Refugio boutique en el Valle del Elqui</title>",
                  "<title>Valle Petra — Refugio boutique en el Valle del Elqui</title>\n  "
                  f'<link rel="icon" type="image/svg+xml" href="{fav_uri}">', 1)
changes.append("vista previa de carga")
# imágenes como data: (igual que las fuentes) para que carguen en visores que bloquean blob:
out = out.replace(
    "if (FONT_MIME.test(entry.mime) && MIME_TOKEN.test(entry.mime)) {\n"
    "          // Strict artifact hosts allow font-src data: but not blob:.",
    "if ((FONT_MIME.test(entry.mime) || /^image[/]/i.test(entry.mime)) && MIME_TOKEN.test(entry.mime)) {\n"
    "          // Fuentes e imágenes como data: — los visores estrictos bloquean blob:.",
    1,
)
assert "/^image[/]/i.test(entry.mime)" in out
changes.append("imágenes como data: en vez de blob:")
open(DST, "w", encoding="utf-8").write(out)
print("\n".join(changes))
print("tamaño", len(out.encode()) // 1024, "KB")
