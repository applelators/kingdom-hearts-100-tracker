/*
 * Cloudflare Worker entrypoint.
 *
 * - Serves the static SPA from the [assets] binding.
 * - /api/state — optional cross-device progress sync. State is keyed by
 *   sha256(passphrase): anyone with the same code shares a save, and the raw
 *   code is never stored. Last-write-wins by the client's `lastModified` stamp,
 *   with a 409 guard so an older device can't clobber a newer save.
 *
 *   GET  /api/state?code=CODE  -> { state, lastModified } | { lastModified: 0 }
 *   PUT  /api/state?code=CODE  body {state,lastModified} -> 200 {ok} | 409 {newer}
 */
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET,PUT,OPTIONS",
  "access-control-allow-headers": "content-type",
};
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json", ...CORS } });

async function keyFor(code) {
  const data = new TextEncoder().encode("kh1fm:" + code);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return "state:" + [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function handleApi(request, env) {
  if (!env.KH1_STATE) return json({ error: "sync not configured" }, 503);
  if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

  const url = new URL(request.url);
  if (url.pathname !== "/api/state") return json({ error: "not found" }, 404);

  const code = (url.searchParams.get("code") || "").trim();
  if (code.length < 4) return json({ error: "code too short (min 4 chars)" }, 400);
  const key = await keyFor(code);

  if (request.method === "GET") {
    const raw = await env.KH1_STATE.get(key);
    if (!raw) return json({ lastModified: 0, state: null });
    return new Response(raw, { headers: { "content-type": "application/json", ...CORS } });
  }

  if (request.method === "PUT") {
    let body;
    try { body = await request.json(); } catch { return json({ error: "bad json" }, 400); }
    const incoming = Number(body && body.lastModified) || 0;
    const existingRaw = await env.KH1_STATE.get(key);
    if (existingRaw) {
      try {
        const existing = JSON.parse(existingRaw);
        if (Number(existing.lastModified) > incoming) {
          // someone else saved a newer version — don't clobber it
          return json({ error: "stale", newer: existing }, 409);
        }
      } catch { /* corrupt record — overwrite */ }
    }
    await env.KH1_STATE.put(key, JSON.stringify({ state: body.state, lastModified: incoming }));
    return json({ ok: true, lastModified: incoming });
  }

  return json({ error: "method not allowed" }, 405);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) return handleApi(request, env);
    return env.ASSETS.fetch(request);
  },
};
