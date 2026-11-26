// API de conversiones de Meta para www.lavaforte.com.mx
// El navegador manda cada evento aquí (mismo event_id que el Pixel) y esta
// función lo reenvía a Meta desde el servidor, con la IP y el navegador del
// visitante. Así Meta recibe el evento aunque un bloqueador frene el Pixel.
//
// Secretos (Supabase → Edge Functions → Secrets):
//   META_PIXEL_ID      id del conjunto de datos / Pixel
//   META_CAPI_TOKEN    token de acceso generado en el Administrador de eventos
//   META_TEST_CODE     opcional: código de "Probar eventos" mientras se verifica
//   META_GRAPH_VERSION opcional, por omisión v24.0
// Se despliega con verify_jwt = false: es un endpoint público que solo acepta
// eventos conocidos que vienen de lavaforte.com.mx.

const ALLOWED_EVENTS = new Set(["PageView", "Contact", "Lead", "FindLocation", "AppDownloadClick"]);
const ALLOWED_HOST = /(^|\.)lavaforte\.com\.mx$/;

function hostOf(u: string | null): string {
  try { return u ? new URL(u).hostname : ""; } catch { return ""; }
}

Deno.serve(async (req) => {
  const cors = { "Access-Control-Allow-Origin": "https://www.lavaforte.com.mx", "Vary": "Origin" };
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...cors, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "content-type" } });
  if (req.method !== "POST") return new Response("method", { status: 405, headers: cors });

  const pixel = Deno.env.get("META_PIXEL_ID");
  const token = Deno.env.get("META_CAPI_TOKEN");
  if (!pixel || !token) return new Response("not configured", { status: 503, headers: cors });

  let ev: Record<string, unknown>;
  try { ev = JSON.parse(await req.text()); } catch { return new Response("bad json", { status: 400, headers: cors }); }

  const sourceUrl = String(ev.event_source_url || "");
  const originHost = hostOf(req.headers.get("origin")) || hostOf(req.headers.get("referer")) || hostOf(sourceUrl);
  if (!ALLOWED_HOST.test(originHost) || !ALLOWED_HOST.test(hostOf(sourceUrl))) return new Response("origin", { status: 403, headers: cors });

  const name = String(ev.event_name || "");
  if (!ALLOWED_EVENTS.has(name)) return new Response("event", { status: 400, headers: cors });

  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim() || req.headers.get("cf-connecting-ip") || "";
  const ua = req.headers.get("user-agent") || "";
  const user_data: Record<string, string> = { client_user_agent: ua };
  if (ip) user_data.client_ip_address = ip;
  if (typeof ev.fbp === "string" && ev.fbp) user_data.fbp = ev.fbp;
  if (typeof ev.fbc === "string" && ev.fbc) user_data.fbc = ev.fbc;

  const custom = (ev.custom_data && typeof ev.custom_data === "object") ? ev.custom_data as Record<string, unknown> : {};
  const payload: Record<string, unknown> = {
    data: [{
      event_name: name,
      event_time: Math.floor(Date.now() / 1000),
      event_id: String(ev.event_id || "").slice(0, 100),
      event_source_url: sourceUrl.slice(0, 1000),
      action_source: "website",
      user_data,
      custom_data: {
        content_category: String(custom.content_category || "").slice(0, 50),
        content_name: String(custom.content_name || "").slice(0, 80),
      },
    }],
  };
  const test = Deno.env.get("META_TEST_CODE");
  if (test) payload.test_event_code = test;

  const version = Deno.env.get("META_GRAPH_VERSION") || "v24.0";
  const r = await fetch(`https://graph.facebook.com/${version}/${pixel}/events?access_token=${encodeURIComponent(token)}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload),
  });
  const out = await r.text();
  if (!r.ok) console.error("meta capi", r.status, out.slice(0, 500));
  return new Response(r.ok ? "ok" : "meta error", { status: r.ok ? 200 : 502, headers: cors });
});
