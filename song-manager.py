# -*- coding: utf-8 -*-
"""
ふみはBGM 曲管理ツール
songs.jsを直接読み書きするデスクトップGUIツール
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, re, subprocess, sys

# フォント設定（日本語ゴシック）
FONT_FAMILY = 'Yu Gothic UI'
F_NORMAL = (FONT_FAMILY, 11)
F_BOLD   = (FONT_FAMILY, 11, 'bold')
F_SMALL  = (FONT_FAMILY, 10)
F_LARGE  = (FONT_FAMILY, 13, 'bold')
F_TITLE  = (FONT_FAMILY, 14, 'bold')

# PyInstallerでexe化した場合はexeのディレクトリ、通常実行はスクリプトのディレクトリ
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_JS   = os.path.join(SCRIPT_DIR, 'songs.js')
DEPLOY_BAT = os.path.join(SCRIPT_DIR, 'deploy.bat')
DESC_DIR   = os.path.join(SCRIPT_DIR, 'description')
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')
AUDIO_DIR  = os.path.join(SCRIPT_DIR, 'audio')

TYPE_OPTIONS = [
    ('regular',       '通常販売'),
    ('one-of-a-kind', '限定1点'),
    ('free',          'フリー（無料）'),
]
GRAD_PRESETS = [
    ('ダークパープル', 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)'),
    ('ダークティール', 'linear-gradient(135deg, #1c3a3a, #2d5a5a, #1a2e2e)'),
    ('オレンジ',       'linear-gradient(135deg, #f7971e, #ffd200, #f7971e)'),
    ('グリーン',       'linear-gradient(135deg, #56ab2f, #a8e063, #56ab2f)'),
    ('ダーク',         'linear-gradient(135deg, #0a0a0a, #1a0533, #2d1b69)'),
    ('ブルー',         'linear-gradient(135deg, #1a237e, #3949ab, #7986cb)'),
    ('ピンク',         'linear-gradient(135deg, #f953c6, #b91d73)'),
    ('レッド',         'linear-gradient(135deg, #f12711, #f5af19)'),
]
TYPE_LABEL  = {k: v for k, v in TYPE_OPTIONS}
TYPE_MAP    = {v: k for k, v in TYPE_OPTIONS}

# ── タグ定義 ──────────────────────────────────────────────
TAG_CATEGORIES = [
    ('雰囲気・感情', ['明るい','楽しい','穏やか','爽やか','お洒落','力強い','可愛い',
                     '不思議','シリアス','緊張感','切ない','暗い','恐ろしい','激しい','日常']),
    ('リズム・曲調', ['速い','遅い','軽快','壮大','ポップ','ロック','ジャズ','クラシック',
                     'EDM','アンビエント','アコースティック','和風','ゲーム','シネマ','ヒーリング']),
]

# キーワード → タグ のマッピング（テキストファイル自動解析用）
TAG_KEYWORDS = {
    '明るい':         ['明るい', '明るく', '明るさ', '元気'],
    '楽しい':         ['楽しい', '楽しく', 'ハッピー', '陽気', '弾む'],
    '穏やか':         ['穏やか', 'おだやか', 'セレーン', '落ち着き', '落ち着い', '穏やかな'],
    '爽やか':         ['爽やか', 'さわやか', 'フレッシュ', 'クリア'],
    'お洒落':         ['お洒落', 'おしゃれ', 'スタイリッシュ', 'クール'],
    '力強い':         ['力強い', '力強さ', '力強く', 'パワフル', 'エネルギッシュ'],
    '可愛い':         ['可愛い', 'かわいい', 'キュート', 'カワイイ', 'kawaii', 'Kawaii'],
    '不思議':         ['不思議', '神秘的', 'ミステリアス'],
    'シリアス':       ['シリアス', '真剣', '重厚'],
    '緊張感':         ['緊張感', '緊張', 'スリル', 'サスペンス'],
    '切ない':         ['切ない', '切なさ', 'メランコリック', '哀愁', 'センチメンタル'],
    '暗い':           ['暗い', '暗く', 'ダーク'],
    '恐ろしい':       ['恐ろしい', '恐怖', 'ホラー'],
    '激しい':         ['激しい', '激しく', 'アグレッシブ'],
    '日常':           ['日常', '日常的', '普段', 'ふだん'],
    '速い':           ['速い', 'アップテンポ', '疾走', 'ファスト'],
    '遅い':           ['遅い', 'スロー', 'ゆっくり', 'ダウンテンポ'],
    '軽快':           ['軽快', '軽やか', '軽い'],
    '壮大':           ['壮大', 'エピック', 'ドラマチック', 'epic', 'Epic', 'dramatic', 'Dramatic'],
    'ポップ':         ['ポップ', 'pop', 'Pop', 'POP'],
    'ロック':         ['ロック', 'rock', 'Rock', 'ROCK'],
    'ジャズ':         ['ジャズ', 'jazz', 'Jazz', 'スウィング'],
    'クラシック':     ['クラシック', 'classic', 'Classic', 'オーケストラ'],
    'EDM':            ['EDM', 'edm', 'エレクトロ', 'テクノ', 'ダンス'],
    'アンビエント':   ['アンビエント', 'ambient', 'Ambient'],
    'アコースティック': ['アコースティック', 'acoustic', 'Acoustic'],
    '和風':           ['和風', '日本風', '雅', '和楽器', '和太鼓'],
    'ゲーム':         ['ゲーム', 'game', 'Game', 'ゲームBGM'],
    'シネマ':         ['シネマ', 'cinema', 'Cinema', '映画', '映像', 'ドラマ'],
    'ヒーリング':     ['ヒーリング', 'healing', 'Healing', 'リラックス', '癒し', 'リラクゼーション', '睡眠'],
}

# ── テキストファイル解析 ──────────────────────────────────
def extract_from_txt(filepath):
    """テキストファイルから説明文とタグを抽出して返す"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 説明文: 1行目（タイトル）の後、最初の空行をスキップして次のパラグラフ
    description = ''
    in_desc = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0:
            continue  # タイトル行スキップ
        if not in_desc:
            if stripped == '':
                continue  # 空行スキップ
            in_desc = True
        if in_desc:
            if stripped == '':
                break  # パラグラフ終了
            description += stripped + ' '
    description = description.strip()

    # タグ: ファイル全体のテキストとキーワードを照合
    full_text = ''.join(lines)
    matched = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in full_text for kw in keywords):
            matched.append(tag)

    return description, matched


