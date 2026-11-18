# Valle Petra

Sitio web y marca de **Valle Petra**, refugio boutique entre piedra y cielo en Vicuña, Valle del Elqui, Chile.

- Instagram: [@vallepetraelqui](https://www.instagram.com/vallepetraelqui/)
- Reservas y consultas: [WhatsApp +56 9 9097 6513](https://wa.me/56990976513)

## Estado

| Parte | Estado |
| --- | --- |
| Logo e identidad | Listo (`brand/`) |
| Diseño de la landing | Listo como referencia (`design/claude-design/`) |
| Landing en código limpio | Lista (`site/`); faltan precios, capacidad y m² |
| Fotos reales | Interiores listos; faltan frontis, piscina, quincho, fogón y tinas (hay provisorias marcadas) |
| Publicación | Pendiente (GitHub Pages) |

## Estructura

```
valle-petra/
├── CLAUDE.md          contexto de marca y decisiones para Claude
├── site/              el sitio que se publica
│   └── img/           fotos optimizadas para web
├── brand/             kit del logo (SVG, PNG, PDF/EPS), favicon y ficha técnica
├── design/
│   ├── claude-design/ landing exportada de Claude Design, con la marca aplicada
│   ├── capturas/      vistas en modo claro y oscuro
│   └── fotos-simuladas/  renders ficticios para prototipos (no publicar)
└── tools/             scripts que generan logo, favicon, página y fotos simuladas
```

## Trabajar en tu computador

```bash
mkdir -p ~/Developer/portafolio && cd ~/Developer/portafolio
git clone https://github.com/Bogotor/valle-petra.git
```

Las fotos originales (ProRAW/HEIC) se guardan **fuera** del repo, por ejemplo en `~/Developer/portafolio/valle-petra-fotos-originales/`.

## Licencias

La fuente Fraunces se distribuye bajo SIL Open Font License 1.1 (`tools/logo/fonts/OFL.txt`).
El logo, las imágenes y el contenido de Valle Petra son de sus dueños; no se licencian para reutilizarse.
