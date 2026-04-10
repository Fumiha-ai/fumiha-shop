/**
 * 統計API（インプレッション・ダウンロード数）
 *
 * GET  /api/stats → 全統計を返す（管理ページ用）
 * POST /api/stats → イベントをバッチ記録
 *   body: { events: [{ songId: "audio1", type: "impression" | "download" }] }
 *
 * KV バインディング名: PRODUCTS_KV（既存を流用、キー "stats" で保存）
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

  const kv = env.PRODUCTS_KV;

  // ── GET: 統計データ取得 ──
  if (method === 'GET') {
    let stats = {};
    try {
      stats = (await kv.get('stats', 'json')) || {};
    } catch {}
    return new Response(JSON.stringify(stats), { status: 200, headers: CORS_HEADERS });
  }

  // ── POST: イベント記録 ──
  if (method === 'POST') {
    try {
      const { events } = await request.json();
      if (!Array.isArray(events) || events.length === 0) {
        return new Response(JSON.stringify({ error: 'events required' }), { status: 400, headers: CORS_HEADERS });
      }

      let stats = {};
      try {
        stats = (await kv.get('stats', 'json')) || {};
      } catch {}

      for (const { songId, type } of events) {
        if (!songId || !['impression', 'download'].includes(type)) continue;
        if (!stats[songId]) stats[songId] = { impressions: 0, downloads: 0 };
        if (type === 'impression') stats[songId].impressions++;
        if (type === 'download')   stats[songId].downloads++;
      }

      await kv.put('stats', JSON.stringify(stats));
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: CORS_HEADERS });
    }
  }

  return new Response('Method Not Allowed', { status: 405, headers: CORS_HEADERS });
}