# ── フォルダスキャン ──────────────────────────────────
def scan_new_songs(existing_songs):
    """description フォルダをスキャンして songs.js 未登録の曲を検出"""
    existing_titles = {s.get('title', '') for s in existing_songs}
    new_songs = []

    if not os.path.isdir(DESC_DIR):
        return new_songs

    for fname in sorted(os.listdir(DESC_DIR)):
        if not fname.lower().endswith('.txt'):
            continue
        title = os.path.splitext(fname)[0]
        if title in existing_titles:
            continue

        txt_path = os.path.join(DESC_DIR, fname)
        try:
            desc, tags = extract_from_txt(txt_path)
        except Exception:
            desc, tags = '', []

        # 画像・音声ファイルの検索（png/jpg/mp3/wav）
        jacket = ''
        for ext in ('.png', '.jpg', '.jpeg', '.webp'):
            if os.path.exists(os.path.join(IMAGES_DIR, title + ext)):
                jacket = f'images/{title}{ext}'
                break

        audio = ''
        for ext in ('.mp3', '.wav', '.ogg', '.m4a'):
            if os.path.exists(os.path.join(AUDIO_DIR, title + ext)):
                audio = f'audio/{title}{ext}'
                break

        new_songs.append({
            'id':             '',
            'title':          title,
            'type':           'free',
            'description':    desc,
            'price':          0,
            'duration':       '--:--',
            'jacket':         jacket,
            'jacketGradient': GRAD_PRESETS[0][1],
            'jacketEmoji':    '🎵',
            'audio':          audio,
            'youtube':        '',
            'licenses':       [],
            'tags':           tags,
        })

    return new_songs


