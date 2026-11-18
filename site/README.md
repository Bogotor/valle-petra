# site/

Landing de Valle Petra en código limpio: HTML estático, CSS y JS sin dependencias ni paso de compilación.
Se pasó desde `design/claude-design/valle-petra-marca.html` (diseño aprobado) y se ve igual en modo claro y oscuro, en escritorio y en celular.

```
site/
├── index.html            toda la página; las tarjetas y galerías están escritas en el HTML
├── css/
│   ├── fuentes.css       Fraunces (con SOFT/WONK) e Inter, alojadas en fonts/
│   ├── tokens.css        colores de marca y de modo claro/oscuro, tipografías
│   └── estilos.css       estilos por sección, en el orden de la página
├── js/
│   ├── tema.js           selector Día / Noche (va en <head> para que no parpadee)
│   ├── animaciones.js    menú, aparición al bajar, escalonado y parallax
│   └── galerias.js       carrusel de cada alojamiento y visor de galería
├── fonts/                woff2 recortadas a latín
├── img/                  WebP sin metadatos (los genera tools/web/recursos.py)
├── _headers              cabeceras de seguridad que aplica Cloudflare Pages (no se publica)
└── favicon.*, site.webmanifest
```

## Verlo en tu computador

```bash
python3 -m http.server 8765 --directory site
```

Luego abre `http://localhost:8765`.

Para probarlo con las cabeceras de seguridad de `_headers`, como quedará en Cloudflare:

```bash
python3 tools/web/servidor.py
```

Abre `http://127.0.0.1:8766`. Si la Content-Security-Policy bloquea algo, el navegador lo avisa en la consola ("Refused to load…").

## Cabeceras de seguridad

Están en `_headers`, cada una explicada en el propio archivo. La CSP solo permite archivos del propio sitio y el iframe del mapa de Google. Por eso:

- No agregues `<script>` ni `style="…"` dentro del HTML: van en `js/` y `css/`.
- Si sumas un servicio externo (por ejemplo, un motor de reservas o un video), hay que agregar su dominio a la directiva que corresponda (`script-src`, `frame-src`, `img-src`…).

## Fotos

Las genera `tools/web/recursos.py` (ver `tools/README.md`). Todas quedan sin EXIF, GPS ni perfil de color.

| Carpeta | Contenido |
| --- | --- |
| `img/encabezado/` | Foto del valle en dos recortes: ancho (escritorio) y vertical 9:16 (celular) |
| `img/alojamientos/` | Fotos reales de interiores, en 800 y 1.200 px de ancho (`-sm` = tarjeta) |
| `img/espacios/` | Fotos reales de espacios comunes (por ahora, una de los jardines) |
| `img/provisorias/` | **Fotos de stock del diseño. No son de Valle Petra.** |
| `img/deco/` | Iconografía diaguita del fondo (solo modo claro) |

### Fotos provisorias

En el HTML llevan el atributo `data-provisoria` y se muestran con la etiqueta "Imagen referencial".
Faltan fotos reales de:

- Frontis de cada alojamiento: Anku, Llu Llu, Chañar, Antay y Cachi. Es la portada de cada tarjeta. Los interiores de Anku y Llu Llu son idénticos, igual que los de Antay y Cachi: solo cambia el frontis.
- Piscina (6), quincho (5), fogón (3) y tinas (4).
- Jardines: hay 1 foto real y 4 provisorias.

Para reemplazar una: agrega la foto original a `REALES` en `tools/web/recursos.py`, corre el script y, en `index.html`, cambia la ruta, quita `data-provisoria` y, si era la portada, también la etiqueta `ref-tag` y la clase `es-provisoria`.

## Datos pendientes de confirmar

Llevan `data-pendiente` en el HTML y se muestran entre corchetes:

- `[precio]` por noche de cada alojamiento. El diseño decía desde $80.000 (Chañar desde $120.000); otra fuente, $100.000–$150.000.
- `[capacidad]` y `[m²]` de cada alojamiento.

## Antes de lanzar

- `index.html` lleva `<meta name="robots" content="noindex">` para que los buscadores no muestren el sitio mientras tenga fotos provisorias y datos pendientes. Quítalo cuando esté listo para clientes.
- No bloquees el sitio con `robots.txt` (`Disallow`): el buscador dejaría de leer la página y no vería el `noindex`.

## Reglas

- Nada de `backdrop-filter`: en Mac (Chrome y Safari) causó parpadeos. Usar fondos semitransparentes.
- Contraste de 4,5:1 o más en el texto; controles de al menos 44 px de alto (en los puntos y flechas del carrusel, el área táctil se agranda con un pseudo-elemento invisible).
- Las fotos de `design/fotos-simuladas/` nunca van al sitio.
