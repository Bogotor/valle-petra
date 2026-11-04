# BRAND DNA — Valle Petra: generación de `design.md`

## ROL

Actúa como Senior Brand Designer, Director de Arte y Design Systems Architect.

Tu misión es **documentar el sistema visual que Valle Petra ya decidió** y convertirlo en reglas concretas dentro de `design.md`, en la raíz del repo. Con ese archivo, otro agente de IA debe poder crear piezas coherentes con la marca sin explicaciones adicionales.

No rediseñes la marca ni propongas una identidad nueva. Cuando falte una regla, puedes proponerla, pero marcada como propuesta.

## 1. FUENTES Y PRIORIDAD

Si dos fuentes se contradicen, manda la que está más arriba:

1. **Decisiones aprobadas:** `CLAUDE.md` y `brand/FICHA-TECNICA.md`.
2. **Recursos oficiales:** `brand/svg/`, `brand/png/`, `brand/imprenta/`, `brand/favicon/`.
3. **Diseño aprobado de la landing:** `design/claude-design/valle-petra-marca.html` y `design/capturas/`. Sirve para composición, componentes, espaciado, movimiento y tratamiento de los modos claro y oscuro.
   - Excepción: las fotos de alojamientos y espacios de esa página son de stock y no son del Elqui. No saques reglas fotográficas de ellas.
4. **Fotos reales** en `site/img/`, cuando existan.
5. **Inspiración externa** (referencias de Pinterest, prototipos A/B/C de Claude Design): solo como patrones generales. Nunca como regla de marca ni para copiar.

**No uses como evidencia** `design/fotos-simuladas/`: son renders ficticios.

Lee los valores exactos desde los archivos (CSS dentro del HTML, SVG, ficha técnica). No estimes colores ni tamaños a partir de capturas o fotos. Si un valor solo se puede estimar, márcalo así.

## 2. NIVELES DE CERTEZA

Cada regla de `design.md` lleva uno:

- **Aprobada:** la decidió el dueño (fuentes 1 y 2).
- **Observada:** aparece en el diseño aprobado de la landing (fuente 3).
- **Propuesta:** recomendación nueva para cubrir un hueco. Escríbela como `[Propuesta]`. Nunca la presentes como regla vigente.

## 3. QUÉ ANALIZAR

### 3.1. Color
- Tokens semánticos para modo claro y oscuro: `color.background.*`, `color.surface.*`, `color.text.*`, `color.brand.*`, `color.accent`, `color.border`, más los de logo (letras y estrella por modo).
- Equivalencia con las variables CSS que usa la página (`--bg`, `--fg`, `--accent`, `--surface`, etc.).
- Contraste calculado de los pares texto/fondo principales; mínimo 4.5:1 en texto.
- Transparencias y degradados observados (oscurecimiento sobre fotos, fundido del encabezado).

### 3.2. Tipografía
- Fraunces (variable completa, con `SOFT` y `WONK`) para títulos e Inter para texto. Ejes, pesos y cursiva real.
- Escala desde el CSS (`clamp()` de h1–h4, `.lead`, `.eyebrow`), interlineado y espaciado entre letras.
- Uso de mayúsculas (etiquetas o *eyebrows*) y tratamiento de palabras destacadas.

### 3.3. Composición, retícula y espaciado
- Ancho máximo del contenido, márgenes laterales, espaciado entre secciones y entre tarjetas.
- Jerarquía de lectura, proporción imagen/texto y comportamiento en celular.

### 3.4. Componentes y lenguaje gráfico
- Web: menú, encabezado, botones, tarjetas de alojamiento, bloques de espacios, etiquetas, tablas de información, botón flotante de WhatsApp y selector de modo.
- Radios, bordes, sombras e iconografía (trazo fino).
- Elementos distintivos: la estrella, el cielo estrellado del modo oscuro y los motivos tipo petroglifo diaguita del modo claro.
  - Su origen y aprobación no están claros: documéntalos como **Observados — pendientes de validar**. Son iconografía de un pueblo originario, así que el dueño debe decidir si se usan y cómo.

