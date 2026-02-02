"""
Configuração do banco de dados
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mangadex_db")

# Criar engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    poolclass=NullPool,  # Desabilitar pool de conexões para melhor compatibilidade
    connect_args={
        "connect_timeout": 10,
        "application_name": "mangadex-pt"
    }
)

# Criar SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def criar_tabelas():
    """Criar todas as tabelas no banco de dados"""
    from models import Base
    Base.metadata.create_all(bind=engine)

def limpar_banco():
    """Limpar todas as tabelas (use com cuidado!)"""
    from models import Base
    Base.metadata.drop_all(bind=engine)
