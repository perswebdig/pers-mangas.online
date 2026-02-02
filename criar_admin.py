#!/usr/bin/env python3
"""
Script para criar usuário administrador
Execute: python criar_admin.py
"""

import sys
from getpass import getpass
from sqlalchemy.orm import Session
import hashlib
from passlib.context import CryptContext

# Importar do main.py
try:
    from main import SessionLocal, User
except ImportError:
    print("❌ Erro: Não foi possível importar de main.py")
    print("Certifique-se de estar no diretório correto do projeto")
    sys.exit(1)

# Configurar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash com SHA256 + bcrypt para evitar limite de 72 bytes"""
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256(password_bytes).hexdigest()
    return pwd_context.hash(sha256_hash)

def criar_admin():
    """Cria um usuário administrador"""
    print("=" * 50)
    print("CRIAR USUÁRIO ADMINISTRADOR")
    print("=" * 50)
    print()
    
    username = input("Nome de usuário (mínimo 3 caracteres): ").strip()
    if len(username) < 3:
        print("❌ Erro: Nome de usuário deve ter no mínimo 3 caracteres")
        return False
    
    email = input("Email: ").strip()
    if '@' not in email:
        print("❌ Erro: Email inválido")
        return False
    
    senha = getpass("Senha (mínimo 6 caracteres): ")
    if len(senha) < 6:
        print("❌ Erro: Senha deve ter no mínimo 6 caracteres")
        return False
    
    senha_confirm = getpass("Confirme a senha: ")
    if senha != senha_confirm:
        print("❌ Erro: As senhas não coincidem")
        return False
    
    print()
    print("Criando usuário administrador...")
    
    db: Session = SessionLocal()
    
    try:
        if db.query(User).filter(User.username == username).first():
            print(f"❌ Erro: Usuário '{username}' já existe")
            return False
        
        if db.query(User).filter(User.email == email).first():
            print(f"❌ Erro: Email '{email}' já está cadastrado")
            return False
        
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(senha),
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print()
        print("✅ Usuário administrador criado com sucesso!")
        print(f"   Usuário: {username}")
        print(f"   Email: {email}")
        print(f"   Admin: Sim")
        print()
        print("Acesse: http://localhost:8000/login")
        print("Painel admin: http://localhost:8000/admin/personalizar")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def listar_usuarios():
    """Lista todos os usuários"""
    db: Session = SessionLocal()
    
    try:
        usuarios = db.query(User).all()
        
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return
        
        print()
        print("=" * 70)
        print("USUÁRIOS CADASTRADOS")
        print("=" * 70)
        print(f"{'ID':<5} {'Usuário':<20} {'Email':<30} {'Admin':<10}")
        print("-" * 70)
        
        for user in usuarios:
            admin_status = "Sim" if user.is_admin else "Não"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {admin_status:<10}")
        
        print("-" * 70)
        print(f"Total: {len(usuarios)} usuário(s)")
        print()
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        
    finally:
        db.close()

def tornar_admin():
    """Torna um usuário existente em admin"""
    db: Session = SessionLocal()
    
    try:
        username = input("Nome de usuário para tornar admin: ").strip()
        
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ Usuário '{username}' não encontrado")
            return False
        
        if user.is_admin:
            print(f"⚠️  Usuário '{username}' já é administrador")
            return False
        
        user.is_admin = True
        db.commit()
        
        print(f"✅ Usuário '{username}' agora é administrador!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def menu():
    """Menu principal"""
    while True:
        print()
        print("=" * 50)
        print("GERENCIADOR DE USUÁRIOS - MangaDex PT")
        print("=" * 50)
        print()
        print("1. Criar novo usuário administrador")
        print("2. Listar todos os usuários")
        print("3. Tornar usuário existente em admin")
        print("4. Sair")
        print()
        
        opcao = input("Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            criar_admin()
        elif opcao == "2":
            listar_usuarios()
        elif opcao == "3":
            tornar_admin()
        elif opcao == "4":
            print("Até logo!")
            break
        else:
            print("❌ Opção inválida")
        
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\nCancelado.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)