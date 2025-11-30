"""
データ整形モジュール
取得したデータを整形・正規化する
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import utils

logger = logging.getLogger(__name__)


class DataProcessor:
    """データ整形クラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def process_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        事業所データを整形
        
        Args:
            raw_data: 取得した生データ
            
        Returns:
            整形されたデータ
        """
        processed = {}
        
        # 必須項目の処理
        processed['company_name'] = utils.clean_text(raw_data.get('company_name'))
        processed['address'] = utils.clean_text(raw_data.get('address'))
        processed['postal_code'] = utils.normalize_postal_code(raw_data.get('postal_code'))
        processed['phone_number'] = utils.normalize_phone_number(raw_data.get('phone_number'))
        processed['website_url'] = utils.normalize_url(raw_data.get('website_url'))
        processed['source_url'] = raw_data.get('source_url')
        
        # 任意項目の処理
        processed['company_number'] = utils.clean_text(raw_data.get('company_number'))
        processed['representative'] = utils.clean_text(raw_data.get('representative'))
        
        # 日付の処理
        established_date = raw_data.get('established_date')
        if established_date:
            if isinstance(established_date, str):
                date_obj = utils.parse_date(established_date)
                processed['established_date'] = date_obj.date() if date_obj else None
            elif isinstance(established_date, datetime):
                processed['established_date'] = established_date.date()
            else:
                processed['established_date'] = None
        else:
            processed['established_date'] = None
        
        # 数値の処理
        employee_count = raw_data.get('employee_count')
        if employee_count:
            if isinstance(employee_count, (int, float)):
                processed['employee_count'] = int(employee_count)
            elif isinstance(employee_count, str):
                processed['employee_count'] = utils.extract_numbers(employee_count)
            else:
                processed['employee_count'] = None
        else:
            processed['employee_count'] = None
        
        annual_sales = raw_data.get('annual_sales')
        if annual_sales:
            if isinstance(annual_sales, (int, float)):
                processed['annual_sales'] = int(annual_sales)
            elif isinstance(annual_sales, str):
                processed['annual_sales'] = utils.extract_numbers(annual_sales)
            else:
                processed['annual_sales'] = None
        else:
            processed['annual_sales'] = None
        
        # その他の項目
        processed['product_categories'] = utils.clean_text(raw_data.get('product_categories'))
        
        email = raw_data.get('email')
        if email and utils.validate_email(email):
            processed['email'] = email.strip()
        else:
            processed['email'] = None
        
        processed['notes'] = utils.clean_text(raw_data.get('notes'))
        
        # 必須項目の検証
        if not processed.get('company_name'):
            logger.warning("事業所名が空のため、データをスキップします")
            return None
        
        return processed
    
    def process_companies_batch(self, raw_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        複数の事業所データを一括整形
        
        Args:
            raw_data_list: 生データのリスト
            
        Returns:
            整形されたデータのリスト
        """
        processed_list = []
        
        for raw_data in raw_data_list:
            processed = self.process_company_data(raw_data)
            if processed:
                processed_list.append(processed)
            else:
                logger.warning("データの整形に失敗しました")
        
        logger.info(f"{len(processed_list)}/{len(raw_data_list)}件のデータを整形しました")
        return processed_list
    
    def validate_required_fields(self, data: Dict[str, Any]) -> bool:
        """
        必須項目の検証
        
        Args:
            data: 検証するデータ
            
        Returns:
            必須項目がすべて揃っている場合はTrue
        """
        required_fields = ['company_name']
        
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"必須項目が不足しています: {field}")
                return False
        
        return True
    
    def remove_duplicates(self, data_list: List[Dict[str, Any]], key: str = 'website_url') -> List[Dict[str, Any]]:
        """
        重複データを除去
        
        Args:
            data_list: データのリスト
            key: 重複チェックのキー（デフォルト: website_url）
            
        Returns:
            重複を除去したデータのリスト
        """
        seen = set()
        unique_list = []
        
        for data in data_list:
            value = data.get(key)
            if value and value not in seen:
                seen.add(value)
                unique_list.append(data)
            elif not value:
                # キーが存在しない場合はそのまま追加
                unique_list.append(data)
        
        removed_count = len(data_list) - len(unique_list)
        if removed_count > 0:
            logger.info(f"{removed_count}件の重複データを除去しました")
        
        return unique_list

