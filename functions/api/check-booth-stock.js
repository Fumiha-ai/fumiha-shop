/**
 * BOOTH在庫確認 API
 * GET /api/check-booth-stock?url=https://xxxxx.booth.pm/items/xxxxxxx
 */

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);
  const boothUrl = url.searchParams.get('url');

  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  };

  if (!boothUrl) {
    return new Response(JSON.stringify({ error: 'url パラメータが必要です' }), { status: 400, headers });
  }
  if (!boothUrl.includes('booth.pm')) {
    return new Response(JSON.stringify({ error: 'BOOTHのURLを指定してください' }), { status: 400, headers });
  }

  try {
    const res = await fetch(boothUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ja,en;q=0.9',
      },
    });

    if (!res.ok) {
      return new Response(JSON.stringify({ error: `BOOTH取得失敗: ${res.status}` }), { status: 502, headers });
    }

    const html = await res.text();

    const soldOutSignals = [
      html.includes('在庫なし'),
      html.includes('"is_sold_out":true'),
      html.includes('"soldout":true'),
      html.includes('sold-out'),
      html.includes('soldout'),
      html.includes('SOLD OUT'),
      !html.includes('cart'),
    ];

    const matchCount = soldOutSignals.filter(Boolean).length;
    const soldOut = matchCount >= 3;

    return new Response(JSON.stringify({ soldOut, url: boothUrl }), { status: 200, headers });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
  }
}
