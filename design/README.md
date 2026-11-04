# design/

Referencias de diseño. Nada de esta carpeta se publica tal cual.

## claude-design/valle-petra-marca.html
Landing diseñada en Claude Design, exportada como "Standalone" y adaptada a la marca con `tools/web/patch.py`:
- logo definitivo en menú, encabezado y pie, y favicon de estrella;
- Fraunces completa con SOFT/WONK;
- encabezado centrado sobre la foto, "Vicuña · Chile";
- sin `backdrop-filter` en zonas que se animan (evita parpadeos);
- imágenes como `data:` para que carguen en visores estrictos.

Es un archivo empaquetado (las imágenes van dentro del HTML, unos 10 MB): sirve como referencia, no para publicar.
**Ojo:** varias fotos de alojamientos y espacios son de stock y no son del Elqui; hay que reemplazarlas por fotos reales.

## capturas/
Vistas de la landing en modo claro y oscuro.

## fotos-simuladas/
Renders generados por código (`tools/fotos-simuladas/render.py`) para probar los prototipos A "Noche del Elqui" y C "Casa en el valle" en Claude Design.
**Son lugares ficticios: no usarlos en el sitio publicado.**

## Prototipos en Claude Design
Los canvas "Logo Valle Petra" y "Landing Valle Petra" (prototipos A, B y C) están en Claude Design, en la cuenta del dueño.
