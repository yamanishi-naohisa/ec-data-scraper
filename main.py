"""
メインスクリプト
通販事業所データ取得システムのエントリーポイント
"""
import logging
import sys
from pathlib import Path
from typing import List, Optional
import config
from database import DatabaseManager
from scraper import WebScraper
from data_processor import DataProcessor
from exporter import DataExporter


def setup_logging():
    """ログ設定"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = Path(config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def scrape_and_save(urls: List[str]):
    """
    データを取得してデータベースに保存
    
    Args:
        urls: データ取得元URLのリスト
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=== データ取得処理を開始します ===")
    
    # 各モジュールの初期化
    db_manager = DatabaseManager()
    scraper = WebScraper()
    processor = DataProcessor()
    
    # データ取得
    logger.info(f"{len(urls)}件のURLからデータを取得します")
    raw_data_list = scraper.scrape_multiple_urls(urls)
    
    if not raw_data_list:
        logger.warning("取得したデータがありません")
        return
    
    # データ整形
    logger.info("データを整形します")
    processed_data_list = processor.process_companies_batch(raw_data_list)
    
    # 重複除去
    processed_data_list = processor.remove_duplicates(processed_data_list)
    
    # データベースに保存
    logger.info("データベースに保存します")
    saved_count = db_manager.add_companies_batch(processed_data_list)
    
    logger.info(f"=== データ取得処理が完了しました（{saved_count}件保存） ===")


def export_data(format_type: str = 'csv', search_params: Optional[dict] = None):
    """
    データをエクスポート
    
    Args:
        format_type: エクスポート形式（'csv' または 'excel'）
        search_params: 検索パラメータ
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=== データエクスポート処理を開始します ===")
    
    db_manager = DatabaseManager()
    exporter = DataExporter(db_manager)
    
    if format_type.lower() == 'csv':
        filepath = exporter.export_to_csv(search_params=search_params)
    elif format_type.lower() == 'excel':
        filepath = exporter.export_to_excel(search_params=search_params)
    else:
        logger.error(f"サポートされていない形式です: {format_type}")
        return
    
    if filepath:
        logger.info(f"=== データエクスポート処理が完了しました: {filepath} ===")
    else:
        logger.warning("エクスポートするデータがありませんでした")


def show_statistics():
    """データベースの統計情報を表示"""
    logger = logging.getLogger(__name__)
    
    logger.info("=== データベース統計情報 ===")
    
    db_manager = DatabaseManager()
    count = db_manager.get_company_count()
    
    logger.info(f"登録事業所数: {count}件")
    
    # サンプルデータを表示
    companies = db_manager.get_all_companies(limit=5)
    if companies:
        logger.info("\nサンプルデータ（最新5件）:")
        for company in companies:
            logger.info(f"  - {company.company_name}: {company.website_url}")


def main():
    """メイン関数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("通販事業所データ取得システムを起動しました")
    
    # コマンドライン引数の処理（簡易版）
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'scrape':
            # データ取得
            # 実際の使用時は、URLを引数で指定するか、設定ファイルから読み込む
            urls = []
            if len(sys.argv) > 2:
                urls = sys.argv[2].split(',')
            else:
                # デフォルトのURL（実際の使用時は適切なURLに変更）
                logger.warning("URLが指定されていません。設定ファイルから読み込むか、引数で指定してください。")
                # urls = ['https://example.com/companies']
            
            if urls:
                scrape_and_save(urls)
            else:
                logger.error("URLが指定されていません")
        
        elif command == 'export':
            # データエクスポート
            format_type = sys.argv[2] if len(sys.argv) > 2 else 'csv'
            export_data(format_type)
        
        elif command == 'stats':
            # 統計情報表示
            show_statistics()
        
        elif command == 'report':
            # サマリーレポート出力
            db_manager = DatabaseManager()
            exporter = DataExporter(db_manager)
            filepath = exporter.export_summary_report()
            if filepath:
                logger.info(f"サマリーレポートを出力しました: {filepath}")
        
        else:
            logger.error(f"不明なコマンド: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """使用方法を表示"""
    usage = """
使用方法:
  python main.py <command> [options]

コマンド:
  scrape [url1,url2,...]  データを取得してデータベースに保存
  export [csv|excel]      データをエクスポート
  stats                   データベースの統計情報を表示
  report                  サマリーレポートを出力

例:
  python main.py scrape https://example.com/companies
  python main.py export excel
  python main.py stats
  python main.py report
"""
    print(usage)


if __name__ == '__main__':
    main()

