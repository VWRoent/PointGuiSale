import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
from PIL import Image, ImageTk
import os
import csv
import calendar
from datetime import datetime, timedelta

"""
############################################################
# プログラム名: PointGuiSale
# バージョン: 2.0.0
# 制作日: 2026年1月18日
# 制作者: VWRoent（紫波レント）
# 使用技術: ChatGPT
# GitHub : https://github.com/VWRoent/PointGuiSale
# YouTube: https://www.youtube.com/@trans-cyp4365
# Twitter: https://x.com/VioWaveRoentgen
############################################################
"""


class ProductCounterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PointGuiSale")

        # 保存先を PGS_info 配下に統一
        self._init_storage()

        # 初期設定：商品数、資格数、およびデータの読み込み
        self.load_product_count()
        self.load_column_counts()
        self.load_products_from_csv()
        self.load_product_catalog()
        self.load_qualification_count()
        self.load_qualifications_from_csv()
        self.load_question_responses()
        self.load_image_scale()
        self.load_survey_count()
        self.load_ui_theme()
        self.load_window_settings()
        self.load_business_day_cutoff()

        self.product_counts = [0] * self.product_count
        self.product_images = [None] * self.product_count  # 画像を格納するリスト

        # 空画像(プレースホルダ)のキャッシュ
        self._blank_photos = {}

        # 顧客（ID管理）
        self.load_customers()

        # UIテーマ
        self.setup_style()
        self._try_set_window_icon()

        # ウィンドウサイズ（商品数が少なくてもタブが見えなくならないよう最小サイズを設定）
        self.update_window_size()

        self.setup_tabs()
        self.load_survey_from_csv()
        self.update_total_price()

        # 起動時は必ずレジタブを表示
        try:
            self._select_tab_by_text('レジ')
        except Exception:
            pass

        self.root.resizable(True, True)

    def _init_storage(self):
        """PGS_info/images, PGS_info/setting, PGS_info/log を用意し、旧配置があれば移行する。"""
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.info_dir = os.path.join(self.app_dir, 'PGS_info')
        self.images_dir = os.path.join(self.info_dir, 'images')
        self.setting_dir = os.path.join(self.info_dir, 'setting')
        self.log_dir = os.path.join(self.info_dir, 'log')

        for d in (self.info_dir, self.images_dir, self.setting_dir, self.log_dir):
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                pass

        self._migrate_legacy_storage()

    def _p_setting(self, filename: str) -> str:
        return os.path.join(self.setting_dir, filename)

    def _p_log(self, filename: str) -> str:
        return os.path.join(self.log_dir, filename)

    def _p_image(self, filename: str) -> str:
        return os.path.join(self.images_dir, filename)

    def _migrate_legacy_storage(self):
        """旧: 実行ファイルと同階層に保存していた設定/ログ/画像を、PGS_info配下へコピー移行。"""
        try:
            import shutil
        except Exception:
            shutil = None

        setting_files = [
            'ui_theme.txt', 'image_scale.txt',
            'product_count.csv', 'survey_count.csv', 'qualification_count.csv',
            'column_counts.csv',
            'products.csv', 'qualifications.csv', 'question_responses.csv',
            'shop_name.txt', 'persistent_text.txt',
            'product_catalog.csv',
            'window_settings.csv',
            'customers.csv',
        ]
        log_files = [
            'log.csv', 'survey_log.csv', 'management_log.csv',
            'qualification_log.csv', 'customer_notes.csv'
        ]

        def copy_if_needed(src_path: str, dst_path: str):
            if not src_path or not dst_path:
                return
            if not os.path.exists(src_path) or os.path.exists(dst_path):
                return
            if shutil is None:
                return
            try:
                shutil.copy2(src_path, dst_path)
            except Exception:
                pass

        # Setting files
        for fn in setting_files:
            src = os.path.join(self.app_dir, fn)
            dst = self._p_setting(fn)
            copy_if_needed(src, dst)

        # Log files
        for fn in log_files:
            src = os.path.join(self.app_dir, fn)
            dst = self._p_log(fn)
            copy_if_needed(src, dst)

        # images/ フォルダ
        old_images = os.path.join(self.app_dir, 'images')
        if os.path.isdir(old_images) and shutil is not None:
            try:
                for name in os.listdir(old_images):
                    src = os.path.join(old_images, name)
                    dst = self._p_image(name)
                    if os.path.isfile(src) and not os.path.exists(dst):
                        shutil.copy2(src, dst)
            except Exception:
                pass

    def setup_style(self):
        # なるべく色が効くテーマへ
        style = ttk.Style(self.root)
        for theme in ("clam", "alt", "default"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                continue

        # Color palette (themes)
        # 明るい4テーマ + Dark 1テーマ（管理タブで切り替えできます）
        self.UI_THEMES = {
            "Light Slate": {
                "bg": "#f1f5f9", "panel": "#ffffff", "panel2": "#e2e8f0",
                "text": "#0f172a", "muted": "#475569", "accent": "#2563eb",
                "danger": "#dc2626", "select": "#cbd5e1", "entry": "#ffffff",
            },
            "Light Mint": {
                "bg": "#f0fdf4", "panel": "#ffffff", "panel2": "#dcfce7",
                "text": "#052e16", "muted": "#166534", "accent": "#16a34a",
                "danger": "#dc2626", "select": "#bbf7d0", "entry": "#ffffff",
            },
            "Light Sand": {
                "bg": "#fffbeb", "panel": "#ffffff", "panel2": "#fef3c7",
                "text": "#1f2937", "muted": "#6b7280", "accent": "#d97706",
                "danger": "#dc2626", "select": "#fde68a", "entry": "#ffffff",
            },
            "Light Sakura": {
                "bg": "#fff1f2", "panel": "#ffffff", "panel2": "#ffe4e6",
                "text": "#3f0d12", "muted": "#7f1d1d", "accent": "#e11d48",
                "danger": "#b91c1c", "select": "#fecdd3", "entry": "#ffffff",
            },
            "Dark Emerald": {
                "bg": "#0b1220", "panel": "#0f172a", "panel2": "#111827",
                "text": "#e5e7eb", "muted": "#94a3b8", "accent": "#22c55e",
                "danger": "#ef4444", "select": "#334155", "entry": "#0b1220",
            },
        }
        self.UI_THEME_NAMES = list(self.UI_THEMES.keys())
        theme_name = getattr(self, "ui_theme_name", "Light Slate")
        if theme_name not in self.UI_THEMES:
            theme_name = "Light Slate"
            self.ui_theme_name = theme_name
            self.save_ui_theme()

        p = self.UI_THEMES[theme_name]
        self.UI_BG = p["bg"]
        self.UI_PANEL = p["panel"]
        self.UI_PANEL_2 = p["panel2"]
        self.UI_TEXT = p["text"]
        self.UI_MUTED = p["muted"]
        self.UI_ACCENT = p["accent"]
        self.UI_DANGER = p["danger"]
        self.UI_SELECT = p["select"]
        self.UI_ENTRY = p["entry"]

        # Root background (tk widgetsが残っても違和感を減らす)
        self.root.configure(bg=self.UI_BG)

        # Fonts
        self.FONT_BASE = ("Segoe UI", 13)
        self.FONT_BOLD = ("Segoe UI", 13, "bold")
        self.FONT_TITLE = ("Segoe UI", 18, "bold")
        self.FONT_BIG = ("Segoe UI", 28, "bold")
        self.FONT_IMG_BTN = ("Segoe UI", 10)

        # Register font（全タブを約1.5倍にしたため、レジは同等サイズで統一）
        reg_size = int(self.FONT_BASE[1])
        self.FONT_REG = (self.FONT_BASE[0], reg_size)
        self.FONT_REG_BOLD = (self.FONT_BASE[0], reg_size, "bold")

        # Product line font (商品名/金額は小さめ)
        prod_size = max(8, int(reg_size * 0.55))
        self.FONT_REG_PRODUCT = (self.FONT_BASE[0], prod_size)

        style.configure(".", font=self.FONT_BASE, background=self.UI_BG, foreground=self.UI_TEXT)

        # Frames / Labelframes
        style.configure("TFrame", background=self.UI_BG)
        style.configure("TLabelframe", background=self.UI_BG, foreground=self.UI_TEXT)
        style.configure("TLabelframe.Label", background=self.UI_BG, foreground=self.UI_TEXT, font=self.FONT_BOLD)

        # Notebook
        style.configure("TNotebook", background=self.UI_BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(10, 6), background=self.UI_PANEL_2, foreground=self.UI_TEXT)
        style.map(
            "TNotebook.Tab",
            background=[('selected', self.UI_PANEL)],
            foreground=[('selected', (self.UI_TEXT if getattr(self, 'ui_theme_name', '').startswith('Light') else '#ffffff'))],
        )

        # Labels
        style.configure("TLabel", background=self.UI_BG, foreground=self.UI_TEXT)
        style.configure("Muted.TLabel", foreground=self.UI_MUTED)
        style.configure("Footer.TLabel", font=(self.FONT_BASE[0], 9), background=self.UI_BG, foreground=self.UI_MUTED)
        style.configure("Title.TLabel", font=self.FONT_TITLE)
        style.configure(
            "Final.TLabel",
            font=self.FONT_BIG,
            background=self.UI_PANEL,
            foreground=(self.UI_TEXT if getattr(self, 'ui_theme_name', '').startswith('Light') else '#ffffff'),
            padding=(10, 6),
            anchor='center',
        )
        style.configure(
            "Chip.TLabel",
            background=self.UI_PANEL_2,
            foreground=self.UI_TEXT,
            padding=(10, 6),
        )

        # Buttons
        style.configure("TButton", padding=(8, 4), background=self.UI_PANEL_2, foreground=self.UI_TEXT)
        style.map(
            "TButton",
            background=[("active", "#1f2937"), ("pressed", "#0f172a"), ("disabled", self.UI_PANEL_2)],
            foreground=[("disabled", self.UI_MUTED)],
        )
        style.configure("Accent.TButton", background=self.UI_ACCENT, foreground="#ffffff")
        style.map(
            "Accent.TButton",
            background=[("active", "#16a34a"), ("pressed", "#15803d")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )
        style.configure("Danger.TButton", background=self.UI_DANGER, foreground="#ffffff")
        style.map(
            "Danger.TButton",
            background=[("active", "#dc2626"), ("pressed", "#b91c1c")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )
        style.configure("Small.TButton", padding=(6, 2))
        style.configure("Img.TButton", font=self.FONT_IMG_BTN, padding=(6, 2))

        # Entries / Combobox
        style.configure("TEntry", fieldbackground=self.UI_ENTRY, foreground=self.UI_TEXT)
        style.configure("TCombobox", padding=(6, 4))

        # Treeview
        style.configure(
            "Treeview",
            background=self.UI_ENTRY,
            fieldbackground=self.UI_ENTRY,
            foreground=self.UI_TEXT,
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=self.UI_PANEL_2,
            foreground=self.UI_TEXT,
            font=self.FONT_BOLD,
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[('selected', self.UI_SELECT)],
            foreground=[('selected', (self.UI_TEXT if getattr(self, 'ui_theme_name', '').startswith('Light') else '#ffffff'))],
        )

        # ---- Register-only styles (レジだけ文字を大きく) ----
        style.configure("Reg.TLabel", font=self.FONT_REG, background=self.UI_BG, foreground=self.UI_TEXT)
        style.configure("Reg.Muted.TLabel", font=self.FONT_REG, background=self.UI_BG, foreground=self.UI_MUTED)
        style.configure("Reg.ProductName.TLabel", font=self.FONT_REG_PRODUCT, background=self.UI_BG, foreground=self.UI_TEXT)
        style.configure("Reg.ProductPrice.TLabel", font=self.FONT_REG_PRODUCT, background=self.UI_BG, foreground=self.UI_MUTED)
        style.configure("Reg.TButton", font=self.FONT_REG, padding=(8, 3))
        style.configure("Reg.Small.TButton", font=self.FONT_REG, padding=(6, 2))
        style.configure("Reg.Chip.TLabel", font=self.FONT_REG, background=self.UI_PANEL_2, foreground=self.UI_TEXT, padding=(10, 6))
        style.configure("Reg.TEntry", font=self.FONT_REG)
        style.configure("Reg.TCombobox", font=self.FONT_REG)
        style.configure("Reg.TCheckbutton", font=self.FONT_REG, background=self.UI_BG, foreground=self.UI_TEXT)

        style.configure("Reg.Accent.TButton", font=self.FONT_REG_BOLD, background=self.UI_ACCENT, foreground="#ffffff", padding=(8, 3))
        style.map(
            "Reg.Accent.TButton",
            background=[("active", "#16a34a"), ("pressed", "#15803d")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )
        style.configure("Reg.Danger.TButton", font=self.FONT_REG_BOLD, background=self.UI_DANGER, foreground="#ffffff", padding=(8, 3))
        style.map(
            "Reg.Danger.TButton",
            background=[("active", "#dc2626"), ("pressed", "#b91c1c")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )

    def _try_set_window_icon(self):
        """同階層の icon.png / icon.ico があれば適用（任意）。"""
        # iconphotoはPNGが確実。ICOはWindowsだと効くが環境差あり。
        for p in ("icon.png", "app_icon.png"):
            if os.path.exists(p):
                try:
                    img = Image.open(p)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    # 参照保持
                    self._window_icon_ref = photo
                    return
                except Exception:
                    pass
        # iconbitmap (ico) も試す
        if os.path.exists("icon.ico"):
            try:
                self.root.iconbitmap("icon.ico")
            except Exception:
                pass

    # ----------------------------
    # Data load/save (元のロジックを維持)
    # ----------------------------
    def load_image_scale(self):
        """画像倍率設定の読み込み（x1は廃止。x2=小 / x3=大）"""
        try:
            with open(self._p_setting("image_scale.txt"), "r", encoding="utf-8") as f:
                val = int(f.read().strip())
        except FileNotFoundError:
            val = 3
        except Exception:
            val = 3

        if val <= 1:
            val = 2
        if val not in (2, 3):
            val = 3

        self.image_scale = val
        self.save_image_scale()

    def save_image_scale(self):
        """画像倍率設定の保存"""
        with open(self._p_setting("image_scale.txt"), "w", encoding="utf-8") as f:
            f.write(str(self.image_scale))

    def load_ui_theme(self):
        """UI配色テーマ名の読み込み"""
        try:
            with open(self._p_setting("ui_theme.txt"), "r", encoding="utf-8") as f:
                name = f.read().strip()
                self.ui_theme_name = name if name else "Light Slate"
        except FileNotFoundError:
            self.ui_theme_name = "Light Slate"
            self.save_ui_theme()
        except Exception:
            self.ui_theme_name = "Light Slate"
            self.save_ui_theme()

    def save_ui_theme(self):
        """UI配色テーマ名の保存"""
        with open(self._p_setting("ui_theme.txt"), "w", encoding="utf-8") as f:
            f.write(str(getattr(self, "ui_theme_name", "Light Slate")))

    def apply_ui_theme(self, theme_name: str):
        """管理タブから呼ぶ：テーマを保存→適用→UI再構築"""
        if not theme_name:
            return
        if hasattr(self, "UI_THEMES") and theme_name not in self.UI_THEMES:
            # 不正値は無視
            return
        self.ui_theme_name = theme_name
        self.save_ui_theme()
        self.setup_style()
        self.refresh_ui(keep_tab=True)

    def load_product_count(self):
        try:
            with open(self._p_setting("product_count.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.product_count = int(next(reader)[0])
        except FileNotFoundError:
            self.product_count = 6  # 初期値
            self.save_product_count_to_csv()
        except Exception:
            self.product_count = 6
            self.save_product_count_to_csv()

    def load_survey_count(self):
        try:
            with open(self._p_setting("survey_count.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.survey_count = int(next(reader)[0])
        except FileNotFoundError:
            self.survey_count = 3  # 初期値
            self.save_survey_count_to_csv()
        except Exception:
            self.survey_count = 3
            self.save_survey_count_to_csv()

    def save_product_count_to_csv(self):
        with open(self._p_setting("product_count.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.product_count])

    def save_survey_count_to_csv(self):
        with open(self._p_setting("survey_count.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.survey_count])

    def load_qualification_count(self):
        try:
            with open(self._p_setting("qualification_count.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.qualification_count = int(next(reader)[0])
        except FileNotFoundError:
            self.qualification_count = 3  # 初期値
            self.save_qualification_count_to_csv()
        except Exception:
            self.qualification_count = 3
            self.save_qualification_count_to_csv()

    def save_qualification_count_to_csv(self):
        with open(self._p_setting("qualification_count.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.qualification_count])

    def load_question_responses(self):
        try:
            with open(self._p_setting("question_responses.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.survey_responses = [row[0] for row in reader]
        except FileNotFoundError:
            self.survey_responses = ["未回答", "回答1", "回答2"]  # 初期値
            self.save_question_responses_to_csv()
        except Exception:
            self.survey_responses = ["未回答", "回答1", "回答2"]
            self.save_question_responses_to_csv()

    def save_question_responses_to_csv(self):
        with open(self._p_setting("question_responses.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for response in self.survey_responses:
                writer.writerow([response])


    # ----------------------------
    # Column split / Customers
    # ----------------------------
    def load_column_counts(self):
        try:
            with open(self._p_setting("column_counts.csv"), "r", newline="", encoding="utf-8") as f:
                row = next(csv.reader(f))
                self.left_column_count = int(row[0])
                self.right_column_count = int(row[1])
        except FileNotFoundError:
            n = int(getattr(self, 'product_count', 6))
            if n == 6:
                self.left_column_count = 4
                self.right_column_count = 2
            else:
                self.left_column_count = min(4, max(0, (n + 1) // 2))
                self.right_column_count = max(0, n - self.left_column_count)
            self.save_column_counts()
        except Exception:
            n = int(getattr(self, 'product_count', 6))
            if n == 6:
                self.left_column_count = 4
                self.right_column_count = 2
            else:
                self.left_column_count = min(4, max(0, (n + 1) // 2))
                self.right_column_count = max(0, n - self.left_column_count)
            self.save_column_counts()

        self._normalize_column_counts(default_reset=False)

    def save_column_counts(self):
        with open(self._p_setting("column_counts.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([int(getattr(self, 'left_column_count', 0)), int(getattr(self, 'right_column_count', 0))])

    def _normalize_column_counts(self, default_reset: bool):
        n = int(self.product_count)
        left = int(getattr(self, 'left_column_count', (n + 1)//2))
        right = int(getattr(self, 'right_column_count', n - left))

        if left < 0: left = 0
        if right < 0: right = 0

        if left + right != n:
            if default_reset:
                left = (n + 1) // 2
                right = n - left
            else:
                # 右を自動調整（合計が一致するように）
                left = max(0, min(left, n))
                right = n - left

        self.left_column_count = left
        self.right_column_count = right

    def update_column_counts(self):
        left_s = self.left_col_entry.get().strip() if hasattr(self, 'left_col_entry') else ''
        right_s = self.right_col_entry.get().strip() if hasattr(self, 'right_col_entry') else ''

        if not left_s.isdigit() or not right_s.isdigit():
            messagebox.showwarning("警告", "左/右には0以上の整数を入力してください。")
            return

        left = int(left_s)
        right = int(right_s)
        if left + right < 1:
            messagebox.showwarning("警告", "商品数は1以上にしてください。")
            return

        # 反映
        self.left_column_count = left
        self.right_column_count = right
        new_count = left + right

        count_changed = (new_count != self.product_count)
        self.product_count = new_count
        self.save_product_count_to_csv()
        self.save_column_counts()

        # 商品定義/画像リスト
        if count_changed:
            self.load_products_from_csv()
            self.load_product_catalog()
            self.product_counts = [0] * self.product_count
            self.product_images = [None] * self.product_count

        self.update_window_size()
        self.refresh_ui(keep_tab=True)
        self._reorder_tabs()
        messagebox.showinfo('成功', '商品数/カラムを更新しました。')

    def _summarize_counts(self, counts):
        """履歴表示用のサマリ。
        returns: (total_qty, breakdown_str, top_item_str)
        breakdown_str: "ID_個数; ID_個数; ..."（個数降順）
        """
        try:
            counts_i = [int(x) for x in counts]
        except Exception:
            counts_i = [0] * self.product_count

        total_qty = sum(counts_i)
        if total_qty <= 0:
            return 0, "-", "-"

        # breakdown
        pairs = []
        for i, v in enumerate(counts_i):
            if v <= 0:
                continue
            pid = "-"
            try:
                pid = str(self.products[i].get("id", ""))
            except Exception:
                pid = ""
            if not pid:
                pid = f"p{i+1:02d}"[-3:]
            pairs.append((v, pid))
        pairs.sort(key=lambda x: x[0], reverse=True)
        breakdown = "; ".join([f"{pid}_{v}" for v, pid in pairs]) if pairs else "-"

        # top
        max_idx = max(range(len(counts_i)), key=lambda i: counts_i[i])
        max_val = counts_i[max_idx]
        top_name = self.products[max_idx].get("name", "-") if 0 <= max_idx < len(self.products) else "-"
        top_item = f"{top_name}({max_val})"

        return total_qty, breakdown, top_item

    def _get_customer_names(self):
        """レジ用: 名前リスト（履歴の最近順 + 登録顧客）"""
        names_recent = []
        seen = set()
        try:
            with open(self._p_log('log.csv'), 'r', newline='', encoding='utf-8') as f:
                rows = [r for r in csv.reader(f) if r]
            for row in reversed(rows):
                # old: date,time,name,...
                # new: date,time,cid,name,...
                if len(row) >= 4 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                    nm = row[3].strip()
                elif len(row) >= 3:
                    nm = row[2].strip()
                else:
                    nm = ''
                if nm and nm not in seen:
                    names_recent.append(nm)
                    seen.add(nm)
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # customers.csv の追加（作成順）
        for c in getattr(self, 'customers', []):
            nm = (c.get('name') or '').strip()
            if nm and nm not in seen:
                names_recent.append(nm)
                seen.add(nm)

        return names_recent

    def _refresh_customer_name_values(self, extra_name: str | None = None):
        names = self._get_customer_names()
        if extra_name:
            if extra_name not in names:
                names = [extra_name] + names

        if hasattr(self, 'name_combo'):
            try:
                self.name_combo['values'] = names
            except Exception:
                pass

        # 顧客タブ: 001 Name の表示
        if hasattr(self, 'customer_combo'):
            try:
                disp = [f"{c['id']}: {c['name']}" for c in getattr(self, 'customers', [])]
                self.customer_combo['values'] = disp
            except Exception:
                pass

    
    # ---- Customer ID/Name sync (Register) ----
    def _sync_customer_id_from_name(self, event=None):
        # 名前が既存ならIDを反映（存在しない場合は何もしない）
        try:
            name = (self.name_var.get() or '').strip()
        except Exception:
            name = ''
        if not name:
            return
        cid = getattr(self, 'customer_id_by_name', {}).get(name)
        if cid:
            try:
                if hasattr(self, 'customer_id_var'):
                    self.customer_id_var.set(cid)
            except Exception:
                pass

    def _sync_customer_name_from_id(self, event=None):
        # IDが既存なら名前を反映（存在しない場合は何もしない）
        try:
            cid_in = (self.customer_id_var.get() if hasattr(self, 'customer_id_var') else '') or ''
            cid_in = cid_in.strip()
        except Exception:
            cid_in = ''
        if not cid_in:
            return

        cid_try = cid_in
        if cid_try.isdigit() and len(cid_try) < 3:
            cid_try = cid_try.zfill(3)

        name = getattr(self, 'customer_name_by_id', {}).get(cid_try)
        if name:
            try:
                self.name_var.set(name)
            except Exception:
                pass
            try:
                if hasattr(self, 'customer_id_var'):
                    self.customer_id_var.set(cid_try)
            except Exception:
                pass

    def load_window_settings(self):
        """ウィンドウサイズ計算パラメータ（設定タブから変更可）"""
        # defaults
        self.win_width = 780
        self.win_min_width = 780
        # x2 = 小, x3 = 大
        self.win_base_small = 270
        self.win_row_small = 70   # 22 + 18*2 (tuned)
        self.win_min_rows_small = 7

        self.win_base_large = 270
        self.win_row_large = 70   # 22 + 18*3
        self.win_min_rows_large = 7

        path = self._p_setting('window_settings.csv')
        if not os.path.exists(path):
            self.save_window_settings()
            return

        kv = {}
        try:
            with open(path, 'r', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) >= 2:
                        kv[row[0].strip()] = row[1].strip()
        except Exception:
            return

        def gi(key, default):
            v = kv.get(key, '')
            try:
                i = int(v)
                return i
            except Exception:
                return default

        self.win_width = gi('win_width', self.win_width)
        self.win_min_width = gi('win_min_width', self.win_min_width)
        self.win_base_small = gi('win_base_small', self.win_base_small)
        self.win_row_small = gi('win_row_small', self.win_row_small)
        self.win_min_rows_small = gi('win_min_rows_small', self.win_min_rows_small)
        self.win_base_large = gi('win_base_large', self.win_base_large)
        self.win_row_large = gi('win_row_large', self.win_row_large)
        self.win_min_rows_large = gi('win_min_rows_large', self.win_min_rows_large)

        # Normalize legacy defaults (v14): if untouched, bump to new defaults
        try:
            if (gi('win_row_small', 0) == 68 and gi('win_row_large', 0) == 76 and
                gi('win_min_rows_small', 0) == 9 and gi('win_min_rows_large', 0) == 7):
                self.win_row_small = 70
                self.win_row_large = 70
                self.win_min_rows_small = 7
                self.win_min_rows_large = 7
                self.save_window_settings()
        except Exception:
            pass


    def save_window_settings(self):
        path = self._p_setting('window_settings.csv')
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['win_width', str(int(getattr(self, 'win_width', 780)))])
                w.writerow(['win_min_width', str(int(getattr(self, 'win_min_width', 780)))])
                w.writerow(['win_base_small', str(int(getattr(self, 'win_base_small', 270)))])
                w.writerow(['win_row_small', str(int(getattr(self, 'win_row_small', 70)))])
                w.writerow(['win_min_rows_small', str(int(getattr(self, 'win_min_rows_small', 7)))])
                w.writerow(['win_base_large', str(int(getattr(self, 'win_base_large', 270)))])
                w.writerow(['win_row_large', str(int(getattr(self, 'win_row_large', 70)))])
                w.writerow(['win_min_rows_large', str(int(getattr(self, 'win_min_rows_large', 7)))])
        except Exception:
            pass


    # ----------------------------
    # Business day cutoff (for daily sales)
    # ----------------------------
    def load_business_day_cutoff(self):
        # HH:MM; before this time is counted as previous business day
        self.business_day_cutoff = getattr(self, 'business_day_cutoff', '01:00')
        try:
            with open(self._p_setting('business_day_cutoff.txt'), 'r', encoding='utf-8') as f:
                s = (f.read() or '').strip()
            if self._is_valid_hhmm(s):
                self.business_day_cutoff = s
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def save_business_day_cutoff(self):
        try:
            with open(self._p_setting('business_day_cutoff.txt'), 'w', encoding='utf-8') as f:
                f.write((getattr(self, 'business_day_cutoff', '01:00') or '01:00').strip())
        except Exception:
            pass

    def _is_valid_hhmm(self, s: str) -> bool:
        try:
            hh, mm = s.split(':')
            if not (hh.isdigit() and mm.isdigit()):
                return False
            h = int(hh)
            m = int(mm)
            return 0 <= h <= 23 and 0 <= m <= 59
        except Exception:
            return False

    def _cutoff_hm(self):
        s = (getattr(self, 'business_day_cutoff', '01:00') or '01:00').strip()
        if not self._is_valid_hhmm(s):
            s = '01:00'
        hh, mm = s.split(':')
        return int(hh), int(mm)

    def business_date_for_dt(self, dt: datetime) -> datetime:
        # Returns a datetime at 00:00 of the business date.
        h, m = self._cutoff_hm()
        cutoff = dt.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt < cutoff:
            dt = dt - timedelta(days=1)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _today_business_mmdd(self) -> str:
        bd = self.business_date_for_dt(datetime.now())
        return bd.strftime('%m-%d')

    def update_today_sales_label(self):
        if not hasattr(self, 'today_sales_label'):
            return
        target = self._today_business_mmdd()
        total = 0
        now = datetime.now()
        path = self._p_log('log.csv')
        try:
            with open(path, 'r', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) < 5:
                        continue
                    date_s = (row[0] or '').strip()
                    time_s = (row[1] or '').strip()
                    # total index: new format -> 5, old -> 4
                    if len(row) >= 6 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                        total_i = 5
                    else:
                        total_i = 4
                    try:
                        mm, dd = date_s.split('-')
                        hh, mi = time_s.split(':')[:2]
                        dt = datetime(now.year, int(mm), int(dd), int(hh), int(mi))
                    except Exception:
                        continue
                    bd = self.business_date_for_dt(dt).strftime('%m-%d')
                    if bd != target:
                        continue
                    try:
                        total += int(row[total_i])
                    except Exception:
                        pass
        except FileNotFoundError:
            total = 0
        except Exception:
            pass
        try:
            self.today_sales_label.configure(text=f"本日売上: {total}円")
        except Exception:
            pass


    def _window_params_for_scale(self, scale: int):
        if scale == 3:
            return (self.win_base_large, self.win_row_large, self.win_min_rows_large)
        return (self.win_base_small, self.win_row_small, self.win_min_rows_small)


    # ----------------------------
    # Customers (ID: 001,002,...) 
    # ----------------------------
    def load_customers(self):
        """setting/customers.csv を読み込み。なければ log.csv から作成。"""
        self.customers = []  # [{'id':'001','name':'...','created':'...'}]
        self.customer_id_by_name = {}
        self.customer_name_by_id = {}

        path = self._p_setting('customers.csv')
        if os.path.exists(path):
            try:
                with open(path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cid = (row.get('id') or '').strip()
                        name = (row.get('name') or '').strip()
                        created = (row.get('created') or '').strip()
                        if not cid or not cid.isdigit():
                            continue
                        cid = f"{int(cid):03d}"
                        if not name:
                            continue
                        self.customers.append({'id': cid, 'name': name, 'nickname': (row.get('nickname') or '').strip(), 'job': (row.get('job') or '').strip(), 'created': created})
            except Exception:
                self.customers = []

        # 補完（log.csv から、古い順に初出で割り当て）
        seen = {c['name'] for c in self.customers}
        max_id = 0
        for c in self.customers:
            try:
                max_id = max(max_id, int(c['id']))
            except Exception:
                pass

        def add_name(nm: str):
            nonlocal max_id
            if not nm or nm in seen:
                return
            max_id += 1
            cid = f"{max_id:03d}"
            self.customers.append({'id': cid, 'name': nm, 'nickname': '', 'job': '', 'created': datetime.now().strftime('%Y-%m-%d')})
            seen.add(nm)

        try:
            with open(self._p_log('log.csv'), 'r', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if not row:
                        continue
                    # old: date,time,name,...  new: date,time,cid,name,...
                    if len(row) >= 4 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                        nm = row[3].strip()
                    elif len(row) >= 3:
                        nm = row[2].strip()
                    else:
                        nm = ''
                    add_name(nm)
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # マップ生成
        self.customer_id_by_name = {c['name']: c['id'] for c in self.customers}
        self.customer_name_by_id = {c['id']: c['name'] for c in self.customers}

        if not os.path.exists(path):
            self.save_customers()
        else:
            # 既存でも、補完が入ったなら保存
            try:
                with open(path, 'r', newline='', encoding='utf-8') as f:
                    pass
            except Exception:
                pass
            self.save_customers()

    def save_customers(self):
        path = self._p_setting('customers.csv')
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'name', 'nickname', 'job', 'created'])
                writer.writeheader()
                for c in self.customers:
                    writer.writerow({'id': c.get('id', ''), 'name': c.get('name', ''), 'nickname': c.get('nickname', ''), 'job': c.get('job', ''), 'created': c.get('created', '')})
        except Exception:
            pass

    def ensure_customer_id(self, name: str) -> str:
        nm = (name or '').strip()
        if not nm:
            return ''
        cid = self.customer_id_by_name.get(nm)
        if cid:
            return cid
        # 新規
        max_id = 0
        for c in self.customers:
            try:
                max_id = max(max_id, int(c['id']))
            except Exception:
                pass
        cid = f"{max_id+1:03d}"
        self.customers.append({'id': cid, 'name': nm, 'nickname': '', 'job': '', 'created': datetime.now().strftime('%Y-%m-%d')})
        self.customer_id_by_name[nm] = cid
        self.customer_name_by_id[cid] = nm
        self.save_customers()
        return cid

    def _customer_display(self, cid: str, name: str) -> str:
        cid = (cid or '').strip()
        name = (name or '').strip()
        if cid and cid.isdigit():
            return f"{int(cid):03d} {name}".strip()
        return name

    def _parse_customer_display(self, s: str):
        s = (s or '').strip()
        if len(s) >= 4 and s[:3].isdigit() and s[3] == ' ':
            return s[:3], s[4:].strip()
        if len(s) >= 3 and s[:3].isdigit() and (len(s) == 3 or s[3] == ':'):
            # '001: name'
            cid = s[:3]
            nm = s[4:].strip() if len(s) > 4 else ''
            return cid, nm
        return '', s


    def _get_customer_record(self, cid: str):
        cid = (cid or '').strip()
        if not cid:
            return None
        for c in getattr(self, 'customers', []):
            if (c.get('id') or '').strip() == cid:
                return c
        return None

    def copy_customer_nickname(self):
        """レジ: 愛称コピー（愛称がなければ名前）"""
        cid = ''
        try:
            cid = (self.customer_id_var.get() if hasattr(self, 'customer_id_var') else '').strip()
        except Exception:
            cid = ''
        if not cid:
            try:
                nm = (self.name_var.get() if hasattr(self, 'name_var') else '').strip()
                cid = getattr(self, 'customer_id_by_name', {}).get(nm, '')
            except Exception:
                cid = ''
        if not cid or cid not in getattr(self, 'customer_name_by_id', {}):
            return
        rec = self._get_customer_record(cid)
        nick = ''
        if rec:
            nick = (rec.get('nickname') or '').strip()
        if not nick:
            nick = (self.customer_name_by_id.get(cid) or '').strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(nick)
        self.root.update()

    def apply_customer_profile(self):
        """顧客タブ: 愛称/お仕事/名前変更を反映"""
        disp = (self.customer_var.get() or '').strip() if hasattr(self, 'customer_var') else ''
        cid, _ = self._parse_customer_display(disp)
        if not cid and disp[:3].isdigit():
            cid = disp[:3]
        cid = (cid or '').strip()
        if not cid:
            messagebox.showwarning('警告', '顧客を選んでください。')
            return
        rec = self._get_customer_record(cid)
        if not rec:
            messagebox.showwarning('警告', '顧客が見つかりません。')
            return

        nick = (self.customer_nickname_entry.get() or '').strip() if hasattr(self, 'customer_nickname_entry') else ''
        job = (self.customer_job_entry.get() or '').strip() if hasattr(self, 'customer_job_entry') else ''
        new_name = (self.customer_rename_entry.get() or '').strip() if hasattr(self, 'customer_rename_entry') else ''

        # update nickname/job
        rec['nickname'] = nick
        rec['job'] = job

        # rename (optional)
        if new_name and new_name != rec.get('name', ''):
            old_name = rec.get('name', '')
            rec['name'] = new_name
            # rebuild maps safely
            try:
                if old_name in self.customer_id_by_name and self.customer_id_by_name.get(old_name) == cid:
                    del self.customer_id_by_name[old_name]
            except Exception:
                pass
            self.customer_id_by_name[new_name] = cid
            self.customer_name_by_id[cid] = new_name

        self.save_customers()

        # refresh combos
        self._refresh_customer_name_values()
        try:
            self.customer_combo['values'] = [f"{c['id']}: {c['name']}" for c in getattr(self, 'customers', [])]
            # keep selection
            self.customer_var.set(f"{cid}: {self.customer_name_by_id.get(cid, '')}")
        except Exception:
            pass

        # clear rename box
        try:
            if hasattr(self, 'customer_rename_entry'):
                self.customer_rename_entry.delete(0, tk.END)
        except Exception:
            pass

        self.refresh_customer_view()
        messagebox.showinfo('成功', '顧客情報を更新しました。')


    # ----------------------------
    # Row deletion helpers
    # ----------------------------
    def _confirm_delete(self, label: str) -> bool:
        return messagebox.askyesno('確認', f"{label}の選択行を本当に削除しますか？")

    def delete_selected_log_row(self):
        if not hasattr(self, 'log_tree'):
            return
        sel = self.log_tree.selection()
        if not sel:
            messagebox.showwarning('警告', '削除する行を選択してください。')
            return
        if not self._confirm_delete('履歴'):
            return

        # 解析済み標準行リストから削除し、ファイルを書き直す
        try:
            idx = int(sel[0])
        except Exception:
            # fallback: iidから探す
            idx = None
            for i, iid in enumerate(self.log_tree.get_children()):
                if iid == sel[0]:
                    idx = i
                    break
        if idx is None:
            return

        if not hasattr(self, '_log_rows'):
            self.load_log_from_csv()
        rows = list(getattr(self, '_log_rows', []))
        if idx < 0 or idx >= len(rows):
            return
        rows.pop(idx)
        self._write_log_rows(rows)
        self.load_log_from_csv()
        self._refresh_customer_name_values()

    def delete_selected_survey_row(self):
        if not hasattr(self, 'survey_tree'):
            return
        sel = self.survey_tree.selection()
        if not sel:
            messagebox.showwarning('警告', '削除する行を選択してください。')
            return
        if not self._confirm_delete('アンケート'):
            return
        try:
            idx = int(sel[0])
        except Exception:
            idx = None
            for i, iid in enumerate(self.survey_tree.get_children()):
                if iid == sel[0]:
                    idx = i
                    break
        if idx is None:
            return

        if not hasattr(self, '_survey_rows'):
            self.load_survey_from_csv()
        rows = list(getattr(self, '_survey_rows', []))
        if idx < 0 or idx >= len(rows):
            return
        rows.pop(idx)
        self._write_survey_rows(rows)
        self.load_survey_from_csv()

    def delete_selected_customer_note_row(self):
        if not hasattr(self, 'customer_note_tree'):
            return
        sel = self.customer_note_tree.selection()
        if not sel:
            messagebox.showwarning('警告', '削除する行を選択してください。')
            return
        if not self._confirm_delete('顧客メモ'):
            return

        # 選択顧客
        cid, _ = self._parse_customer_display(getattr(self, 'customer_var', tk.StringVar()).get())
        if not cid:
            return

        try:
            idx = int(sel[0])
        except Exception:
            idx = None
            for i, iid in enumerate(self.customer_note_tree.get_children()):
                if iid == sel[0]:
                    idx = i
                    break
        if idx is None:
            return

        # customer_notes.csv から該当行を1件削除
        path = self._p_log('customer_notes.csv')
        all_rows = []
        try:
            with open(path, 'r', newline='', encoding='utf-8') as f:
                all_rows = [r for r in csv.reader(f) if r]
        except FileNotFoundError:
            return
        except Exception:
            return

        # その顧客の行だけ抽出（新しい順表示だが、ファイルは古い順）
        matches = []
        for file_i, r in enumerate(all_rows):
            # old: date,time,name,note
            # new: date,time,cid,name,note
            if len(r) >= 5 and r[2].strip() == cid:
                matches.append(file_i)
            elif len(r) == 4:
                # 旧形式は name で紐付け（cidが無い）
                name = self.customer_name_by_id.get(cid, '')
                if name and r[2].strip() == name:
                    matches.append(file_i)

        # 表示は新しい順なので、idx番目は matches の末尾から
        if idx < 0 or idx >= len(matches):
            return
        file_index = matches[-1 - idx]
        try:
            all_rows.pop(file_index)
        except Exception:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                for r in all_rows:
                    w.writerow(r)
        except Exception:
            return

        self.load_customer_notes(cid)
        self.refresh_customer_images(cid)


    # ----------------------------
    # Image size toggle
    # ----------------------------
    def toggle_image_size(self):
        self.image_scale = 3 if int(getattr(self, 'image_scale', 2)) == 2 else 2
        self.save_image_scale()
        self.update_window_size()
        self.refresh_ui(keep_tab=True)


    # ----------------------------
    # Settings tab
    # ----------------------------
    def setup_settings_tab(self):
        if hasattr(self, 'settings_frame'):
            self.settings_frame.destroy()

        self.settings_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.settings_frame, text='設定')

        self._add_created_by_footer(self.settings_frame)

        box = ttk.Labelframe(self.settings_frame, text='画面サイズ設定', padding=10)
        box.pack(fill=tk.X)

        sales_box = ttk.Labelframe(self.settings_frame, text='売上設定', padding=10)
        sales_box.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(sales_box, text='営業日更新(HH:MM)').grid(row=0, column=0, sticky='w')
        self.ent_business_cutoff = ttk.Entry(sales_box, width=8)
        self.ent_business_cutoff.grid(row=0, column=1, sticky='w', padx=(6, 0))
        self.ent_business_cutoff.insert(0, str(getattr(self, 'business_day_cutoff', '01:00')))
        ttk.Button(sales_box, text='反映', command=self.apply_sales_settings).grid(row=0, column=2, sticky='w', padx=(8, 0))

        # Grid
        for c in range(6):
            box.columnconfigure(c, weight=0)
        box.columnconfigure(1, weight=1)
        box.columnconfigure(3, weight=1)

        def add_row(r, label, key, col0=0, col1=1):
            ttk.Label(box, text=label).grid(row=r, column=col0, sticky='w', pady=2)
            ent = ttk.Entry(box, width=10)
            ent.grid(row=r, column=col1, sticky='w', padx=(6, 18), pady=2)
            ent.insert(0, str(int(getattr(self, key))))
            return ent

        self.ent_win_width = add_row(0, '幅', 'win_width')
        self.ent_win_min_width = add_row(0, '最小幅', 'win_min_width', col0=2, col1=3)

        ttk.Separator(box, orient='horizontal').grid(row=1, column=0, columnspan=6, sticky='ew', pady=8)

        ttk.Label(box, text='小画像').grid(row=2, column=0, sticky='w')
        self.ent_base_small = add_row(3, 'ベース高さ', 'win_base_small')
        self.ent_row_small = add_row(3, '1行高さ', 'win_row_small', col0=2, col1=3)
        self.ent_minrows_small = add_row(4, '最小行数', 'win_min_rows_small')

        ttk.Separator(box, orient='horizontal').grid(row=5, column=0, columnspan=6, sticky='ew', pady=8)

        ttk.Label(box, text='大画像').grid(row=6, column=0, sticky='w')
        self.ent_base_large = add_row(7, 'ベース高さ', 'win_base_large')
        self.ent_row_large = add_row(7, '1行高さ', 'win_row_large', col0=2, col1=3)
        self.ent_minrows_large = add_row(8, '最小行数', 'win_min_rows_large')

        btns = ttk.Frame(self.settings_frame)
        btns.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btns, text='反映', style='Accent.TButton', command=self.apply_window_settings).pack(side=tk.LEFT)

    def apply_window_settings(self):
        def to_int(ent, label, minv=0, maxv=10000):
            s = ent.get().strip()
            if not s.isdigit():
                messagebox.showwarning('警告', f'{label}は整数で入力してください。')
                raise ValueError
            v = int(s)
            if v < minv or v > maxv:
                messagebox.showwarning('警告', f'{label}の範囲が不正です。')
                raise ValueError
            return v

        try:
            self.win_width = to_int(self.ent_win_width, '幅', 500, 4000)
            self.win_min_width = to_int(self.ent_win_min_width, '最小幅', 500, 4000)
            self.win_base_small = to_int(self.ent_base_small, '小:ベース高さ', 100, 4000)
            self.win_row_small = to_int(self.ent_row_small, '小:1行高さ', 10, 400)
            self.win_min_rows_small = to_int(self.ent_minrows_small, '小:最小行数', 1, 50)
            self.win_base_large = to_int(self.ent_base_large, '大:ベース高さ', 100, 4000)
            self.win_row_large = to_int(self.ent_row_large, '大:1行高さ', 10, 500)
            self.win_min_rows_large = to_int(self.ent_minrows_large, '大:最小行数', 1, 50)
        except ValueError:
            return

        self.save_window_settings()
        self.update_window_size()
        self.refresh_ui(keep_tab=True)
        messagebox.showinfo('成功', '画面サイズ設定を反映しました。')
    def apply_sales_settings(self):
        # Apply and persist business day cutoff time (HH:MM)
        if not hasattr(self, 'ent_business_cutoff'):
            return
        s = (self.ent_business_cutoff.get() or '').strip()
        if not self._is_valid_hhmm(s):
            messagebox.showwarning('警告', '営業日更新は HH:MM 形式で入力してください。例: 01:00')
            try:
                self.ent_business_cutoff.delete(0, tk.END)
                self.ent_business_cutoff.insert(0, str(getattr(self, 'business_day_cutoff', '01:00')))
            except Exception:
                pass
            return
        self.business_day_cutoff = s
        self.save_business_day_cutoff()
        self.update_today_sales_label()
        messagebox.showinfo('成功', '売上設定を反映しました。')


    def setup_customer_tab(self):
        if hasattr(self, 'customer_frame'):
            self.customer_frame.destroy()

        self.customer_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.customer_frame, text='顧客')

        self._add_created_by_footer(self.customer_frame)

        top = ttk.Frame(self.customer_frame)
        top.pack(fill=tk.X, pady=(0, 2))
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text='顧客').grid(row=0, column=0, sticky='w')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(top, textvariable=self.customer_var, state='readonly')
        self.customer_combo['values'] = [f"{c['id']}: {c['name']}" for c in getattr(self, 'customers', [])]
        self.customer_combo.grid(row=0, column=1, sticky='ew', padx=(6, 0))
        self.customer_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_customer_view())

        self.customer_summary = ttk.Label(self.customer_frame, text='')
        self.customer_summary.pack(fill=tk.X, pady=(2, 4))

        # プロフィール（愛称/お仕事/名前変更）
        prof = ttk.Frame(self.customer_frame)
        prof.pack(fill=tk.X, pady=(0, 4))
        prof_left = ttk.Frame(prof)
        prof_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        prof_left.columnconfigure(1, weight=1)
        prof_left.columnconfigure(3, weight=1)
        prof_left.columnconfigure(5, weight=1)

        ttk.Label(prof_left, text='愛称').grid(row=0, column=0, sticky='w')
        self.customer_nickname_entry = ttk.Entry(prof_left, width=16)
        self.customer_nickname_entry.grid(row=0, column=1, sticky='ew', padx=(6, 12))

        ttk.Label(prof_left, text='お仕事').grid(row=0, column=2, sticky='w')
        self.customer_job_entry = ttk.Entry(prof_left, width=16)
        self.customer_job_entry.grid(row=0, column=3, sticky='ew', padx=(6, 12))

        ttk.Label(prof_left, text='名前変更').grid(row=0, column=4, sticky='w')
        self.customer_rename_entry = ttk.Entry(prof_left, width=16)
        self.customer_rename_entry.grid(row=0, column=5, sticky='ew', padx=(6, 0))

        ttk.Button(prof, text='変更', style='Accent.TButton', command=self.apply_customer_profile).pack(side=tk.RIGHT)

        # 購入履歴(集計) + 顧客画像（左:履歴 2/3, 右:画像 1/3）
        buy_box = ttk.Labelframe(self.customer_frame, text='購入履歴(集計)', padding=6)
        buy_box.pack(fill=tk.X, expand=False, pady=(0, 6))

        main = ttk.Frame(buy_box)
        main.pack(fill=tk.X)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky='ne')

        cols = ['product', 'qty', 'ratio']
        self.customer_tree = self._make_treeview(left, cols, height=3)
        self.customer_tree.heading('product', text='商品')
        self.customer_tree.heading('qty', text='個数')
        self.customer_tree.heading('ratio', text='比率')
        self.customer_tree.column('product', width=280, minwidth=140)
        self.customer_tree.column('qty', width=80, minwidth=60, anchor='e')
        self.customer_tree.column('ratio', width=70, minwidth=60, anchor='e')

        # 右側: 顧客画像
        self.customer_image_var = tk.StringVar()
        self.customer_image_label = ttk.Label(right)
        self.customer_image_label.pack(anchor='center', pady=(0, 2))

        img_ctrl = ttk.Frame(right)
        img_ctrl.pack(fill=tk.X)
        ttk.Button(img_ctrl, text='画像追加', command=self.add_customer_image).pack(side=tk.LEFT)
        self.customer_image_combo = ttk.Combobox(img_ctrl, textvariable=self.customer_image_var, state='readonly', width=18)
        self.customer_image_combo.pack(side=tk.LEFT, padx=(6, 0), fill=tk.X, expand=True)
        self.customer_image_combo.bind('<<ComboboxSelected>>', lambda e: self._load_selected_customer_image())

        # メモ（メモ履歴も同じ枠）

        # メモ（メモ履歴も同じ枠）
        memo_box = ttk.Labelframe(self.customer_frame, text='メモ', padding=6)
        memo_box.pack(fill=tk.BOTH, expand=True)

        self.customer_note_text = tk.Text(memo_box, height=4)
        self.customer_note_text.pack(fill=tk.X)

        btn_row = ttk.Frame(memo_box)
        btn_row.pack(fill=tk.X, pady=(6, 4))
        ttk.Button(btn_row, text='記録', style='Accent.TButton', command=self.add_customer_note).pack(side=tk.LEFT)
        ttk.Button(btn_row, text='削除', command=self.delete_selected_customer_note_row).pack(side=tk.LEFT, padx=(6, 0))

        note_cols = ['date', 'time', 'note']
        self.customer_note_tree = self._make_treeview(memo_box, note_cols, height=3)
        self.customer_note_tree.heading('date', text='日付')
        self.customer_note_tree.heading('time', text='時刻')
        self.customer_note_tree.heading('note', text='内容')
        self.customer_note_tree.column('date', width=78, minwidth=60, anchor='center')
        self.customer_note_tree.column('time', width=78, minwidth=60, anchor='center')
        self.customer_note_tree.column('note', width=520, minwidth=240)

        self.refresh_customer_view()

    def refresh_customer_view(self):
        disp = self.customer_var.get().strip()
        cid = ''
        name = ''
        if disp:
            if len(disp) >= 4 and disp[:3].isdigit():
                cid = disp[:3]
                name = disp[4:].strip() if len(disp) > 4 else ''
                if name.startswith(':'):
                    name = name[1:].strip()
            else:
                cid, name = self._parse_customer_display(disp)

        # clear trees
        for t in ('customer_tree', 'customer_note_tree'):
            if hasattr(self, t):
                tree = getattr(self, t)
                for item in tree.get_children():
                    tree.delete(item)

        if not cid:
            if hasattr(self, 'customer_summary'):
                self.customer_summary.configure(text='')
            return

        # プロフィール欄を表示更新
        try:
            rec = self._get_customer_record(cid)
            if hasattr(self, 'customer_nickname_entry'):
                self.customer_nickname_entry.delete(0, tk.END)
                self.customer_nickname_entry.insert(0, (rec.get('nickname', '') if rec else ''))
            if hasattr(self, 'customer_job_entry'):
                self.customer_job_entry.delete(0, tk.END)
                self.customer_job_entry.insert(0, (rec.get('job', '') if rec else ''))
            if hasattr(self, 'customer_rename_entry'):
                # do not auto-fill rename
                self.customer_rename_entry.delete(0, tk.END)
        except Exception:
            pass

        # 集計
        counts_sum = [0] * self.product_count
        total_amount = 0
        tx = 0
        last_visit = ''
        try:
            with open(self._p_log('log.csv'), 'r', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) < 5:
                        continue
                    # old: date,time,name,qual,total,...
                    # new: date,time,cid,name,qual,total,...
                    if len(row) >= 6 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                        if row[2].strip() != cid:
                            continue
                        nm = row[3].strip()
                        qual_i = 4
                        total_i = 5
                        counts_start = 6
                    else:
                        # 旧形式は名前でひも付け
                        nm = row[2].strip() if len(row) >= 3 else ''
                        if nm != self.customer_name_by_id.get(cid, ''):
                            continue
                        qual_i = 3
                        total_i = 4
                        counts_start = 5

                    tx += 1
                    try:
                        last_visit = row[0].strip()
                    except Exception:
                        pass
                    try:
                        total_amount += int(row[total_i])
                    except Exception:
                        pass
                    for i in range(self.product_count):
                        try:
                            counts_sum[i] += int(row[counts_start + i])
                        except Exception:
                            pass
        except FileNotFoundError:
            pass

        total_qty = sum(counts_sum)
        items = []
        for i, q in enumerate(counts_sum):
            if q > 0:
                try:
                    price = int(self.products[i]['price'])
                except Exception:
                    price = 0
                pid = self.products[i].get('id', '')
                pname = self.products[i].get('name', '-')
                items.append((pid, pname, q, q * price))
        items.sort(key=lambda x: x[2], reverse=True)

        if hasattr(self, 'customer_summary'):
            nm_show = self.customer_name_by_id.get(cid, name)
            lv = last_visit if last_visit else '-'
            self.customer_summary.configure(text=f"ID: {cid} / {nm_show}  | 回数: {tx} / 前回来店: {lv}")

        if hasattr(self, 'customer_tree'):
            for pid, pname, q, y in items:
                ratio = f"{(q / total_qty * 100):.0f}%" if total_qty > 0 else '0%'
                self.customer_tree.insert('', 'end', values=[f"{pid} {pname}", q, ratio])

        self.load_customer_notes(cid)
        self.refresh_customer_images(cid)

    def add_customer_note(self):
        disp = self.customer_var.get().strip()
        cid = ''
        if disp and len(disp) >= 3 and disp[:3].isdigit():
            cid = disp[:3]
        note = self.customer_note_text.get('1.0', 'end').strip()
        if not cid:
            messagebox.showwarning('警告', '顧客を選んでください。')
            return
        if not note:
            messagebox.showwarning('警告', 'メモが空です。')
            return

        name = self.customer_name_by_id.get(cid, '')

        current_time = datetime.now()
        date_str = current_time.strftime('%m-%d')
        time_str = current_time.strftime('%H:%M')

        with open(self._p_log('customer_notes.csv'), 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # new format
            writer.writerow([date_str, time_str, cid, name, note])

        self.customer_note_text.delete('1.0', 'end')
        self.load_customer_notes(cid)
        self.refresh_customer_images(cid)

    def load_customer_notes(self, cid: str):
        if not hasattr(self, 'customer_note_tree'):
            return
        for item in self.customer_note_tree.get_children():
            self.customer_note_tree.delete(item)

        cid = (cid or '').strip()
        if not cid:
            return

        rows = []
        try:
            with open(self._p_log('customer_notes.csv'), 'r', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if not row:
                        continue
                    # new: date,time,cid,name,note
                    if len(row) >= 5 and row[2].strip() == cid:
                        rows.append(row)
                    # old: date,time,name,note
                    elif len(row) == 4:
                        nm = self.customer_name_by_id.get(cid, '')
                        if nm and row[2].strip() == nm:
                            rows.append([row[0], row[1], cid, nm, row[3]])
        except FileNotFoundError:
            pass

        # 新しい順に表示（iidは0..）
        rows_rev = list(reversed(rows))
        for i, row in enumerate(rows_rev):
            self.customer_note_tree.insert('', 'end', iid=str(i), values=[row[0], row[1], row[-1]])

    # ----------------------------
    # Customer images
    # ----------------------------
    def _customer_image_prefix(self, cid: str) -> str:
        cid = (cid or '').strip()
        if cid.isdigit() and len(cid) < 3:
            cid = cid.zfill(3)
        return f"{cid}_" if cid else ''

    def _list_customer_image_files(self, cid: str):
        prefix = self._customer_image_prefix(cid)
        if not prefix:
            return []
        try:
            files = []
            for fn in os.listdir(self.images_dir):
                if not fn.startswith(prefix):
                    continue
                if fn.startswith('image_'):
                    continue
                path = self._p_image(fn)
                if os.path.isfile(path):
                    files.append(fn)
            files.sort()
            return files
        except Exception:
            return []

    def refresh_customer_images(self, cid: str):
        if not hasattr(self, 'customer_image_combo'):
            return
        files = self._list_customer_image_files(cid)
        bases = [os.path.splitext(f)[0] for f in files]
        try:
            self.customer_image_combo['values'] = bases
        except Exception:
            pass
        if bases:
            try:
                self.customer_image_var.set(bases[-1])
            except Exception:
                pass
            self._load_selected_customer_image()
        else:
            try:
                self.customer_image_var.set('')
            except Exception:
                pass
            self._set_customer_image_preview(None)

    def _set_customer_image_preview(self, photo):
        try:
            self._customer_photo = photo  # keep ref
            if hasattr(self, 'customer_image_label'):
                if photo is None:
                    self.customer_image_label.configure(image='', text='')
                else:
                    self.customer_image_label.configure(image=photo, text='')
        except Exception:
            pass

    def _load_selected_customer_image(self):
        disp = (self.customer_var.get() if hasattr(self, 'customer_var') else '').strip()
        cid = ''
        if disp and len(disp) >= 3 and disp[:3].isdigit():
            cid = disp[:3]
        base = (self.customer_image_var.get() if hasattr(self, 'customer_image_var') else '').strip()
        if not cid or not base:
            self._set_customer_image_preview(None)
            return

        # Find by any extension
        for ext in ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'):
            fn = base + ext
            path = self._p_image(fn)
            if os.path.exists(path):
                self._load_customer_image_preview(path)
                return

        # Fallback search
        for fn in self._list_customer_image_files(cid):
            if os.path.splitext(fn)[0] == base:
                self._load_customer_image_preview(self._p_image(fn))
                return

        self._set_customer_image_preview(None)

    def _load_customer_image_preview(self, path: str):
        try:
            img = Image.open(path)
            max_w, max_h = 220, 140
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._set_customer_image_preview(photo)
        except Exception:
            self._set_customer_image_preview(None)

    def add_customer_image(self):
        disp = (self.customer_var.get() if hasattr(self, 'customer_var') else '').strip()
        cid = ''
        if disp and len(disp) >= 3 and disp[:3].isdigit():
            cid = disp[:3]
        if not cid:
            messagebox.showwarning('警告', '顧客を選んでください。')
            return

        path = filedialog.askopenfilename(title='画像を選択', filetypes=[
            ('Image files', '*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif'),
            ('All files', '*.*')
        ])
        if not path:
            return

        ext = os.path.splitext(path)[1] or ''
        ext = ext.lower()
        if not ext:
            ext = '.png'

        now = datetime.now()
        # YYDD: year(2) + day(2)
        yydd = now.strftime('%y') + now.strftime('%d')
        prefix = f"{cid}_{yydd}_"

        seq = 0
        for fn in self._list_customer_image_files(cid):
            if not fn.startswith(prefix):
                continue
            base = os.path.splitext(fn)[0]
            parts = base.split('_')
            if len(parts) >= 3:
                try:
                    seq = max(seq, int(parts[-1]) + 1)
                except Exception:
                    pass
        seq = min(seq, 99)

        dst_name = f"{cid}_{yydd}_{seq:02d}{ext}"
        dst_path = self._p_image(dst_name)

        try:
            import shutil
            shutil.copy2(path, dst_path)
        except Exception as e:
            messagebox.showerror('エラー', f'画像の保存に失敗しました: {e}')
            return

        # refresh list and select new
        self.refresh_customer_images(cid)
        try:
            self.customer_image_var.set(os.path.splitext(dst_name)[0])
        except Exception:
            pass
        self._load_selected_customer_image()



    # --- Tab selection helpers (prevent unexpected tab jumps) ---
    def _get_selected_tab_text(self):
        try:
            if not hasattr(self, 'notebook'):
                return None
            sel = self.notebook.select()
            return self.notebook.tab(sel, 'text')
        except Exception:
            return None

    def _select_tab_by_text(self, tab_text: str | None):
        if not tab_text:
            return
        if not hasattr(self, 'notebook'):
            return
        try:
            end = self.notebook.index('end')
        except Exception:
            return
        try:
            for i in range(end):
                if self.notebook.tab(i, 'text') == tab_text:
                    self.notebook.select(i)
                    break
        except Exception:
            pass

    def _reorder_tabs(self):
        """情報更新でタブが末尾に移動しないよう、順番を固定する。"""
        if not hasattr(self, 'notebook'):
            return

        current_tab_text = self._get_selected_tab_text()

        # 左から: レジ, 管理, 顧客, 履歴, 備考, 質問, 資格, 設定
        order = [
            (getattr(self, 'register_frame', None), 'レジ'),
            (getattr(self, 'management_frame', None), '管理'),
            (getattr(self, 'customer_frame', None), '顧客'),
            (getattr(self, 'log_frame', None), '履歴'),
            (getattr(self, 'survey_frame', None), '備考'),
            (getattr(self, 'question_frame', None), '質問'),
            (getattr(self, 'qualification_frame', None), '資格'),
            (getattr(self, 'settings_frame', None), '設定'),
        ]
        for idx, (frame, title) in enumerate(order):
            if frame is None:
                continue
            try:
                self.notebook.insert(idx, frame)
                self.notebook.tab(frame, text=title)
            except Exception:
                pass

        # Re-select previously active tab (by text) to avoid jumps
        self._select_tab_by_text(current_tab_text)
    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # NOTE: registerは最後に作る（shop_name_entry/persistent_text_entryが先に生成される想定を維持）
        self.setup_log_tab()
        self.setup_survey_tab()
        self.setup_customer_tab()
        self.setup_question_tab()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_settings_tab()
        self.setup_register_tab()
        self._reorder_tabs()

    def refresh_ui(self, keep_tab: bool = True):
        """スタイル変更などでUI全体を再構築する（カウント等の状態はメモリ値を優先）"""
        current_tab_text = None
        try:
            if keep_tab and hasattr(self, "notebook"):
                sel = self.notebook.select()
                current_tab_text = self.notebook.tab(sel, "text")
        except Exception:
            current_tab_text = None

        try:
            if hasattr(self, "notebook"):
                self.notebook.destroy()
        except Exception:
            pass

        self.update_window_size()
        self.setup_tabs()

        # 同名タブを再選択（順番が変わっても維持）
        if keep_tab and current_tab_text and hasattr(self, "notebook"):
            try:
                for i in range(self.notebook.index('end')):
                    if self.notebook.tab(i, 'text') == current_tab_text:
                        self.notebook.select(i)
                        break
            except Exception:
                pass

        # 最終表示更新
        self.load_survey_from_csv()
        self.update_total_price()

    # -------- Register --------

    def _add_created_by_footer(self, parent):
        """全タブ最下部に小さくクレジットを表示（placeなのでgrid/packと共存可）"""
        try:
            old = getattr(parent, '_created_by_footer', None)
            if old is not None and old.winfo_exists():
                old.destroy()
        except Exception:
            pass
        lbl = ttk.Label(parent, text='created by 紫波レント', style='Footer.TLabel')
        # 右下に小さく表示
        lbl.place(relx=1.0, rely=1.0, anchor='se', x=-6, y=-4)
        parent._created_by_footer = lbl

    def _ellipsize(self, s: str, max_chars: int) -> str:
        """表示用：長い文字列を…で切り詰める"""
        if s is None:
            return ""
        t = str(s)
        if max_chars <= 0:
            return ""
        if len(t) <= max_chars:
            return t
        if max_chars == 1:
            return "…"
        return t[: max_chars - 1] + "…"

    def _wrap_text_px(self, text: str, max_px: int, font: tkfont.Font, max_lines: int = 2) -> str:
        """ピクセル幅で日本語も確実に折り返す（必要なら末尾を…で省略）。"""
        if text is None:
            return ""
        s = str(text).replace("\r\n", "\n").replace("\r", "\n")
        if max_px <= 0:
            return s

        lines = []
        cur = ""
        i = 0
        # まずは行を作る（max_lines+1行目が出るなら後で省略）
        while i < len(s):
            ch = s[i]
            if ch == "\n":
                lines.append(cur)
                cur = ""
                i += 1
                continue

            # 1文字でも入らない場合の安全策
            if cur == "":
                cur = ch
                i += 1
                continue

            if font.measure(cur + ch) <= max_px:
                cur += ch
                i += 1
            else:
                lines.append(cur)
                cur = ""
                if len(lines) >= max_lines:
                    # ここから先は省略対象
                    break

        if len(lines) < max_lines and cur != "":
            lines.append(cur)

        # 省略が必要か判定
        remaining = s[i:] if i < len(s) else ""
        if remaining != "" and len(lines) >= 1:
            # 最終行に…を付けて収める
            last = lines[max_lines - 1] if len(lines) >= max_lines else lines[-1]
            # max_linesに揃える
            lines = lines[:max_lines]
            # …が収まるまで削る
            ell = "…"
            while last and font.measure(last + ell) > max_px:
                last = last[:-1]
            if last == "":
                last = ell
            else:
                last = last + ell
            lines[-1] = last

        return "\n".join(lines[:max_lines])

    def _commit_count_entry(self, index: int):
        """商品個数の手入力を確定する（Enter / フォーカスアウト）"""
        try:
            if index < 0 or index >= len(self.product_counts):
                return
        except Exception:
            return

        # 文字列取得
        s = ''
        try:
            if hasattr(self, 'count_vars') and index < len(self.count_vars):
                s = self.count_vars[index].get().strip()
            else:
                s = self.entries[index].get().strip()
        except Exception:
            s = ''

        if s == '':
            v = 0
        elif s.isdigit():
            v = int(s)
        else:
            # 不正値：元に戻す
            try:
                cur = int(self.product_counts[index])
            except Exception:
                cur = 0
            try:
                if hasattr(self, 'count_vars') and index < len(self.count_vars):
                    self.count_vars[index].set(str(cur))
                else:
                    ent = self.entries[index]
                    ent.delete(0, tk.END)
                    ent.insert(0, str(cur))
            except Exception:
                pass
            return

        if v < 0:
            v = 0
        self.product_counts[index] = v
        try:
            if hasattr(self, 'count_vars') and index < len(self.count_vars):
                self.count_vars[index].set(str(v))
            else:
                ent = self.entries[index]
                ent.delete(0, tk.END)
                ent.insert(0, str(v))
        except Exception:
            pass

        self.update_total_price()


    def setup_register_tab(self):
        if hasattr(self, "register_frame"):
            self.register_frame.destroy()

        self.register_frame = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(self.register_frame, text="レジ")

        self._add_created_by_footer(self.register_frame)

        # --- Top inputs (さらにコンパクト) ---
        top = ttk.Frame(self.register_frame)
        top.pack(fill=tk.X, pady=(0, 2))
        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=1)

        ttk.Label(top, text="名前", style="Reg.TLabel").grid(row=0, column=0, sticky="w")

        # 名前(2/3) + 顧客ID(1/3)
        name_box = ttk.Frame(top)
        name_box.grid(row=0, column=1, sticky="ew", padx=(4, 8))
        name_box.columnconfigure(0, weight=2)
        name_box.columnconfigure(1, weight=1)

        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(name_box, textvariable=self.name_var, style="Reg.TCombobox")
        self.name_combo["values"] = self._get_customer_names()
        self.name_combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.customer_id_var = tk.StringVar()
        self.customer_id_entry = ttk.Entry(name_box, textvariable=self.customer_id_var, width=6, justify="center", style="Reg.TEntry")
        self.customer_id_entry.grid(row=0, column=1, sticky="ew")

        # sync (存在しない名前/IDなら連動しない)
        self.name_combo.bind("<<ComboboxSelected>>", self._sync_customer_id_from_name)
        self.name_combo.bind("<Return>", self._sync_customer_id_from_name)
        self.name_combo.bind("<FocusOut>", self._sync_customer_id_from_name)
        self.customer_id_entry.bind("<Return>", self._sync_customer_name_from_id)
        self.customer_id_entry.bind("<FocusOut>", self._sync_customer_name_from_id)

        ttk.Label(top, text="資格", style="Reg.TLabel").grid(row=0, column=2, sticky="w")
        self.qualification_var = tk.StringVar()
        self.qualification_menu = ttk.Combobox(top, textvariable=self.qualification_var, state="readonly", style="Reg.TCombobox")
        self.qualification_menu["values"] = [q["name"] for q in self.qualifications]
        self.qualification_menu.current(0)
        self.qualification_menu.grid(row=0, column=3, sticky="ew", padx=(4, 0))
        self.qualification_var.trace_add("write", lambda *args: self.update_total_price())

        ttk.Label(top, text="備考", style="Reg.TLabel").grid(row=1, column=0, sticky="w")
        self.remarks_entry = ttk.Entry(top, style="Reg.TEntry")
        self.remarks_entry.grid(row=1, column=1, sticky="ew", padx=(4, 8))

        ttk.Label(top, text="質問", style="Reg.TLabel").grid(row=1, column=2, sticky="w")
        self.survey_var = tk.StringVar()
        self.survey_menu = ttk.Combobox(top, textvariable=self.survey_var, state="readonly", style="Reg.TCombobox")
        self.survey_menu["values"] = self.survey_responses
        self.survey_menu.current(0)
        self.survey_menu.grid(row=1, column=3, sticky="ew", padx=(4, 0))

        # --- Datetime selector (manual) ---
        ttk.Label(top, text="日時", style="Reg.TLabel").grid(row=2, column=0, sticky="w", pady=(2, 0))
        dt_box = ttk.Frame(top)
        dt_box.grid(row=2, column=1, sticky="w", padx=(4, 8), pady=(2, 0))

        now = datetime.now()
        self.manual_date_var = tk.StringVar(value=now.strftime('%Y-%m-%d'))
        self.manual_time_var = tk.StringVar(value=now.strftime('%H:%M'))

        self.manual_date_entry = ttk.Entry(dt_box, textvariable=self.manual_date_var, width=12, style="Reg.TEntry")
        self.manual_date_entry.pack(side=tk.LEFT)
        self.manual_date_pick_btn = ttk.Button(dt_box, text="選択", style="Reg.Small.TButton", command=self._open_date_picker)
        self.manual_date_pick_btn.pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(dt_box, text="時刻", style="Reg.TLabel").pack(side=tk.LEFT)
        self.manual_time_entry = ttk.Entry(dt_box, textvariable=self.manual_time_var, width=6, style="Reg.TEntry")
        self.manual_time_entry.pack(side=tk.LEFT, padx=(4, 0))

        self.use_now_var = tk.BooleanVar(value=True)
        self.use_now_chk = ttk.Checkbutton(top, text="現在日時", variable=self.use_now_var, style="Reg.TCheckbutton", command=self._toggle_use_now)
        self.use_now_chk.grid(row=2, column=2, columnspan=2, sticky="w", pady=(2, 0))
        self._toggle_use_now()

        # --- Actions ---
        actions = ttk.Frame(self.register_frame)
        actions.pack(fill=tk.X, pady=(0, 2))

        ttk.Button(actions, text="請求額コピー", style="Reg.Small.TButton", command=self.copy_total_price).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="愛称コピー", style="Reg.Small.TButton", command=self.copy_customer_nickname).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="お手紙コピー", style="Reg.Small.TButton", command=self.copy_name_and_message).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="送信", style="Reg.Accent.TButton", command=self.save_log).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="復元", style="Reg.Small.TButton", command=self.restore_from_history).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="クリア", style="Reg.Danger.TButton", command=self.clear_register).pack(side=tk.LEFT)

        # --- Totals ---
        totals = ttk.Frame(self.register_frame)
        totals.pack(fill=tk.X, pady=(0, 2))

        meta = ttk.Frame(totals)
        meta.pack(side=tk.RIGHT)
        self.discount_label = ttk.Label(meta, text="割引: 0円", style="Reg.Chip.TLabel")
        self.discount_label.pack(side=tk.LEFT)
        self.total_label = ttk.Label(meta, text="合計: 0円", style="Reg.Chip.TLabel")
        self.total_label.pack(side=tk.LEFT, padx=(6, 0))
        self.today_sales_label = ttk.Label(meta, text="本日売上: 0円", style="Reg.Chip.TLabel")
        self.today_sales_label.pack(side=tk.LEFT, padx=(6, 0))

        self.final_label = ttk.Label(totals, text="0円", style="Final.TLabel")
        self.final_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # --- Items: 2カラム（左/右の商品数は管理タブで指定） ---
        items = ttk.Frame(self.register_frame)
        items.pack(fill=tk.BOTH, expand=True)
        items.columnconfigure(0, weight=1)
        items.columnconfigure(1, weight=1)

        left_col = ttk.Frame(items)
        right_col = ttk.Frame(items)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.entries = []
        self.count_vars = []

        # 表示用：商品名/金額は小さく固定幅（商品名はピクセル幅で折り返し）
        name_box_w = 90
        # 商品名が2行 + 金額1行でも見切れにくい高さ（行高は他要素の方が大きいので崩れにくい）
        name_box_h = 50
        name_font = tkfont.Font(font=self.FONT_REG_PRODUCT)

        split_index = int(getattr(self, 'left_column_count', (len(self.products) + 1) // 2))
        split_index = max(0, min(split_index, len(self.products)))

        for i, product in enumerate(self.products):
            parent = left_col if i < split_index else right_col

            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=1)

            # 商品名/単価を縦に（文字サイズは小さめ・固定幅）
            np = ttk.Frame(row, width=name_box_w, height=name_box_h)
            np.pack(side=tk.LEFT, padx=(0, 6))
            try:
                np.pack_propagate(False)
            except Exception:
                pass

            name_disp = self._wrap_text_px(product.get("name", ""), max_px=max(10, name_box_w - 4), font=name_font, max_lines=2)
            ttk.Label(np, text=name_disp, style="Reg.ProductName.TLabel", anchor="w", justify="left").pack(anchor="w", fill=tk.X)
            ttk.Label(np, text=f"{product['price']}円", style="Reg.ProductPrice.TLabel", anchor="w").pack(anchor="w", fill=tk.X)

            img_lbl = ttk.Label(row, borderwidth=1, relief="solid")
            img_lbl.pack(side=tk.LEFT, padx=(0, 6))
            self.product_images[i] = img_lbl
            self.update_product_image(i)

            try:
                current = int(self.product_counts[i])
            except Exception:
                current = 0

            var = tk.StringVar(value=str(current))
            entry = ttk.Entry(row, width=4, justify="center", textvariable=var, style="Reg.TEntry")
            entry.pack(side=tk.LEFT, padx=(0, 6))
            # Enter / フォーカスアウトで確定
            entry.bind('<Return>', lambda e, i=i: self._commit_count_entry(i))
            entry.bind('<KP_Enter>', lambda e, i=i: self._commit_count_entry(i))
            entry.bind('<FocusOut>', lambda e, i=i: self._commit_count_entry(i))

            self.entries.append(entry)
            self.count_vars.append(var)

            # ボタン（横幅は小さめ）
            btn = ttk.Frame(row)
            btn.pack(side=tk.LEFT)

            ttk.Button(btn, text="+1", style="Reg.Small.TButton", width=3, command=lambda i=i: self.update_count(i, 1)).grid(row=0, column=0, padx=1, pady=0)
            ttk.Button(btn, text="+10", style="Reg.Small.TButton", width=4, command=lambda i=i: self.update_count(i, 10)).grid(row=0, column=1, padx=1, pady=0)
            ttk.Button(btn, text="C", style="Reg.Small.TButton", width=3, command=lambda i=i: self.clear_count(i)).grid(row=0, column=2, padx=1, pady=0)

            ttk.Button(btn, text="-1", style="Reg.Small.TButton", width=3, command=lambda i=i: self.update_count(i, -1)).grid(row=1, column=0, padx=1, pady=0)
            ttk.Button(btn, text="-10", style="Reg.Small.TButton", width=4, command=lambda i=i: self.update_count(i, -10)).grid(row=1, column=1, padx=1, pady=0)

    def setup_log_tab(self):
        if hasattr(self, "log_frame"):
            self.log_frame.destroy()

        self.log_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.log_frame, text="履歴")

        self._add_created_by_footer(self.log_frame)

        topbar = ttk.Frame(self.log_frame)
        topbar.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(topbar, text='選択行削除', command=self.delete_selected_log_row).pack(side=tk.LEFT)

        base_cols = ["date", "time", "customer", "qualification", "total"]
        prod_cols = [f"product{i+1}" for i in range(self.product_count)]
        summary_cols = ["items_total", "breakdown"]
        columns = base_cols + prod_cols + summary_cols

        self.log_tree = self._make_treeview(self.log_frame, columns)
        self.log_tree["displaycolumns"] = base_cols + summary_cols

        self.log_tree.heading("date", text="日付")
        self.log_tree.heading("time", text="時刻")
        self.log_tree.heading("customer", text="顧客")
        self.log_tree.heading("qualification", text="資格")
        self.log_tree.heading("total", text="請求")
        self.log_tree.heading("items_total", text="個数")
        self.log_tree.heading("breakdown", text="内訳")

        self.log_tree.column("date", width=78, minwidth=60, anchor="center")
        self.log_tree.column("time", width=78, minwidth=60, anchor="center")
        self.log_tree.column("customer", width=180, minwidth=120)
        self.log_tree.column("qualification", width=60, minwidth=50)
        self.log_tree.column("total", width=95, minwidth=75, anchor="e")
        self.log_tree.column("items_total", width=65, minwidth=55, anchor="e")
        self.log_tree.column("breakdown", width=320, minwidth=160)

        for c in prod_cols:
            self.log_tree.column(c, width=0, minwidth=0, stretch=False)

        self.load_log_from_csv()

    def setup_survey_tab(self):
        if hasattr(self, "survey_frame"):
            self.survey_frame.destroy()

        self.survey_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.survey_frame, text="備考")

        self._add_created_by_footer(self.survey_frame)

        topbar = ttk.Frame(self.survey_frame)
        topbar.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(topbar, text='選択行削除', command=self.delete_selected_survey_row).pack(side=tk.LEFT)

        columns = ["date", "time", "customer", "qualification", "survey", "remarks"]
        self.survey_tree = self._make_treeview(self.survey_frame, columns)

        self.survey_tree.heading("date", text="日付")
        self.survey_tree.heading("time", text="時刻")
        self.survey_tree.heading("customer", text="顧客")
        self.survey_tree.heading("qualification", text="資格")
        self.survey_tree.heading("survey", text="回答")
        self.survey_tree.heading("remarks", text="備考")

        self.survey_tree.column("date", width=70, minwidth=60, anchor="center")
        self.survey_tree.column("time", width=70, minwidth=60, anchor="center")
        self.survey_tree.column("customer", width=180, minwidth=120)
        self.survey_tree.column("qualification", width=90, minwidth=70)
        self.survey_tree.column("survey", width=120, minwidth=80)
        self.survey_tree.column("remarks", width=260, minwidth=120)

        self.load_survey_from_csv()

    def _make_treeview(self, parent, columns, height=None):
        """Treeview + scrollbars"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        tree = ttk.Treeview(container, columns=columns, show="headings", height=(height if height is not None else 10))
        ysb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        xsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")

        return tree

    # -------- Question --------
    def setup_question_tab(self):
        if hasattr(self, "question_frame"):
            self.question_frame.destroy()

        self.question_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.question_frame, text="質問")

        self._add_created_by_footer(self.question_frame)

        top = ttk.Labelframe(self.question_frame, text="質問数", padding=10)
        top.pack(fill=tk.X, pady=(0, 10))
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="質問数").grid(row=0, column=0, sticky="w")
        self.question_count_entry = ttk.Entry(top, width=10)
        self.question_count_entry.insert(0, str(len(self.survey_responses)))
        self.question_count_entry.grid(row=0, column=1, sticky="w", padx=(8, 10))
        ttk.Button(top, text="更新", command=self.update_question_count).grid(row=0, column=2, sticky="w")

        body = ttk.Labelframe(self.question_frame, text="回答ラベル", padding=10)
        body.pack(fill=tk.BOTH, expand=True)

        self.question_entries = []
        for i, question in enumerate(self.survey_responses):
            row = ttk.Frame(body)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"質問 {i+1}", width=10).pack(side=tk.LEFT)
            ent = ttk.Entry(row)
            ent.insert(0, question)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
            self.question_entries.append(ent)

        ttk.Button(self.question_frame, text="決定", style="Accent.TButton", command=self.save_question_changes).pack(pady=10)

    def update_question_count(self):
        cur_tab_text = self._get_selected_tab_text()
        new_count_str = self.question_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "質問数には1以上の整数を入力してください。")
            return

        new_count = int(new_count_str)
        current_questions = self.survey_responses

        if new_count > len(current_questions):
            new_questions = current_questions + [f"質問 {i+1}" for i in range(len(current_questions), new_count)]
        else:
            new_questions = current_questions[:new_count]

        self.survey_responses = new_questions
        self.save_question_responses_to_csv()
        self.setup_question_tab()
        self._reorder_tabs()
        self._select_tab_by_text(cur_tab_text)

    def save_question_changes(self):
        cur_tab_text = self._get_selected_tab_text()
        new_questions = [entry.get().strip() for entry in self.question_entries]

        if not all(new_questions):
            messagebox.showwarning("警告", "全ての質問名を入力してください。")
            return

        self.survey_responses = new_questions
        self.save_question_responses_to_csv()
        self.setup_register_tab()
        self._reorder_tabs()
        messagebox.showinfo("成功", "質問が更新されました。")
        self._select_tab_by_text(cur_tab_text)

    # -------- Management --------
    def setup_management_tab(self):
        if hasattr(self, "management_frame"):
            self.management_frame.destroy()

        self.management_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.management_frame, text="管理")

        self._add_created_by_footer(self.management_frame)

        top = ttk.Frame(self.management_frame)
        top.pack(fill=tk.X, pady=(0, 8))
        top.columnconfigure(1, weight=1)

        # Row0: 店舗名 + 配色（店舗名の右）
        ttk.Label(top, text="店舗名").grid(row=0, column=0, sticky="w")
        self.shop_name_entry = ttk.Entry(top)
        self.shop_name_entry.grid(row=0, column=1, sticky="ew", padx=(6, 10))
        self.load_shop_name()

        ttk.Label(top, text="配色").grid(row=0, column=2, sticky="w")
        self.ui_theme_var = tk.StringVar(value=getattr(self, "ui_theme_name", "Light Slate"))
        self.ui_theme_menu = ttk.Combobox(top, textvariable=self.ui_theme_var, state="readonly", width=14)
        self.ui_theme_menu["values"] = getattr(self, "UI_THEME_NAMES", ["Light Slate", "Light Mint", "Light Sand", "Light Sakura", "Dark Emerald"])
        try:
            self.ui_theme_menu.current(self.ui_theme_menu["values"].index(self.ui_theme_var.get()))
        except Exception:
            self.ui_theme_menu.current(0)
        self.ui_theme_menu.grid(row=0, column=3, sticky="w")
        self.ui_theme_menu.bind("<<ComboboxSelected>>", lambda e: self.apply_ui_theme(self.ui_theme_var.get()))

        # Row1: お手紙
        ttk.Label(top, text="お手紙").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.persistent_text_entry = ttk.Entry(top)
        self.persistent_text_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=(6, 0))
        self.load_persistent_text()

        # Row2: 商品数（左/右）→ 合計を商品数にして反映 + 画像サイズトグル（反映の右）
        row3 = ttk.Frame(self.management_frame)
        row3.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(row3, text='商品数').pack(side=tk.LEFT)

        ttk.Label(row3, text='左').pack(side=tk.LEFT, padx=(10, 0))
        self.left_col_entry = ttk.Entry(row3, width=6)
        self.left_col_entry.insert(0, str(int(getattr(self, 'left_column_count', (self.product_count + 1)//2))))
        self.left_col_entry.pack(side=tk.LEFT, padx=(6, 12))

        ttk.Label(row3, text='右').pack(side=tk.LEFT)
        self.right_col_entry = ttk.Entry(row3, width=6)
        self.right_col_entry.insert(0, str(int(getattr(self, 'right_column_count', self.product_count - int(self.left_col_entry.get())))))
        self.right_col_entry.pack(side=tk.LEFT, padx=(6, 12))

        ttk.Button(row3, text='反映', command=self.update_column_counts).pack(side=tk.LEFT)

        # 右側（右詰）に 画像サイズトグル + 決定 + ID反映 をまとめて配置（縦幅節約）
        right_controls = ttk.Frame(row3)
        right_controls.pack(side=tk.RIGHT)

        scale_label = '小' if int(getattr(self, 'image_scale', 2)) == 2 else '大'
        self.image_toggle_btn = ttk.Button(right_controls, text=f"画像サイズ: {scale_label}", command=self.toggle_image_size)
        self.image_toggle_btn.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(right_controls, text="商品決定", style="Accent.TButton", command=self.save_management_changes).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(right_controls, text="ID反映", command=self.apply_ids_from_catalog).pack(side=tk.LEFT)

        products = ttk.Labelframe(self.management_frame, text="商品設定", padding=6)
        products.pack(fill=tk.BOTH, expand=True)

        wrap = ttk.Frame(products)
        wrap.pack(fill=tk.BOTH, expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(wrap)
        right_frame = ttk.Frame(wrap)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(6, 0))

        self.management_entries = []  # (id_entry, name_entry, price_entry, desc_entry)

        split_index = int(getattr(self, 'left_column_count', (len(self.products) + 1)//2))
        split_index = max(0, min(split_index, len(self.products)))
        def make_row(parent, i):
            product = self.products[i]
            outer = ttk.Frame(parent)
            # 行間を詰める（ウィンドウ高さ節約）
            outer.pack(fill=tk.X, pady=1)

            # 2列構成: [商品ID + 画像] | [その他（商品名/金額/画像ボタン + 説明）]
            outer.grid_columnconfigure(1, weight=1)

            left_col = ttk.Frame(outer)
            left_col.grid(row=0, column=0, sticky='nw')

            right_col = ttk.Frame(outer)
            right_col.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
            right_col.grid_columnconfigure(0, weight=1)

            # --- left column (ID + image) ---
            id_entry = ttk.Entry(left_col, width=5, justify='center')
            id_entry.insert(0, product.get('id', ''))
            id_entry.grid(row=0, column=0, sticky='w')
            id_entry.bind('<Return>', lambda e, idx=i: self.on_product_id_enter(idx))
            img_lbl = ttk.Label(left_col, borderwidth=1, relief='solid')
            img_lbl.grid(row=0, column=1, sticky='w', padx=(6, 0))
            self.product_images[i] = img_lbl
            self.update_product_image(i, pid_override=id_entry.get())

            # --- right column: top row (name/price/button) ---
            top_row = ttk.Frame(right_col)
            top_row.grid(row=0, column=0, sticky='ew', pady=(0, 0))
            top_row.grid_columnconfigure(0, weight=1)

            name_entry = ttk.Entry(top_row, width=18)
            name_entry.insert(0, product.get('name', ''))
            name_entry.grid(row=0, column=0, sticky='ew', padx=(0, 6))

            price_entry = ttk.Entry(top_row, width=10)
            price_entry.insert(0, str(product.get('price', '')))
            price_entry.grid(row=0, column=1, sticky='w', padx=(0, 6))

            ttk.Button(top_row, text='画像', style='Img.TButton', command=lambda idx=i: self.select_image(idx)).grid(row=0, column=2, sticky='w')

            # --- right column: desc row under the top row ---
            desc_entry = tk.Entry(
                right_col,
                bd=0,
                highlightthickness=1,
                relief='flat',
                highlightbackground=self.UI_PANEL_2,
                highlightcolor=self.UI_ACCENT,
                bg=self.UI_ENTRY,
                fg=self.UI_TEXT,
                insertbackground=self.UI_TEXT,
                font=self.FONT_BASE,
            )
            # 行間を詰める
            desc_entry.grid(row=1, column=0, sticky='ew', pady=(1, 0))

            self._init_desc_entry(desc_entry, (product.get('desc') or '').strip())

            self.management_entries.append((id_entry, name_entry, price_entry, desc_entry))

        for i in range(0, split_index):
            make_row(left_frame, i)
        for i in range(split_index, len(self.products)):
            make_row(right_frame, i)


    def apply_ids_from_catalog(self):
        """管理タブ: 各商品のIDに従って、カタログ(product_catalog.csv)から商品名/単価を呼び出す"""
        if not hasattr(self, 'management_entries'):
            return

        loaded = 0
        for i, (id_entry, name_entry, price_entry, desc_entry) in enumerate(self.management_entries):
            pid = self._sanitize_product_id(id_entry.get())
            if not pid:
                continue

            # normalize ID
            try:
                id_entry.delete(0, tk.END)
                id_entry.insert(0, pid)
            except Exception:
                pass

            cat = getattr(self, 'product_catalog', {}).get(pid)
            if cat:
                try:
                    if cat.get('name'):
                        name_entry.delete(0, tk.END)
                        name_entry.insert(0, cat['name'])
                except Exception:
                    pass
                try:
                    if str(cat.get('price', '')).isdigit():
                        price_entry.delete(0, tk.END)
                        price_entry.insert(0, cat['price'])
                except Exception:
                    pass

                try:
                    if cat.get('desc') is not None:
                        self._set_desc_value(desc_entry, cat.get('desc', ''))
                except Exception:
                    pass

                loaded += 1

            # image update
            self.update_product_image(i, pid_override=pid)

        if loaded > 0:
            messagebox.showinfo('完了', f'IDから商品情報を読み込みました（{loaded}件）。')
        else:
            messagebox.showinfo('完了', '読み込める商品情報がありませんでした。')


    def on_product_id_enter(self, index: int):
        """管理タブ: ID欄でEnter → 過去カタログから名前/単価を自動読み込み + 画像更新"""
        try:
            id_entry, name_entry, price_entry, desc_entry = self.management_entries[index]
        except Exception:
            return

        pid_raw = id_entry.get()
        pid = self._sanitize_product_id(pid_raw)
        if not pid:
            messagebox.showwarning('警告', '商品IDは英数字3文字で入力してください。例: f01')
            return

        # サニタイズした値を戻す
        id_entry.delete(0, tk.END)
        id_entry.insert(0, pid)

        # カタログから補完
        cat = getattr(self, 'product_catalog', {}).get(pid)
        if cat:
            if cat.get('name'):
                name_entry.delete(0, tk.END)
                name_entry.insert(0, cat['name'])
            if str(cat.get('price', '')).isdigit():
                price_entry.delete(0, tk.END)
                price_entry.insert(0, cat['price'])
            try:
                if cat.get('desc') is not None:
                    self._set_desc_value(desc_entry, cat.get('desc', ''))
            except Exception:
                pass

        # 画像更新（存在すれば表示）
        self.update_product_image(index, pid_override=pid)
    def change_image_size(self, scale):
        cur_tab_text = self._get_selected_tab_text()
        if scale not in (2, 3):
            scale = 2
        self.image_scale = scale
        self.save_image_scale()
        self.update_window_size()
        self.setup_management_tab()
        self.setup_register_tab()
        self._reorder_tabs()
        self._select_tab_by_text(cur_tab_text)
    def update_window_size(self):
        # 2カラム表示なので、縦サイズは「多い方のカラム数」で決める
        left = int(getattr(self, 'left_column_count', (len(self.products) + 1) // 2))
        right = int(getattr(self, 'right_column_count', len(self.products) - left))
        rows = max(1, left, right)

        base, row_h, min_rows = self._window_params_for_scale(int(getattr(self, 'image_scale', 2)))
        min_h = int(base + row_h * max(1, int(min_rows)))
        h = int(base + row_h * rows)
        h = max(h, min_h)

        w = int(getattr(self, 'win_width', 780))
        min_w = int(getattr(self, 'win_min_width', w))

        self.default_width = w
        self.default_height = h
        try:
            self.root.minsize(min_w, min_h)
        except Exception:
            pass
        try:
            self.root.geometry(f"{w}x{h}")
        except Exception:
            pass

    def setup_qualification_tab(self):
        if hasattr(self, "qualification_frame"):
            self.qualification_frame.destroy()

        self.qualification_frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(self.qualification_frame, text="資格")

        self._add_created_by_footer(self.qualification_frame)

        top = ttk.Labelframe(self.qualification_frame, text="資格数", padding=10)
        top.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top, text="資格数").grid(row=0, column=0, sticky="w")
        self.qualification_count_entry = ttk.Entry(top, width=10)
        self.qualification_count_entry.insert(0, str(self.qualification_count))
        self.qualification_count_entry.grid(row=0, column=1, sticky="w", padx=(8, 10))
        ttk.Button(top, text="更新", command=self.update_qualification_count).grid(row=0, column=2, sticky="w")

        body = ttk.Labelframe(self.qualification_frame, text="割引設定", padding=10)
        body.pack(fill=tk.BOTH, expand=True)

        self.qualification_entries = []
        for i, qualification in enumerate(self.qualifications):
            row = ttk.Frame(body)
            row.pack(fill=tk.X, pady=2)

            ttk.Label(row, text=f"資格 {i+1}", width=10).pack(side=tk.LEFT)

            name_entry = ttk.Entry(row, width=18)
            name_entry.insert(0, qualification["name"])
            name_entry.pack(side=tk.LEFT, padx=(8, 10))

            disc_entry = ttk.Entry(row, width=8)
            disc_entry.insert(0, qualification["discount"])
            disc_entry.pack(side=tk.LEFT)
            ttk.Label(row, text="%", style="Muted.TLabel").pack(side=tk.LEFT, padx=(4, 0))

            self.qualification_entries.append((name_entry, disc_entry))

        ttk.Button(self.qualification_frame, text="決定", style="Accent.TButton", command=self.save_qualification_changes).pack(pady=10)

    # ----------------------------
    # Image handling (元のロジックを維持)
    # ----------------------------
    def select_image(self, index):
        """管理タブ: 選択した画像を images/image_<id>.png として保存"""
        cur_tab_text = self._get_selected_tab_text()

        pid = ''
        try:
            pid = self._sanitize_product_id(self.management_entries[index][0].get())
        except Exception:
            pid = ''
        if not pid:
            messagebox.showwarning('警告', '画像を設定する前に、3文字の商品IDを入力してください。例: f01')
            return

        filepath = filedialog.askopenfilename(filetypes=[('PNG Images', '*.png')], title='画像を選択')
        if not filepath:
            return

        image_dir = self.images_dir
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, f'image_{pid}.png')
        try:
            Image.open(filepath).save(image_path)
        except Exception:
            messagebox.showwarning('警告', '画像の保存に失敗しました。PNG画像を選んでください。')
            return

        self.update_product_image(index, pid_override=pid)
        self.setup_management_tab()
        self.setup_register_tab()
        self._reorder_tabs()
        self._select_tab_by_text(cur_tab_text)
    def _get_blank_photo(self, size: int):
        """透明の空画像を返す（ラベルの幅が0になって崩れるのを防ぐ）"""
        if size not in self._blank_photos or self._blank_photos.get(size) is None:
            try:
                img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                self._blank_photos[size] = ImageTk.PhotoImage(img)
            except Exception:
                self._blank_photos[size] = None
        return self._blank_photos.get(size)

    def update_product_image(self, index, pid_override: str | None = None):
        image_dir = self.images_dir
        pid = ''
        if pid_override:
            pid = self._sanitize_product_id(pid_override)
        if not pid:
            try:
                pid = self._sanitize_product_id(self.products[index].get('id', ''))
            except Exception:
                pid = ''

        size = 20 * self.image_scale
        lbl = self.product_images[index]
        if lbl is None:
            return

        blank = self._get_blank_photo(size)
        if not pid:
            lbl.configure(image=blank)
            lbl.image = blank
            return

        image_path = os.path.join(image_dir, f'image_{pid}.png')
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((size, size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                lbl.configure(image=photo)
                lbl.image = photo
                return
            except Exception:
                pass

        lbl.configure(image=blank)
        lbl.image = blank

    def update_count(self, index, delta):
        new_count = max(0, self.product_counts[index] + delta)
        self.product_counts[index] = new_count

        # 手入力対応：StringVarがあればそれを更新
        if hasattr(self, 'count_vars') and index < len(self.count_vars):
            try:
                self.count_vars[index].set(str(new_count))
            except Exception:
                pass
        else:
            try:
                ent = self.entries[index]
                ent.state(["!readonly"])
                ent.delete(0, tk.END)
                ent.insert(0, str(new_count))
                ent.state(["readonly"])
            except Exception:
                pass

        self.update_total_price()

    def clear_count(self, index):
        self.product_counts[index] = 0

        if hasattr(self, 'count_vars') and index < len(self.count_vars):
            try:
                self.count_vars[index].set('0')
            except Exception:
                pass
        else:
            try:
                ent = self.entries[index]
                ent.state(["!readonly"])
                ent.delete(0, tk.END)
                ent.insert(0, '0')
                ent.state(["readonly"])
            except Exception:
                pass

        self.update_total_price()

    def update_total_price(self, *args):
        total = sum(count * int(product["price"]) for count, product in zip(self.product_counts, self.products))
        qualification_name = self.qualification_var.get() if hasattr(self, "qualification_var") else ""
        qualification = next((q for q in self.qualifications if q["name"] == qualification_name), None)
        discount_rate = int(qualification["discount"]) if qualification else 0
        discount = total * (discount_rate / 100)
        final_total = total - discount
        if hasattr(self, "total_label"):
            self.total_label.configure(text=f"合計: {total}円")
        if hasattr(self, "discount_label"):
            self.discount_label.configure(text=f"割引: {int(discount)}円")
        if hasattr(self, "final_label"):
            self.final_label.configure(text=f"{int(final_total)}円")
        self.update_today_sales_label()

    def save_log(self):
        name = self.name_var.get().strip() if hasattr(self, 'name_var') else ''
        cid_in = ''
        try:
            if hasattr(self, 'customer_id_var'):
                cid_in = (self.customer_id_var.get() or '').strip()
        except Exception:
            cid_in = ''

        # 名前が空なら、IDから既存顧客を引く（存在しないIDなら連動しない）
        if not name:
            cid_try = cid_in
            if cid_try.isdigit() and len(cid_try) < 3:
                cid_try = cid_try.zfill(3)
            nm = getattr(self, 'customer_name_by_id', {}).get(cid_try)
            if nm:
                name = nm
                try:
                    self.name_var.set(name)
                except Exception:
                    pass
                cid_in = cid_try
            else:
                messagebox.showwarning("警告", "名前を入力してください。")
                return

        # 顧客ID（入力IDが名前と整合するならそれを使用。そうでなければ名前から決定）
        cid = ''
        cid_norm = cid_in
        if cid_norm.isdigit() and len(cid_norm) < 3:
            cid_norm = cid_norm.zfill(3)
        if cid_norm and getattr(self, 'customer_name_by_id', {}).get(cid_norm) == name:
            cid = cid_norm
        else:
            cid = self.ensure_customer_id(name)

        try:
            if hasattr(self, 'customer_id_var'):
                self.customer_id_var.set(cid)
        except Exception:
            pass

        qualification = self.qualification_var.get()
        remarks = self.remarks_entry.get().strip()
        survey_response = self.survey_var.get()

        selected_dt = self._get_selected_datetime()
        if selected_dt is None:
            return

        date_str = selected_dt.strftime("%m-%d")
        time_str = selected_dt.strftime("%H:%M")

        total = sum(count * int(product["price"]) for count, product in zip(self.product_counts, self.products))
        discount_rate = int(next((q["discount"] for q in self.qualifications if q["name"] == qualification), 0))
        discount = total * (discount_rate / 100)
        final_total = total - discount

        counts = list(self.product_counts)
        # CSV用（標準）
        base_row = [date_str, time_str, cid, name, qualification, int(final_total)] + counts

        items_total, breakdown, _ = self._summarize_counts(counts)
        customer_disp = self._customer_display(cid, name)
        tree_values = [date_str, time_str, customer_disp, qualification, int(final_total)] + counts + [items_total, breakdown]

        # tree iid は行番号で付与
        if not hasattr(self, '_log_rows'):
            self._log_rows = []
        idx = len(self._log_rows)
        self._log_rows.append(base_row)
        try:
            self.log_tree.insert("", "end", iid=str(idx), values=tree_values)
        except Exception:
            self.log_tree.insert("", "end", values=tree_values)

        self.append_log_to_csv(base_row)

        survey_entry = [date_str, time_str, cid, name, qualification, survey_response, remarks]
        if not hasattr(self, '_survey_rows'):
            self._survey_rows = []
        sidx = len(self._survey_rows)
        self._survey_rows.append(survey_entry)
        try:
            self.survey_tree.insert("", "end", iid=str(sidx), values=[date_str, time_str, customer_disp, qualification, survey_response, remarks])
        except Exception:
            self.survey_tree.insert("", "end", values=[date_str, time_str, customer_disp, qualification, survey_response, remarks])
        self.append_survey_to_csv(survey_entry)

        # update daily sales display
        self.update_today_sales_label()

        # 名前候補更新
        self._refresh_customer_name_values(extra_name=name)

        # 入力をクリア
        self.name_var.set("")
        try:
            if hasattr(self, 'customer_id_var'):
                self.customer_id_var.set("")
        except Exception:
            pass
        self.remarks_entry.delete(0, tk.END)
        self.survey_menu.current(0)
        self.qualification_menu.current(0)
        for i in range(len(self.products)):
            self.clear_count(i)


    # ---- Datetime helpers (Register) ----
    def _toggle_use_now(self):
        """現在日時チェックに応じて、手動日時入力を有効/無効にする"""
        use_now = True
        try:
            use_now = bool(self.use_now_var.get())
        except Exception:
            use_now = True

        state = 'disabled' if use_now else 'normal'
        for w in (getattr(self, 'manual_date_entry', None), getattr(self, 'manual_time_entry', None)):
            if w is None:
                continue
            try:
                w.configure(state=state)
            except Exception:
                try:
                    w['state'] = state
                except Exception:
                    pass
        btn = getattr(self, 'manual_date_pick_btn', None)
        if btn is not None:
            try:
                btn.configure(state=state)
            except Exception:
                pass

    def _get_selected_datetime(self):
        """送信時に使用する日時を返す。Noneなら警告済みで中断。"""
        try:
            if getattr(self, 'use_now_var', None) is not None and bool(self.use_now_var.get()):
                return datetime.now()
        except Exception:
            return datetime.now()

        date_s = ''
        time_s = ''
        try:
            date_s = self.manual_date_var.get().strip()
        except Exception:
            pass
        try:
            time_s = self.manual_time_var.get().strip()
        except Exception:
            pass

        # Parse date
        try:
            d = datetime.strptime(date_s, '%Y-%m-%d')
        except Exception:
            messagebox.showwarning('警告', '日付は YYYY-MM-DD 形式で入力してください。')
            return None

        # Parse time
        try:
            t = datetime.strptime(time_s, '%H:%M')
        except Exception:
            messagebox.showwarning('警告', '時刻は HH:MM 形式で入力してください。')
            return None

        return datetime(d.year, d.month, d.day, t.hour, t.minute)

    def _open_date_picker(self):
        """簡易カレンダーで日付を選ぶ（外部依存なし）。"""
        # 入力が無効なら何もしない
        try:
            if getattr(self, 'use_now_var', None) is not None and bool(self.use_now_var.get()):
                return
        except Exception:
            pass

        # 初期年月
        try:
            base = datetime.strptime(self.manual_date_var.get().strip(), '%Y-%m-%d')
            y, m = base.year, base.month
        except Exception:
            now = datetime.now()
            y, m = now.year, now.month

        top = tk.Toplevel(self.root)
        top.title('日付選択')
        try:
            top.transient(self.root)
            top.grab_set()
        except Exception:
            pass

        header = ttk.Frame(top, padding=8)
        header.pack(fill=tk.X)
        body = ttk.Frame(top, padding=8)
        body.pack(fill=tk.BOTH, expand=True)

        ym_var = tk.StringVar()

        def redraw():
            for w in body.winfo_children():
                w.destroy()

            ym_var.set(f"{y:04d}-{m:02d}")

            # Weekday header
            wd = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
            for i, lab in enumerate(wd):
                ttk.Label(body, text=lab).grid(row=0, column=i, padx=2, pady=2)

            cal = calendar.monthcalendar(y, m)
            for r, week in enumerate(cal, start=1):
                for c, day in enumerate(week):
                    if day == 0:
                        ttk.Label(body, text='').grid(row=r, column=c, padx=2, pady=2)
                        continue

                    def pick(d=day):
                        try:
                            self.manual_date_var.set(f"{y:04d}-{m:02d}-{d:02d}")
                        except Exception:
                            pass
                        try:
                            top.destroy()
                        except Exception:
                            pass

                    ttk.Button(body, text=f"{day:02d}", width=3, command=pick).grid(row=r, column=c, padx=2, pady=2)

        def prev_month():
            nonlocal y, m
            m -= 1
            if m <= 0:
                y -= 1
                m = 12
            redraw()

        def next_month():
            nonlocal y, m
            m += 1
            if m >= 13:
                y += 1
                m = 1
            redraw()

        ttk.Button(header, text='<', width=3, command=prev_month).pack(side=tk.LEFT)
        ttk.Label(header, textvariable=ym_var).pack(side=tk.LEFT, padx=10)
        ttk.Button(header, text='>', width=3, command=next_month).pack(side=tk.LEFT)

        redraw()
    def append_log_to_csv(self, log_entry):
        with open(self._p_log("log.csv"), "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)

    def append_survey_to_csv(self, survey_entry):
        with open(self._p_log("survey_log.csv"), "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(survey_entry)


    def _write_log_rows(self, rows):
        """標準形式で log.csv を書き直す"""
        try:
            with open(self._p_log('log.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                for r in rows:
                    w.writerow(r)
        except Exception:
            pass

    def _write_survey_rows(self, rows):
        try:
            with open(self._p_log('survey_log.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                for r in rows:
                    w.writerow(r)
        except Exception:
            pass

    def load_log_from_csv(self):
        # 既存をクリア
        if hasattr(self, 'log_tree'):
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)

        self._log_rows = []

        try:
            with open(self._p_log("log.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue

                    # old: date,time,name,qualification,total, count...
                    # new: date,time,cid,name,qualification,total, count...
                    if len(row) >= 6 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                        cid = row[2].strip()
                        name = row[3].strip()
                        qualification = row[4].strip() if len(row) > 4 else ''
                        total_s = row[5].strip() if len(row) > 5 else '0'
                        counts_start = 6
                    else:
                        cid = self.ensure_customer_id(row[2].strip() if len(row) >= 3 else '')
                        name = row[2].strip() if len(row) >= 3 else ''
                        qualification = row[3].strip() if len(row) > 3 else ''
                        total_s = row[4].strip() if len(row) > 4 else '0'
                        counts_start = 5

                    try:
                        total_v = int(total_s)
                    except Exception:
                        total_v = 0

                    counts = []
                    for i in range(self.product_count):
                        try:
                            counts.append(int(row[counts_start + i]))
                        except Exception:
                            counts.append(0)

                    # 標準行として保持
                    base_row = [row[0], row[1], cid, name, qualification, total_v] + counts
                    self._log_rows.append(base_row)

                    items_total, breakdown, _ = self._summarize_counts(counts)
                    customer_disp = self._customer_display(cid, name)
                    values = [row[0], row[1], customer_disp, qualification, total_v] + counts + [items_total, breakdown]
                    iid = str(len(self._log_rows) - 1)
                    self.log_tree.insert('', 'end', iid=iid, values=values)
        except FileNotFoundError:
            pass

        # レジ/顧客の名前候補を更新
        self._refresh_customer_name_values()

    def load_survey_from_csv(self):
        if not hasattr(self, "survey_tree"):
            return
        for item in self.survey_tree.get_children():
            self.survey_tree.delete(item)

        self._survey_rows = []
        try:
            with open(self._p_log("survey_log.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    # old: date,time,name,qualification,survey,remarks
                    # new: date,time,cid,name,qualification,survey,remarks
                    if len(row) >= 7 and row[2].strip().isdigit() and len(row[2].strip()) == 3:
                        cid = row[2].strip()
                        name = row[3].strip()
                        qual = row[4].strip()
                        ans = row[5].strip()
                        rem = row[6].strip() if len(row) > 6 else ''
                        std = [row[0], row[1], cid, name, qual, ans, rem]
                    else:
                        name = row[2].strip() if len(row) >= 3 else ''
                        cid = self.ensure_customer_id(name)
                        qual = row[3].strip() if len(row) > 3 else ''
                        ans = row[4].strip() if len(row) > 4 else ''
                        rem = row[5].strip() if len(row) > 5 else ''
                        std = [row[0], row[1], cid, name, qual, ans, rem]

                    self._survey_rows.append(std)
                    customer_disp = self._customer_display(cid, name)
                    iid = str(len(self._survey_rows) - 1)
                    self.survey_tree.insert('', 'end', iid=iid, values=[row[0], row[1], customer_disp, qual, ans, rem])
        except FileNotFoundError:
            pass



    # ----------------------------
    # Description entry helpers (Management)
    # ----------------------------
    DESC_PLACEHOLDER = '説明'

    def _init_desc_entry(self, ent, value: str):
        value = (value or '').strip()
        if value:
            try:
                ent.delete(0, tk.END)
                ent.insert(0, value)
                ent.config(fg=self.UI_TEXT)
            except Exception:
                pass
        else:
            try:
                ent.delete(0, tk.END)
                ent.insert(0, self.DESC_PLACEHOLDER)
                ent.config(fg=self.UI_MUTED)
            except Exception:
                pass

        try:
            ent.bind('<FocusIn>', lambda e, w=ent: self._desc_focus_in(w))
            ent.bind('<FocusOut>', lambda e, w=ent: self._desc_focus_out(w))
        except Exception:
            pass

    def _desc_focus_in(self, ent):
        try:
            if ent.get() == self.DESC_PLACEHOLDER:
                ent.delete(0, tk.END)
            ent.config(fg=self.UI_TEXT)
        except Exception:
            pass

    def _desc_focus_out(self, ent):
        try:
            if not ent.get().strip():
                ent.delete(0, tk.END)
                ent.insert(0, self.DESC_PLACEHOLDER)
                ent.config(fg=self.UI_MUTED)
        except Exception:
            pass

    def _get_desc_value(self, ent) -> str:
        try:
            v = (ent.get() or '').strip()
        except Exception:
            v = ''
        if v == self.DESC_PLACEHOLDER:
            return ''
        return v

    def _set_desc_value(self, ent, value: str):
        self._init_desc_entry(ent, value)

    def _sanitize_product_id(self, raw: str) -> str:
        s = (raw or '').strip().lower()
        s = ''.join(ch for ch in s if ch.isalnum())
        if len(s) != 3:
            return ''
        return s

    def _default_product_ids(self, left: int | None = None, right: int | None = None):
        n = int(getattr(self, 'product_count', 0))
        if left is None:
            left = int(getattr(self, 'left_column_count', (n + 1)//2))
        if right is None:
            right = int(getattr(self, 'right_column_count', n - left))
        left = max(0, min(left, n))
        right = max(0, min(right, n - left))

        ids = []
        for i in range(left):
            ids.append(f"f{i+1:02d}"[-3:])
        for i in range(right):
            ids.append(f"d{i+1:02d}"[-3:])
        # 念のため長さ合わせ
        while len(ids) < n:
            ids.append(f"p{len(ids)+1:02d}"[-3:])
        return ids[:n]

    def load_product_catalog(self):
        """過去の商品設定（ID→名前/単価）を保存しておくカタログ"""
        self.product_catalog = {}
        try:
            with open(self._p_setting('product_catalog.csv'), 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pid = self._sanitize_product_id(row.get('id', ''))
                    if not pid:
                        continue
                    name = (row.get('name') or '').strip()
                    price = (row.get('price') or '').strip()
                    if name and price.isdigit():
                        desc = (row.get('desc') or '').strip()
                        self.product_catalog[pid] = {'name': name, 'price': price, 'desc': desc}
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def save_product_catalog(self):
        try:
            with open(self._p_setting('product_catalog.csv'), 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'name', 'price', 'desc'])
                writer.writeheader()
                for pid in sorted(self.product_catalog.keys()):
                    v = self.product_catalog[pid]
                    writer.writerow({'id': pid, 'name': v.get('name', ''), 'price': v.get('price', ''), 'desc': v.get('desc', '')})
        except Exception:
            pass

    def _migrate_index_images_to_id(self):
        """旧:image1.png方式から image_<id>.png へコピー（残しておく）"""
        image_dir = self.images_dir
        if not os.path.isdir(image_dir):
            return
        defaults = self._default_product_ids()
        for idx in range(int(getattr(self, 'product_count', 0))):
            old_path = os.path.join(image_dir, f'image{idx+1}.png')
            pid = ''
            try:
                pid = self.products[idx].get('id', '')
            except Exception:
                pid = defaults[idx] if idx < len(defaults) else ''
            pid = self._sanitize_product_id(pid) or (defaults[idx] if idx < len(defaults) else '')
            if not pid:
                continue
            new_path = os.path.join(image_dir, f'image_{pid}.png')
            if os.path.exists(old_path) and not os.path.exists(new_path):
                try:
                    import shutil
                    shutil.copyfile(old_path, new_path)
                except Exception:
                    pass

    def load_products_from_csv(self):
        upgraded = False
        defaults = self._default_product_ids()
        try:
            with open(self._p_setting('products.csv'), 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                rows = [row for row in reader]

            self.products = []
            for i, row in enumerate(rows):
                name = (row.get('name') or '').strip() or f"品{i+1}"
                price = (row.get('price') or '').strip() or '10000'
                pid = row.get('id') if 'id' in fieldnames else ''
                pid = self._sanitize_product_id(pid) if pid else ''
                if not pid:
                    pid = defaults[i] if i < len(defaults) else f"p{i+1:02d}"[-3:]
                    upgraded = True
                desc = (row.get('desc') or '').strip()
                self.products.append({'id': pid, 'name': name, 'price': price, 'desc': desc})

            while len(self.products) < self.product_count:
                i = len(self.products)
                pid = defaults[i] if i < len(defaults) else f"p{i+1:02d}"[-3:]
                self.products.append({'id': pid, 'name': f"品{i+1}", 'price': '10000', 'desc': ''})
                upgraded = True

            self.products = self.products[: self.product_count]

        except FileNotFoundError:
            self.products = [{'id': defaults[i], 'name': f"品{i+1}", 'price': '10000', 'desc': ''} for i in range(self.product_count)]
            upgraded = True

        if upgraded:
            self.save_products_to_csv()

        # 旧画像ファイルがあればID形式にコピー
        self._migrate_index_images_to_id()

    def save_products_to_csv(self):
        with open(self._p_setting('products.csv'), 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'name', 'price', 'desc']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in self.products:
                writer.writerow({'id': product.get('id', ''), 'name': product.get('name', ''), 'price': product.get('price', ''), 'desc': product.get('desc', '')})


    def load_shop_name(self):
        try:
            with open(self._p_setting("shop_name.txt"), "r", encoding="utf-8") as f:
                self.shop_name_entry.insert(0, f.read().strip())
        except FileNotFoundError:
            pass

    def save_shop_name(self):
        with open(self._p_setting("shop_name.txt"), "w", encoding="utf-8") as f:
            f.write(self.shop_name_entry.get().strip())

    def load_persistent_text(self):
        try:
            with open(self._p_setting("persistent_text.txt"), "r", encoding="utf-8") as f:
                self.persistent_text_entry.insert(0, f.read().strip())
        except FileNotFoundError:
            pass

    def save_persistent_text(self):
        with open(self._p_setting("persistent_text.txt"), "w", encoding="utf-8") as f:
            f.write(self.persistent_text_entry.get().strip())

    def save_management_changes(self):
        cur_tab_text = self._get_selected_tab_text()
        self.save_shop_name()
        self.save_persistent_text()
        current_time = datetime.now()
        date_str = current_time.strftime("%y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        new_products = []
        seen = set()
        for i, (id_entry, name_entry, price_entry, desc_entry) in enumerate(self.management_entries):
            pid = self._sanitize_product_id(id_entry.get())
            if not pid:
                messagebox.showwarning("警告", f"商品 {i+1} のIDが無効です。英数字3文字で入力してください。例: f01")
                return
            if pid in seen:
                messagebox.showwarning("警告", f"商品IDが重複しています: {pid}")
                return
            seen.add(pid)

            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", f"商品 {i+1} の名前を入力してください。")
                return

            price = price_entry.get().strip()
            if not price.isdigit():
                messagebox.showwarning("警告", f"商品 {i+1} の価格が無効です。整数で入力してください。")
                return

            desc = self._get_desc_value(desc_entry)  # 空欄OK

            new_products.append({"id": pid, "name": name, "price": price, "desc": desc})

        self.products = new_products
        self.save_products_to_csv()

        # カタログ更新（過去設定として保存）
        if not hasattr(self, 'product_catalog'):
            self.product_catalog = {}
        for p in self.products:
            self.product_catalog[p['id']] = {'name': p['name'], 'price': p['price'], 'desc': p.get('desc', '')}
        self.save_product_catalog()

        management_log_entry = [date_str, time_str] + [f"{p['id']}:{p['name']}:{p['price']}" for p in self.products]
        self.append_management_log_to_csv(management_log_entry)

        self.setup_log_tab()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()
        self._reorder_tabs()
        self.setup_customer_tab()
        self._reorder_tabs()
        messagebox.showinfo("成功", "商品の設定が更新されました。")
        self._select_tab_by_text(cur_tab_text)

    def append_management_log_to_csv(self, log_entry):
        with open(self._p_log("management_log.csv"), "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)

    def update_product_count(self):
        cur_tab_text = self._get_selected_tab_text()
        new_count_str = self.product_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "商品数には1以上の整数を入力してください。")
            return

        new_count = int(new_count_str)
        self.product_count = new_count
        self.save_product_count_to_csv()

        self.load_products_from_csv()
        self.load_product_catalog()
        self.product_counts = [0] * self.product_count
        self.product_images = [None] * self.product_count

        # カラム数を整合させる
        self._normalize_column_counts(default_reset=True)
        self.save_column_counts()

        self.update_window_size()
        self.setup_log_tab()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()
        self._reorder_tabs()
        self.setup_customer_tab()
        self._reorder_tabs()

        messagebox.showinfo("成功", "商品数が更新されました。")
        self._select_tab_by_text(cur_tab_text)

    def update_qualification_count(self):
        cur_tab_text = self._get_selected_tab_text()
        new_count_str = self.qualification_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "資格数には1以上の整数を入力してください。")
            return

        new_count = int(new_count_str)
        self.qualification_count = new_count
        self.save_qualification_count_to_csv()

        self.load_qualifications_from_csv()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()
        self._reorder_tabs()
        messagebox.showinfo("成功", "資格数が更新されました。")
        self._select_tab_by_text(cur_tab_text)

    def load_qualifications_from_csv(self):
        try:
            with open(self._p_setting("qualifications.csv"), "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.qualifications = [row for row in reader]

                while len(self.qualifications) < self.qualification_count:
                    self.qualifications.append({"name": f"資格 {len(self.qualifications) + 1}", "discount": "0"})

                self.qualifications = self.qualifications[: self.qualification_count]

        except FileNotFoundError:
            self.qualifications = [{"name": f"資格 {i+1}", "discount": "0"} for i in range(self.qualification_count)]
            self.save_qualifications_to_csv()

    def save_qualifications_to_csv(self):
        with open(self._p_setting("qualifications.csv"), "w", newline="", encoding="utf-8") as f:
            fieldnames = ["name", "discount"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for qualification in self.qualifications:
                writer.writerow(qualification)

    def save_qualification_changes(self):
        cur_tab_text = self._get_selected_tab_text()
        current_time = datetime.now()
        date_str = current_time.strftime("%y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        new_qualifications = []
        for i, (name_entry, discount_entry) in enumerate(self.qualification_entries):
            name = name_entry.get().strip()
            discount = discount_entry.get().strip()
            if not name or not discount.isdigit():
                messagebox.showwarning("警告", f"資格 {i+1} の名前または割引率が無効です。")
                return
            new_qualifications.append({"name": name, "discount": discount})

        self.qualifications = new_qualifications
        self.save_qualifications_to_csv()

        qualification_log_entry = [date_str, time_str] + [f"{q['name']}:{q['discount']}%" for q in self.qualifications]
        self.append_qualification_log_to_csv(qualification_log_entry)

        self.setup_register_tab()
        self._reorder_tabs()
        messagebox.showinfo("成功", "資格の設定が更新されました。")
        self._select_tab_by_text(cur_tab_text)

    def append_qualification_log_to_csv(self, log_entry):
        with open(self._p_log("qualification_log.csv"), "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)

    # ----------------------------
    # Clipboard / Restore / Clear
    # ----------------------------
    def copy_name_and_message(self):
        # お手紙コピー：先頭の「[name]さん、」や「<実名>さん、」は不要なので、本文のみコピーする
        message = self.persistent_text_entry.get().strip()
        # 念のため、テンプレに含まれている場合は除去
        for pat in ("[name]さん、", "[name]さん,", "[name]さん"):
            if message.startswith(pat):
                message = message[len(pat):].lstrip(" \t\n\r")
        # 以前の仕様で先頭に付けていた「<名前>さん、」が残っている場合も除去
        try:
            name = self.name_var.get().strip() if hasattr(self, 'name_var') else ''
        except Exception:
            name = ''
        if name:
            for pat in (f"{name}さん、", f"{name}さん,"):
                if message.startswith(pat):
                    message = message[len(pat):].lstrip(" \t\n\r")
        self.root.clipboard_clear()
        self.root.clipboard_append(f"{message}")
        self.root.update()

    def copy_total_price(self):
        # 数字だけコピー（例: 1234）
        try:
            total = sum(int(c) * int(p.get('price', 0)) for c, p in zip(self.product_counts, self.products))
        except Exception:
            total = 0

        qualification_name = self.qualification_var.get() if hasattr(self, 'qualification_var') else ''
        qualification = next((q for q in self.qualifications if q.get('name') == qualification_name), None)
        try:
            discount_rate = int(qualification.get('discount', 0)) if qualification else 0
        except Exception:
            discount_rate = 0

        final_total = int(total - (total * (discount_rate / 100)))
        self.root.clipboard_clear()
        self.root.clipboard_append(str(final_total))
        self.root.update()

    def copy_shop_name(self):
        shop_name = self.shop_name_entry.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(shop_name)
        self.root.update()

    def restore_from_history(self):
        if not messagebox.askyesno("確認", "現在のレジ内容が消えますが、よろしいですか？"):
            return

        if not self.log_tree.get_children():
            messagebox.showwarning("警告", "履歴が空です。")
            return

        last_log = self.log_tree.item(self.log_tree.get_children()[-1])["values"]
        last_survey = self.survey_tree.item(self.survey_tree.get_children()[-1])["values"]

        # log: [date,time,customer,qualification,total] + counts + [items_total,breakdown]
        cust_disp = str(last_log[2])
        _, name = self._parse_customer_display(cust_disp)
        self.name_var.set(name)
        self.qualification_var.set(str(last_log[3]))

        # survey: [date,time,customer,qualification,survey,remarks]
        self.survey_var.set(str(last_survey[4]))

        self.remarks_entry.delete(0, tk.END)
        self.remarks_entry.insert(0, str(last_survey[5]))

        for i in range(len(self.products)):
            self.product_counts[i] = int(last_log[5 + i])
            ent = self.entries[i]
            ent.state(["!readonly"])
            ent.delete(0, tk.END)
            ent.insert(0, str(self.product_counts[i]))
            ent.state(["readonly"])

        self.update_total_price()

    def clear_register(self):
        if not messagebox.askyesno("確認", "現在のレジ内容が消えますが、よろしいですか？"):
            return

        self.name_var.set("")
        self.remarks_entry.delete(0, tk.END)
        self.survey_menu.current(0)
        self.qualification_menu.current(0)
        for i in range(len(self.products)):
            self.clear_count(i)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductCounterApp(root)
    root.mainloop()

