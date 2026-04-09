# -*- coding: utf-8 -*-
"""
ふみはBGM 曲管理ツール
songs.jsを直接読み書きするデスクトップGUIツール
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os, re, subprocess

# フォント設定（日本語ゴシック）
FONT_FAMILY = 'Yu Gothic UI'
F_NORMAL = (FONT_FAMILY, 11)
F_BOLD   = (FONT_FAMILY, 11, 'bold')
F_SMALL  = (FONT_FAMILY, 10)
F_LARGE  = (FONT_FAMILY, 13, 'bold')
F_TITLE  = (FONT_FAMILY, 14, 'bold')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_JS   = os.path.join(SCRIPT_DIR, 'songs.js')
DEPLOY_BAT = os.path.join(SCRIPT_DIR, 'deploy.bat')

TYPE_OPTIONS = [
    ('regular',       '通常販売'),
    ('one-of-a-kind', '一品物（限定1点）'),
    ('free',          'フリー（無料）'),
]
LICENSE_OPTIONS = [
    '配信OK', '収益化OK', 'ループ', 'YouTube収益化OK',
    '商用可', 'SNS投稿OK', 'ゲーム内使用OK', 'アプリOK', '社内動画OK', '広告OK',
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


# ── songs.js 読み書き ──────────────────────────────────
def parse_songs():
    with open(SONGS_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    # コメントアウトされたブロックを除去
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
        if s.get('id', '').startswith('audio'):
            songs.append(s)
    return songs


def write_songs(songs):
    entries = []
    for s in songs:
        lic  = ', '.join(f"'{l}'" for l in (s.get('licenses') or []))
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

    # ── スタイル ──
    def _setup_style(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('Treeview', rowheight=38, font=F_NORMAL, background='#fff',
                    fieldbackground='#fff', borderwidth=0)
        s.configure('Treeview.Heading', font=F_BOLD,
                    background='#EEF1FE', foreground='#4A6CF7', relief='flat')
        s.map('Treeview', background=[('selected','#4A6CF7')],
              foreground=[('selected','white')])
        # 縞模様タグ（_refreshで適用）
        self._stripe_odd  = '#F4F6FF'
        self._stripe_even = '#FFFFFF'
        s.configure('TCombobox', font=F_NORMAL)
        s.configure('TCheckbutton', font=F_NORMAL)

    # ── UI構築 ──
    def _build_ui(self):
        # ヘッダー
        hdr = tk.Frame(self.root, bg='#4A6CF7', height=52)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text='ふみはBGM  曲管理ツール', bg='#4A6CF7', fg='white',
                 font=F_TITLE).pack(side='left', padx=22, pady=13)

        # ツールバー
        tb = tk.Frame(self.root, bg='white', pady=8, padx=16,
                      relief='flat', bd=0,
                      highlightthickness=1, highlightbackground='#E4E7F0')
        tb.pack(fill='x')
        self._btn(tb, '＋ 追加',           self._add,    '#4A6CF7', 'white').pack(side='left', padx=(0,6))
        self._btn(tb, '✏  編集',           self._edit,   '#F7F8FC', '#1A1C2A').pack(side='left', padx=(0,6))
        self._btn(tb, '🗑  削除',          self._delete, '#FEF2F2', '#D94545').pack(side='left', padx=(0,18))
        self._btn(tb, '💾  songs.js に保存', self._save,  '#1A7A47', 'white').pack(side='left', padx=(0,6))
        self._btn(tb, '🚀  Deploy',         self._deploy, '#C25F00', 'white').pack(side='left')

        # 曲リスト
        pane = tk.Frame(self.root, bg='#F7F8FC')
        pane.pack(fill='both', expand=True, padx=16, pady=12)

        cols = ('no','title','type','price','duration')
        heads = ('No.','タイトル','販売種別','価格','時間')
        widths = (40, 300, 160, 80, 70)

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

        # ステータスバー
        self.status = tk.StringVar(value='読み込み中...')
        tk.Label(self.root, textvariable=self.status, bg='#E4E7F0', fg='#6B7080',
                 font=F_SMALL, anchor='w', padx=14, pady=4).pack(fill='x', side='bottom')

    def _btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         font=F_SMALL, relief='flat',
                         padx=14, pady=5, cursor='hand2', activebackground=bg)

    # ── データ操作 ──
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
        TYPE_JP = {'regular':'通常', 'one-of-a-kind':'一品物', 'free':'フリー'}
        for i, s in enumerate(self.songs):
            price = '無料' if s.get('price',0)==0 else f"¥{s.get('price',0):,}"
            tag = 'odd' if i % 2 == 0 else 'even'
            self.tree.insert('', 'end', iid=i, tags=(tag,), values=(
                i+1, s.get('title','（無題）'),
                TYPE_JP.get(s.get('type',''), s.get('type','')),
                price, s.get('duration',''),
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
            subprocess.Popen(f'start cmd /k "{DEPLOY_BAT}"', shell=True, cwd=SCRIPT_DIR)
            self.status.set('🚀 deploy.batを起動しました')


# ── 曲編集ダイアログ ──────────────────────────────────
class SongDialog:
    def __init__(self, parent, title, song):
        self.result = None
        self.song   = dict(song)

        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.geometry('500x660')
        self.win.configure(bg='#F7F8FC')
        self.win.resizable(False, True)
        self.win.grab_set()
        self.win.transient(parent)

        self._build()
        parent.wait_window(self.win)

    def _build(self):
        # スクロール可能なフレーム
        canvas = tk.Canvas(self.win, bg='#F7F8FC', highlightthickness=0)
        vsb    = ttk.Scrollbar(self.win, orient='vertical', command=canvas.yview)
        self.f = tk.Frame(canvas, bg='#F7F8FC')
        self.f.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0), window=self.f, anchor='nw', width=480)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(-1*(e.delta//120),'units'))
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        p = {'padx': 20, 'pady': (6,0), 'fill': 'x'}
        s = self.song

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
        self._lbl(self.f, 'YouTube URL（任意 — あればジャケット部分に埋め込み表示）', pad=p)
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
            # グラデーションは描けないので代替色を設定
            try:
                from re import findall
                colors = findall(r'#[0-9a-fA-F]{6}', val)
                if colors: btn.configure(bg=colors[0])
            except: pass

        # ライセンス
        self._lbl(self.f, 'ライセンス表示', pad=p)
        lic_frame = tk.Frame(self.f, bg='#F7F8FC')
        lic_frame.pack(padx=20, fill='x')
        self.lic_vars = {}
        for i, opt in enumerate(LICENSE_OPTIONS):
            var = tk.BooleanVar(value=opt in s.get('licenses',[]))
            self.lic_vars[opt] = var
            r, c = i // 2, i % 2
            ttk.Checkbutton(lic_frame, text=opt, variable=var,
                            style='TCheckbutton').grid(row=r, column=c, sticky='w', padx=4, pady=3)

        # ボタン
        btn_frame = tk.Frame(self.f, bg='#F7F8FC')
        btn_frame.pack(padx=20, pady=(20,16), fill='x')
        tk.Button(btn_frame, text='キャンセル', command=self.win.destroy,
                  bg='#F7F8FC', fg='#6B7080', relief='flat',
                  font=F_NORMAL, padx=14, pady=6, cursor='hand2').pack(side='right', padx=(6,0))
        tk.Button(btn_frame, text='保存', command=self._save,
                  bg='#4A6CF7', fg='white', relief='flat',
                  font=F_BOLD, padx=18, pady=6, cursor='hand2').pack(side='right')

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
            'licenses':       [o for o, v in self.lic_vars.items() if v.get()],
        }
        self.win.destroy()


# ── 起動 ──────────────────────────────────────────────
if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
