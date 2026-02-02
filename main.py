"""
MangaDex PT - Plataforma de Leitura de Mangás
FastAPI + PostgreSQL/SQLite + HTML/CSS/JavaScript
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import httpx
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
import jwt
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
# Prioriza DATABASE_URL do .env (PostgreSQL), se não existir usa SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mangadex.db")
MANGADEX_API_URL = "https://api.mangadex.org"
SECRET_KEY = os.getenv("SECRET_KEY", "773c5bb4feaae6d1dc39fc3c4bcdbea5899b59e9804962fddd425950efbe191392d5bae19f20c42a8d5bf45d0e7b5e892f346b6fc9f4e589b4e7d57a75154865")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 semana

# Auth - Configuração do bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify(plain_password: str, hashed_password: str) -> bool:
    # ADICIONAR AQUI:
    plain_password = plain_password[:72]
 #   return pwd_context.verify(plain_password, hashed_password)

# Banco de Dados
# Configuração condicional para SQLite ou PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SiteConfig(Base):
    __tablename__ = "site_config"
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(255), default="MangaDex PT")
    primary_color = Column(String(50), default="#6366f1")
    secondary_color = Column(String(50), default="#ec4899")
    logo_url = Column(String(500), default="")
    footer_text = Column(String(500), default="MangaDex PT - Todos os direitos reservados")
    custom_links = Column(Text, default="[]")
    ad_header_script = Column(Text, default="")
    ad_sidebar_script = Column(Text, default="")
    ad_footer_script = Column(Text, default="")
    ad_popunder_script = Column(Text, default="")

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

# Inicializar Configuração se não existir
def init_db():
    db = SessionLocal()
    try:
        if not db.query(SiteConfig).first():
            config = SiteConfig()
            db.add(config)
            db.commit()
            logger.info("Configuração inicial criada")
    except Exception as e:
        logger.error(f"Erro ao inicializar DB: {e}")
    finally:
        db.close()

init_db()

# FastAPI
app = FastAPI(title="MangaDex PT")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Helpers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    password = password[:72]  # Garantir truncagem aqui também
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    try:
        plain_password = plain_password[:72]  # ADICIONAR ESTA LINHA
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False


def create_access_token(data: dict) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Pega o usuário atual baseado no token JWT"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = db.query(User).filter(User.username == username).first()
        return user
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return None

def get_site_config(db: Session) -> SiteConfig:
    """Pega a configuração do site"""
    config = db.query(SiteConfig).first()
    if not config:
        config = SiteConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Rotas de Autenticação
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    config = get_site_config(db)
    return templates.TemplateResponse("login.html", {"request": request, "config": config})

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro_page(request: Request, db: Session = Depends(get_db)):
    config = get_site_config(db)
    return templates.TemplateResponse("cadastro.html", {"request": request, "config": config})

@app.post("/api/auth/cadastro")
async def api_cadastro(
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """Endpoint de cadastro de usuário"""
    try:
        # Validações
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Usuário deve ter no mínimo 3 caracteres")
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 6 caracteres")
        
        # Verifica se usuário já existe
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Usuário já existe")
        
        # Verifica se email já existe
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Cria novo usuário
        user = User(
            username=username, 
            email=email, 
            hashed_password=hash_password(password),
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Novo usuário cadastrado: {username}")
        return {"status": "sucesso", "message": "Cadastro realizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno ao processar cadastro")

@app.post("/api/auth/login")
async def api_login(
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """Endpoint de login"""
    try:
        # Busca o usuário
        user = db.query(User).filter(User.username == username).first()
        
        # Verifica se usuário existe e senha está correta
        if not user:
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
        
        # Cria token JWT
        access_token = create_access_token(data={"sub": user.username})
        
        # Define cookie com o token
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False  # Mudar para True em produção com HTTPS
        )
        
        logger.info(f"Login realizado: {username}")
        return {"status": "sucesso", "message": "Login realizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar login")

@app.get("/logout")
async def logout(response: Response):
    """Endpoint de logout"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response

# Rotas Principais
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "config": config})

