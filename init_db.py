import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from main import Base, User, SiteConfig, get_password_hash, SessionLocal

# Carregar variáveis do .env
load_dotenv()

def init_postgresql():
    # Pega a URL do banco do ambiente ou usa uma padrão para teste
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url or "postgresql" not in db_url:
        print("ERRO: DATABASE_URL não configurada ou não é PostgreSQL no arquivo .env")
        print("Exemplo: DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco")
        return

    print(f"Conectando ao banco: {db_url.split('@')[-1]}") # Mostra apenas o host/banco por segurança
    
    try:
        engine = create_engine(db_url)
        
        # Criar todas as tabelas definidas nos modelos
        print("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")

        # Criar usuário admin inicial e configuração básica
        db = SessionLocal()
        
        # Verificar se já existe configuração
        if not db.query(SiteConfig).first():
            config = SiteConfig(
                site_name="MangaDex PT",
                footer_text="MangaDex PT - Todos os direitos reservados"
            )
            db.add(config)
            print("Configuração inicial do site criada.")

        # Verificar se já existe admin
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@admin.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin)
            print("Usuário admin criado: admin / admin123")
        
        db.commit()
        db.close()
        print("\nInicialização concluída com sucesso!")
        
    except Exception as e:
        print(f"ERRO ao inicializar banco: {e}")

if __name__ == "__main__":
    init_postgresql()
