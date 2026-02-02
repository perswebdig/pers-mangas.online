"""
Modelos de banco de dados para MangaDex PT
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Manga(Base):
    """Modelo de mangá (cache da API MangaDex)"""
    __tablename__ = "mangas"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID do MangaDex
    title = Column(String(500), index=True)
    description = Column(Text)
    status = Column(String(50))  # ongoing, completed, hiatus, cancelled
    demographic = Column(String(50))  # shounen, shoujo, seinen, josei
    cover_url = Column(String(500))
    rating = Column(Float)
    followers = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    cached_at = Column(DateTime, default=datetime.utcnow)

class Chapter(Base):
    """Modelo de capítulo"""
    __tablename__ = "chapters"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID do MangaDex
    manga_id = Column(String(36), index=True)
    title = Column(String(500))
    chapter_number = Column(Float)
    volume_number = Column(String(50))
    language = Column(String(10))  # pt-br, pt, en, etc
    pages = Column(Integer)
    published_at = Column(DateTime)
    cached_at = Column(DateTime, default=datetime.utcnow)

class Favorite(Base):
    """Modelo de mangá favorito"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    manga_id = Column(String(36), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

class Advertisement(Base):
    """Modelo de anúncio"""
    __tablename__ = "advertisements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    image_url = Column(String(500))
    click_url = Column(String(500))
    position = Column(String(50))  # header, footer, reader, popunder, social
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdvertisementAnalytics(Base):
    """Modelo de analytics de anúncios"""
    __tablename__ = "advertisement_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    advertisement_id = Column(Integer, index=True)
    event_type = Column(String(50))  # impression, click
    user_ip = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class DownloadedImage(Base):
    """Modelo de imagens baixadas e cacheadas"""
    __tablename__ = "downloaded_images"
    
    id = Column(Integer, primary_key=True, index=True)
    manga_id = Column(String(36), index=True)
    chapter_id = Column(String(36), index=True)
    original_url = Column(String(500))
    local_path = Column(String(500))
    file_size = Column(Integer)
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

class ReadingHistory(Base):
    """Modelo de histórico de leitura"""
    __tablename__ = "reading_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    manga_id = Column(String(36), index=True)
    chapter_id = Column(String(36), index=True)
    last_page = Column(Integer, default=0)
    read_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
