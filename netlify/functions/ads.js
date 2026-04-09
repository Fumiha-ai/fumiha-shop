/**
 * 広告データ API（Netlify Blobs使用）
 *
 * GET  /.netlify/functions/ads   → 広告リストを返す
 * POST /.netlify/functions/ads   → 管理ページからの保存。body: { ads: [...] }
 */
const { getStore } = require('@netlify/blobs');

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  const store = getStore('fumiha-ads');

  // ── POST: 広告リスト保存 ──
  if (event.httpMethod === 'POST') {
    try {
      const { ads } = JSON.parse(event.body || '{}');
      if (!Array.isArray(ads)) {
        return { statusCode: 400, headers: CORS_HEADERS, body: JSON.stringify({ error: 'ads array required' }) };
      }
      await store.setJSON('data', { ads });
      return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify({ ok: true }) };
    } catch (e) {
      return { statusCode: 500, headers: CORS_HEADERS, body: JSON.stringify({ error: e.message }) };
    }
  }

  // ── GET: 広告リスト取得 ──
  // stored が null = まだ一度も保存されていない → null を返してクライアントの
  // localStorage を上書きしないようにする（[] との区別のため）
  let stored = null;
  try {
    stored = await store.get('data', { type: 'json' });
  } catch {}

  if (stored === null) {
    return { statusCode: 200, headers: CORS_HEADERS, body: 'null' };
  }
  return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify(stored.ads ?? []) };
};
