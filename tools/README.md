# tools/

Scripts que generan los archivos de `brand/` y `design/`. Requieren Python 3.

```bash
pip install fonttools uharfbuzz skia-pathops brotli numpy scipy pillow
```

| Script | Qué hace | Salida |
| --- | --- | --- |
| `logo/build.py` | Arma el logo desde Fraunces: kerning, ligadura RA, LL encajadas, PETRA justificada y contorno "hecho a mano". `python3 build.py` reproduce el logo definitivo. | `logo/out/*.svg` |
| `logo/favicon.py` | Set de favicon con la estrella (requiere `rsvg-convert` e ImageMagick). | `logo/out/favicon/` |
| `web/patch.py` | Aplica la marca al export "Standalone" de Claude Design. | `design/claude-design/valle-petra-marca.html` |
| `fotos-simuladas/render.py` | Renders ficticios (cielo, cerros, domos, cabañas, piscina…). | `fotos-simuladas/out/` |

Las carpetas `out/` no se suben al repo: se regeneran.
