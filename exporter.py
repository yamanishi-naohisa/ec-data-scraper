"""
データエクスポートモジュール
データベースからデータを取得してCSV/Excel形式でエクスポート
"""
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import pandas as pd
from database import DatabaseManager, ECCompany
import config

logger = logging.getLogger(__name__)


class DataExporter:
    """データエクスポートクラス"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初期化
        
        Args:
            db_manager: DatabaseManagerインスタンス
        """
        self.db_manager = db_manager
        self.export_dir = Path(config.BASE_DIR) / 'data' / 'exports'
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def companies_to_dataframe(self, companies: List[ECCompany]) -> pd.DataFrame:
        """
        事業所データのリストをDataFrameに変換
        
        Args:
            companies: ECCompanyオブジェクトのリスト
            
        Returns:
            pandas DataFrame
        """
        data = [company.to_dict() for company in companies]
        df = pd.DataFrame(data)
        return df
    
    def export_to_csv(
        self,
        companies: Optional[List[ECCompany]] = None,
        filename: Optional[str] = None,
        search_params: Optional[dict] = None
    ) -> str:
        """
        データをCSV形式でエクスポート
        
        Args:
            companies: エクスポートする事業所データ（Noneの場合は全件）
            filename: 出力ファイル名（Noneの場合は自動生成）
            search_params: 検索パラメータ（companiesがNoneの場合に使用）
            
        Returns:
            出力ファイルのパス
        """
        # データの取得
        if companies is None:
            if search_params:
                companies = self.db_manager.search_companies(**search_params)
            else:
                companies = self.db_manager.get_all_companies()
        
        if not companies:
            logger.warning("エクスポートするデータがありません")
            return None
        
        # DataFrameに変換
        df = self.companies_to_dataframe(companies)
        
        # ファイル名の生成
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ec_companies_{timestamp}.csv'
        
        filepath = self.export_dir / filename
        
        # CSV出力
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"CSVファイルを出力しました: {filepath} ({len(companies)}件)")
        
        return str(filepath)
    
    def export_to_excel(
        self,
        companies: Optional[List[ECCompany]] = None,
        filename: Optional[str] = None,
        search_params: Optional[dict] = None,
        sheet_name: str = '通販事業所データ'
    ) -> str:
        """
        データをExcel形式でエクスポート
        
        Args:
            companies: エクスポートする事業所データ（Noneの場合は全件）
            filename: 出力ファイル名（Noneの場合は自動生成）
            search_params: 検索パラメータ（companiesがNoneの場合に使用）
            sheet_name: シート名
            
        Returns:
            出力ファイルのパス
        """
        # データの取得
        if companies is None:
            if search_params:
                companies = self.db_manager.search_companies(**search_params)
            else:
                companies = self.db_manager.get_all_companies()
        
        if not companies:
            logger.warning("エクスポートするデータがありません")
            return None
        
        # DataFrameに変換
        df = self.companies_to_dataframe(companies)
        
        # ファイル名の生成
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ec_companies_{timestamp}.xlsx'
        
        filepath = self.export_dir / filename
        
        # Excel出力
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Excelファイルを出力しました: {filepath} ({len(companies)}件)")
        
        return str(filepath)
    
    def export_summary_report(self) -> str:
        """
        サマリーレポートをエクスポート
        
        Returns:
            出力ファイルのパス
        """
        # 全データを取得
        companies = self.db_manager.get_all_companies()
        
        if not companies:
            logger.warning("レポート用のデータがありません")
            return None
        
        # サマリー情報を作成
        summary_data = {
            '項目': [
                '総事業所数',
                'ウェブサイトURL登録数',
                'メールアドレス登録数',
                '従業員数平均',
                '売上高合計（万円）'
            ],
            '値': [
                len(companies),
                sum(1 for c in companies if c.website_url),
                sum(1 for c in companies if c.email),
                int(sum(c.employee_count for c in companies if c.employee_count) / 
                    sum(1 for c in companies if c.employee_count)) if 
                    sum(1 for c in companies if c.employee_count) > 0 else 0,
                sum(c.annual_sales for c in companies if c.annual_sales) if 
                    any(c.annual_sales for c in companies) else 0
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_data = self.companies_to_dataframe(companies)
        
        # ファイル名の生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ec_companies_report_{timestamp}.xlsx'
        filepath = self.export_dir / filename
        
        # Excel出力（サマリーとデータを別シートに）
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='サマリー', index=False)
            df_data.to_excel(writer, sheet_name='詳細データ', index=False)
        
        logger.info(f"サマリーレポートを出力しました: {filepath}")
        
        return str(filepath)

