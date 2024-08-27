import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import csv
from datetime import datetime

"""
############################################################
# プログラム名: PointGuiSale
# バージョン: 1.0.0
# 制作日: 2024年8月27日
# 制作者: VWRoent（紫波レント）
# 使用技術: ChatGPT-4o
# GitHub : https://github.com/VWRoent/PointGuiSale
# YouTube: https://www.youtube.com/@VioWaveRoentgen
# Twitter: https://x.com/VioWaveRoentgen
############################################################
"""

class ProductCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PointGuiSale")
        
        # 初期設定：商品数、資格数、およびデータの読み込み
        self.load_product_count()
        self.load_products_from_csv()
        self.load_qualification_count()
        self.load_qualifications_from_csv()
        self.load_question_responses()
        self.load_image_scale()
        self.load_survey_count()
        
        self.product_counts = [0] * self.product_count
        self.product_images = [None] * self.product_count  # 画像を格納するリスト

        # デフォルトのウィンドウサイズの初期化
        self.default_width = 500
        self.default_height = 260 + (20 + 20 * self.image_scale) * len(self.products)
        self.update_window_size()

        self.setup_tabs()
        self.load_survey_from_csv() 
        self.update_total_price()

        # ウィンドウのサイズ変更を許可

        self.root.resizable(True, True)

    def load_image_scale(self):
        """画像倍率設定の読み込み"""
        try:
            with open("image_scale.txt", "r") as f:
                self.image_scale = int(f.read().strip())
        except FileNotFoundError:
            self.image_scale = 1  # 初期設定はx1
            self.save_image_scale()

    def save_image_scale(self):
        """画像倍率設定の保存"""
        with open("image_scale.txt", "w") as f:
            f.write(str(self.image_scale))

    def load_product_count(self):
        try:
            with open("product_count.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.product_count = int(next(reader)[0])
        except FileNotFoundError:
            self.product_count = 6  # 初期値
            self.save_product_count_to_csv()

    def load_survey_count(self):
        try:
            with open("survey_count.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.survey_count = int(next(reader)[0])
        except FileNotFoundError:
            self.survey_count = 3  # 初期値
            self.save_survey_count_to_csv()
    
    def save_product_count_to_csv(self):
        with open("product_count.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.product_count])

    def save_survey_count_to_csv(self):
        with open("survey_count.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.survey_count])

    def load_qualification_count(self):
        try:
            with open("qualification_count.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.qualification_count = int(next(reader)[0])
        except FileNotFoundError:
            self.qualification_count = 3  # 初期値
            self.save_qualification_count_to_csv()
    
    def save_qualification_count_to_csv(self):
        with open("qualification_count.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([self.qualification_count])

    def load_question_responses(self):
        try:
            with open("question_responses.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.survey_responses = [row[0] for row in reader]
        except FileNotFoundError:
            self.survey_responses = ["未回答", "回答1", "回答2"]  # 初期値
            self.save_question_responses_to_csv()

    def save_question_responses_to_csv(self):
        with open("question_responses.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for response in self.survey_responses:
                writer.writerow([response])
    
    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.setup_log_tab()
        self.setup_survey_tab()  # 新しいアンケートタブのセットアップ
        self.setup_question_tab()  # 新しい質問タブのセットアップ
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()

    def setup_register_tab(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.destroy()
        
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="レジ")
        
        # 名前入力
        name_frame = tk.Frame(self.register_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(name_frame, text="名前:").pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, width=23)
        self.name_entry.pack(side=tk.LEFT, padx=10)

        # 備考入力フィールド
        tk.Label(name_frame, text="備考:").pack(side=tk.LEFT)
        self.remarks_entry = tk.Entry(name_frame, width=35)
        self.remarks_entry.pack(side=tk.LEFT, padx=10)

        quali_frame = tk.Frame(self.register_frame)
        quali_frame.pack(fill=tk.X, padx=5, pady=5)

        # 資格のプルダウンメニュー
        tk.Label(quali_frame, text="資格:").pack(side=tk.LEFT)
        self.qualification_var = tk.StringVar()
        self.qualification_menu = ttk.Combobox(quali_frame, textvariable=self.qualification_var, state="readonly")
        self.qualification_menu['values'] = [q['name'] for q in self.qualifications]
        self.qualification_menu.current(0)
        self.qualification_menu.pack(side=tk.LEFT, padx=10)
        self.qualification_var.trace("w", self.update_total_price)

        # アンケートのチェックボックス
        tk.Label(quali_frame, text="質問:").pack(side=tk.LEFT)
        self.survey_var = tk.StringVar()
        self.survey_menu = ttk.Combobox(quali_frame, textvariable=self.survey_var, state="readonly")
        self.survey_menu['values'] = self.survey_responses
        self.survey_menu.current(0)
        self.survey_menu.pack(side=tk.LEFT, padx=10)

        send_frame = tk.Frame(self.register_frame)
        send_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(send_frame, text="請求額の取得", command=self.copy_total_price).pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="店舗名の取得", command=self.copy_shop_name).pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="お手紙の取得", command=self.copy_name_and_message).pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="内容を送信", command=self.save_log).pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="内容を復元", command=self.restore_from_history).pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="クリア", command=self.clear_register).pack(side=tk.LEFT, padx=5)

        
        # 請求額の金額表示       
        self.final_label = tk.Label(self.register_frame, text="請求額: 0円", font=("Helvetica", 32))
        self.final_label.pack(pady=1)
        
        # 割引額の金額表示
        self.discount_label = tk.Label(self.register_frame, text="割引額: 0円", font=("Helvetica", 14))
        self.discount_label.pack(pady=5)
        
        self.entries = []
        for i, product in enumerate(self.products):
            frame = tk.Frame(self.register_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)

            label = tk.Label(frame, text=product['name'], width=15)
            label.pack(side=tk.LEFT)
            
            # 画像表示
            image_label = tk.Label(frame, relief=tk.RAISED)
            image_label.pack(side=tk.LEFT)
            self.product_images[i] = image_label
            self.update_product_image(i)
            
            entry = tk.Entry(frame, width=5, justify='center')
            entry.insert(0, "0")
            entry.config(state='readonly')
            entry.pack(side=tk.LEFT, padx=10)
            self.entries.append(entry)
            
            btn_frame = tk.Frame(frame)
            btn_frame.pack(side=tk.LEFT, padx=10)
            
            tk.Button(btn_frame, text="+1", command=lambda i=i: self.update_count(i, 1)).pack(side=tk.LEFT)
            tk.Button(btn_frame, text="+5", command=lambda i=i: self.update_count(i, 5)).pack(side=tk.LEFT)
            tk.Button(btn_frame, text="+10", command=lambda i=i: self.update_count(i, 10)).pack(side=tk.LEFT)
            tk.Label(btn_frame, text="   ").pack(side=tk.LEFT)
            tk.Button(btn_frame, text="-1", command=lambda i=i: self.update_count(i, -1)).pack(side=tk.LEFT)
            tk.Button(btn_frame, text="-5", command=lambda i=i: self.update_count(i, -5)).pack(side=tk.LEFT)
            tk.Button(btn_frame, text="-10", command=lambda i=i: self.update_count(i, -10)).pack(side=tk.LEFT)
            tk.Label(btn_frame, text="   ").pack(side=tk.LEFT)
            tk.Button(btn_frame, text="クリア", command=lambda i=i: self.clear_count(i)).pack(side=tk.LEFT)
        
        # 合計金額表示
        self.total_label = tk.Label(self.register_frame, text="合計金額: 0円", font=("Helvetica", 16))
        self.total_label.pack(pady=10)

    def setup_log_tab(self):
        if hasattr(self, 'log_frame'):
            self.log_frame.destroy()
        
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="履歴")
        
        # 日付、時刻、名前、資格、請求額のカラムを固定して、その後に商品が続くように設定
        columns = ['date', 'time', 'name', 'qualification', 'total'] + [f'product{i+1}' for i in range(self.product_count)]
        self.log_tree = ttk.Treeview(self.log_frame, columns=columns, show='headings')
        self.log_tree.pack(fill=tk.BOTH, expand=True)
        
        # ヘッダーの設定
        self.log_tree.heading('date', text='日付')
        self.log_tree.heading('time', text='時刻')
        self.log_tree.heading('name', text='名前')
        self.log_tree.heading('qualification', text='資格')
        self.log_tree.heading('total', text='請求')
        for i, product in enumerate(self.products):
            self.log_tree.heading(f'product{i+1}', text=product['name'])
        
        # 列の幅を調整
        self.log_tree.column('date', width=22)
        self.log_tree.column('time', width=20)
        self.log_tree.column('name', width=20)
        self.log_tree.column('qualification', width=20)
        self.log_tree.column('total', width=20)
        for i in range(self.product_count):
            self.log_tree.column(f'product{i+1}', width=20)
        
        # CSVから履歴を読み込む
        self.load_log_from_csv()

    def setup_survey_tab(self):
        if hasattr(self, 'survey_frame'):
            self.survey_frame.destroy()

        self.survey_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.survey_frame, text="回答")

        columns = ['date', 'time', 'name', 'qualification', 'survey', 'remarks']
        self.survey_tree = ttk.Treeview(self.survey_frame, columns=columns, show='headings')
        self.survey_tree.pack(fill=tk.BOTH, expand=True)

        # ヘッダーの設定
        self.survey_tree.heading('date', text='日付')
        self.survey_tree.heading('time', text='時刻')
        self.survey_tree.heading('name', text='名前')
        self.survey_tree.heading('qualification', text='資格')
        self.survey_tree.heading('survey', text='回答')
        self.survey_tree.heading('remarks', text='備考')

        self.survey_tree.column('date', width=22)
        self.survey_tree.column('time', width=20)
        self.survey_tree.column('name', width=20)
        self.survey_tree.column('qualification', width=20)
        self.survey_tree.column('survey', width=20)
        self.survey_tree.column('remarks', width=50)
        
        self.load_survey_from_csv()

    def load_survey_from_csv(self):
        for item in self.survey_tree.get_children():
            self.survey_tree.delete(item)
        try:
            with open("survey_log.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    self.survey_tree.insert("", "end", values=row)
        except FileNotFoundError:
            pass

    def append_survey_to_csv(self, survey_entry):
        with open("survey_log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(survey_entry)

    def setup_question_tab(self):
        if hasattr(self, 'question_frame'):
            self.question_frame.destroy()

        self.question_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.question_frame, text="質問")

        # 質問の数の設定
        count_frame = tk.Frame(self.question_frame)
        count_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(count_frame, text="質問数:").pack(side=tk.LEFT)
        self.question_count_entry = tk.Entry(count_frame, width=10)
        self.question_count_entry.insert(0, str(len(self.survey_responses)))
        self.question_count_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(count_frame, text="質問数を更新", command=self.update_question_count).pack(side=tk.LEFT)

        # 質問名の入力フィールド
        self.question_entries = []
        for i, question in enumerate(self.survey_responses):
            frame = tk.Frame(self.question_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(frame, text=f"質問 {i+1}").pack(side=tk.LEFT)
            
            question_entry = tk.Entry(frame, width=15)
            question_entry.insert(0, question)
            question_entry.pack(side=tk.LEFT, padx=5)
            
            self.question_entries.append(question_entry)

        tk.Button(self.question_frame, text="決定", command=self.save_question_changes).pack(pady=20)

    def update_question_count(self):
        new_count_str = self.question_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "質問数には1以上の整数を入力してください。")
            return

        new_count = int(new_count_str)
        current_questions = self.survey_responses

        if new_count > len(current_questions):
            # 質問数が増えた場合、新しい質問を追加
            new_questions = current_questions + [f'質問 {i+1}' for i in range(len(current_questions), new_count)]
        else:
            # 質問数が減った場合、余分な質問を削除
            new_questions = current_questions[:new_count]

        self.survey_responses = new_questions
        self.save_question_responses_to_csv()
        self.setup_question_tab()  # 質問タブを再セットアップして、新しい質問数を反映

    def save_question_changes(self):
        new_questions = [entry.get().strip() for entry in self.question_entries]
        
        if not all(new_questions):
            messagebox.showwarning("警告", "全ての質問名を入力してください。")
            return

        self.survey_responses = new_questions
        self.save_question_responses_to_csv()
        self.setup_register_tab()  # 質問の変更を反映するため、再度レジタブをセットアップ
        messagebox.showinfo("成功", "質問が更新されました。")

    def setup_management_tab(self):
        if hasattr(self, 'management_frame'):
            self.management_frame.destroy()
        
        self.management_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.management_frame, text="管理")

        # 店名の入力フィールド
        shop_name_frame = tk.Frame(self.management_frame)
        shop_name_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(shop_name_frame, text="店舗名:").pack(side=tk.LEFT)
        self.shop_name_entry = tk.Entry(shop_name_frame, width=50)
        self.shop_name_entry.pack(side=tk.LEFT, padx=10)
        self.load_shop_name()
    
        # 維持されるテキストボックスの追加
        persistent_text_frame = tk.Frame(self.management_frame)
        persistent_text_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(persistent_text_frame, text="お手紙:").pack(side=tk.LEFT)
        self.persistent_text_entry = tk.Entry(persistent_text_frame, width=50)
        self.persistent_text_entry.pack(side=tk.LEFT, padx=10)
        self.load_persistent_text()
        
        # 商品数の入力フィールドと更新ボタン
        count_frame = tk.Frame(self.management_frame)
        count_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(count_frame, text="商品数:").pack(side=tk.LEFT)
        self.product_count_entry = tk.Entry(count_frame, width=10)
        self.product_count_entry.insert(0, str(self.product_count))
        self.product_count_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(count_frame, text="商品数を更新", command=self.update_product_count).pack(side=tk.LEFT)
        
        # 画像サイズ変更ボタン
        size_frame = tk.Frame(self.management_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(size_frame, text="画像サイズ:").pack(side=tk.LEFT)
        tk.Button(size_frame, text="x1", command=lambda: self.change_image_size(1)).pack(side=tk.LEFT)
        tk.Button(size_frame, text="x2", command=lambda: self.change_image_size(2)).pack(side=tk.LEFT)
        tk.Button(size_frame, text="x3", command=lambda: self.change_image_size(3)).pack(side=tk.LEFT)

        # 商品名、価格、画像の入力フィールド
        self.management_entries = []
        for i, product in enumerate(self.products):
            frame = tk.Frame(self.management_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(frame, text=f"商品_{i+1}").pack(side=tk.LEFT, padx=10)

            # 画像表示
            image_label = tk.Label(frame, relief=tk.RAISED)
            image_label.pack(side=tk.LEFT, padx=10)
            self.product_images[i] = image_label
            self.update_product_image(i)
            
            name_entry = tk.Entry(frame, width=15)
            name_entry.insert(0, product['name'])
            name_entry.pack(side=tk.LEFT, padx=10)
            
            price_entry = tk.Entry(frame, width=10)
            price_entry.insert(0, product['price'])
            price_entry.pack(side=tk.LEFT, padx=10)
            
            image_button = tk.Button(frame, text="画像選択", command=lambda i=i: self.select_image(i))
            image_button.pack(side=tk.LEFT, padx=5)
            
            self.management_entries.append((name_entry, price_entry))
        
        tk.Button(self.management_frame, text="決定", command=self.save_management_changes).pack(pady=20)

    def change_image_size(self, scale):
        self.image_scale = scale
        self.save_image_scale()
        self.update_window_size()
        self.setup_management_tab()
        self.setup_register_tab()

    def update_window_size(self):
        # 商品数と選択された画像サイズに基づいてウィンドウサイズを更新
        self.default_height = 260 + (20 + 20 * self.image_scale) * len(self.products)
        self.root.geometry(f"{self.default_width}x{self.default_height}")

    def setup_qualification_tab(self):
        if hasattr(self, 'qualification_frame'):
            self.qualification_frame.destroy()
        
        self.qualification_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.qualification_frame, text="資格")
        
        # 資格数の入力フィールドと更新ボタン
        count_frame = tk.Frame(self.qualification_frame)
        count_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(count_frame, text="資格数:").pack(side=tk.LEFT)
        self.qualification_count_entry = tk.Entry(count_frame, width=10)
        self.qualification_count_entry.insert(0, str(self.qualification_count))
        self.qualification_count_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(count_frame, text="資格数を更新", command=self.update_qualification_count).pack(side=tk.LEFT)
        
        # 資格名と割引率の入力フィールド
        self.qualification_entries = []
        for i, qualification in enumerate(self.qualifications):
            frame = tk.Frame(self.qualification_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(frame, text=f"資格 {i+1}").pack(side=tk.LEFT)
            
            name_entry = tk.Entry(frame, width=15)
            name_entry.insert(0, qualification['name'])
            name_entry.pack(side=tk.LEFT, padx=5)
            
            discount_entry = tk.Entry(frame, width=10)
            discount_entry.insert(0, qualification['discount'])
            discount_entry.pack(side=tk.LEFT, padx=5)
            
            self.qualification_entries.append((name_entry, discount_entry))
        
        tk.Button(self.qualification_frame, text="決定", command=self.save_qualification_changes).pack(pady=20)
    
    def select_image(self, index):
        filepath = filedialog.askopenfilename(
            filetypes=[("PNG Images", "*.png")],
            title="画像を選択"
        )
        if filepath:
            image_dir = "images"
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            image_path = os.path.join(image_dir, f"image{index+1}.png")
            Image.open(filepath).save(image_path)  # 選択された画像をコピー
            
            # レジタブの画像を更新
            self.update_product_image(index)
            self.setup_management_tab()
            self.setup_register_tab()

    def update_product_image(self, index):
        image_dir = "images"
        image_path = os.path.join(image_dir, f"image{index+1}.png")
        if os.path.exists(image_path):
            image = Image.open(image_path)
            size = 20 * self.image_scale
            image = image.resize((size, size), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.product_images[index].config(image=photo, width=size + 4, height=size + 4)
            self.product_images[index].image = photo
        else:
            # 画像がない場合は枠だけ表示
            self.product_images[index].config(image='', relief=tk.RAISED)
    
    def update_count(self, index, delta):
        new_count = max(0, self.product_counts[index] + delta)
        self.product_counts[index] = new_count
        self.entries[index].config(state=tk.NORMAL)
        self.entries[index].delete(0, tk.END)
        self.entries[index].insert(0, str(new_count))
        self.entries[index].config(state='readonly')
        self.update_total_price()
    
    def clear_count(self, index):
        self.product_counts[index] = 0
        self.entries[index].config(state=tk.NORMAL)
        self.entries[index].delete(0, tk.END)
        self.entries[index].insert(0, "0")
        self.entries[index].config(state='readonly')
        self.update_total_price()
    
    def update_total_price(self, *args):
        total = sum(count * int(product['price']) for count, product in zip(self.product_counts, self.products))
        qualification_name = self.qualification_var.get()
        qualification = next((q for q in self.qualifications if q['name'] == qualification_name), None)
        discount_rate = int(qualification['discount']) if qualification else 0
        discount = total * (discount_rate / 100)
        final_total = total - discount
        
        self.total_label.config(text=f"合計金額: {total}円")
        self.discount_label.config(text=f"割引額: {int(discount)}円")
        self.final_label.config(text=f"請求額: {int(final_total)}円")
    
    def save_log(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "名前を入力してください。")
            return
        
        qualification = self.qualification_var.get()
        remarks = self.remarks_entry.get().strip()
        survey_response = self.survey_var.get()
        
        current_time = datetime.now()
        date_str = current_time.strftime('%m-%d')
        time_str = current_time.strftime('%H:%M')
        total = sum(count * int(product['price']) for count, product in zip(self.product_counts, self.products))
        discount_rate = int(next((q['discount'] for q in self.qualifications if q['name'] == qualification), 0))
        discount = total * (discount_rate / 100)
        final_total = total - discount
        
        log_entry = [date_str, time_str, name, qualification, int(final_total)] + self.product_counts
        
        # 履歴をTreeviewに追加
        self.log_tree.insert("", "end", values=log_entry)
        
        # 履歴をCSVに保存
        self.append_log_to_csv(log_entry)
        
        # アンケート結果をCSVに保存
        survey_entry = [date_str, time_str, name, qualification, survey_response, remarks]
        self.survey_tree.insert("", "end", values=survey_entry)
        self.append_survey_to_csv(survey_entry)
        
        # 入力をクリア
        self.name_entry.delete(0, tk.END)
        self.remarks_entry.delete(0, tk.END)
        self.survey_menu.current(0)
        self.qualification_menu.current(0)
        for i in range(len(self.products)):
            self.clear_count(i)
    
    def append_log_to_csv(self, log_entry):
        with open("log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)

    def append_survey_to_csv(self, survey_entry):
        with open("survey_log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(survey_entry)
    
    def load_log_from_csv(self):
        try:
            with open("log.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    self.log_tree.insert("", "end", values=row)
        except FileNotFoundError:
            pass
    
    def load_products_from_csv(self):
        try:
            with open("products.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.products = [row for row in reader]
                
                # products.csv が現在の product_count より少ない場合、新しい商品を追加
                while len(self.products) < self.product_count:
                    self.products.append({'name': f'品{len(self.products) + 1}', 'price': '10000'})
                
                # products.csv が現在の product_count より多い場合、余分な商品を削除
                self.products = self.products[:self.product_count]
                
        except FileNotFoundError:
            self.products = [{'name': f'品{i+1}', 'price': '10000'} for i in range(self.product_count)]
            self.save_products_to_csv()
    
    def save_products_to_csv(self):
        with open("products.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ['name', 'price']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in self.products:
                writer.writerow(product)
    
    def load_shop_name(self):
        try:
            with open("shop_name.txt", "r", encoding="utf-8") as f:
                self.shop_name_entry.insert(0, f.read().strip())
        except FileNotFoundError:
            pass
    
    def save_shop_name(self):
        with open("shop_name.txt", "w", encoding="utf-8") as f:
            f.write(self.shop_name_entry.get().strip())

    def load_persistent_text(self):
        try:
            with open("persistent_text.txt", "r", encoding="utf-8") as f:
                self.persistent_text_entry.insert(0, f.read().strip())
        except FileNotFoundError:
            pass
    
    def save_persistent_text(self):
        with open("persistent_text.txt", "w", encoding="utf-8") as f:
            f.write(self.persistent_text_entry.get().strip())
    
    def save_management_changes(self):
        # 店名とテキストの保存
        self.save_shop_name()
        self.save_persistent_text()
        current_time = datetime.now()
        date_str = current_time.strftime('%y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')
        
        new_products = []
        for i, (name_entry, price_entry) in enumerate(self.management_entries):
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", "名前を入力してください。")
                return
            price = price_entry.get().strip()
            if not name or not price.isdigit():
                messagebox.showwarning("警告", f"商品 {i+1} の名前または価格が無効です。")
                return
            new_products.append({'name': name, 'price': price})
        
        self.products = new_products
        self.save_products_to_csv()
        
        management_log_entry = [date_str, time_str] + [f"{p['name']}:{p['price']}" for p in self.products]
        self.append_management_log_to_csv(management_log_entry)
        
        # 商品名と価格の表示を更新
        self.setup_log_tab()       # 商品名の変更を反映するため、履歴タブも再セットアップ
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()  # 商品数が変更された場合に再度レジタブをセットアップ
        messagebox.showinfo("成功", "商品の設定が更新されました。")
    
    def append_management_log_to_csv(self, log_entry):
        with open("management_log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)
    
    def update_product_count(self):
        new_count_str = self.product_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "商品数には1以上の整数を入力してください。")
            return
        
        new_count = int(new_count_str)
        self.product_count = new_count
        self.save_product_count_to_csv()
        
        # すべてのタブを再構築
        self.load_products_from_csv()
        self.product_counts = [0] * self.product_count
        self.product_images = [None] * self.product_count
        
        self.update_window_size()  # 商品数変更時にウィンドウサイズを更新
        self.setup_log_tab()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()
        
        messagebox.showinfo("成功", "商品数が更新されました。")
    
    def update_qualification_count(self):
        new_count_str = self.qualification_count_entry.get().strip()
        if not new_count_str.isdigit() or int(new_count_str) < 1:
            messagebox.showwarning("警告", "資格数には1以上の整数を入力してください。")
            return
        
        new_count = int(new_count_str)
        self.qualification_count = new_count
        self.save_qualification_count_to_csv()
        
        # 資格情報の再設定
        self.load_qualifications_from_csv()
        self.setup_qualification_tab()
        self.setup_management_tab()
        self.setup_register_tab()  # 資格数が変更された場合に再度レジタブをセットアップ
        
        messagebox.showinfo("成功", "資格数が更新されました。")
    
    def load_qualifications_from_csv(self):
        try:
            with open("qualifications.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.qualifications = [row for row in reader]
                
                # qualifications.csv が現在の qualification_count より少ない場合、新しい資格を追加
                while len(self.qualifications) < self.qualification_count:
                    self.qualifications.append({'name': f'資格 {len(self.qualifications) + 1}', 'discount': '0'})
                
                # qualifications.csv が現在の qualification_count より多い場合、余分な資格を削除
                self.qualifications = self.qualifications[:self.qualification_count]
                
        except FileNotFoundError:
            self.qualifications = [{'name': f'資格 {i+1}', 'discount': '0'} for i in range(self.qualification_count)]
            self.save_qualifications_to_csv()
    
    def save_qualifications_to_csv(self):
        with open("qualifications.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ['name', 'discount']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for qualification in self.qualifications:
                writer.writerow(qualification)
    
    def save_qualification_changes(self):
        current_time = datetime.now()
        date_str = current_time.strftime('%y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')
        
        new_qualifications = []
        for i, (name_entry, discount_entry) in enumerate(self.qualification_entries):
            name = name_entry.get().strip()
            discount = discount_entry.get().strip()
            if not name or not discount.isdigit():
                messagebox.showwarning("警告", f"資格 {i+1} の名前または割引率が無効です。")
                return
            new_qualifications.append({'name': name, 'discount': discount})
        
        self.qualifications = new_qualifications
        self.save_qualifications_to_csv()
        
        qualification_log_entry = [date_str, time_str] + [f"{q['name']}:{q['discount']}%" for q in self.qualifications]
        self.append_qualification_log_to_csv(qualification_log_entry)
        
        # 資格名と割引額の表示を更新
        self.setup_register_tab()  # 資格の変更を反映するため、再度レジタブをセットアップ
        
        messagebox.showinfo("成功", "資格の設定が更新されました。")
    
    def append_qualification_log_to_csv(self, log_entry):
        with open("qualification_log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(log_entry)
    
    def copy_name_and_message(self):
        name = self.name_entry.get().strip()
        message = self.persistent_text_entry.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(f"{name}さん、{message}")
        self.root.update()
        
    def copy_total_price(self):
        total_price = self.final_label.cget("text")
        self.root.clipboard_clear()
        self.root.clipboard_append(total_price)
        self.root.update()
    
    def copy_shop_name(self):
        shop_name = self.shop_name_entry.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(shop_name)
        self.root.update()

    def restore_from_history(self):
        # 警告ダイアログの表示
        if messagebox.askyesno("確認", "現在のレジ内容が消えますが、よろしいですか？"):
            # 最後の履歴を取得
            if not self.log_tree.get_children():
                messagebox.showwarning("警告", "履歴が空です。")
                return
    
            last_log = self.log_tree.item(self.log_tree.get_children()[-1])['values']
            last_survey = self.survey_tree.item(self.survey_tree.get_children()[-1])['values']
    
            # 名前、資格、アンケート回答、備考の復元
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, last_log[2])
    
            self.qualification_var.set(last_log[3])
    
            self.survey_var.set(last_survey[4])
    
            self.remarks_entry.delete(0, tk.END)
            self.remarks_entry.insert(0, last_survey[5])

            # 商品の数量の復元
            for i in range(len(self.products)):
                self.product_counts[i] = int(last_log[5 + i])
                self.entries[i].config(state=tk.NORMAL)
                self.entries[i].delete(0, tk.END)
                self.entries[i].insert(0, str(self.product_counts[i]))
                self.entries[i].config(state='readonly')

            # 合計金額と割引額の更新
            self.update_total_price()
        else:
            # 「戻る」を選んだ場合は何もせずに終了
            return

    def clear_register(self):
        # 警告ダイアログの表示
        if messagebox.askyesno("確認", "現在のレジ内容が消えますが、よろしいですか？"):
    
            # 入力をクリア
            self.name_entry.delete(0, tk.END)
            self.remarks_entry.delete(0, tk.END)
            self.survey_menu.current(0)  # 質問を「未回答」にリセット
            self.qualification_menu.current(0)  # 資格を「資格 1」にリセット
            for i in range(len(self.products)):
                self.clear_count(i)
        else:
            # 「戻る」を選んだ場合は何もせずに終了
            return


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductCounterApp(root)
    root.mainloop()
