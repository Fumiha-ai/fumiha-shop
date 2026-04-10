/**
 * 商品データ API（Cloudflare KV使用）
 *
 * GET  /api/products  → 商品データを返す（5分キャッシュでBOOTH在庫自動チェック）
 * POST /api/products  → 管理ページからの保存。body: { products: { ... } }
 *
 * KV バインディング名: PRODUCTS_KV
 */

const SYNC_TTL_MS = 5 * 60 * 1000;

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

async function checkBoothSoldOut(url) {
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ja,en;q=0.9',
      },
    });
    if (!res.ok) return null;
    const html = await res.text();
    const signals = [
      html.includes('在庫なし'),
      html.includes('"is_sold_out":true'),
      html.includes('"soldout":true'),
      html.includes('sold-out'),
      html.includes('soldout'),
      html.includes('SOLD OUT'),
      !html.includes('cart'),
    ];
    return signals.filter(Boolean).length >= 3;
  } catch {
    return null;
  }
}

export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method;

  if (method === 'OPTIONS') {
    return new Response('', { status: 204, headers: CORS_HEADERS });
  }

  const kv = env.PRODUCTS_KV;

  // ── POST: 管理ページから設定保存 ──
  if (method === 'POST') {
    try {
      const { products } = await request.json();
      if (!products) {
        return new Response(JSON.stringify({ error: 'products required' }), { status: 400, headers: CORS_HEADERS });
      }
      let lastSync = 0;
      try {
        const current = await kv.get('data', 'json');
        lastSync = current?.lastSync || 0;
      } catch {}
      await kv.put('data', JSON.stringify({ products, lastSync }));
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: CORS_HEADERS });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: CORS_HEADERS });
    }
  }

  // ── GET: 商品データ取得 + 自動同期 ──
  let stored = null;
  try {
    stored = await kv.get('data', 'json');
  } catch {}

  const products = stored?.products || {};
  const lastSync = stored?.lastSync || 0;
  const now = Date.now();

  if (now - lastSync > SYNC_TTL_MS) {
    const targets = Object.entries(products).filter(([, d]) => d.boothUrl);
    await Promise.all(targets.map(async ([id, data]) => {
      const soldOut = await checkBoothSoldOut(data.boothUrl);
      if (soldOut !== null) products[id] = { ...data, soldOut };
    }));
    try {
      await kv.put('data', JSON.stringify({ products, lastSync: now }));
    } catch {}
  }

  return new Response(JSON.stringify(products), { status: 200, headers: CORS_HEADERS });
}
