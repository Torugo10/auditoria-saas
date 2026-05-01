"""Helpers de conexao para os bancos usados pela aplicacao."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
import sqlite3

import pandas as pd
import psycopg2

from backend.core.settings import Settings, get_settings


SQLITE = "sqlite"
POSTGRES = "postgres"


class PostgresCompatCursor:
    """Cursor com compatibilidade basica para SQL escrito no dialeto SQLite."""

    def __init__(self, raw_cursor):
        self._raw_cursor = raw_cursor
        self.lastrowid = None

    def execute(self, query: str, params=None):
        normalized_query, normalized_params = normalize_query_for_postgres(query, params)
        insert_match = re.match(
            r"\s*INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            normalized_query,
            flags=re.IGNORECASE,
        )

        if insert_match and "RETURNING" not in normalized_query.upper():
            normalized_query = f"{normalized_query.rstrip()} RETURNING id"

        if normalized_params is None:
            self._raw_cursor.execute(normalized_query)
        else:
            self._raw_cursor.execute(normalized_query, normalized_params)

        if insert_match:
            inserted_row = self._raw_cursor.fetchone()
            self.lastrowid = inserted_row[0] if inserted_row else None
        else:
            self.lastrowid = None
        return self

    def fetchone(self):
        return self._raw_cursor.fetchone()

    def fetchall(self):
        return self._raw_cursor.fetchall()

    def close(self) -> None:
        self._raw_cursor.close()

    @property
    def description(self):
        return self._raw_cursor.description

    def __getattr__(self, item):
        return getattr(self._raw_cursor, item)


class PostgresCompatConnection:
    """Conexao PostgreSQL com interface usada hoje pelo monolito."""

    def __init__(self, raw_connection):
        self.raw_connection = raw_connection
        self.backend = POSTGRES

    def cursor(self) -> PostgresCompatCursor:
        return PostgresCompatCursor(self.raw_connection.cursor())

    def commit(self) -> None:
        self.raw_connection.commit()

    def rollback(self) -> None:
        self.raw_connection.rollback()

    def close(self) -> None:
        self.raw_connection.close()

    def __getattr__(self, item):
        return getattr(self.raw_connection, item)


class SQLiteCompatCursor:
    """Cursor SQLite com suporte aos poucos comandos PostgreSQL usados no app."""

    def __init__(self, raw_cursor):
        self._raw_cursor = raw_cursor
        self.lastrowid = None

    def execute(self, query: str, params=None):
        normalized_query, normalized_params, should_skip = normalize_query_for_sqlite(
            query,
            params,
            self._raw_cursor,
        )
        if should_skip:
            return self

        if normalized_params is None:
            self._raw_cursor.execute(normalized_query)
        else:
            self._raw_cursor.execute(normalized_query, normalized_params)

        self.lastrowid = self._raw_cursor.lastrowid
        return self

    def fetchone(self):
        return self._raw_cursor.fetchone()

    def fetchall(self):
        return self._raw_cursor.fetchall()

    def close(self) -> None:
        self._raw_cursor.close()

    @property
    def description(self):
        return self._raw_cursor.description

    def __getattr__(self, item):
        return getattr(self._raw_cursor, item)


class SQLiteCompatConnection:
    """Conexao SQLite com a mesma superficie usada pelo monolito."""

    def __init__(self, raw_connection):
        self.raw_connection = raw_connection
        self.backend = SQLITE

    def cursor(self) -> SQLiteCompatCursor:
        return SQLiteCompatCursor(self.raw_connection.cursor())

    def commit(self) -> None:
        self.raw_connection.commit()

    def rollback(self) -> None:
        self.raw_connection.rollback()

    def close(self) -> None:
        self.raw_connection.close()

    def __getattr__(self, item):
        return getattr(self.raw_connection, item)


def ensure_sqlite_directory(database_path: str) -> None:
    """Garante que o diretorio do arquivo SQLite exista."""
    db_dir = Path(database_path).expanduser().resolve().parent
    db_dir.mkdir(parents=True, exist_ok=True)


def get_sqlite_connection(database_path: str) -> sqlite3.Connection:
    """Abre conexao SQLite com o caminho informado."""
    ensure_sqlite_directory(database_path)
    return SQLiteCompatConnection(sqlite3.connect(database_path))


def get_postgres_connection(database_url: str):
    """Abre conexao PostgreSQL com a URL informada."""
    return psycopg2.connect(database_url)


def connect_db(settings: Settings | None = None, *, database_url: str | None = None, database_path: str | None = None):
    """Abre conexao priorizando PostgreSQL e caindo para SQLite se necessario."""
    settings = settings or get_settings()
    database_url = database_url if database_url is not None else settings.database_url
    database_path = database_path or settings.database_path
    backend = resolve_database_backend(database_url, database_path)

    if backend == POSTGRES:
        return PostgresCompatConnection(get_postgres_connection(database_url))

    return get_sqlite_connection(database_path)


def read_sql_query(query: str, conn, params=None) -> pd.DataFrame:
    """Executa SELECT de forma compativel com SQLite e PostgreSQL."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description] if cursor.description else []
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()


@lru_cache(maxsize=8)
def resolve_database_backend(database_url: str | None, database_path: str) -> str:
    """Detecta o backend disponivel para o ambiente atual."""
    if database_url:
        try:
            conn = get_postgres_connection(database_url)
            conn.close()
            return POSTGRES
        except Exception:
            pass

    ensure_sqlite_directory(database_path)
    return SQLITE


def normalize_query_for_postgres(query: str, params=None):
    """Converte pequenos trechos do dialeto SQLite para PostgreSQL."""
    normalized_query = query
    normalized_params = params

    sqlite_master_match = re.search(
        r"SELECT\s+name\s+FROM\s+sqlite_master\s+WHERE\s+type='table'\s+AND\s+name='([^']+)'",
        normalized_query,
        flags=re.IGNORECASE,
    )
    if sqlite_master_match:
        table_name = sqlite_master_match.group(1)
        normalized_query = (
            "SELECT table_name AS name "
            "FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = %s"
        )
        normalized_params = (table_name,)
        return normalized_query, normalized_params

    normalized_query = re.sub(
        r"INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT",
        "SERIAL PRIMARY KEY",
        normalized_query,
        flags=re.IGNORECASE,
    )
    normalized_query = normalized_query.replace(
        "strftime('%Y-%m', data_vencimento)",
        "TO_CHAR(data_vencimento, 'YYYY-MM')",
    )
    normalized_query = normalized_query.replace("?", "%s")

    return normalized_query, normalized_params


def normalize_query_for_sqlite(query: str, params=None, cursor=None):
    """Converte pequenos trechos PostgreSQL para SQLite quando necessario."""
    normalized_query = query
    normalized_params = params

    alter_match = re.match(
        r"\s*ALTER\s+TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+ADD\s+COLUMN\s+IF\s+NOT\s+EXISTS\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(.+?)\s*$",
        normalized_query,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if alter_match:
        table_name, column_name, column_definition = alter_match.groups()
        if cursor is not None and _sqlite_column_exists(cursor, table_name, column_name):
            return normalized_query, normalized_params, True

        normalized_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"

    normalized_query = re.sub(
        r"\bSERIAL\s+PRIMARY\s+KEY\b",
        "INTEGER PRIMARY KEY AUTOINCREMENT",
        normalized_query,
        flags=re.IGNORECASE,
    )

    return normalized_query, normalized_params, False


def _sqlite_column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(row[1] == column_name for row in cursor.fetchall())
