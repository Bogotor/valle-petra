# Valle Petra — contexto para Claude

Refugio boutique familiar en Sector La Compañía, Vicuña, Valle del Elqui (Chile).
Este repo contiene el sitio web (landing de una página) y la identidad de marca.

## Negocio
- Alojamientos: 2 domos (**Anku**, **Llu Llu**) y 3 cabañas (**Chañar**, **Antay**, **Cachi**). Una sexta cabaña está en remodelación.
- Espacios: piscina infinity, quincho, fogón, tinas calientes, jardines de piedra y parrales.
- Público: parejas, familias y viajeros wellness. Competencia de referencia: Casa Molle.
- Conversión principal: **WhatsApp +56 9 9097 6513** (`https://wa.me/56990976513`). El motor de reservas queda para una fase posterior.
- Instagram: `@vallepetraelqui`.
- Pendiente de confirmar por el dueño: precios por noche (la página dice $80.000–$120.000; otra fuente decía $100.000–$150.000), capacidad y m² de cada alojamiento. No inventar datos: si falta uno, usar `[placeholder]`.

## Tono
- Español de Chile, trato de **tú**. Premium pero cercano; nunca lenguaje de camping ni de alojamiento masivo.
- Evocador: piedra, cielo, familia (los tres pilares de la marca). Espiritual sin ser esotérico.
- La sustentabilidad es un valor central, no una nota al pie.

## Identidad visual (ver `brand/FICHA-TECNICA.md`)
- **Logo:** wordmark VALLE / PETRA con estrella de 4 puntas. Son trazos vectoriales: nunca reescribirlo con la fuente. Usar los SVG de `brand/svg/`.
  - Apilado = logo principal. Horizontal = menú y pie. `currentColor` = cuando el color lo controla el CSS.
  - Isotipo/favicon: la estrella sola (`brand/favicon/`).
- **Colores** (fondo / letras / estrella):
  - Modo claro: `#FDEEDD` / `#AA4529` / `#E0AF7F`
  - Modo oscuro: `#111832` / `#EEEDF0` / `#E9CA94`
  - Principal sobre terracota: `#AA4529` / `#FDEEDD` / `#E9CA94`
  - Apoyo: adobe `#A03E25`, oro arena `#D6B98B`, texto oscuro `#2A1F1A`.
- **Tipografía:** Fraunces (OFL) en títulos con `font-variation-settings: 'SOFT' 100, 'WONK' 1` y `font-optical-sizing: auto`; Inter en texto. La Fraunces de Google Fonts "estática" no trae SOFT/WONK: usar la variable completa.

## Decisiones técnicas
- Landing de una sola página primero; multipágina más adelante.
- Fotos: originales ProRAW fuera del repo. En `site/img/` solo versiones web (WebP/AVIF), de unos 1.600 px para tarjetas y 2.400 px para el encabezado.
- Encabezado: dos recortes de la misma foto (ancho para escritorio, vertical para celular) con `<picture>` + `srcset` + `object-fit: cover`.
- **No usar `backdrop-filter`** en zonas grandes, sobre fotos que se animan ni en capas ocultas: en Mac (Chrome y Safari) causó parpadeos al bajar y pasar el mouse. Usar fondos semitransparentes.
- Modo claro y oscuro con `html[data-theme]`; el oscuro va con el cielo estrellado.
- Las fotos de `design/fotos-simuladas/` son renders ficticios: **nunca** publicarlas en el sitio.
- Contraste mínimo 4.5:1 en texto; botones de al menos 44 px de alto.

## Estructura
- `site/` — el sitio que se publica (código limpio: HTML, CSS, JS, `img/`).
- `brand/` — kit del logo, favicon y ficha técnica.
- `design/` — referencias: página exportada de Claude Design con la marca aplicada, capturas y fotos simuladas.
- `tools/` — scripts que generan el logo, el favicon, la página de referencia y las fotos simuladas.