# ── songs.js 読み書き ──────────────────────────────────
def parse_songs():
    with open(SONGS_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'//[^\n]*', '', content)
    songs = []
    for block in re.findall(r'\{([^{}]+?)\}', content, re.DOTALL):
        s = {}
        for key in ['id','title','type','description',
                    'duration','jacket','jacketGradient','jacketEmoji','audio','youtube']:
            m = re.search(rf'\b{key}:\s*[\'"]([^\'"]*)[\'"]', block)
            if m:
                s[key] = m.group(1)
        m = re.search(r'\bprice:\s*(\d+)', block)
        if m:
            s['price'] = int(m.group(1))
        m = re.search(r'\blicenses:\s*\[(.*?)\]', block, re.DOTALL)
        s['licenses'] = re.findall(r'[\'"]([^\'"]+)[\'"]', m.group(1)) if m else []
        m = re.search(r'\btags:\s*\[(.*?)\]', block, re.DOTALL)
        s['tags'] = re.findall(r'[\'"]([^\'"]+)[\'"]', m.group(1)) if m else []
        if s.get('id', '').startswith('audio'):
            songs.append(s)
    return songs


def write_songs(songs):
    entries = []
    for s in songs:
        lic  = ', '.join(f"'{l}'" for l in (s.get('licenses') or []))
        tags = ', '.join(f"'{t}'" for t in (s.get('tags') or []))
        desc = (s.get('description') or '').replace("'", "\\'")
        yt = s.get('youtube', '').strip()
        yt_line = f"\n    youtube:        '{yt}'," if yt else ''
        entries.append(f"""  {{
    id:             '{s.get('id','')}',
    title:          '{s.get('title','')}',
    type:           '{s.get('type','')}',
    description:    '{desc}',
    price:          {s.get('price', 0)},
    duration:       '{s.get('duration','--:--')}',
    jacket:         '{s.get('jacket','')}',
    jacketGradient: '{s.get('jacketGradient','')}',
    jacketEmoji:    '{s.get('jacketEmoji','🎵')}',
    audio:          '{s.get('audio','')}',{yt_line}
    licenses:       [{lic}],
    tags:           [{tags}],
  }}""")
    content = ('const SONGS = [\n' + ',\n'.join(entries) +
               ',\n\n  // ↓ 新しい曲はここに追加 ↓\n];\n')
    with open(SONGS_JS, 'w', encoding='utf-8') as f:
        f.write(content)


