# Arquitetura do Projeto

## Objetivo

Introduzir uma arquitetura modular sem quebrar o comportamento atual do app
Streamlit. O monolito continua operando como legado, mas agora existe uma
estrutura oficial para evolucao incremental.

## Estrutura Atual

```text
backend/
  app.py                  # ponto de entrada oficial
  bootstrap.py            # inicializacao do projeto
  auditoria_fiscal.py     # monolito legado ainda ativo
  core/
    settings.py           # configuracoes centralizadas
    session.py            # estado base do Streamlit
  db/
    connection.py         # adaptadores e helpers de banco
  modules/
    legacy.py             # ponte para o monolito
    auditoria/            # dominio de auditoria
    usuarios/             # dominio de usuarios e autenticacao
    financeiro/           # dominio financeiro
    suporte/              # dominio de suporte
```

## Direcao de Refatoracao

1. Consolidar a extracao de autenticacao e sessao em `modules/usuarios`.
2. Mover SQLite/PostgreSQL para adaptadores em `db/`.
3. Extrair auditorias de entrada, saida e notas para `modules/auditoria`.
4. Extrair financeiro e suporte para seus respectivos dominios.
5. Reduzir `auditoria_fiscal.py` ate ele virar apenas composicao.

## Extracao Ja Concluida

- `modules/usuarios/models.py`: modelo de usuario autenticado.
- `modules/usuarios/service.py`: autenticacao e validacao de sessao.
- `modules/usuarios/session.py`: escrita e limpeza do estado autenticado.
- `db/connection.py`: helper para conexao PostgreSQL usado pelo dominio.

O arquivo legado ainda expõe wrappers de compatibilidade, mas a regra central de
usuarios nao mora mais nele.

## Regras Praticas

- Novos codigos nao devem entrar diretamente em `auditoria_fiscal.py` quando
  houver um modulo de destino claro.
- Configuracoes devem sair de `os.getenv(...)` espalhado e passar por
  `backend.core.settings`.
- Conexoes com banco devem ser centralizadas em `backend.db`.
- A migracao deve ser incremental, com preservacao do fluxo atual.
- O backend preferencial e PostgreSQL, com fallback automatico para SQLite em
  desenvolvimento quando o banco principal nao estiver acessivel.
