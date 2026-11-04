# Ficha técnica del logo Valle Petra

Versión definitiva, aprobada el 3 de noviembre de 2026. Dirección "Nouveau del Elqui": wordmark apilado VALLE / PETRA con estrella de cuatro puntas. Reemplaza al logo anterior de montañas con sol.

Las letras son trazos vectoriales, no texto. No volver a escribir el logo con la fuente.

## Tipografía

Base: Fraunces (Undercase Type), variable. Licencia SIL Open Font License 1.1, que permite uso y modificación en logos.

| Eje | Valor |
| --- | --- |
| opsz | 144 |
| wght | 430 |
| SOFT | 100 |
| WONK | 1 |

Ajustes propios:
- Ligadura RA: R y A comparten un mismo remate.
- LL encajadas con kerning óptico.
- PETRA justificada al ancho de VALLE.
- Deformación suave del contorno (amplitud 9 sobre mayúscula de 1400 unidades, semilla 7).
- Estrella de cuatro puntas con lados cóncavos.

`build.py` reproduce el logo exacto.

Tipografía complementaria: Fraunces en títulos, Inter o Manrope en cuerpo.

## Colores (hex, pantalla)

| Versión | Fondo | Letras | Estrella |
| --- | --- | --- | --- |
| Principal · terracota | #AA4529 | #FDEEDD | #E9CA94 |
| Modo claro | #FDEEDD | #AA4529 | #E0AF7F |
| Modo noche | #111832 | #EEEDF0 | #E9CA94 |
| Monocromo negro | claro | #000000 | #000000 |
| Monocromo blanco | oscuro | #FFFFFF | #FFFFFF |

Apoyo: Adobe #A03E25, Oro arena #D6B98B.

## Archivos

- `svg/`: web (horizontal, apilado, currentColor, negro, blanco, avatar).
- `png/`: transparentes de 2400 px y avatar Instagram 1080 × 1080.
- `png/web/`: 600 px para correo, WhatsApp y documentos.
- `imprenta/`: PDF y EPS vectoriales (apilado 150 mm, horizontal 200 mm).
- `favicon/`: favicon.svg (terracota en pestañas claras, oro en oscuras), favicon.ico 16/32/48, apple-touch-icon 180 px, icon 192 y 512 px, site.webmanifest y head.html con el código para la web.

## Isotipo

El isotipo es la estrella sola (decidido el 3 nov 2026), para favicon y tamaños muy chicos. En favicon va algo más gruesa que en el logo para que las puntas no desaparezcan a 16 px.

## Reglas de uso (propuesta)

- Mínimo apilado: 80 px / 20 mm. Mínimo horizontal: 160 px / 40 mm.
- Zona de respeto: media altura de mayúscula libre alrededor (ya incluida en los archivos).
- No estirar, deformar, recolorear fuera de paleta ni agregar efectos.

## Pendientes

- CMYK y Pantone con prueba de imprenta.
