#!/usr/bin/env python3
"""
Genera las páginas HTML del sitio de Lavaforte.

Fuente de verdad:
  src/_header.html, src/_footer.html      → layout compartido
  src/<pagina>.main.html                  → cuerpo de las páginas "a mano"
  SEGMENTOS y SUCURSALES (abajo)          → páginas generadas por datos
  PAGES (abajo)                           → título, descripción y schema de cada URL

Uso:
  python3 build.py                 # imágenes locales (assets/img/gen/*.webp)
  python3 build.py --remote-images # usa las URLs de Higgsfield (vista previa)
El resultado son .html estáticos en la raíz: se pueden subir tal cual.
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.lavaforte.com.mx/"
WA = "524779075087"
REMOTE = "--remote-images" in sys.argv

# ---------------------------------------------------------------- imágenes
HF = "https://d8j0ntlcm91z4.cloudfront.net/user_3EzN1ZAEOjOnzrveUuzPUHJUNAc/"
IMAGES = {  # nombre local → archivo generado en Higgsfield
    "tecnico-industrial": "hf_20261109_234938_18861fcb-7b39-4c80-881b-951c34bf4cbf.png",
    "lavanderia-hotel": "hf_20261109_234845_9795ec2a-b088-4702-87bd-a029ec2a2700.png",
    "lavanderia-hospital": "hf_20261109_234845_5dea4343-ffac-4a5f-b307-0462bf8699aa.png",
    "tecnico-autoservicio": "hf_20261109_234938_a87058b9-a7b3-4df3-8c27-6675224f1d5d.png",
    "cliente-app": "hf_20261109_234844_8e55ca1b-96dd-4e87-92fa-88c30034a407.png",
    "encargo-doblado": "hf_20261109_234845_332b0096-88d3-4851-b772-a25b1745f84a.png",
    "pago-lector": "hf_20261109_234946_4c52f39e-e613-4b8c-a072-2c762cf82f31.png",
    "dueno-reportes": "hf_20261109_234946_3f0dab68-c6a3-4b1e-b1ba-d0addeed66eb.png",
    "hero-clientes": "hf_20261110_001744_2d89b828-ec24-4dae-8a2d-dc252930b4c3.png",
    "hero-tecnico": "hf_20261110_001744_15467c5d-025a-413d-beab-e7a330365975.png",
    "hero-kiosoft": "hf_20261110_202029_e3bfd288-f30e-48e3-ae97-bae524f387bf.png",
    "hero-inversion": "hf_20261110_001820_16e51f18-09dc-4fc7-997f-24c83da3ff89.png",
    "kiosoft-lector": "hf_20261110_202029_5e153f7b-5221-423b-abeb-1fa6b4a46a94.png",
    "recarga-mostrador": "hf_20261110_202629_fa8902e7-b59e-4e8a-afee-f7e8fe5d107d.png",
    "kiosoft-instalacion": "hf_20261110_001808_b42160f6-80f8-406a-9e00-7a52ec1f21a3.png",
    "burbujas": "hf_20261110_001820_946044ae-c331-4819-85ba-1678bd212d62.png",
    "planchado": "hf_20261110_001918_4d06b1d2-4c39-4d94-8c65-61c84c9abe0d.png",
    "edredones": "hf_20261110_001918_407bc8f5-6198-4d4d-9071-442688f5f1b9.png",
    "tintoreria": "hf_20261110_001918_94e6e90e-4e8b-4b14-b2e0-2873810f33e6.png",
}
def imgs(text):
    return re.sub(r"\{\{IMG:([a-z-]+)\}\}", lambda m: img(m.group(1)), text)
def img(name):
    if REMOTE:
        return HF + IMAGES[name]
    return "assets/img/gen/%s.webp" % name

def photo(name, alt, cls="photo", eager=False):
    return ('<figure class="%s"><img src="%s" alt="%s" width="1200" height="800"%s /></figure>'
            % (cls, img(name), html.escape(alt), "" if eager else ' loading="lazy"'))

# ---------------------------------------------------------------- piezas
WAVE = '''<svg class="hero__wave" viewBox="0 0 816 120" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0,120 C140,44 340,30 500,66 C620,94 700,80 816,40 L816,120 Z" fill="#0060B0" opacity=".55"/>
        <path d="M0,120 C180,68 380,52 560,82 C660,100 720,92 816,74 L816,120 Z" fill="#0090D0" opacity=".85"/>
        <path d="M0,84 C200,40 440,40 620,74 C700,90 760,88 816,78 L816,96 C740,110 660,110 560,90 C420,60 200,62 0,100 Z" fill="url(#rib)"/>
        <path d="M0,120 C200,76 440,68 620,92 C710,104 760,106 816,100 L816,120 Z" fill="#FFFFFF"/>
        <defs><linearGradient id="rib" x1="0" x2="1"><stop offset="0" stop-color="#F0E010"/><stop offset="1" stop-color="#F0C000"/></linearGradient></defs>
      </svg>'''

STRIPS = {
    "tecnico": '<div class="promo-strip"><a href="servicio-tecnico.html">¿Hotel, hospital o lavandería? <b>Reparamos tu equipo de lavandería</b> en León <span class="arrow" aria-hidden="true">→</span></a></div>',
    "kiosoft": '<div class="promo-strip"><a href="kiosoft.html">¿Tienes una lavandería? <b>Instalamos KioSoft by PayRange</b>: tus clientes pagan desde la app <span class="arrow" aria-hidden="true">→</span></a></div>',
    None: "",
}

def faq_html(items):
    out = ['<div class="faq" data-reveal>']
    for q, a in items:
        out.append("<details><summary>%s</summary><p>%s</p></details>" % (q, a))
    out.append("</div>")
    return "\n          ".join(out)

def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in items]}

def crumbs(*pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(pairs)]}

ORG = {"@type": "Organization", "@id": SITE + "#org", "name": "Lavaforte Lavanderías", "url": SITE,
       "logo": SITE + "assets/img/lavaforte-logo-180.png", "slogan": "La evolución de lavar.",
       "telephone": "+52 477 907 5087",
       "contactPoint": {"@type": "ContactPoint", "telephone": "+52 477 907 5087", "contactType": "customer service", "availableLanguage": "es",
                        "contactOption": "WhatsApp", "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "18:00"}},
       "knowsAbout": ["Lavandería de autoservicio", "Reparación de lavadoras industriales", "KioSoft", "Lavanderías de hotel y hospital"],
       "address": {"@type": "PostalAddress", "streetAddress": "Manantial 806-B, Valle del Campestre",
                   "postalCode": "37150", "addressLocality": "León", "addressRegion": "Guanajuato", "addressCountry": "MX"},
       "sameAs": ["https://www.instagram.com/lavaforte_lavanderias", "https://www.tiktok.com/@lavaforte_lavanderias",
                  "https://www.facebook.com/lavaforte.lavanderias"]}

# ---------------------------------------------------------------- servicio técnico: bloques compartidos
def services_block():
    return open(os.path.join(ROOT, "src/_servicios-tecnicos.html")).read()

PROCESS = '''<section class="section">
      <div class="container">
        <div class="section-head" data-reveal>
          <p class="eyebrow">Cómo trabajamos</p>
          <h2 class="h-2">De la falla a funcionando</h2>
        </div>
        <div class="grid grid--4 steps" data-stagger>
          <div class="step"><h3 class="h-3">Nos escribes</h3><p>Mándanos foto o video de la falla por WhatsApp y te decimos el costo de la visita.</p></div>
          <div class="step"><h3 class="h-3">Diagnóstico</h3><p>Revisamos el equipo en sitio y te damos la cotización antes de reparar.</p></div>
          <div class="step"><h3 class="h-3">Reparación</h3><p>Reparamos y probamos con un ciclo completo.</p></div>
          <div class="step"><h3 class="h-3">Reporte y factura</h3><p>Qué se hizo, cómo evitar que se repita y tu factura.</p></div>
        </div>
      </div>
    </section>'''

def contact_form(segment_value, wa_msg, title="¿Qué está fallando?"):
    opts = ["Hotel o motel", "Hospital o clínica", "Lavandería de autoservicio", "Lavandería industrial o tintorería", "Otro"]
    o = "".join('<option%s>%s</option>' % (' selected' if x == segment_value else "", x) for x in opts)
    return '''<section class="section section--dark" id="contacto">
      <div class="bubbles" data-bubbles="right" aria-hidden="true"></div>
      <div class="container split" style="position:relative;z-index:2">
        <div data-reveal>
          <p class="eyebrow">Solicita servicio</p>
          <h2 class="h-2">%s</h2>
          <p class="lead">Te decimos cuándo podemos ir.</p>
        </div>
        <form class="form" data-wa-form="%s" data-reveal>
          <div class="row">
            <label>Nombre<input name="nombre" required autocomplete="name" /></label>
            <label>Tipo de negocio<select name="segmento">%s</select></label>
          </div>
          <div class="row">
            <label>Equipo<input name="equipo" placeholder="Marca o capacidad" /></label>
            <label>Ciudad<input name="ciudad" required autocomplete="address-level2" value="León" /></label>
          </div>
          <label>¿Qué está pasando?<textarea name="falla" rows="3"></textarea></label>
          <button class="btn" type="submit">Enviar por WhatsApp</button>
          <p class="note">Adjunta en WhatsApp una foto o video de la falla.</p>
        </form>
      </div>
    </section>''' % (title, html.escape(wa_msg), o)

# ---------------------------------------------------------------- segmentos (páginas de campaña + SEO)
SEGMENTOS = {
    "hoteles": dict(
        slug="reparacion-lavanderia-hoteles", nav="tecnico", img="lavanderia-hotel",
        title="Reparación de lavandería de hotel en León | Lavaforte",
        desc="Reparación de lavadoras, secadoras y planchadoras de hotel en León. Diagnóstico en sitio, cotización antes de reparar y factura.",
        eyebrow="Lavanderías de hotel y motel · León",
        h1='Reparación de lavandería <span class="hl">para hoteles</span>',
        lead="Si la secadora se detiene, las habitaciones no se liberan. Reparamos en sitio y en tu horario.",
        wa="Hola Lavaforte, necesito servicio técnico para la lavandería de mi hotel.",
        select="Hotel o motel", band_h='Operamos lavanderías. <span class="hl">Sabemos qué no puede esperar.</span>',
        pains=[("Blancos atrasados", "Una secadora lenta o una lavadora que no centrifuga retrasa todo el turno de camaristas."),
               ("Consumo de gas alto", "Quemadores sucios, ductos tapados y sensores descalibrados cuestan dinero cada ciclo."),
               ("Planchadora con marcas", "Rodillo desgastado, temperatura dispareja o banda floja dejan sábanas mal planchadas."),
               ("Paros en temporada alta", "Revisamos el equipo antes del puente o la temporada para que no falle cuando más lo usas.")],
        faq=[("¿Pueden venir fuera del horario pico del hotel?", "Sí. Agendamos la visita en el horario en que la lavandería tenga menos carga para no frenar la operación."),
             ("¿Reparan planchadoras de rodillo?", "Sí. Revisamos rodillo, bandas, temperatura y alimentación, además de lavadoras extractoras y secadoras industriales."),
             ("¿Cómo se cobra el servicio?", "Pagas cada servicio: la visita de diagnóstico y, si apruebas la cotización, la reparación y las refacciones. Todo con factura a nombre del hotel."),
             ("¿Hacen revisiones antes de temporada alta?", "Sí. Agenda una revisión antes del puente o la temporada y te entregamos el estado de cada equipo con lo que conviene reparar.")]),
    "hospitales": dict(
        slug="reparacion-lavanderia-hospitales", nav="tecnico", img="lavanderia-hospital",
        title="Reparación de lavandería hospitalaria en León | Lavaforte",
        desc="Reparación de lavadoras y secadoras industriales de hospitales y clínicas en León, con reporte de cada servicio y factura.",
        eyebrow="Hospitales y clínicas · León",
        h1='Servicio técnico para <span class="hl">lavandería hospitalaria</span>',
        lead="La ropa del hospital no puede esperar. Atención prioritaria y reporte por máquina.",
        wa="Hola Lavaforte, necesito servicio técnico para la lavandería de mi hospital.",
        select="Hospital o clínica", band_h='Cada visita, <span class="hl">documentada.</span>',
        pains=[("Equipo detenido", "Un paro en la lavandería obliga a mandar ropa fuera o a reducir la rotación de blancos."),
               ("Temperaturas de lavado", "Revisamos calentamiento, sensores y ciclos para que el equipo alcance la temperatura programada."),
               ("Secado incompleto", "Ductos, filtros y quemadores en mal estado alargan los ciclos y elevan el consumo."),
               ("Evidencia para auditoría", "Cada servicio queda documentado: falla, refacciones, pruebas y recomendaciones.")],
        faq=[("¿Atienden con prioridad a hospitales?", "Sí. Las fallas de lavandería hospitalaria se agendan con prioridad dentro de nuestra ruta del día."),
             ("¿Entregan reporte del servicio?", "Sí. Cada visita incluye un reporte con la falla encontrada, lo que se reparó y las pruebas realizadas."),
             ("¿Cómo se cobra el servicio?", "Pagas cada servicio: la visita de diagnóstico y, si apruebas la cotización, la reparación y las refacciones. Todo con factura."),
             ("¿Qué equipos atienden?", "Lavadoras extractoras, secadoras industriales de gas y eléctricas y planchadoras de rodillo.")]),
    "autoservicio": dict(
        slug="reparacion-lavanderia-autoservicio", nav="tecnico", img="tecnico-autoservicio",
        title="Reparación de lavadoras de autoservicio en León | Lavaforte",
        desc="Reparamos lavadoras, secadoras y lectores de pago de lavanderías de autoservicio en León. Técnicos que operan sus propias lavanderías.",
        eyebrow="Lavanderías de autoservicio · León",
        h1='Reparación de lavadoras y secadoras <span class="hl">de autoservicio</span>',
        lead="Máquina parada, dinero perdido. Operamos lavanderías: sabemos qué falla primero.",
        wa="Hola Lavaforte, necesito reparar equipo de mi lavandería de autoservicio.",
        select="Lavandería de autoservicio", band_h='Tenemos lavanderías como la tuya. <span class="hl">Sabemos qué falla.</span>',
        pains=[("Lavadora que no arranca", "Falla en la placa electrónica, la chapa de la puerta o las válvulas de agua."),
               ("Secadora que no calienta", "Encendido, sensores, quemador, banda o flujo de aire."),
               ("Lavadora que no drena", "Bomba, manguera o filtro tapado que deja el ciclo a medias."),
               ("Lector de pago sin conexión", "Lectores que no arrancan la máquina, sin internet o con precios mal configurados.")],
        faq=[("¿Reparan lectores de pago?", "Sí. Revisamos lectores, conexión y configuración de precios. Si tu lavandería todavía cobra en mostrador, instalamos KioSoft para que cobre por app."),
             ("¿Cuánto tarda una reparación?", "Muchas fallas se resuelven en la primera visita. Si hace falta una refacción, te damos la fecha antes de pedirla."),
             ("¿Cómo se cobra el servicio?", "Pagas cada servicio: la visita de diagnóstico y, si apruebas la cotización, la reparación y las refacciones. Todo con factura."),
             ("¿Por qué con Lavaforte?", "Porque operamos nuestras propias lavanderías de autoservicio en León y vivimos las mismas fallas que tú.")]),
}

def hx(bg, alt, eyebrow, h1, lead, buttons, chips=None, crumb=None):
    ch = '<div class="chips" data-stagger>%s</div>' % "".join('<span class="chip">%s</span>' % c for c in chips) if chips else ""
    cr = '<nav class="crumbs" aria-label="Ruta">%s</nav>' % crumb if crumb else ""
    return '''<section class="hx hx--short ph">
      <div class="hx__bg" data-parallax="0.18"><img src="%s" alt="%s" width="1200" height="1600" fetchpriority="high" /></div>
      <div class="bubbles" data-bubbles="right" aria-hidden="true"></div>
      <div class="hx__content">
        %s
        <p class="eyebrow" data-reveal>%s</p>
        <h1 data-reveal>%s</h1>
        <p class="lead" data-reveal>%s</p>
        <div class="btn-row" data-reveal>%s</div>
        %s
      </div>
    </section>''' % (img(bg), html.escape(alt), cr, eyebrow, h1, lead, buttons, ch)

def segment_body(s):
    pains = "\n".join('<div class="perk"><div class="icon"><svg viewBox="0 0 24 24"><path d="M12 3 2.5 20h19L12 3Z"/><path d="M12 10v4M12 17h.01"/></svg></div><b>%s</b><p class="small muted">%s</p></div>' % p for p in s["pains"])
    others = [v for v in SEGMENTOS.values() if v is not s]
    tiles = "".join('<a class="tile ph" href="%s.html"><img src="%s" alt="" width="1200" height="800" loading="lazy" /><div class="tile__body"><h3>%s</h3><span class="price">Ver servicio →</span></div></a>'
                    % (v["slug"], img(v["img"]), v["eyebrow"].split(" · ")[0]) for v in others)
    short = s["eyebrow"].split(" · ")[0]
    btns = '<a class="btn" href="https://wa.me/%s" data-wa="%s">Pide un técnico</a><a class="btn btn--ghost" href="#contacto">Cotizar</a>' % (WA, html.escape(s["wa"]))
    return '''<main id="main">
    %(hero)s

    <section class="section">
      <div class="container split">
        <div data-reveal>
          <p class="eyebrow">Fallas que resolvemos</p>
          <h2 class="h-2">Lo que más nos llaman a reparar</h2>
        </div>
        <div class="perks perks--2" data-stagger>
          %(pains)s
        </div>
      </div>
    </section>

    %(services)s

    <section class="band ph">
      <div class="band__bg" data-parallax="0.28"><img src="%(band)s" alt="" width="1200" height="800" loading="lazy" /></div>
      <div class="container">
        <p class="eyebrow" data-reveal>Por qué Lavaforte</p>
        <h2 data-reveal>%(band_h)s</h2>
      </div>
    </section>

    %(process)s

    <section class="section">
      <div class="container">
        <div class="section-head center" data-reveal>
          <p class="eyebrow">Preguntas frecuentes</p>
          <h2 class="h-2">Antes de llamarnos</h2>
        </div>
          %(faq)s
      </div>
    </section>

    %(contact)s

    <section class="section">
      <div class="container">
        <div class="section-head" data-reveal><p class="eyebrow">También atendemos</p></div>
        <div class="rail" style="--cols:2" data-stagger>%(tiles)s</div>
      </div>
    </section>
  </main>''' % dict(hero=hx(s["img"], short, s["eyebrow"], s["h1"], s["lead"], btns, ["Diagnóstico en sitio", "Cotización antes de reparar", "Con factura"],
                          '<a href="servicio-tecnico.html">Servicio técnico</a> / <span>%s</span>' % short),
                    pains=pains, services=services_block(), band=img("tecnico-industrial"), process=PROCESS, band_h=s["band_h"],
                    faq=faq_html(s["faq"]), contact=contact_form(s["select"], s["wa"]), tiles=tiles)

# ---------------------------------------------------------------- sucursales (SEO local)
SUCURSALES = {
    "san-juan-bosco": dict(
        name="San Juan Bosco", zona="Blvd. San Juan Bosco", street="Blvd. San Juan Bosco 3802, L2", cp="37669",
        cerca="Blvd. San Juan Bosco y colonias cercanas del poniente de León",
        hours=[("Lun, Jue a Dom", "7:00 a 21:00"), ("Mar y Mié", "7:00 a 15:00")],
        spec=[(["Monday", "Thursday", "Friday", "Saturday", "Sunday"], "07:00", "21:00"), (["Tuesday", "Wednesday"], "07:00", "15:00")],
        badge="Autoservicio 24 h con app", maps="Lavaforte+Blvd.+San+Juan+Bosco+3802+Le%C3%B3n+Gto"),
    "canaveral": dict(
        name="Cañaveral", zona="Blvd. Cañaveral", street="Blvd. Cañaveral 703, Local 3, Granja Santa Teresa", cp="37544",
        cerca="Granja Santa Teresa y colonias cercanas a Blvd. Cañaveral",
        hours=[("Lun, Jue a Dom", "7:00 a 21:00"), ("Mar y Mié", "7:00 a 15:00")],
        spec=[(["Monday", "Thursday", "Friday", "Saturday", "Sunday"], "07:00", "21:00"), (["Tuesday", "Wednesday"], "07:00", "15:00")],
        badge="Autoservicio 24 h con app", maps="Lavaforte+Blvd.+Ca%C3%B1averal+703+Le%C3%B3n+Gto"),
    "hermenegildo-bustos": dict(
        name="Hermenegildo Bustos", zona="Valle del Moral", street="Blvd. Hermenegildo Bustos 1338, L4, Valle del Moral", cp="37178",
        cerca="Valle del Moral y colonias cercanas a Blvd. Hermenegildo Bustos",
        hours=[("Lunes", "7:00 a 15:00"), ("Martes", "15:00 a 21:30"), ("Mié a Dom", "7:00 a 21:00")],
        spec=[(["Monday"], "07:00", "15:00"), (["Tuesday"], "15:00", "21:30"), (["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "07:00", "21:00")],
        badge="Puerta abierta hasta las 12:00 am", maps="Lavaforte+Blvd.+Hermenegildo+Bustos+1338+Le%C3%B3n+Gto"),
}

def branch_card(key, b):
    hours = "".join("<li><span>%s</span><span>%s</span></li>" % h for h in b["hours"])
    return ('<article class="branch-x"><div class="branch-x__top"><span class="badge-24">%s</span><h3><a href="sucursal-%s.html" style="text-decoration:none">%s</a></h3>'
            '<p class="addr">%s · C.P. %s</p></div><ul class="hours">%s</ul><div class="btn-row"><a class="btn btn--outline btn--sm" href="sucursal-%s.html">Ver</a>'
            '<a class="btn btn--navy btn--sm" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&amp;query=%s">Cómo llegar</a></div></article>'
            % (b["badge"], key, b["name"], b["street"], b["cp"], hours, key, b["maps"]))

def branch_body(key, b):
    others = "".join(branch_card(k, v) for k, v in SUCURSALES.items() if k != key)
    btns = ('<a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&amp;query=%s">Cómo llegar</a>'
            '<a class="btn btn--ghost" href="https://wa.me/%s" data-wa="Hola Lavaforte %s, quiero información.">WhatsApp</a>') % (b["maps"], WA, b["name"])
    tiles = "".join('<div class="tile ph"><img src="%s" alt="%s" width="1200" height="1500" loading="lazy" /><div class="tile__body"><h3>%s</h3><p>%s</p></div></div>' % (img(i), a, t, p)
                    for i, a, t, p in [("cliente-app", "Autoservicio con app", "Autoservicio", "Paga con la app, a cualquier hora."),
                                       ("encargo-doblado", "Ropa doblada", "Por encargo", "Desde $30/kg, mínimo 3 kg."),
                                       ("planchado", "Camisas planchadas", "Planchado", "Por docena o pieza."),
                                       ("edredones", "Edredones limpios", "Edredones", "Individual a king size.")])
    return '''<main id="main">
    %(hero)s

    <section class="section">
      <div class="container split">
        <div class="branch-x" data-reveal style="max-width:460px">
          <div class="branch-x__top"><span class="badge-24">%(badge)s</span><h2 class="h-3" style="font-size:1.3rem">Horario de mostrador</h2></div>
          <ul class="hours">%(hours)s</ul>
          <p class="small muted" style="padding:0 18px 18px">%(street)s · C.P. %(cp)s, León, Gto.</p>
        </div>
        <div class="map" data-reveal><iframe title="Mapa de Lavaforte %(name)s" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q=%(maps)s&amp;output=embed"></iframe></div>
      </div>
    </section>

    <section class="section section--muted">
      <div class="container">
        <div class="section-head" data-reveal>
          <p class="eyebrow">Qué encuentras aquí</p>
          <h2 class="h-2">Tu lavandería cerca de %(zona)s</h2>
        </div>
        <div class="rail" style="--cols:4" data-stagger>%(tiles)s</div>
        <p class="swipe-hint">Desliza</p>
        <div class="app-cta" data-reveal><p><b>Paga el autoservicio con la app KioSoft Wash.</b> Descárgala gratis:</p>
          <div class="stores">
            <a class="store" href="https://apps.apple.com/mx/app/kiosoft-wash/id6458121942" data-app="ios" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.2 1-4 2.5-1.7 3-.4 7.4 1.2 9.8.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.5-1-2.5-4zM14 5.4c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1.1.1 2.1-.6 2.8-1.4z"/></svg><span><small>Descárgala en</small>App Store</span></a>
            <a class="store" href="https://play.google.com/store/apps/details?id=com.kiosoft.kiosoftwash" data-app="android" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3.6 1.8c-.3.3-.4.7-.4 1.2v18c0 .5.1.9.4 1.2l10-10.2-10-10.2zm11.1 11.3l2.8 2.8-11.8 6.7c-.4.2-.8.3-1.1.2l10.1-9.7zm0-2.2L4.6 1.2c.3-.1.7 0 1.1.2l11.8 6.7-2.8 2.8zm3.9-1.9l3 1.7c.9.5.9 1.3 0 1.8l-3 1.7-3-3 3-2.2z"/></svg><span><small>Disponible en</small>Google Play</span></a>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head center" data-reveal>
          <p class="eyebrow">Preguntas frecuentes</p>
          <h2 class="h-2">Lavaforte %(name)s</h2>
        </div>
          %(faq)s
      </div>
    </section>

    <section class="section section--muted">
      <div class="container">
        <div class="section-head" data-reveal><p class="eyebrow">Otras sucursales</p></div>
        <div class="rail" style="--cols:2" data-stagger>%(others)s</div>
      </div>
    </section>
  </main>''' % dict(hero=hx("hero-clientes", "Lavandería Lavaforte", b["badge"], 'Lavandería en <span class="hl">%s</span>' % b["zona"],
                          "Autoservicio con app, encargo, planchado y edredones. %s." % b["street"], btns, None,
                          '<a href="index.html#sucursales">Sucursales</a> / <span>%s</span>' % b["name"]),
                    name=b["name"], badge=b["badge"], zona=b["zona"], street=b["street"], cp=b["cp"], maps=b["maps"],
                    hours="".join("<li><span>%s</span><span>%s</span></li>" % h for h in b["hours"]),
                    tiles=tiles, faq=faq_html(branch_faq(b)), others=others)

def branch_faq(b):
    h = "; ".join("%s de %s" % x for x in b["hours"])
    return [("¿Qué horario tiene Lavaforte %s?" % b["name"], "El mostrador atiende %s. %s." % (h, b["badge"])),
            ("¿Dónde está Lavaforte %s?" % b["name"], "En %s, C.P. %s, León, Guanajuato." % (b["street"], b["cp"])),
            ("¿Cómo pago el autoservicio?", "Con la app KioSoft Wash (App Store y Google Play): recargas saldo, eliges tu máquina y arranca. Al recargar recibes hasta 30% de saldo extra."),
            ("¿Cuánto cuesta el lavado por encargo?", "Desde $30 por kilo con carga mínima de 3 kg. Escríbenos por WhatsApp al 477 907 5087 para precios de planchado y edredones.")]

def branch_schema(key, b):
    return {"@type": "LaundryOrDryCleaner", "@id": SITE + "sucursal-%s.html#negocio" % key, "name": "Lavaforte %s" % b["name"],
            "url": SITE + "sucursal-%s.html" % key, "image": SITE + "assets/img/gen/hero-clientes.webp", "telephone": "+52 477 907 5087",
            "priceRange": "$", "parentOrganization": {"@id": SITE + "#org"},
            "address": {"@type": "PostalAddress", "streetAddress": b["street"], "postalCode": b["cp"], "addressLocality": "León",
                        "addressRegion": "Guanajuato", "addressCountry": "MX"},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c} for d, o, c in b["spec"]],
            "hasMap": "https://www.google.com/maps/search/?api=1&query=" + b["maps"],
            "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": "WiFi gratis", "value": True}]}

# ---------------------------------------------------------------- FAQ de páginas "a mano"
FAQ_INDEX = [
    ("¿Cómo funciona el autoservicio?", "Con la app KioSoft Wash: la descargas gratis en App Store o Google Play, recargas saldo y eliges tu máquina desde el celular. La app te avisa cuando termina tu ciclo."),
    ("¿Puedo recargar saldo en mostrador?", "Sí. En horario de mostrador te ayudamos a recargar y a usar la app la primera vez."),
    ("¿Necesito llevar detergente?", "Nuestras lavadoras son de alta eficiencia y funcionan con detergente HE. Si no traes, pregunta en mostrador."),
    ("¿Cuánto cuesta lavar por encargo?", "Desde $30 por kilo con carga mínima de 3 kg. Te confirmamos la hora de entrega por WhatsApp."),
    ("¿Mi saldo sirve en cualquier sucursal?", "Sí. El saldo y el bono de recarga funcionan en todas las sucursales Lavaforte y no vencen."),
    ("¿Hay lavandería 24 horas en León?", "Sí. En Lavaforte San Juan Bosco y Cañaveral el autoservicio funciona las 24 horas con la app."),
]
FAQ_TECNICO = [
    ("¿Qué equipos reparan?", "Lavadoras extractoras, lavadoras y secadoras de autoservicio, secadoras industriales de gas y eléctricas, planchadoras de rodillo y lectores de pago."),
    ("¿Qué marcas atienden?", "Trabajamos con las principales marcas de equipo comercial e industrial. Mándanos marca y modelo y te confirmamos antes de la visita."),
    ("¿Qué zona cubren?", "León y su zona metropolitana. Para otras ciudades del Bajío, consúltanos."),
    ("¿Cuánto cuesta la visita?", "Te decimos el costo de la visita de diagnóstico antes de agendarla, junto con el día en que podemos ir."),
    ("¿Cómo se cobra el servicio?", "Pagas cada servicio: la visita de diagnóstico y, si apruebas la cotización, la reparación y las refacciones. Todo con factura."),
]
FAQ_KIOSOFT = [
    ("¿Qué es KioSoft by PayRange?", "KioSoft by PayRange es un sistema de cobro para lavanderías de autoservicio: un lector en cada lavadora y secadora y una app donde los clientes pagan y recargan saldo con bono."),
    ("¿Mis clientes tienen que descargar una app?", "Sí. La descarga toma un minuto. En el lanzamiento capacitamos a tu personal y te damos material para que tus clientes la usen desde el primer día."),
    ("¿Funciona con mis lavadoras actuales?", "KioSoft es compatible con la mayoría de equipos comerciales de autoservicio. En el diagnóstico confirmamos marca y modelo antes de cotizar."),
    ("¿Puedo seguir cobrando en mostrador?", "Sí. Tu personal puede recargar saldo a quien lo pida en mostrador, y el cliente usa ese saldo en las máquinas."),
    ("¿Cuánto tarda la instalación?", "Depende del número de equipos. La programamos para no frenar tu operación y te damos el calendario en la propuesta."),
    ("¿Trabajan en todo México?", "Sí. La configuración de precios y promociones la hacemos a distancia, y la instalación en sitio se agenda en tu ciudad."),
    ("¿KioSoft y PayRange son lo mismo?", "Sí. KioSoft ahora forma parte de PayRange. Por eso hoy se le conoce como KioSoft by PayRange. Instalamos y configuramos sus lectores y su app de pago."),
    ("¿Lavaforte es KioSoft?", "No. Lavaforte opera lavanderías de autoservicio en León y usa KioSoft en ellas. Instalamos y configuramos KioSoft (PayRange) para otros dueños; KioSoft y PayRange son marcas de su fabricante."),
]
FAQ_INV = [
    ("¿Cuánto se necesita para invertir?", "Depende del tamaño del local y del número de equipos. Te compartimos los escenarios en el dossier y en una reunión uno a uno."),
    ("¿Tengo que operar la lavandería?", "No. Lavaforte opera todo: personal, mantenimiento, insumos, marketing y contabilidad. Tú recibes reportes y resultados."),
    ("¿Puedo visitar una sucursal en operación?", "Sí, y lo recomendamos. Agendamos un recorrido para que veas el sistema de cobro y los reportes en vivo."),
    ("¿Dónde están las próximas aperturas?", "Estamos evaluando nuevas plazas en León y otras ciudades del centro del país. Te contamos el detalle en la reunión."),
]

def replace_faq(body, items):
    return re.sub(r'<div class="faq" data-reveal>.*?</div>', faq_html(items), body, count=1, flags=re.S)

# ---------------------------------------------------------------- páginas
def read(p):
    return open(os.path.join(ROOT, "src", p)).read()

def page_index():
    b = read("index.main.html").replace("{{SUCURSALES}}", "".join(branch_card(k, v) for k, v in SUCURSALES.items()))
    return imgs(replace_faq(b, FAQ_INDEX))

def page_tecnico():
    b = read("servicio-tecnico.main.html")
    b = replace_faq(b, FAQ_TECNICO)
    b = b.replace("{{SERVICIOS}}", services_block()).replace("{{PROCESO}}", PROCESS)
    return imgs(b.replace("{{CONTACTO}}", contact_form("", "Hola Lavaforte, necesito servicio técnico para equipo de lavandería.")))

def page_kiosoft():
    b = read("kiosoft.main.html")
    return imgs(replace_faq(b, FAQ_KIOSOFT))

def page_inv():
    b = read("inversionistas.main.html")
    return imgs(replace_faq(b, FAQ_INV))

LOCAL_BRANCHES = [branch_schema(k, v) for k, v in SUCURSALES.items()]

PAGES = [
    dict(file="index.html", nav="clientes", strip="tecnico", body=page_index, wa="Hola Lavaforte, quiero información.",
         title="Lavandería de autoservicio con app en León | Lavaforte",
         desc="Lava cuando puedas: autoservicio con app (24 h en dos sucursales), encargo desde $30/kg, planchado y edredones. 3 sucursales en León, Gto.",
         schema=lambda: [{"@type": "WebSite", "@id": SITE + "#web", "url": SITE, "name": "Lavaforte Lavanderías", "inLanguage": "es-MX", "publisher": {"@id": SITE + "#org"}}, ORG] + LOCAL_BRANCHES + [faq_schema(FAQ_INDEX)], priority="1.0"),
    dict(file="servicio-tecnico.html", nav="tecnico", strip=None, dock=("Cotizar", "#contacto"), og_image="hero-tecnico", body=page_tecnico, wa="Hola Lavaforte, necesito servicio técnico para equipo de lavandería.",
         title="Reparación de lavadoras industriales en León | Lavaforte",
         desc="Reparamos lavadoras, secadoras y planchadoras de hoteles, hospitales y lavanderías de autoservicio en León. Cotización antes de reparar y factura.",
         schema=lambda: [ORG, {"@type": "Service", "name": "Reparación de equipo de lavandería industrial y de autoservicio",
                                "serviceType": "Reparación de lavadoras y secadoras industriales", "description": "Diagnóstico en sitio, cotización antes de reparar, reparación, refacciones, instalación y reubicación de lavadoras, secadoras y planchadoras industriales y de autoservicio.", "provider": {"@id": SITE + "#org"},
                                "areaServed": {"@type": "City", "name": "León, Guanajuato"},
                                "audience": [{"@type": "BusinessAudience", "name": n} for n in ["Hoteles", "Hospitales", "Lavanderías de autoservicio"]]},
                          faq_schema(FAQ_TECNICO), crumbs(("Inicio", ""), ("Servicio técnico", "servicio-tecnico.html"))], priority="0.9"),
    dict(file="kiosoft.html", nav="kiosoft", strip=None, dock=("Cotizar", "#cotiza"), og_image="hero-kiosoft", body=page_kiosoft, wa="Hola Lavaforte, quiero cotizar la instalación de KioSoft.",
         title="Instalación de KioSoft by PayRange en lavanderías | Lavaforte",
         desc="Instalamos KioSoft by PayRange en lavanderías de autoservicio de todo México: tus clientes pagan desde la app, recargan con bono y tu lavandería vende las 24 h.",
         schema=lambda: [ORG, {"@type": "Service", "name": "Instalación y configuración de KioSoft by PayRange para lavanderías",
                                "serviceType": "Sistema de cobro por app para lavanderías de autoservicio", "description": "Instalación de lectores KioSoft en lavadoras y secadoras, configuración de la app de pago, recargas con bono, y precios. Lavaforte es instalador; KioSoft es marca de su fabricante.", "provider": {"@id": SITE + "#org"},
                                "areaServed": {"@type": "Country", "name": "México"}},
                          faq_schema(FAQ_KIOSOFT), crumbs(("Inicio", ""), ("KioSoft", "kiosoft.html"))], priority="0.9"),
    dict(file="inversionistas.html", nav="inversion", strip="kiosoft", dock=("Dossier", "#contacto"), og_image="hero-inversion", body=page_inv, wa="Hola Lavaforte, me interesa invertir.",
         title="Invierte en lavanderías de autoservicio | Lavaforte",
         desc="Lavaforte desarrolla y opera lavanderías de autoservicio con cobro por app en León. Conoce el modelo de inversión y pide el dossier.",
         schema=lambda: [ORG, faq_schema(FAQ_INV), crumbs(("Inicio", ""), ("Inversionistas", "inversionistas.html"))], priority="0.6"),
]
for k, s in SEGMENTOS.items():
    PAGES.append(dict(file=s["slug"] + ".html", nav="tecnico", strip=None, dock=("Cotizar", "#contacto"), body=(lambda s=s: segment_body(s)), wa=s["wa"],
                      title=s["title"], desc=s["desc"], og_image=s["img"], priority="0.8",
                      schema=(lambda s=s: [ORG, {"@type": "Service", "name": re.sub("<[^>]+>", "", s["h1"]), "provider": {"@id": SITE + "#org"},
                                                 "areaServed": {"@type": "City", "name": "León, Guanajuato"}},
                                           faq_schema(s["faq"]), crumbs(("Inicio", ""), ("Servicio técnico", "servicio-tecnico.html"),
                                                                        (s["eyebrow"].split(" · ")[0], s["slug"] + ".html"))])))
for k, b in SUCURSALES.items():
    PAGES.append(dict(file="sucursal-%s.html" % k, nav="sucursales", strip="tecnico", dock=("Cómo llegar", "https://www.google.com/maps/search/?api=1&amp;query=" + b["maps"]), body=(lambda k=k, b=b: branch_body(k, b)),
                      wa="Hola Lavaforte %s, quiero información." % b["name"],
                      title="Lavandería en %s, León | Lavaforte" % b["name"],
                      desc="Lavaforte %s: autoservicio con app, encargo desde $30/kg, planchado y edredones en %s, León. Horario y cómo llegar." % (b["name"], b["zona"]),
                      priority="0.8",
                      schema=(lambda k=k, b=b: [branch_schema(k, b), faq_schema(branch_faq(b)),
                                                crumbs(("Inicio", ""), ("Sucursales", "index.html#sucursales"), (b["name"], "sucursal-%s.html" % k))])))

HEAD = '''<!DOCTYPE html>
<html lang="es-MX">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script>document.documentElement.classList.add("js");</script>
  <title>%(title)s</title>
  <meta name="description" content="%(desc)s" />
  <link rel="canonical" href="%(url)s" />
  <meta name="theme-color" content="#001040" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="es_MX" />
  <meta property="og:site_name" content="Lavaforte Lavanderías" />
  <meta property="og:title" content="%(title)s" />
  <meta property="og:description" content="%(desc)s" />
  <meta property="og:url" content="%(url)s" />
  <meta property="og:image" content="%(og)s" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="assets/img/favicon.png" type="image/png" />
  <link rel="preload" href="assets/fonts/allotrope-black.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="css/tokens.css" />
  <link rel="stylesheet" href="css/site.css" />
  <link rel="stylesheet" href="css/v2.css" />
  <script type="application/ld+json">%(ld)s</script>
</head>
'''

TODAY = __import__("datetime").date.today().isoformat()

def build():
    header = read("_header.html"); footer = read("_footer.html")
    urls = []
    for p in PAGES:
        url = SITE + ("" if p["file"] == "index.html" else p["file"])
        og = p.get("og_image", "hero-clientes")
        og_url = (img(og) if REMOTE else SITE + img(og)) if og else SITE + "assets/img/lavaforte-logo-180.png"
        ld = json.dumps({"@context": "https://schema.org", "@graph": p["schema"]()}, ensure_ascii=False)
        h = header.replace("{{STRIP}}", STRIPS[p["strip"]]).replace("{{WA}}", html.escape(p["wa"]))
        h = h.replace('data-nav="%s"' % p["nav"], 'data-nav="%s" aria-current="page"' % p["nav"])
        out = HEAD % dict(title=html.escape(p["title"]), desc=html.escape(p["desc"]), url=url, og=og_url, ld=ld) + h + p["body"]() + footer.replace("{{WA}}", html.escape(p["wa"])).replace("{{DOCK_LABEL}}", p.get("dock", ("Sucursales", "index.html#sucursales"))[0]).replace("{{DOCK_HREF}}", p.get("dock", ("Sucursales", "index.html#sucursales"))[1])
        open(os.path.join(ROOT, p["file"]), "w").write(out)
        urls.append((url, p["priority"]))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>" % (u, TODAY, pr))
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    print("ok:", len(PAGES), "páginas", "(imágenes remotas)" if REMOTE else "")

if __name__ == "__main__":
    build()
