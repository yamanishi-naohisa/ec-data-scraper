"""
データベース操作モジュール
SQLiteデータベースへの接続、テーブル作成、CRUD操作を提供
"""
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import config

logger = logging.getLogger(__name__)

Base = declarative_base()


class ECCompany(Base):
    """通販事業所データモデル"""
    __tablename__ = 'ec_companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    postal_code = Column(String(10), index=True)
    phone_number = Column(String(20))
    website_url = Column(Text, index=True)
    company_number = Column(String(20))
    representative = Column(String(100))
    established_date = Column(Date)
    employee_count = Column(Integer)
    product_categories = Column(Text)
    annual_sales = Column(Integer)
    email = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    source_url = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        """データモデルを辞書に変換"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'address': self.address,
            'postal_code': self.postal_code,
            'phone_number': self.phone_number,
            'website_url': self.website_url,
            'company_number': self.company_number,
            'representative': self.representative,
            'established_date': self.established_date.isoformat() if self.established_date else None,
            'employee_count': self.employee_count,
            'product_categories': self.product_categories,
            'annual_sales': self.annual_sales,
            'email': self.email,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source_url': self.source_url
        }


class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, database_path: str = None):
        """
        初期化
        
        Args:
            database_path: データベースファイルのパス
        """
        self.database_path = database_path or config.DATABASE_PATH
        self.engine = create_engine(f'sqlite:///{self.database_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """テーブルを作成"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info(f"データベーステーブルを作成しました: {self.database_path}")
        except SQLAlchemyError as e:
            logger.error(f"テーブル作成エラー: {e}")
            raise
    
    def get_session(self) -> Session:
        """セッションを取得"""
        return self.SessionLocal()
    
    def add_company(self, company_data: Dict[str, Any]) -> Optional[ECCompany]:
        """
        事業所データを追加
        
        Args:
            company_data: 事業所データの辞書
            
        Returns:
            追加されたECCompanyオブジェクト、失敗時はNone
        """
        session = self.get_session()
        try:
            # 既存データのチェック（website_urlで重複チェック）
            existing = None
            if company_data.get('website_url'):
                existing = session.query(ECCompany).filter_by(
                    website_url=company_data['website_url']
                ).first()
            
            if existing:
                # 既存データを更新
                for key, value in company_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                session.commit()
                logger.info(f"既存データを更新しました: {existing.company_name}")
                return existing
            else:
                # 新規データを追加
                company = ECCompany(**company_data)
                session.add(company)
                session.commit()
                logger.info(f"新規データを追加しました: {company.company_name}")
                return company
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"データ追加エラー: {e}")
            return None
        finally:
            session.close()
    
    def add_companies_batch(self, companies_data: List[Dict[str, Any]]) -> int:
        """
        複数の事業所データを一括追加
        
        Args:
            companies_data: 事業所データのリスト
            
        Returns:
            追加されたデータ数
        """
        session = self.get_session()
        count = 0
        try:
            for company_data in companies_data:
                # 既存データのチェック
                existing = None
                if company_data.get('website_url'):
                    existing = session.query(ECCompany).filter_by(
                        website_url=company_data['website_url']
                    ).first()
                
                if existing:
                    # 既存データを更新
                    for key, value in company_data.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.now()
                else:
                    # 新規データを追加
                    company = ECCompany(**company_data)
                    session.add(company)
                    count += 1
            
            session.commit()
            logger.info(f"{count}件の新規データを追加しました")
            return count
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"一括追加エラー: {e}")
            return 0
        finally:
            session.close()
    
    def search_companies(
        self,
        company_name: Optional[str] = None,
        postal_code: Optional[str] = None,
        limit: int = 100
    ) -> List[ECCompany]:
        """
        事業所データを検索
        
        Args:
            company_name: 事業所名（部分一致）
            postal_code: 郵便番号
            limit: 取得件数の上限
            
        Returns:
            検索結果のリスト
        """
        session = self.get_session()
        try:
            query = session.query(ECCompany)
            
            if company_name:
                query = query.filter(ECCompany.company_name.like(f'%{company_name}%'))
            
            if postal_code:
                query = query.filter(ECCompany.postal_code == postal_code)
            
            results = query.limit(limit).all()
            logger.info(f"{len(results)}件のデータを取得しました")
            return results
        except SQLAlchemyError as e:
            logger.error(f"検索エラー: {e}")
            return []
        finally:
            session.close()
    
    def get_all_companies(self, limit: int = None) -> List[ECCompany]:
        """
        すべての事業所データを取得
        
        Args:
            limit: 取得件数の上限
            
        Returns:
            事業所データのリスト
        """
        session = self.get_session()
        try:
            query = session.query(ECCompany)
            if limit:
                results = query.limit(limit).all()
            else:
                results = query.all()
            logger.info(f"{len(results)}件のデータを取得しました")
            return results
        except SQLAlchemyError as e:
            logger.error(f"データ取得エラー: {e}")
            return []
        finally:
            session.close()
    
    def get_company_count(self) -> int:
        """データベース内の事業所数を取得"""
        session = self.get_session()
        try:
            count = session.query(ECCompany).count()
            return count
        except SQLAlchemyError as e:
            logger.error(f"カウント取得エラー: {e}")
            return 0
        finally:
            session.close()

