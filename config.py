"""
設定ファイル
環境変数やアプリケーション設定を管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).parent

# データベース設定
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'ec_companies.db'))

# スクレイピング設定
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))  # リクエスト間隔（秒）
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))  # タイムアウト（秒）
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))  # 最大リトライ回数
USER_AGENT = os.getenv(
    'USER_AGENT',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# ログ設定
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))

# ディレクトリの作成
(BASE_DIR / 'logs').mkdir(exist_ok=True)
(BASE_DIR / 'data').mkdir(exist_ok=True)
(BASE_DIR / 'data' / 'exports').mkdir(exist_ok=True)

