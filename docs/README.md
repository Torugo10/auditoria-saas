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
- Para forcar outra conexao PostgreSQL, configure `DATABASE_URL`
- Opcionalmente, voce pode usar `LOCAL_DATABASE_URL`

## Como Usar

1. Clone o repositório
2. Instale as dependências: `pip install -r backend/requirements.txt`
3. Configure as variáveis de ambiente a partir de `.env.example`
4. Execute: `streamlit run backend/app.py`

## Autor

Victor Hugo - Contador/Empresário
