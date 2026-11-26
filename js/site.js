/* ============================================================
   LAVAFORTE — JS del sitio (sin dependencias)
   CONFIG centraliza contacto y enlaces. Mientras `provisional` sea
   true se muestran las etiquetas "por confirmar".
   ============================================================ */
(function () {
  "use strict";

  var CONFIG = {
    provisional: true,
    whatsapp: "524779075087",          // WhatsApp único (solo mensajes)
    whatsappDisplay: "477 907 5087",
    // Línea directa (Fernando). La usan las páginas que build.py marca como
    // line "directo" (KioSoft y servicio técnico). Vacío = usa la general.
    whatsappDirect: "524777290604",
    whatsappDirectDisplay: "477 729 0604",
    // Google Ads: id "AW-…" y una etiqueta de conversión por tipo de página.
    // Mientras id esté vacío no se carga ningún script de Google.
    // Google: una sola etiqueta (gtag.js) para Ads y Analytics 4.
    // labels: conversión de Ads por tipo de contacto. "clientes" = WhatsApp desde
    // páginas de lavandería; "direcciones" = clic en "Cómo llegar".
    ads: { id: "AW-11035918867", labels: { kiosoft: "CGm_CIPp2LYdEJOEq44p", tecnico: "SGtNCIbp2LYdEJOEq44p",
                                          clientes: "_oCMCPenm8AdEJOEq44p", direcciones: "LnBkCPqnm8AdEJOEq44p" } },
    ga4: "G-GWDD6KWV5D",
    // Meta: Pixel en el navegador + API de conversiones (servidor) con el mismo
    // event_id para que Meta no cuente doble. Pixel vacío = no se carga nada.
    meta: { pixel: "", capi: "https://bzyxiadoibukmzmgdnha.supabase.co/functions/v1/meta-capi" },
    // TikTok Pixel: vacío = apagado. Prenderlo solo si se pautan anuncios en TikTok.
    tiktok: "",
    appName: "KioSoft Wash",
    appIos: "https://apps.apple.com/mx/app/kiosoft-wash/id6458121942",
    appAndroid: "https://play.google.com/store/apps/details?id=com.kiosoft.kiosoftwash",
    social: {
      instagram: "https://www.instagram.com/lavaforte_lavanderias",
      tiktok: "https://www.tiktok.com/@lavaforte_lavanderias",
      facebook: "https://www.facebook.com/lavaforte.lavanderias"
    }
  };
  window.LAVAFORTE = CONFIG;

  if (!CONFIG.provisional) document.documentElement.classList.add("is-final");

  var PAGE = window.LF_PAGE || {};
  var IS_DIRECT = PAGE.line === "directo" && !!CONFIG.whatsappDirect;
  var WA_NUMBER = IS_DIRECT ? CONFIG.whatsappDirect : CONFIG.whatsapp;
  var WA_DISPLAY = IS_DIRECT ? CONFIG.whatsappDirectDisplay : CONFIG.whatsappDisplay;
  function waLink(text) {
    return "https://wa.me/" + WA_NUMBER + (text ? "?text=" + encodeURIComponent(text) : "");
  }

  // ---------------------------------------------------------------- medición
  // Un solo punto (track) manda cada acción a Google Analytics 4, a Google Ads
  // y a Meta (Pixel + API de conversiones). Acciones que se miden:
  //   whatsapp     → clic a WhatsApp            (GA4 contact_whatsapp · Meta Contact)
  //   lead         → formulario enviado a WA     (GA4 generate_lead    · Meta Lead)
  //   directions   → clic en "Cómo llegar"       (GA4 get_directions   · Meta FindLocation)
  //   app          → clic a descargar la app     (GA4 app_download_click · Meta AppDownloadClick)
  //   call         → clic a un teléfono          (GA4 click_to_call    · Meta Contact)
  var gtagReady = false;
  if (CONFIG.ads.id || CONFIG.ga4) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    if (CONFIG.ga4) window.gtag("config", CONFIG.ga4, { page_type: PAGE.conv || "clientes", branch: PAGE.branch || undefined });
    if (CONFIG.ads.id) window.gtag("config", CONFIG.ads.id);
    var gs = document.createElement("script");
    gs.async = true; gs.src = "https://www.googletagmanager.com/gtag/js?id=" + (CONFIG.ga4 || CONFIG.ads.id);
    document.head.appendChild(gs);
    gtagReady = true;
  }

  function cookie(name) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }
  function eventId() {
    return "lf." + Date.now().toString(36) + "." + Math.random().toString(36).slice(2, 10);
  }
  var metaReady = false;
  if (CONFIG.meta.pixel) {
    /* Código base del Pixel de Meta */
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0;
      t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", CONFIG.meta.pixel);
    metaReady = true;
  }
  // Envía el mismo evento a la API de conversiones (servidor). text/plain evita
  // la verificación previa de CORS y sendBeacon sobrevive al cambio de página.
  function capi(name, id, data) {
    if (!metaReady || !CONFIG.meta.capi) return;
    var fbc = cookie("_fbc");
    var click = /[?&]fbclid=([^&#]+)/.exec(location.search);
    if (!fbc && click) fbc = "fb.1." + Date.now() + "." + click[1];
    var body = JSON.stringify({ event_name: name, event_id: id, event_source_url: location.href,
      fbp: cookie("_fbp"), fbc: fbc, custom_data: data || {} });
    try {
      if (!(navigator.sendBeacon && navigator.sendBeacon(CONFIG.meta.capi, body)))
        fetch(CONFIG.meta.capi, { method: "POST", body: body, keepalive: true, mode: "no-cors" });
    } catch (e) {}
  }
  function meta(name, data, custom) {
    if (!metaReady) return;
    var id = eventId();
    window.fbq(custom ? "trackCustom" : "track", name, data || {}, { eventID: id });
    capi(name, id, data);
  }
  meta("PageView");

  var ttReady = false;
  if (CONFIG.tiktok) {
    /* Código base del Pixel de TikTok */
    !function (w, d, t) { w.TiktokAnalyticsObject = t; var ttq = w[t] = w[t] || [];
      ttq.methods = ["page", "track", "identify", "instances", "debug", "on", "off", "once", "ready", "alias", "group", "enableCookie", "disableCookie"];
      ttq.setAndDefer = function (t, e) { t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))); }; };
      for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]);
      ttq.load = function (e, n) { var r = "https://analytics.tiktok.com/i18n/pixel/events.js"; ttq._i = ttq._i || {}; ttq._i[e] = []; ttq._i[e]._u = r;
        ttq._t = ttq._t || {}; ttq._t[e] = +new Date(); ttq._o = ttq._o || {}; ttq._o[e] = n || {};
        var o = d.createElement("script"); o.type = "text/javascript"; o.async = !0; o.src = r + "?sdkid=" + e + "&lib=" + t;
        var a = d.getElementsByTagName("script")[0]; a.parentNode.insertBefore(o, a); };
      ttq.load(CONFIG.tiktok); ttq.page(); }(window, document, "ttq");
    ttReady = true;
  }
  var TT_EVENT = { whatsapp: "Contact", lead: "SubmitForm", directions: "FindLocation", app: "Download", call: "Contact" };

  var GA_EVENT = { whatsapp: "contact_whatsapp", lead: "generate_lead", directions: "get_directions", app: "app_download_click", call: "click_to_call" };
  var META_EVENT = { whatsapp: ["Contact"], lead: ["Lead"], directions: ["FindLocation"], app: ["AppDownloadClick", true], call: ["Contact"] };
  var lastTrack = {};
  function track(kind, extra) {
    // Un clic puede disparar dos escuchas (formulario + enlace): uno por segundo.
    var now = Date.now();
    if (lastTrack[kind] && now - lastTrack[kind] < 1000) return;
    lastTrack[kind] = now;
    var pageType = PAGE.conv || "clientes";
    var data = { page_type: pageType, branch: (extra && extra.branch) || PAGE.branch || "", page_path: location.pathname };
    if (gtagReady) {
      window.gtag("event", GA_EVENT[kind], data);
      var label = null;
      if (kind === "directions") label = CONFIG.ads.labels.direcciones;
      else if (kind === "whatsapp" || kind === "lead" || kind === "call") label = CONFIG.ads.labels[pageType];
      if (label && CONFIG.ads.id) window.gtag("event", "conversion", { send_to: CONFIG.ads.id + "/" + label });
    }
    if (ttReady) window.ttq.track(TT_EVENT[kind], { content_category: pageType, content_name: data.branch || pageType });
    var m = META_EVENT[kind];
    meta(m[0], { content_category: pageType, content_name: data.branch || pageType }, m[1]);
  }
  window.LF_TRACK = track;

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (/wa\.me\//.test(a.href)) track("whatsapp");
    else if (/google\.[^/]+\/maps|maps\.google\.|maps\.app\.goo\.gl/.test(a.href)) track("directions", { branch: a.getAttribute("data-branch") });
    else if (/apps\.apple\.com|play\.google\.com/.test(a.href)) track("app");
    else if (/^tel:/.test(href)) track("call");
  }, true);


  // Enlaces de WhatsApp con mensaje según la página
  document.querySelectorAll("[data-wa]").forEach(function (a) {
    a.href = waLink(a.getAttribute("data-wa"));
    a.target = "_blank";
    a.rel = "noopener";
  });
  document.querySelectorAll("[data-wa-display]").forEach(function (el) { el.textContent = WA_DISPLAY; });
  document.querySelectorAll("[data-social]").forEach(function (a) {
    var u = CONFIG.social[a.getAttribute("data-social")];
    if (u) { a.href = u; a.target = "_blank"; a.rel = "noopener"; }
  });
  // Descarga de la app: [data-app] elige la tienda según el celular;
  // [data-app="ios"] / [data-app="android"] fijan la tienda.
  var isIOS = /iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent) && !/Android/.test(navigator.userAgent);
  document.querySelectorAll("[data-app]").forEach(function (a) {
    var which = a.getAttribute("data-app");
    var url = which === "ios" ? CONFIG.appIos : which === "android" ? CONFIG.appAndroid : (isIOS ? CONFIG.appIos : CONFIG.appAndroid);
    a.href = url; a.target = "_blank"; a.rel = "noopener";
  });

  // Navegación móvil
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Burbujas de marca (posiciones fijas por preset)
  var PRESETS = {
    right: [[90,16,78,.9],[80,10,28,.55],[84,48,16,.5],[76,62,42,.65],[70,24,20,.5],[60,80,14,.4]],
    scatter: [[6,22,58,.8],[18,64,22,.55],[42,14,30,.6],[63,58,18,.5],[84,18,70,.85],[93,64,26,.55]],
    left: [[7,20,62,.85],[17,12,26,.6],[14,52,15,.5],[21,42,36,.7],[26,30,12,.45]]
  };
  document.querySelectorAll("[data-bubbles]").forEach(function (host) {
    var items = PRESETS[host.getAttribute("data-bubbles")] || PRESETS.scatter;
    items.forEach(function (b, i) {
      var s = document.createElement("span");
      s.className = "bubble";
      s.style.left = b[0] + "%";
      s.style.top = b[1] + "%";
      s.style.width = s.style.height = b[2] + "px";
      s.style.marginLeft = s.style.marginTop = (-b[2] / 2) + "px";
      s.style.opacity = b[3];
      s.style.animationDelay = (i * -1.4) + "s";
      host.appendChild(s);
    });
  });

  // Aparición al hacer scroll
  var els = document.querySelectorAll("[data-reveal],[data-stagger]");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("is-in"); });
  }

  // Formularios → WhatsApp con el resumen (sin backend todavía)
  document.querySelectorAll("form[data-wa-form]").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!form.reportValidity()) return;
      var lines = [form.getAttribute("data-wa-form")];
      form.querySelectorAll("input,select,textarea").forEach(function (f) {
        if (!f.name || !f.value) return;
        var label = f.closest("label");
        var name = label ? label.firstChild.textContent.trim() : f.name;
        lines.push("• " + name + ": " + f.value.trim());
      });
      track("lead");
      window.open(waLink(lines.join("\n")), "_blank", "noopener");
    });
  });


  // Fotos que no cargan: dejamos el fondo de marca
  document.querySelectorAll("img").forEach(function (im) {
    function bad() { im.classList.add("is-broken"); }
    if (im.complete && im.naturalWidth === 0 && im.getAttribute("src")) bad();
    else im.addEventListener("error", bad);
  });

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Parallax suave: [data-parallax="0.25"]
  var px = Array.prototype.slice.call(document.querySelectorAll("[data-parallax]"));
  var dock = document.querySelector(".dock");
  var hero = document.querySelector(".hx");
  var ticking = false;
  function onScroll() {
    var vh = window.innerHeight;
    if (!reduce) px.forEach(function (el) {
      var r = el.parentElement.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var k = parseFloat(el.getAttribute("data-parallax")) || 0.2;
      var off = (r.top + r.height / 2 - vh / 2) * -k;
      el.style.transform = "translate3d(0," + off.toFixed(1) + "px,0)";
    });
    var y = window.scrollY || window.pageYOffset;
    document.documentElement.classList.toggle("is-scrolled", y > 20);
    if (dock) dock.classList.toggle("is-on", hero ? hero.getBoundingClientRect().bottom < vh * 0.6 : y > 300);
    ticking = false;
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  // Contadores: <b data-count="40" data-suffix="%">
  var cs = document.querySelectorAll("[data-count]");
  function run(el) {
    var to = parseFloat(el.getAttribute("data-count")), suf = el.getAttribute("data-suffix") || "", pre = el.getAttribute("data-prefix") || "";
    if (reduce) { el.textContent = pre + to + suf; return; }
    var t0 = null;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / 1400, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + Math.round(to * e) + suf;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { run(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.5 });
    cs.forEach(function (c) { co.observe(c); });
  } else cs.forEach(run);

  // Calculadora KioSoft
  document.querySelectorAll("[data-calc]").forEach(function (f) {
    var out = f.querySelector("[data-calc-out]"), wa = f.querySelector("[data-calc-wa]");
    function money(n) { return "$" + Math.round(n).toLocaleString("es-MX"); }
    function calc() {
      var m = +f.maquinas.value || 0, c = +f.ciclos.value || 0, p = +f.precio.value || 0, t = m * c * p * 30;
      out.textContent = money(t);
      wa.href = waLink("Hola Lavaforte, quiero cotizar KioSoft. Tengo " + m + " máquinas, unos " + c + " ciclos por máquina al día a $" + p + " (≈ " + money(t) + " al mes).");
      wa.target = "_blank"; wa.rel = "noopener";
    }
    f.addEventListener("input", calc);
    f.addEventListener("submit", function (e) { e.preventDefault(); });
    calc();
  });

  var y = document.querySelectorAll("[data-year]");
  y.forEach(function (n) { n.textContent = new Date().getFullYear(); });
})();
