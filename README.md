# Lavaforte — sitio web (migración desde Canva)

Sitio estático, sin dependencias en el navegador, con el mismo enfoque que el repo
`PLAGOTECHSITE`: HTML + CSS + JS plano, tokens del Lavaforte Design System como única
fuente de verdad. El HTML se genera con `build.py` (Python 3, sin librerías).

## Páginas (una URL por búsqueda)

| Archivo | Para quién / qué búsqueda |
|---|---|
| `index.html` | Clientes: "lavandería en León", servicios, app, bono de recarga, sucursales, FAQ |
| `sucursal-san-juan-bosco.html`, `sucursal-canaveral.html`, `sucursal-hermenegildo-bustos.html`, `sucursal-satelite.html` | Búsquedas locales por sucursal, con horario y mapa (enlazar desde cada Google Business Profile) |
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

## Medición (Google, Meta, TikTok)

Todo vive en `CONFIG` de `js/site.js` y en una sola función `track()`:

| Acción en el sitio | GA4 (G-GWDD6KWV5D) | Google Ads (AW-11035918867) | Meta | TikTok |
|---|---|---|---|---|
| Clic a WhatsApp | `contact_whatsapp` | conversión según página: clientes / técnico / KioSoft | `Contact` | `Contact` |
| Formulario enviado a WhatsApp | `generate_lead` | igual que arriba | `Lead` | `SubmitForm` |
| Clic en "Cómo llegar" | `get_directions` (con sucursal) | "Cómo llegar desde el sitio" | `FindLocation` | `FindLocation` |
| Clic a la tienda de la app | `app_download_click` | — | `AppDownloadClick` | `Download` |

Cada evento lleva `page_type` (clientes, tecnico, kiosoft) y `branch` (sucursal), así un solo
Pixel separa clientes finales de negocios con conversiones personalizadas.

- Meta: `meta.pixel` vacío = apagado. Con id, carga el Pixel y manda cada evento también a la
  API de conversiones (`supabase/functions/meta-capi`, proyecto Supabase bzyxiadoibukmzmgdnha)
  con el mismo `event_id` para que Meta no cuente doble. El token va en los secretos de Supabase.
- TikTok: `tiktok` vacío = apagado.
- IndexNow: `64c52c28cc2be5278b493b275eb80412.txt` en la raíz. Después de publicar cambios,
  avisar a Bing/Yandex con `https://api.indexnow.org/indexnow?url=<url>&key=<clave>`.

## Desarrollo local

```bash
python3 -m http.server 4173
```

## Publicación

Repo `proplago/lavaforte-site` en GitHub → Cloudflare Pages (gratis, HTTPS, deploy en cada
push, sin comando de build: se publica la raíz) → apuntar `www.lavaforte.com.mx` al proyecto
de Pages. Después: Search Console y Bing Webmaster Tools con `sitemap.xml`.
