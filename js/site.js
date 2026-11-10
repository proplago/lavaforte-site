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
    appUrl: null,                      // ← enlace de descarga de la app (pendiente)
    social: {
      instagram: "https://www.instagram.com/lavaforte_lavanderias",
      tiktok: "https://www.tiktok.com/@lavaforte_lavanderias",
      facebook: "https://www.facebook.com/lavaforte.lavanderias"
    }
  };
  window.LAVAFORTE = CONFIG;

  if (!CONFIG.provisional) document.documentElement.classList.add("is-final");

  function waLink(text) {
    return "https://wa.me/" + CONFIG.whatsapp + (text ? "?text=" + encodeURIComponent(text) : "");
  }


  // Enlaces de WhatsApp con mensaje según la página
  document.querySelectorAll("[data-wa]").forEach(function (a) {
    a.href = waLink(a.getAttribute("data-wa"));
    a.target = "_blank";
    a.rel = "noopener";
  });
  document.querySelectorAll("[data-social]").forEach(function (a) {
    var u = CONFIG.social[a.getAttribute("data-social")];
    if (u) { a.href = u; a.target = "_blank"; a.rel = "noopener"; }
  });
  document.querySelectorAll("[data-app]").forEach(function (a) {
    if (CONFIG.appUrl) { a.href = CONFIG.appUrl; a.target = "_blank"; a.rel = "noopener"; }
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
