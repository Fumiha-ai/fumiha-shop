/**
 * 広告データ API（Cloudflare KV使用）
 *
 * GET  /api/ads  → 広告リストを返す
 * POST /api/ads  → 管理ページからの保存。body: { ads: [...] }
 *
 * KV バインディング名: ADS_KV
 */

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method;

  if (method === 'OPTIONS') {
    return new Response('', { status: 204, headers: CORS_HEADERS });
  }

  const kv = env.ADS_KV;

  // ── POST: 広告リスト保存 ──
  if (method === 'POST') {
    try {
      const { ads } = await request.json();
      if (!Array.isArray(ads)) {
        return new Response(JSON.stringify({ error: 'ads array required' }), { status: 400, headers: CORS_HEADERS });
      }
      await kv.put('data', JSON.stringify({ ads }));
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: CORS_HEADERS });
    }
  }

  // ── GET: 広告リスト取得 ──
  let stored = null;
  try {
    stored = await kv.get('data', 'json');
  } catch {}

  if (stored === null) {
    return new Response('null', { status: 200, headers: CORS_HEADERS });
  }
  return new Response(JSON.stringify(stored.ads ?? []), { status: 200, headers: CORS_HEADERS });
}