### 3.5. Movimiento (solo web)
- Lo observado en el CSS y JS: aparición al bajar, entrada del logo, elevación de tarjetas al pasar el mouse, zoom de fotos y paralaje del encabezado. Incluye duraciones y curvas reales.
- Restricciones técnicas de `CLAUDE.md`: no usar `backdrop-filter`, y respetar `prefers-reduced-motion`.

### 3.6. Dirección fotográfica
- Las fotos reales se toman en iPhone 17 Pro, en ProRAW. Define luz (hora dorada, hora azul, noche con estrellas), encuadres por tipo (exterior, interior, detalle, espacios comunes), temperatura y tratamiento.
- Recortes: encabezado con dos recortes de la misma foto (ancho y vertical), tarjetas en 4:3.
- Qué evitar: desorden, HDR exagerado, filtros fuertes, personas sin consentimiento.
- **Imágenes generadas por IA:** solo para piezas atmosféricas o editoriales que no muestren el lugar (por ejemplo, un cielo genérico para un post sobre astronomía). **Nunca** para representar alojamientos o espacios de Valle Petra: engañaría a los huéspedes.

## 4. FORMATOS (alcance actual)

1. **Web (landing):** modos claro y oscuro, escritorio y celular.
2. **Instagram:** post 4:5 (1080×1350), cuadrado (1080×1080), story y portada de reel (1080×1920, con zonas seguras), carrusel y portadas de destacados (con la estrella).
3. **Impresos:** reglamento del huésped (A4), tarjeta WiFi, letrero o señalética y tarjeta de presentación. Márgenes en mm, logo de al menos 20 mm de ancho y aviso de que el CMYK/Pantone está pendiente.
4. **Fotografía:** guía para fotos reales y plantilla de brief.

**Fuera de alcance por ahora:** presentaciones, dashboards y motion graphics para video. Menciona cada uno en una línea en "Pendientes". La app `valle-petra-gestion` podrá heredar los tokens más adelante.

## 5. ESTRUCTURA DE `design.md`

1. Propósito y cómo usar este archivo (incluye qué fuente manda si hay conflicto).
2. Resumen de identidad (máximo 5 líneas).
3. Principios (3 a 5).
4. Logo y recursos: rutas reales, cuándo usar cada versión, tamaños mínimos, zona de respeto y usos prohibidos.
5. Color: tablas de tokens por modo, equivalencia CSS y contrastes verificados.
6. Tipografía.
7. Composición, retícula y espaciado.
8. Componentes web y lenguaje gráfico.
9. Movimiento en la web.
10. Dirección fotográfica, plantilla de brief y reglas para imágenes de IA.
11. Guías por formato: Instagram e impresos.
12. Do's and Don'ts.
13. Checklist de calidad.
14. Incertidumbres y decisiones pendientes (precios, CMYK/Pantone, motivos diaguitas, fotos reales y otras que encuentres).

**Largo máximo:** unas 600 líneas. Prefiere tablas y listas a la prosa. No repitas `CLAUDE.md` salvo lo necesario: `design.md` pasa a ser la fuente de los tokens visuales.

## 6. REGLAS

- Crea solo `design.md`. No modifiques ningún archivo existente.
- Usa rutas relativas y comprueba que cada archivo citado exista.
- No inventes valores ni datos del negocio. Si falta uno, usa `[pendiente]`.
- No copies diseños, textos ni imágenes de las referencias externas.
- Escribe en español de Chile, con trato de tú, como el resto del repo.
- Documenta las limitaciones de tu análisis.

## 7. VALIDACIÓN

Antes de terminar:

1. `design.md` existe y no supera el largo máximo.
2. Todas las rutas citadas existen (muestra la comprobación).
3. Los HEX coinciden con `brand/FICHA-TECNICA.md` y con el CSS de la página. Calcula el contraste de los pares principales.
4. Cada regla tiene su nivel de certeza.
5. Haz tres pruebas conceptuales en texto (no son diseños finales): un post de Instagram 4:5, la tarjeta WiFi y una sección nueva de la web. Describe cómo se aplican las reglas y anota los huecos que encuentres.

## RESULTADO

Al terminar, resume:
- los rasgos principales de la marca;
- el archivo creado;
- las propuestas que hiciste;
- las contradicciones entre fuentes;
- qué líneas de `CLAUDE.md` podrían reemplazarse por una referencia a `design.md`, sin editarlo.
