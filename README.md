# PointGuiSale

## 概要

**PointGuiSale**は、GUIベースの販売管理アプリケーションです。このアプリケーションは、商品の管理、販売履歴の記録、アンケート機能を提供します。各商品の画像表示や資格に応じた割引計算が可能で、履歴やアンケート結果をCSVファイルに保存することができます。

## 特徴

- **商品管理**: 商品名、価格、画像を管理し、商品の数量を簡単に調整できます。
- **資格割引機能**: 資格に応じた割引率を設定し、合計金額に反映させることができます。
- **履歴管理**: 販売履歴を記録し、再起動後も履歴を参照可能です。
- **アンケート機能**: 購入時にアンケートを設定し、顧客のフィードバックを収集します。
- **ウィンドウサイズの調整**: 商品数や画像サイズに応じてウィンドウサイズが自動的に調整されます。

## 必要条件

- Python 3.x
- `tkinter` (Python標準ライブラリ)
- `PIL` (Python Imaging Library)

## インストール

Windowsの場合は下記のようにアプリケーションをセットアップしてください。

1. 右上の緑色ボタンの <> CodeのDownload ZIPからPointGuiSaleをダウンロードします。

2. PointGuiSale-mainを解凍(展開)します。

3. PointGuiSale.exeをダブルクリックします。

CUIで起動する場合は下記のようにアプリケーションをセットアップしてください。

1. リポジトリをクローンまたはダウンロードします。
   ```bash
   git clone https://github.com/VWRoent/PointGuiSale.git
   ```

2. 必要なライブラリをインストールします。
   ```bash
   pip install pillow
   ```

3. プログラムを実行します。
   ```bash
   python PointGuiSale.py
   ```

## 使い方

1. PointGuiSale.exeをダブルクリックして、アプリケーションを起動します。

2. **管理タブ**で、商品名、価格、および画像を設定します。必要に応じて商品数を更新してください。

![image](https://github.com/user-attachments/assets/8ed92f30-bda4-4a61-b792-321c12842dfd)

3. **資格タブ**で、資格名と割引率を設定します。資格数を変更することも可能です。

![image](https://github.com/user-attachments/assets/41731cf3-df9b-4f5d-9eb1-f289bac71223)

4. **レジタブ**で、顧客の名前、資格、購入する商品の数量を入力します。請求額が自動的に計算されます。

![image](https://github.com/user-attachments/assets/694cba92-ff1a-4318-98fc-18671c474994)

5. **質問タブ**で、アンケートの回答を設定します。資格数を変更することも可能です。

![image](https://github.com/user-attachments/assets/442d84e4-111a-4b50-a59b-5a7650cefd8f)

6. **回答タブ**で、アンケート結果を確認することができます。過去のアンケート結果はここに保存されます。

![image](https://github.com/user-attachments/assets/f9ff0c28-4d6e-4b15-b704-3295174f1538)

7. **履歴タブ**で、過去の販売履歴を確認することができます。

![image](https://github.com/user-attachments/assets/c87f4be2-f1bc-4145-a450-fe88e8f796ee)

8. 必要に応じて、内容を保存または復元することができます。

## ダウンロードされるファイル

- `PointGuiSale.exe`: メインの実行ファイル (Windows用)。
- `PointGuiSale.py`: メインのPythonスクリプト。
- `PGS_examle.zip`: チュートリアルと同じ設定の例。
- `README.md`: 本マニュアル。

## 生成されるファイル

- `products.csv`: 商品情報を保存するCSVファイル。
- `qualifications.csv`: 資格情報を保存するCSVファイル。
- `log.csv`: 販売履歴を保存するCSVファイル。
- `survey_log.csv`: アンケート結果を保存するCSVファイル。
- `images/`: 商品画像を保存するディレクトリ。

## 開発者情報

- **制作者**: VWRoent（紫波レント）
- **使用技術**: ChatGPT-4o
- **バージョン**: 1.0.0
- **制作日**: 2024年8月27日

## ライセンス

このプロジェクトは、[MITライセンス](LICENSE)のもとで公開されています。
