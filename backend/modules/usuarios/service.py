"""Servicos do dominio de usuarios."""

from __future__ import annotations

import hashlib
from typing import Callable

from backend.db.connection import connect_db
from backend.modules.usuarios.models import AuthenticatedUser


LogCallback = Callable[[int, str, str, str, str], None]


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(
    login: str,
    senha: str,
    database_url: str | None,
    database_path: str,
    log_callback: LogCallback | None = None,
) -> AuthenticatedUser | None:
    """Autentica um usuario priorizando PostgreSQL e com fallback para SQLite."""
    senha_hash = _hash_password(senha)
    conn = connect_db(database_url=database_url, database_path=database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ativo FROM administradores WHERE login = ? AND senha_hash = ?",
            (login, senha_hash),
        )
        admin = cursor.fetchone()
        if admin:
            usuario_id, ativo = admin
            if not ativo:
                _log_login_blocked(log_callback, login)
                return None
            return AuthenticatedUser(usuario_id=usuario_id, tipo="admin", login=login)

        cursor.execute(
            "SELECT id, cnpj_cpf, ativo FROM gerentes WHERE login = ? AND senha_hash = ?",
            (login, senha_hash),
        )
        gerente = cursor.fetchone()
        if gerente:
            usuario_id, cnpj_cpf, ativo = gerente
            if not ativo:
                _log_login_blocked(log_callback, login)
                return None
            return AuthenticatedUser(
                usuario_id=usuario_id,
                tipo="gerente",
                login=login,
                cnpj_cpf=cnpj_cpf,
            )

        cursor.execute(
            "SELECT id, cnpj_cpf, perfil, ativo FROM usuarios_finais WHERE login = ? AND senha_hash = ?",
            (login, senha_hash),
        )
        usuario = cursor.fetchone()
        if usuario:
            usuario_id, cnpj_cpf, perfil, ativo = usuario
            if not ativo:
                _log_login_blocked(log_callback, login)
                return None
            return AuthenticatedUser(
                usuario_id=usuario_id,
                tipo="usuario_final",
                login=login,
                cnpj_cpf=cnpj_cpf,
                perfil=perfil,
            )

        return None
    finally:
        conn.close()


def validate_active_session(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
    tipo_usuario: str,
    login: str,
) -> bool:
    """Confere se o usuario autenticado segue ativo no backend disponivel."""
    query = _resolve_active_session_query(tipo_usuario)
    conn = connect_db(database_url=database_url, database_path=database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, (usuario_id, login))
        resultado = cursor.fetchone()
    finally:
        conn.close()

    return bool(resultado and resultado[0] != 0)


def _resolve_active_session_query(tipo_usuario: str) -> str:
    if tipo_usuario == "admin":
        return "SELECT ativo FROM administradores WHERE id = ? AND login = ?"
    if tipo_usuario == "gerente":
        return "SELECT ativo FROM gerentes WHERE id = ? AND login = ?"
    return "SELECT ativo FROM usuarios_finais WHERE id = ? AND login = ?"


def _log_login_blocked(log_callback: LogCallback | None, login: str) -> None:
    if log_callback is None:
        return
    log_callback(0, "desconhecido", "", "LOGIN_BLOQUEADO", f"Tentativa: {login}")
