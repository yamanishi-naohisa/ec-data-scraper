"""
データ取得モジュール
Webから通販事業所データを取得する
"""
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import config

logger = logging.getLogger(__name__)


class WebScraper:
    """Webスクレイパークラス"""
    
    def __init__(self):
        """初期化"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
    
    def fetch_page(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """
        Webページを取得してBeautifulSoupオブジェクトを返す
        
        Args:
            url: 取得するURL
            retries: リトライ回数（デフォルト: config.MAX_RETRIES）
            
        Returns:
            BeautifulSoupオブジェクト、失敗時はNone
        """
        if retries is None:
            retries = config.MAX_RETRIES
        
        for attempt in range(retries + 1):
            try:
                logger.info(f"ページを取得中: {url} (試行 {attempt + 1}/{retries + 1})")
                
                response = self.session.get(
                    url,
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                # リクエスト間隔を空ける
                time.sleep(config.REQUEST_DELAY)
                
                soup = BeautifulSoup(response.content, 'lxml')
                logger.info(f"ページの取得に成功しました: {url}")
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"ページ取得エラー (試行 {attempt + 1}/{retries + 1}): {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)  # 指数バックオフ
                else:
                    logger.error(f"ページの取得に失敗しました: {url}")
                    return None
        
        return None
    
    def extract_company_data(self, soup: BeautifulSoup, source_url: str) -> List[Dict[str, Any]]:
        """
        HTMLから事業所データを抽出（汎用メソッド）
        
        注意: このメソッドは汎用的な実装です。
        実際のデータソースに応じて、このメソッドをオーバーライドするか、
        専用の抽出メソッドを実装してください。
        
        Args:
            soup: BeautifulSoupオブジェクト
            source_url: データ取得元URL
            
        Returns:
            抽出した事業所データのリスト
        """
        companies = []
        
        # ここに実際のデータ抽出ロジックを実装
        # 例: テーブルからデータを抽出
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # ヘッダー行をスキップ
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    company_data = {
                        'company_name': cells[0].get_text(strip=True) if len(cells) > 0 else None,
                        'address': cells[1].get_text(strip=True) if len(cells) > 1 else None,
                        'phone_number': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                        'website_url': None,
                        'source_url': source_url
                    }
                    
                    # リンクからURLを取得
                    link = row.find('a', href=True)
                    if link:
                        company_data['website_url'] = urljoin(source_url, link['href'])
                    
                    if company_data['company_name']:
                        companies.append(company_data)
        
        logger.info(f"{len(companies)}件のデータを抽出しました")
        return companies
    
    def scrape_companies(self, url: str) -> List[Dict[str, Any]]:
        """
        指定されたURLから事業所データを取得
        
        Args:
            url: データ取得元URL
            
        Returns:
            取得した事業所データのリスト
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        companies = self.extract_company_data(soup, url)
        return companies
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        複数のURLから事業所データを取得
        
        Args:
            urls: データ取得元URLのリスト
            
        Returns:
            取得した事業所データのリスト
        """
        all_companies = []
        
        for url in urls:
            logger.info(f"URLからデータを取得中: {url}")
            companies = self.scrape_companies(url)
            all_companies.extend(companies)
            time.sleep(config.REQUEST_DELAY)
        
        logger.info(f"合計 {len(all_companies)}件のデータを取得しました")
        return all_companies
    
    def check_robots_txt(self, base_url: str) -> bool:
        """
        robots.txtをチェック（簡易版）
        
        注意: 本格的な実装にはrobots.txtパーサーライブラリの使用を推奨
        
        Args:
            base_url: ベースURL
            
        Returns:
            スクレイピングが許可されている場合はTrue
        """
        try:
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                robots_content = response.text.lower()
                # 簡易チェック（実際の実装ではより詳細な解析が必要）
                if 'disallow: /' in robots_content:
                    logger.warning(f"robots.txtでスクレイピングが制限されている可能性があります: {base_url}")
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"robots.txtのチェックに失敗しました: {e}")
            return True  # エラー時は許可とみなす（注意が必要）