@app.get("/manga/{manga_id}", response_class=HTMLResponse)
async def manga_detalhes(request: Request, manga_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("manga_detalhes.html", {"request": request, "manga_id": manga_id, "user": user, "config": config})

@app.get("/leitor/{chapter_id}", response_class=HTMLResponse)
async def leitor(request: Request, chapter_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("leitor.html", {"request": request, "chapter_id": chapter_id, "user": user, "config": config})

@app.get("/adulto", response_class=HTMLResponse)
async def adulto(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("adulto.html", {"request": request, "user": user, "config": config})

@app.get("/buscar", response_class=HTMLResponse)
async def buscar(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("buscar.html", {"request": request, "user": user, "config": config})

@app.get("/categorias", response_class=HTMLResponse)
async def categorias(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    config = get_site_config(db)
    return templates.TemplateResponse("categorias.html", {"request": request, "user": user, "config": config})

# Admin
@app.get("/admin/personalizar", response_class=HTMLResponse)
async def admin_personalizar(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user or not user.is_admin:
        return RedirectResponse(url="/login")
    config = get_site_config(db)
    return templates.TemplateResponse("admin/personalizar.html", {"request": request, "user": user, "config": config})

@app.post("/api/admin/config")
async def update_config(
    site_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    footer_text: str = Form(...),
    ad_header_script: str = Form(""),
    ad_sidebar_script: str = Form(""),
    ad_footer_script: str = Form(""),
    ad_popunder_script: str = Form(""),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    config = db.query(SiteConfig).first()
    config.site_name = site_name
    config.primary_color = primary_color
    config.secondary_color = secondary_color
    config.footer_text = footer_text
    config.ad_header_script = ad_header_script
    config.ad_sidebar_script = ad_sidebar_script
    config.ad_footer_script = ad_footer_script
    config.ad_popunder_script = ad_popunder_script
    db.commit()
    
    return {"status": "sucesso", "message": "Configurações atualizadas"}

# API MangaDex (Proxy)
@app.get("/api/mangadex/populares")
async def get_populares(limit: int = 20, offset: int = 0):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            r = await client.get(f"{MANGADEX_API_URL}/manga", params={
                "limit": limit, 
                "offset": offset, 
                "order[followedCount]": "desc",
                "contentRating[]": ["safe", "suggestive", "erotica"],
                "includes[]": ["cover_art"]
            })
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"Erro API Populares: {e}")
        return {"data": [], "error": str(e)}

@app.get("/api/mangadex/manga/{manga_id}")
async def get_manga(manga_id: str):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            r = await client.get(
                f"{MANGADEX_API_URL}/manga/{manga_id}", 
                params={"includes[]": ["cover_art", "author", "artist"]}
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"Erro ao buscar manga {manga_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar informações do mangá")

@app.get("/api/mangadex/manga/{manga_id}/capitulos")
async def get_capitulos(manga_id: str, limit: int = 100, offset: int = 0):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            r = await client.get(f"{MANGADEX_API_URL}/chapter", params={
                "manga": manga_id, 
                "limit": limit, 
                "offset": offset,
                "order[chapter]": "desc",
                "translatedLanguage[]": ["pt-br", "pt", "en"],
                "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"],
                "includes[]": ["scanlation_group"]
            })
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"Erro ao buscar capítulos: {e}")
        return {"data": []}

@app.get("/api/mangadex/capitulo/{chapter_id}")
async def get_capitulo(chapter_id: str):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            ch = await client.get(f"{MANGADEX_API_URL}/chapter/{chapter_id}")
            ch.raise_for_status()
            srv = await client.get(f"{MANGADEX_API_URL}/at-home/server/{chapter_id}")
            srv.raise_for_status()
            return {"chapter": ch.json()["data"], "pages": srv.json()}
    except Exception as e:
        logger.error(f"Erro ao buscar capítulo {chapter_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao carregar capítulo")

@app.get("/api/mangadex/buscar")
async def api_buscar(q: str, limit: int = 20, offset: int = 0):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            r = await client.get(f"{MANGADEX_API_URL}/manga", params={
                "title": q, 
                "limit": limit, 
                "offset": offset,
                "includes[]": ["cover_art"],
                "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"]
            })
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        return {"data": []}

@app.get("/api/mangadex/adulto")
async def get_adulto(limit: int = 60, offset: int = 0):
    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            r = await client.get(f"{MANGADEX_API_URL}/manga", params={
                "limit": limit, 
                "offset": offset, 
                "contentRating[]": ["pornographic"],
                "includes[]": ["cover_art"], 
                "order[followedCount]": "desc"
            })
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.error(f"Erro API Adulto: {e}")
        return {"data": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
