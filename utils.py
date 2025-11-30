"""
ユーティリティ関数
共通的に使用する関数を提供
"""
import re
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_phone_number(phone: Optional[str]) -> Optional[str]:
    """
    電話番号を正規化（ハイフン統一）
    
    Args:
        phone: 電話番号文字列
        
    Returns:
        正規化された電話番号
    """
    if not phone:
        return None
    
    # 数字とハイフン以外を除去
    phone = re.sub(r'[^\d\-]', '', phone)
    
    # 既に適切な形式の場合はそのまま返す
    if re.match(r'^\d{2,4}-\d{1,4}-\d{4}$', phone):
        return phone
    
    # 数字のみの場合、適切な位置にハイフンを挿入
    digits_only = re.sub(r'[^\d]', '', phone)
    
    if len(digits_only) == 10:
        # 固定電話（10桁）
        return f"{digits_only[:2]}-{digits_only[2:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11:
        # 携帯電話（11桁）
        return f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
    else:
        # その他の形式はそのまま返す
        return phone


def normalize_postal_code(postal_code: Optional[str]) -> Optional[str]:
    """
    郵便番号を正規化（ハイフン統一）
    
    Args:
        postal_code: 郵便番号文字列
        
    Returns:
        正規化された郵便番号（例: 123-4567）
    """
    if not postal_code:
        return None
    
    # 数字とハイフン以外を除去
    digits = re.sub(r'[^\d]', '', postal_code)
    
    if len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"
    elif len(digits) == 6:
        # 6桁の場合は0を追加
        return f"0{digits[:2]}-{digits[2:]}"
    else:
        return postal_code


def normalize_url(url: Optional[str]) -> Optional[str]:
    """
    URLを正規化（プロトコル追加など）
    
    Args:
        url: URL文字列
        
    Returns:
        正規化されたURL
    """
    if not url:
        return None
    
    url = url.strip()
    
    # プロトコルがない場合は追加
    if url and not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    return url


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    テキストをクリーニング（空白、改行の除去など）
    
    Args:
        text: テキスト文字列
        
    Returns:
        クリーニングされたテキスト
    """
    if not text:
        return None
    
    # 前後の空白を除去
    text = text.strip()
    
    # 連続する空白を1つに
    text = re.sub(r'\s+', ' ', text)
    
    # 改行を空白に変換
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    return text if text else None


def validate_email(email: Optional[str]) -> bool:
    """
    メールアドレスの妥当性をチェック
    
    Args:
        email: メールアドレス文字列
        
    Returns:
        妥当な場合はTrue
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    日付文字列をdatetimeオブジェクトに変換
    
    Args:
        date_str: 日付文字列（複数の形式に対応）
        
    Returns:
        datetimeオブジェクト、変換失敗時はNone
    """
    if not date_str:
        return None
    
    date_formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y年%m月%d日',
        '%Y.%m.%d',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    logger.warning(f"日付の解析に失敗しました: {date_str}")
    return None


def extract_numbers(text: Optional[str]) -> Optional[int]:
    """
    テキストから数値を抽出
    
    Args:
        text: テキスト文字列
        
    Returns:
        抽出された数値、抽出失敗時はNone
    """
    if not text:
        return None
    
    # 数字を抽出
    numbers = re.findall(r'\d+', text.replace(',', ''))
    
    if numbers:
        try:
            return int(''.join(numbers))
        except ValueError:
            return None
    
    return None