# ── メインウィンドウ ──────────────────────────────────
class App:
    def __init__(self, root):
        self.root   = root
        self.songs  = []
        root.title('ふみはBGM 曲管理ツール')
        root.geometry('860x560')
        root.minsize(700, 440)
        root.configure(bg='#F7F8FC')
        self._setup_style()
        self._build_ui()
        self._load()

    def _setup_style(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('Treeview', rowheight=38, font=F_NORMAL, background='#fff',
                    fieldbackground='#fff', borderwidth=0)
        s.configure('Treeview.Heading', font=F_BOLD,
                    background='#EEF1FE', foreground='#4A6CF7', relief='flat')
        s.map('Treeview', background=[('selected','#4A6CF7')],
              foreground=[('selected','white')])
        self._stripe_odd  = '#F4F6FF'
        self._stripe_even = '#FFFFFF'
        s.configure('TCombobox', font=F_NORMAL)
        s.configure('TCheckbutton', font=F_NORMAL)

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg='#4A6CF7', height=52)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text='ふみはBGM  曲管理ツール', bg='#4A6CF7', fg='white',
                 font=F_TITLE).pack(side='left', padx=22, pady=13)

        tb = tk.Frame(self.root, bg='white', pady=8, padx=16,
                      relief='flat', bd=0,
                      highlightthickness=1, highlightbackground='#E4E7F0')
        tb.pack(fill='x')
        self._btn(tb, '＋ 追加',            self._add,       '#4A6CF7', 'white').pack(side='left', padx=(0,6))
        self._btn(tb, '📂 自動追加',         self._auto_add,  '#6B3FA0', 'white').pack(side='left', padx=(0,6))
        self._btn(tb, '✏  編集',            self._edit,      '#F7F8FC', '#1A1C2A').pack(side='left', padx=(0,6))
        self._btn(tb, '🗑  削除',           self._delete,    '#FEF2F2', '#D94545').pack(side='left', padx=(0,18))
        self._btn(tb, '💾  songs.js に保存', self._save,      '#1A7A47', 'white').pack(side='left', padx=(0,6))
        self._btn(tb, '🚀  Deploy',          self._deploy,    '#C25F00', 'white').pack(side='left')

        pane = tk.Frame(self.root, bg='#F7F8FC')
        pane.pack(fill='both', expand=True, padx=16, pady=12)

        cols  = ('no','title','type','price','duration','tags')
        heads = ('No.','タイトル','販売種別','価格','時間','タグ')
        widths = (40, 240, 100, 70, 60, 230)

        self.tree = ttk.Treeview(pane, columns=cols, show='headings', selectmode='browse')
        for c, h, w in zip(cols, heads, widths):
            self.tree.heading(c, text=h)
            anchor = 'center' if c in ('no','price','duration','type') else 'w'
            self.tree.column(c, width=w, anchor=anchor, minwidth=w)

        vsb = ttk.Scrollbar(pane, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', lambda _: self._edit())

        self.status = tk.StringVar(value='読み込み中...')
        tk.Label(self.root, textvariable=self.status, bg='#E4E7F0', fg='#6B7080',
                 font=F_SMALL, anchor='w', padx=14, pady=4).pack(fill='x', side='bottom')

    def _btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         font=F_SMALL, relief='flat',
                         padx=14, pady=5, cursor='hand2', activebackground=bg)

    def _load(self):
        try:
            self.songs = parse_songs()
            self._refresh()
            self.status.set(f'✓ {len(self.songs)}曲を読み込みました  —  {SONGS_JS}')
        except Exception as e:
            messagebox.showerror('読み込みエラー', f'songs.jsの読み込みに失敗しました:\n{e}')

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.tag_configure('odd',  background=self._stripe_odd)
        self.tree.tag_configure('even', background=self._stripe_even)
        TYPE_JP = {'regular':'通常', 'one-of-a-kind':'限定1点', 'free':'フリー'}
        for i, s in enumerate(self.songs):
            price = '無料' if s.get('price',0)==0 else f"¥{s.get('price',0):,}"
            tags_str = '  '.join(s.get('tags') or [])
            tag = 'odd' if i % 2 == 0 else 'even'
            self.tree.insert('', 'end', iid=i, tags=(tag,), values=(
                i+1, s.get('title','（無題）'),
                TYPE_JP.get(s.get('type',''), s.get('type','')),
                price, s.get('duration',''), tags_str,
            ))

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('未選択', '曲を選択してください')
            return None
        return int(sel[0])

    def _add(self):
        dlg = SongDialog(self.root, '曲を追加', {})
        if dlg.result:
            max_n = max(
                (int(s['id'].replace('audio','')) for s in self.songs
                 if re.match(r'audio\d+', s.get('id',''))),
                default=0)
            dlg.result['id'] = f'audio{max_n+1}'
            self.songs.append(dlg.result)
            self._refresh()
            self.status.set(f'＋ 「{dlg.result["title"]}」を追加しました（未保存）')

    def _edit(self):
        idx = self._selected()
        if idx is None: return
        dlg = SongDialog(self.root, '曲を編集', self.songs[idx])
        if dlg.result:
            dlg.result['id'] = self.songs[idx]['id']
            self.songs[idx]  = dlg.result
            self._refresh()
            self.status.set(f'✏  「{dlg.result["title"]}」を編集しました（未保存）')

    def _delete(self):
        idx = self._selected()
        if idx is None: return
        title = self.songs[idx].get('title','')
        if messagebox.askyesno('削除確認', f'「{title}」を削除しますか？'):
            self.songs.pop(idx)
            self._refresh()
            self.status.set(f'🗑  「{title}」を削除しました（未保存）')

    def _save(self):
        try:
            write_songs(self.songs)
            self.status.set(f'✓ songs.jsに保存しました（{len(self.songs)}曲）')
            messagebox.showinfo('保存完了',
                'songs.jsを保存しました。\n\ndeploy.batを実行するとサイトに反映されます。')
        except Exception as e:
            messagebox.showerror('保存エラー', str(e))

    def _auto_add(self):
        new_songs = scan_new_songs(self.songs)
        if not new_songs:
            messagebox.showinfo('自動追加', '新しく追加できる曲が見つかりませんでした。\n\ndescription フォルダに .txt ファイルを置いてください。')
            return
        dlg = AutoAddDialog(self.root, new_songs)
        if dlg.result:
            max_n = max(
                (int(s['id'].replace('audio','')) for s in self.songs
                 if re.match(r'audio\d+', s.get('id',''))),
                default=0)
            for i, s in enumerate(dlg.result):
                s['id'] = f'audio{max_n + i + 1}'
                self.songs.append(s)
            self._refresh()
            self.status.set(f'＋ {len(dlg.result)}曲を追加しました（未保存）')

    def _deploy(self):
        if not os.path.exists(DEPLOY_BAT):
            messagebox.showerror('エラー', 'deploy.batが見つかりません')
            return
        if messagebox.askyesno('Deploy', 'songs.jsを保存してサイトに反映しますか？'):
            try:
                write_songs(self.songs)
            except Exception as e:
                messagebox.showerror('保存エラー', str(e))
                return
            subprocess.Popen([DEPLOY_BAT], cwd=SCRIPT_DIR, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status.set('🚀 deploy.batを起動しました')


# ── 自動追加ダイアログ ────────────────────────────────
class AutoAddDialog:
    def __init__(self, parent, new_songs):
        self.result   = None
        self._songs   = [dict(s) for s in new_songs]   # 編集可能なコピー
        self._checks  = []
        self._parent  = parent

        self.win = tk.Toplevel(parent)
        self.win.title('フォルダから新曲を自動追加')
        self.win.geometry('680x560')
        self.win.configure(bg='#F7F8FC')
        self.win.resizable(True, True)
        self.win.grab_set()
        self.win.transient(parent)

        self._build()
        parent.wait_window(self.win)

    def _build(self):
        # ヘッダー
        hdr = tk.Frame(self.win, bg='#6B3FA0', height=46)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text=f'📂  {len(self._songs)}曲の新しいファイルが見つかりました',
                 bg='#6B3FA0', fg='white', font=F_BOLD).pack(side='left', padx=18, pady=12)

        # 説明
        tk.Label(self.win,
                 text='追加する曲にチェックを入れてください。「編集」で詳細を変更できます。',
                 bg='#F7F8FC', fg='#6B7080', font=F_SMALL).pack(padx=18, pady=(10,4), anchor='w')

        # スクロールエリア
        frame_outer = tk.Frame(self.win, bg='#F7F8FC')
        frame_outer.pack(fill='both', expand=True, padx=18, pady=(0,8))

        canvas = tk.Canvas(frame_outer, bg='#F7F8FC', highlightthickness=0)
        vsb = ttk.Scrollbar(frame_outer, orient='vertical', command=canvas.yview)
        self._list_frame = tk.Frame(canvas, bg='#F7F8FC')
        self._list_frame.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self._list_frame, anchor='nw')
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind_all('<MouseWheel>',
            lambda e: canvas.yview_scroll(-1*(e.delta//120), 'units'))
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        self._render_list()

        # フッターボタン
        foot = tk.Frame(self.win, bg='white',
                        highlightthickness=1, highlightbackground='#E4E7F0')
        foot.pack(fill='x', side='bottom')
        tk.Button(foot, text='キャンセル', command=self.win.destroy,
                  bg='#F7F8FC', fg='#6B7080', relief='flat',
                  font=F_NORMAL, padx=14, pady=8, cursor='hand2').pack(side='right', padx=(6,14), pady=8)
        tk.Button(foot, text='選択した曲を追加', command=self._confirm,
                  bg='#6B3FA0', fg='white', relief='flat',
                  font=F_BOLD, padx=18, pady=8, cursor='hand2').pack(side='right', pady=8)
        # 全選択 / 全解除
        tk.Button(foot, text='全選択', command=lambda: [v.set(True)  for v in self._checks],
                  bg='#F7F8FC', fg='#4A6CF7', relief='flat', font=F_SMALL,
                  padx=10, pady=8, cursor='hand2').pack(side='left', padx=(14,4), pady=8)
        tk.Button(foot, text='全解除', command=lambda: [v.set(False) for v in self._checks],
                  bg='#F7F8FC', fg='#6B7080', relief='flat', font=F_SMALL,
                  padx=10, pady=8, cursor='hand2').pack(side='left', pady=8)

    def _render_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._checks = []

        for i, song in enumerate(self._songs):
            bg = '#FFFFFF' if i % 2 == 0 else '#F4F6FF'
            row = tk.Frame(self._list_frame, bg=bg,
                           highlightthickness=1, highlightbackground='#E4E7F0')
            row.pack(fill='x', pady=(0,2))

            # チェックボックス
            var = tk.BooleanVar(value=True)
            self._checks.append(var)
            tk.Checkbutton(row, variable=var, bg=bg,
                           activebackground=bg, selectcolor='#EEF1FE').pack(side='left', padx=(10,0))

            # 情報エリア
            info = tk.Frame(row, bg=bg)
            info.pack(side='left', fill='x', expand=True, padx=8, pady=8)

            # タイトル行
            title_row = tk.Frame(info, bg=bg)
            title_row.pack(fill='x')
            tk.Label(title_row, text=song['title'], bg=bg,
                     font=F_BOLD, fg='#1A1C2A').pack(side='left')

            # ファイル状態バッジ
            badge_row = tk.Frame(info, bg=bg)
            badge_row.pack(fill='x', pady=(2,0))
            self._badge(badge_row, '🖼 画像あり' if song['jacket']  else '🖼 画像なし',
                        '#1A7A47' if song['jacket']  else '#999', bg)
            self._badge(badge_row, '🎵 音声あり' if song['audio']   else '🎵 音声なし',
                        '#1A7A47' if song['audio']   else '#999', bg)
            tag_count = len(song.get('tags') or [])
            self._badge(badge_row, f'🏷 タグ {tag_count}件',
                        '#4A6CF7' if tag_count else '#999', bg)

            # タグプレビュー
            if song.get('tags'):
                tk.Label(info, text='  '.join(song['tags'][:8]),
                         bg=bg, fg='#9B9EAB', font=F_SMALL).pack(anchor='w')

            # 編集ボタン
            tk.Button(row, text='編集', font=F_SMALL,
                      bg='#EEF1FE', fg='#4A6CF7', relief='flat',
                      padx=10, pady=4, cursor='hand2',
                      command=lambda idx=i: self._edit_song(idx)
                      ).pack(side='right', padx=12)

    def _badge(self, parent, text, color, bg):
        tk.Label(parent, text=text, bg=bg, fg=color,
                 font=(FONT_FAMILY, 9), padx=4).pack(side='left')

    def _edit_song(self, idx):
        dlg = SongDialog(self.win, '曲を編集', self._songs[idx])
        if dlg.result:
            dlg.result['id'] = self._songs[idx]['id']
            self._songs[idx] = dlg.result
            self._render_list()

    def _confirm(self):
        selected = [s for s, v in zip(self._songs, self._checks) if v.get()]
        if not selected:
            messagebox.showwarning('未選択', '1曲以上選択してください', parent=self.win)
            return
        self.result = selected
        self.win.destroy()


# ── 曲編集ダイアログ ──────────────────────────────────
class SongDialog:
    def __init__(self, parent, title, song):
        self.result = None
        self.song   = dict(song)

        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.geometry('520x820')
        self.win.configure(bg='#F7F8FC')
        self.win.resizable(False, True)
        self.win.grab_set()
        self.win.transient(parent)

        self._build()
        parent.wait_window(self.win)

    def _build(self):
        canvas = tk.Canvas(self.win, bg='#F7F8FC', highlightthickness=0)
        vsb    = ttk.Scrollbar(self.win, orient='vertical', command=canvas.yview)
        self.f = tk.Frame(canvas, bg='#F7F8FC')
        self.f.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0), window=self.f, anchor='nw', width=500)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(-1*(e.delta//120),'units'))
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        p = {'padx': 20, 'pady': (6,0), 'fill': 'x'}
        s = self.song

        # ── テキストファイル読み込みボタン ──
        tk.Button(
            self.f, text='📄  曲情報テキストファイルから説明文・タグを読み込む',
            command=self._load_from_txt,
            bg='#EEF1FE', fg='#4A6CF7', font=F_SMALL,
            relief='flat', padx=14, pady=7, cursor='hand2',
            activebackground='#D8DFFE',
        ).pack(padx=20, pady=(14,4), fill='x')

        tk.Frame(self.f, bg='#E4E7F0', height=1).pack(padx=20, fill='x', pady=(4,0))

        # タイトル・時間
        row = tk.Frame(self.f, bg='#F7F8FC')
        row.pack(**p)
        lf = tk.Frame(row, bg='#F7F8FC'); lf.pack(side='left', fill='x', expand=True, padx=(0,8))
        rf = tk.Frame(row, bg='#F7F8FC'); rf.pack(side='right', fill='x', expand=True)
        self._lbl(lf, '曲タイトル *')
        self.e_title = self._entry(lf, s.get('title',''))
        self._lbl(rf, '再生時間（例: 2:34）')
        self.e_dur = self._entry(rf, s.get('duration',''))

        # 種別
        self._lbl(self.f, '販売種別', pad=p)
        self.cb_type = ttk.Combobox(self.f, values=[v for _,v in TYPE_OPTIONS], state='readonly', width=24)
        self.cb_type.set(TYPE_LABEL.get(s.get('type',''), TYPE_OPTIONS[0][1]))
        self.cb_type.pack(padx=20, fill='x')

        # 説明
        self._lbl(self.f, '説明文', pad=p)
        self.e_desc = tk.Text(self.f, height=3, font=F_NORMAL, relief='solid', bd=1,
                              bg='white', padx=6, pady=4)
        self.e_desc.insert('1.0', s.get('description',''))
        self.e_desc.pack(padx=20, fill='x')

        # 価格・絵文字
        row3 = tk.Frame(self.f, bg='#F7F8FC')
        row3.pack(**p)
        lf3 = tk.Frame(row3, bg='#F7F8FC'); lf3.pack(side='left', fill='x', expand=True, padx=(0,8))
        rf3 = tk.Frame(row3, bg='#F7F8FC'); rf3.pack(side='right', fill='x', expand=True)
        self._lbl(lf3, '価格（円、無料は0）')
        self.e_price = self._entry(lf3, str(s.get('price', 500)))
        self._lbl(rf3, '絵文字（ジャケット用）')
        self.e_emoji = self._entry(rf3, s.get('jacketEmoji','🎵'))

        # ファイル名
        row4 = tk.Frame(self.f, bg='#F7F8FC')
        row4.pack(**p)
        lf4 = tk.Frame(row4, bg='#F7F8FC'); lf4.pack(side='left', fill='x', expand=True, padx=(0,8))
        rf4 = tk.Frame(row4, bg='#F7F8FC'); rf4.pack(side='right', fill='x', expand=True)
        self._lbl(lf4, '画像ファイル名（images/）')
        self.e_jacket = self._entry(lf4, s.get('jacket','').replace('images/',''))
        self._lbl(rf4, '音声ファイル名（audio/）')
        self.e_audio  = self._entry(rf4, s.get('audio','').replace('audio/',''))

        # YouTube URL
        self._lbl(self.f, 'YouTube URL（任意）', pad=p)
        self.e_youtube = self._entry(self.f, s.get('youtube',''))

        # グラデーション
        self._lbl(self.f, 'ジャケット背景グラデーション', pad=p)
        grad_frame = tk.Frame(self.f, bg='#F7F8FC')
        grad_frame.pack(padx=20, fill='x')
        self.e_grad = self._entry(self.f, s.get('jacketGradient', GRAD_PRESETS[0][1]))
        for label, val in GRAD_PRESETS:
            btn = tk.Button(grad_frame, text='　', bg='white', width=3, height=1,
                            relief='ridge', cursor='hand2',
                            command=lambda v=val: self.e_grad.delete(0,'end') or self.e_grad.insert(0,v))
            btn.pack(side='left', padx=2, pady=4)
            try:
                from re import findall
                colors = findall(r'#[0-9a-fA-F]{6}', val)
                if colors: btn.configure(bg=colors[0])
            except: pass

        # ── タグ ──
        tk.Frame(self.f, bg='#E4E7F0', height=1).pack(padx=20, fill='x', pady=(12,0))
        self._lbl(self.f, 'タグ', pad={**p, 'pady': (8,0)})

        self.tag_vars = {}
        existing_tags = s.get('tags') or []
        tag_outer = tk.Frame(self.f, bg='#F7F8FC')
        tag_outer.pack(padx=20, fill='x', pady=(4,0))

        for cat_name, cat_tags in TAG_CATEGORIES:
            tk.Label(tag_outer, text=cat_name, bg='#F7F8FC', fg='#9B9EAB',
                     font=(FONT_FAMILY, 9, 'bold'), anchor='w').pack(fill='x', pady=(8,3))
            grid = tk.Frame(tag_outer, bg='#F7F8FC')
            grid.pack(fill='x')
            for i, tag in enumerate(cat_tags):
                var = tk.BooleanVar(value=(tag in existing_tags))
                self.tag_vars[tag] = var
                cb = tk.Checkbutton(grid, text=tag, variable=var,
                                    bg='#F7F8FC', font=F_SMALL,
                                    activebackground='#F7F8FC', anchor='w',
                                    selectcolor='#EEF1FE')
                cb.grid(row=i // 5, column=i % 5, sticky='w', padx=1)

        # ボタン
        tk.Frame(self.f, bg='#E4E7F0', height=1).pack(padx=20, fill='x', pady=(14,0))
        btn_frame = tk.Frame(self.f, bg='#F7F8FC')
        btn_frame.pack(padx=20, pady=(10,16), fill='x')
        tk.Button(btn_frame, text='キャンセル', command=self.win.destroy,
                  bg='#F7F8FC', fg='#6B7080', relief='flat',
                  font=F_NORMAL, padx=14, pady=6, cursor='hand2').pack(side='right', padx=(6,0))
        tk.Button(btn_frame, text='保存', command=self._save,
                  bg='#4A6CF7', fg='white', relief='flat',
                  font=F_BOLD, padx=18, pady=6, cursor='hand2').pack(side='right')

    def _load_from_txt(self):
        """テキストファイルから説明文とタグを読み込む"""
        # 曲タイトルと同名のファイルを description フォルダから自動検索
        title = self.e_title.get().strip()
        auto_path = os.path.join(DESC_DIR, f'{title}.txt') if title else ''

        if auto_path and os.path.exists(auto_path):
            path = auto_path
        else:
            # 見つからない場合はファイル選択ダイアログを開く
            init_dir = DESC_DIR if os.path.isdir(DESC_DIR) else SCRIPT_DIR
            path = filedialog.askopenfilename(
                parent=self.win,
                title='曲情報テキストファイルを選択',
                initialdir=init_dir,
                defaultextension='.txt',
                filetypes=[('テキストファイル', '*.txt'), ('すべて', '*.*')],
            )
        if not path:
            return
        try:
            desc, tags = extract_from_txt(path)

            # 説明文を反映
            self.e_desc.delete('1.0', 'end')
            self.e_desc.insert('1.0', desc)

            # タグを反映
            for tag_name, var in self.tag_vars.items():
                var.set(tag_name in tags)

            tag_str = '、'.join(tags) if tags else 'なし'
            messagebox.showinfo(
                '読み込み完了',
                f'説明文とタグを読み込みました。\n\n検出されたタグ:\n{tag_str}',
                parent=self.win,
            )
        except Exception as e:
            messagebox.showerror('エラー', f'ファイルの読み込みに失敗しました:\n{e}', parent=self.win)

    def _lbl(self, parent, text, pad=None):
        kw = pad if pad else {'padx': 0, 'pady': (6,2), 'fill': 'x'}
        tk.Label(parent, text=text, bg='#F7F8FC', fg='#6B7080',
                 font=F_SMALL, anchor='w').pack(**kw)

    def _entry(self, parent, value=''):
        e = tk.Entry(parent, font=F_NORMAL, relief='solid', bd=1, bg='white')
        e.insert(0, value)
        e.pack(fill='x')
        return e

    def _save(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning('入力エラー', '曲タイトルを入力してください', parent=self.win)
            return
        type_label  = self.cb_type.get()
        type_key    = TYPE_MAP.get(type_label, 'regular')
        jacket_file = self.e_jacket.get().strip()
        audio_file  = self.e_audio.get().strip()
        self.result = {
            'id':             '',
            'title':          title,
            'type':           type_key,
            'description':    self.e_desc.get('1.0','end-1c').strip(),
            'price':          int(self.e_price.get() or 0),
            'duration':       self.e_dur.get().strip() or '--:--',
            'jacket':         f'images/{jacket_file}' if jacket_file else '',
            'jacketGradient': self.e_grad.get().strip(),
            'jacketEmoji':    self.e_emoji.get().strip() or '🎵',
            'audio':          f'audio/{audio_file}' if audio_file else '',
            'youtube':        self.e_youtube.get().strip(),
            'licenses':       self.song.get('licenses', []),
            'tags':           [tag for tag, var in self.tag_vars.items() if var.get()],
        }
        self.win.destroy()


# ── 起動 ──────────────────────────────────────────────
if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
