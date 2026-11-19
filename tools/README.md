# tools/

Scripts que generan los archivos de `brand/` y `design/`. Requieren Python 3.

```bash
pip install fonttools uharfbuzz skia-pathops brotli numpy scipy pillow
```

| Script | Qué hace | Salida |
| --- | --- | --- |
| `logo/build.py` | Arma el logo desde Fraunces: kerning, ligadura RA, LL encajadas, PETRA justificada y contorno "hecho a mano". `python3 build.py` reproduce el logo definitivo. | `logo/out/*.svg` |
| `logo/favicon.py` | Set de favicon con la estrella: SVG adaptable e íconos de Apple y Android con fondo (requiere `rsvg-convert`). El `.ico` lo hace `web/favicon_ico.py`. | `logo/out/favicon/` |
| `web/patch.py` | Aplica la marca al export "Standalone" de Claude Design. | `design/claude-design/valle-petra-marca.html` |
| `web/recursos.py` | Recursos de la landing: fotos reales (ProRAW/JPG/PNG) y del paquete del diseño a WebP en sRGB, sin EXIF ni GPS (lo verifica con `webpinfo`), más fuentes (Fraunces y Figtree, desde `tools/web/`) y favicon. Uso: `python3 -I tools/web/recursos.py --originales ../valle-petra-fotos-originales`. Requiere macOS (`sips`) y `brew install webp`. | `site/img/`, `site/fonts/`, favicon |
| `web/compartir.py` | Imagen de vista previa al compartir el enlace (Open Graph): logo apilado sobre terracota, 1200 × 630, PNG sin metadatos. Uso: `python3 tools/web/compartir.py`. Requiere macOS (`sips`). | `site/img/compartir.png` |
| `web/favicon_ico.py` | `favicon.ico` sin fondo: la estrella terracota con borde crema, en 16, 32 y 48 px (Safari usa el .ico porque no lee el SVG). Python puro. Uso: `python3 tools/web/favicon_ico.py`. | `site/favicon.ico`, `brand/favicon/favicon.ico` |
| `web/servidor.py` | Servidor local (solo `127.0.0.1`) que sirve `site/` aplicando las cabeceras de `site/_headers`, como Cloudflare Pages. Para probar la CSP antes de publicar. Uso: `python3 tools/web/servidor.py`. | `http://127.0.0.1:8766` |
| `fotos-simuladas/render.py` | Renders ficticios (cielo, cerros, domos, cabañas, piscina…). | `fotos-simuladas/out/` |

Las carpetas `out/` no se suben al repo: se regeneran.

## prompts/

| Prompt | Para qué | Cuándo usarlo |
| --- | --- | --- |
| `prompts/brand-dna-valle-petra.md` | Genera `design.md`, la guía visual para crear piezas nuevas (web, Instagram, impresos, fotografía). | Cuando la landing esté en código y las fotos reales estén elegidas. **Todavía no se ha corrido.** |
