# Auditoria Contábil Pro

Sistema automatizado de auditoria fiscal, análise de itens e conformidade tributária.

## Funcionalidades

- ✅ Auditoria de itens (entrada/saída)
- ✅ Análise de notas fiscais
- ✅ Conformidade tributária
- ✅ Sistema de tickets de suporte
- ✅ Controle financeiro

## Tecnologias

- **Frontend:** Streamlit
- **Backend:** Python
- **Banco de Dados:** PostgreSQL com fallback para SQLite
- **Deploy:** Railway

## Estrutura

- `backend/app.py`: ponto de entrada oficial
- `backend/bootstrap.py`: inicializacao da aplicacao
- `backend/auditoria_fiscal.py`: modulo legado monolitico
- `docs/ARCHITECTURE.md`: arquitetura modular adotada

## Banco de Dados

- Em desenvolvimento local, a aplicacao tenta conectar primeiro em
  `postgresql://<usuario-local>@localhost/auditoria`
- Se o PostgreSQL nao estiver disponivel, o sistema cai automaticamente para
  SQLite usando `DATABASE_PATH`
- Para forcar a conexao local, configure `LOCAL_DATABASE_URL`
- Em deploy, configure `DATABASE_URL`
- Para criar as tabelas manualmente no PostgreSQL local:
  `psql -d auditoria -f sql/schema.sql`
- Para verificar se faltou alguma coluna:
  `psql -d auditoria -f sql/verify_schema.sql`
- Para criar o primeiro administrador em um banco vazio, configure
  `BOOTSTRAP_ADMIN_LOGIN` e `BOOTSTRAP_ADMIN_PASSWORD` no `.env` e inicie o app
  uma vez. O bootstrap so roda quando a tabela `administradores` esta vazia.

## Como Usar

1. Clone o repositório
2. Instale as dependências: `pip install -r backend/requirements.txt`
3. Configure as variáveis de ambiente a partir de `.env.example`
4. Execute: `streamlit run backend/app.py`

O arquivo `.env` na raiz e carregado automaticamente quando a aplicacao inicia.

## Autor

Victor Hugo - Contador/Empresário
