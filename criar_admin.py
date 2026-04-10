import os
import psycopg2
import hashlib
from dotenv import load_dotenv

# ✅ CORRETO - Carregar variáveis de ambiente
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERRO: DATABASE_URL não definida no .env")
    exit(1)

def criar_admin():
    try:
        print("🔄 Conectando ao banco de dados...")
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        print("✅ Conectado!")
        
        # Criar tabela
        print("📊 Criando tabela...")
        c.execute('''
        CREATE TABLE IF NOT EXISTS administradores (
            id SERIAL PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            email TEXT,
            nome_completo TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Dados do admin
        login = 'Admin.Victor'
        senha = 'SenhaForte2026'
        email = 'victor.fetosa@gmail.com'
        nome = 'Victor Hugo'
        
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        print("👤 Criando usuário admin...")
        # Inserir admin
        c.execute('''
        INSERT INTO administradores 
        (login, senha_hash, email, nome_completo, ativo)
        VALUES (%s, %s, %s, %s, 1)
        ON CONFLICT (login) DO UPDATE SET
            senha_hash = EXCLUDED.senha_hash,
            email = EXCLUDED.email,
            nome_completo = EXCLUDED.nome_completo,
            ativo = 1
        ''', (login, senha_hash, email, nome))
        
        conn.commit()
        c.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ SUCESSO! Admin criado com sucesso!")
        print("="*50)
        print(f"🔐 Login: {login}")
        print(f"🔑 Senha: {senha}")
        print(f"📧 Email: {email}")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print(f"\n⚠️ Verifique se a URL está correta!")
        print(f"DATABASE_URL usado: {DATABASE_URL}")

if __name__ == '__main__':
    criar_admin()