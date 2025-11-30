# EC Data Scraper

通販事業所データをWebから取得するPythonプログラム

## 概要

本プロジェクトは、通販（EC）事業に関連する事業所の情報をWebから自動的に収集し、構造化されたデータとして保存・管理するPythonプログラムです。

## 機能

- Webから通販事業所データの取得
- データの整形・正規化
- SQLiteデータベースへの保存
- CSV/Excel形式でのエクスポート
- ログ機能
- エラーハンドリング

## システム要件

- Python 3.8以上（推奨: 3.10以上）
- 必要なライブラリは `requirements.txt` を参照

## インストール

```bash
# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な使い方

```bash
# データを取得してデータベースに保存
python main.py scrape <URL1,URL2,...>

# データをCSV形式でエクスポート
python main.py export csv

# データをExcel形式でエクスポート
python main.py export excel

# データベースの統計情報を表示
python main.py stats

# サマリーレポートを出力
python main.py report
```

### 設定

`.env`ファイルを作成して、必要に応じて設定を変更できます。
`.env.example`を参考にしてください。

詳細は `詳細仕様書.md` を参照してください。

## プロジェクト構成

```
ec-data-scraper/
├── main.py                 # メインスクリプト
├── config.py               # 設定ファイル
├── scraper.py              # データ取得モジュール
├── data_processor.py       # データ整形モジュール
├── database.py             # データベース操作モジュール
├── exporter.py             # データエクスポートモジュール
├── utils.py                # ユーティリティ関数
├── requirements.txt        # 依存パッケージ一覧
├── .env.example            # 環境変数テンプレート
├── README.md               # 本ファイル
├── 詳細仕様書.md            # 詳細仕様書
├── logs/                   # ログファイル保存ディレクトリ
├── data/                   # データ保存ディレクトリ
└── tests/                  # テストコード
```

## 注意事項

- スクレイピングを行う際は、対象サイトの`robots.txt`や利用規約を確認してください
- サーバーへの負荷を考慮し、適切な間隔でリクエストを送信してください
- 取得したデータの利用目的が対象サイトの利用規約に違反しないことを確認してください

## ライセンス

[ライセンス情報を記載]

## 作成者

[作成者情報を記載]

