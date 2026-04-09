/**
 * 商品データ API（Netlify Blobs使用）
 *
 * GET  /.netlify/functions/products
 *   → 現在の商品データを返す。最後の同期から5分以上経過していれば
 *     BOOTH在庫を自動チェックして更新してから返す。
 *
 * POST /.netlify/functions/products
 *   → 管理ページからの保存。body: { products: { ... } }
 */
const { getStore } = require('@netlify/blobs');

const SYNC_TTL_MS = 5 * 60 * 1000; // 5分キャッシュ

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

exports.handler = async (event) => {
  // CORSプリフライト
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  const store = getStore('fumiha-products');

  // ── POST: 管理ページから設定保存 ──
  if (event.httpMethod === 'POST') {
    try {
      const { products } = JSON.parse(event.body || '{}');
      if (!products) {
        return { statusCode: 400, headers: CORS_HEADERS, body: JSON.stringify({ error: 'products required' }) };
      }
      // 既存の lastSync は引き継ぐ（保存しただけで同期タイマーはリセットしない）
      let lastSync = 0;
      try {
        const current = await store.get('data', { type: 'json' });
        lastSync = current?.lastSync || 0;
      } catch {}
      await store.setJSON('data', { products, lastSync });
      return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify({ ok: true }) };
    } catch (e) {
      return { statusCode: 500, headers: CORS_HEADERS, body: JSON.stringify({ error: e.message }) };
    }
  }

  // ── GET: 商品データ取得 + 自動同期 ──
  let stored = null;
  try {
    stored = await store.get('data', { type: 'json' });
  } catch {}

  const products = stored?.products || {};
  const lastSync = stored?.lastSync || 0;
  const now = Date.now();

  // 5分以上経過していたらBOOTH在庫を再確認
  if (now - lastSync > SYNC_TTL_MS) {
    const targets = Object.entries(products).filter(([, d]) => d.boothUrl);
    await Promise.all(targets.map(async ([id, data]) => {
      const soldOut = await checkBoothSoldOut(data.boothUrl);
      if (soldOut !== null) products[id] = { ...data, soldOut };
    }));
    // 同期結果をBlobs に保存（URLがなくてもタイマーリセット）
    try {
      await store.setJSON('data', { products, lastSync: now });
    } catch {}
  }

  return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify(products) };
};
