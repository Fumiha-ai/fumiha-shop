/**
 * BOOTH在庫確認 サーバーレス関数
 * GET /.netlify/functions/check-booth-stock?url=https://xxxxx.booth.pm/items/xxxxxxx
 */
exports.handler = async (event) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  };

  // URLパラメータの検証
  const { url } = event.queryStringParameters || {};
  if (!url) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'url パラメータが必要です' }) };
  }
  if (!url.includes('booth.pm')) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'BOOTHのURLを指定してください' }) };
  }

  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ja,en;q=0.9',
      },
    });

    if (!res.ok) {
      return { statusCode: 502, headers, body: JSON.stringify({ error: `BOOTH取得失敗: ${res.status}` }) };
    }

    const html = await res.text();

    // ── 売り切れ判定 ──
    // BOOTHのHTMLに含まれる売り切れの手がかりを複数チェック
    const soldOutSignals = [
      html.includes('在庫なし'),
      html.includes('"is_sold_out":true'),
      html.includes('"soldout":true'),
      html.includes('sold-out'),
      html.includes('soldout'),
      html.includes('SOLD OUT'),
      // カートに入れるボタンが存在しない
      !html.includes('cart'),
    ];

    // 3つ以上の手がかりが一致したら売り切れと判定（誤検知を防ぐため）
    const matchCount = soldOutSignals.filter(Boolean).length;
    const soldOut    = matchCount >= 3;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ soldOut, url }),
    };

  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
