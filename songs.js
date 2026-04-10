/**
 * ふみはBGM — 楽曲データ
 *
 * 新しい曲を追加するときはこのファイルに追記するだけでOKです。
 *
 * type:   'one-of-a-kind' | 'regular' | 'free'
 */
const SONGS = [
  {
    id:             'audio1',
    title:          'Neon Lobby',
    type:           'one-of-a-kind',
    description:    '待機画面にぴったりな軽快なシンセポップ。ループ仕様で途切れなし。',
    price:          500,
    duration:       '2:34',
    jacket:         'images/neon-lobby.jpg',
    jacketGradient: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)',
    jacketEmoji:    '🎙',
    audio:          'audio/neon-lobby.mp3',
    youtube:        'https://www.youtube.com/watch?v=dQw4w9WgXcQ', // YouTubeリンクを入力
    licenses:       ['配信OK', '収益化OK', 'ループ'],
    tags:           ['明るい', '楽しい', 'ポップ'],
  },
  {
    id:             'audio2',
    title:          'Cozy Rain Café',
    type:           'regular',
    description:    'ローファイチルのBGM。リラックス配信・作業配信向け。雨音ループ入り。',
    price:          500,
    duration:       '3:10',
    jacket:         'images/cozy-rain-cafe.jpg',
    jacketGradient: 'linear-gradient(135deg, #1c3a3a, #2d5a5a, #1a2e2e)',
    jacketEmoji:    '☕',
    audio:          'audio/cozy-rain-cafe.mp3',
    licenses:       ['配信OK', '収益化OK', 'ループ'],
    tags:           ['穏やか', '優しい', 'ヒーリング', 'アンビエント'],
  },
  {
    id:             'audio3',
    title:          'Spark Intro',
    type:           'regular',
    description:    'オープニング・イントロに最適な元気系ポップ。テンション上げる30秒版も付属。',
    price:          800,
    duration:       '1:45',
    jacket:         'images/spark-intro.jpg',
    jacketGradient: 'linear-gradient(135deg, #f7971e, #ffd200, #f7971e)',
    jacketEmoji:    '⚡',
    audio:          'audio/spark-intro.mp3',
    licenses:       ['YouTube収益化OK', '商用可'],
    tags:           ['明るい', '楽しい', '力強い', '速い', 'ポップ'],
  },
  {
    id:             'audio4',
    title:          'Daily Vlog Drive',
    type:           'free',
    description:    'Vlog・日常動画向けのアコースティックポップ。明るくさりげなく。',
    price:          0,
    duration:       '2:58',
    jacket:         'images/daily-vlog-drive.jpg',
    jacketGradient: 'linear-gradient(135deg, #56ab2f, #a8e063, #56ab2f)',
    jacketEmoji:    '🌿',
    audio:          'audio/daily-vlog-drive.mp3',
    licenses:       ['YouTube収益化OK', 'SNS投稿OK'],
    tags:           ['明るい', '爽やか', '日常', 'アコースティック'],
  },
  {
    id:             'audio5',
    title:          'Dungeon Echo',
    type:           'one-of-a-kind',
    description:    'ダンジョン探索系RPGに合うオーケストラ×エレクトロ。シームレスループ。',
    price:          1200,
    duration:       '3:22',
    jacket:         'images/dungeon-echo.jpg',
    jacketGradient: 'linear-gradient(135deg, #0a0a0a, #1a0533, #2d1b69)',
    jacketEmoji:    '⚔️',
    audio:          'audio/dungeon-echo.mp3',
    licenses:       ['ゲーム内使用OK', 'アプリOK', 'ループ'],
    tags:           ['暗い', '緊張感', '恐ろしい', 'ゲーム', 'シネマ'],
  },
  {
    id:             'audio6',
    title:          'Clarity Pulse',
    type:           'regular',
    description:    'プレゼン・企業VP・展示会向けのクリーンなコーポレートBGM。',
    price:          1500,
    duration:       '2:15',
    jacket:         'images/clarity-pulse.jpg',
    jacketGradient: 'linear-gradient(135deg, #1a237e, #3949ab, #7986cb)',
    jacketEmoji:    '💼',
    audio:          'audio/clarity-pulse.mp3',
    licenses:       ['商用OK', '社内動画OK', '広告OK'],
    tags:           ['お洒落', '冷静', '壮大', 'デジタル'],
  },

  // ↓ 新しい曲はここに追加 ↓
  // {
  //   id:             'audio7',
  //   title:          '曲タイトル',
  //   type:           'regular',       // one-of-a-kind / regular / free
  //   description:    '説明文',
  //   price:          500,
  //   duration:       '3:00',
  //   jacket:         'images/ファイル名.jpg',
  //   jacketGradient: 'linear-gradient(135deg, #111, #333)',
  //   jacketEmoji:    '🎵',
  //   audio:          'audio/ファイル名.mp3',
  //   youtube:        'https://www.youtube.com/watch?v=XXXXXXXXXXX', // 任意: YouTubeリンクがあれば
  //   licenses:       ['配信OK', '収益化OK'],
  //   tags:           ['明るい', 'ポップ'],   // 管理ページで設定可
  // },
];
