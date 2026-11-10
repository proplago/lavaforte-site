# Lavaforte — sitio web (migración desde Canva)

Sitio estático, sin dependencias en el navegador, con el mismo enfoque que el repo
`PLAGOTECHSITE`: HTML + CSS + JS plano, tokens del Lavaforte Design System como única
fuente de verdad. El HTML se genera con `build.py` (Python 3, sin librerías).

## Páginas (una URL por búsqueda)

| Archivo | Para quién / qué búsqueda |
|---|---|
| `index.html` | Clientes: "lavandería en León", servicios, app, bono de recarga, sucursales, FAQ |
| `sucursal-san-juan-bosco.html`, `sucursal-canaveral.html`, `sucursal-hermenegildo-bustos.html` | Búsquedas locales por sucursal, con horario y mapa (enlazar desde cada Google Business Profile) |
| `servicio-tecnico.html` | Campaña local: reparación de lavadoras y secadoras industriales en León, por evento |
| `reparacion-lavanderia-hoteles.html` / `-hospitales.html` / `-autoservicio.html` | Landings por segmento para Google Ads |
| `kiosoft.html` | Campaña nacional: instalación de KioSoft |
| `inversionistas.html` | Inversionistas: modelo "tú inviertes, nosotros operamos" |

SEO / IA: cada página lleva canonical, Open Graph y JSON-LD (Organization, LaundryOrDryCleaner
con horarios, Service, FAQPage, BreadcrumbList). En la raíz: `sitemap.xml` (lo genera el build),
`robots.txt` (abierto a rastreadores de IA) y `llms.txt` (resumen del negocio para asistentes).

## Cómo editar

```
build.py                ← datos (segmentos, sucursales, FAQ, fotos) + plantilla <head> → genera los HTML
src/_header.html, src/_footer.html, src/*.main.html  ← contenido de cada página
css/tokens.css, css/site.css, js/site.js
assets/img/gen/         ← fotos generadas con Higgsfield (webp)
```

Edita `src/` o `build.py` y corre:

```bash
python3 build.py                  # producción: fotos locales en assets/img/gen/
python3 build.py --remote-images  # vista previa: fotos directo desde Higgsfield
./descargar-fotos.sh              # baja las 8 fotos y las pasa a webp (curl + cwebp)
```

No edites los `.html` de la raíz a mano: el build los sobrescribe.

## Datos y pendientes

Todo el contacto vive en `CONFIG` dentro de `js/site.js`.

- `appUrl`: enlace de descarga de la app (pendiente).
- `provisional: true` muestra las etiquetas "Por confirmar". Pásalo a `false` al publicar.
- Los formularios y botones abren WhatsApp al 477 907 5087 con un mensaje distinto por página,
  así se sabe de qué campaña llegó cada contacto.
- Sucursales y horarios: README del design system (fuente única de verdad).
- Servicio técnico es por evento; no hay pólizas todavía.

## Desarrollo local

```bash
python3 -m http.server 4173
```

## Publicación

Repo `proplago/lavaforte-site` en GitHub → Cloudflare Pages (gratis, HTTPS, deploy en cada
push, sin comando de build: se publica la raíz) → apuntar `www.lavaforte.com.mx` al proyecto
de Pages. Después: Search Console y Bing Webmaster Tools con `sitemap.xml`.
