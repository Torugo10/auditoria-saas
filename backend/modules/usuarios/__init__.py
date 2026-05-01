"""Dominio de autenticacao, perfis e gestao de usuarios."""

from backend.modules.usuarios.models import AuthenticatedUser
from backend.modules.usuarios.service import authenticate_user, validate_active_session
from backend.modules.usuarios.session import (
    apply_authenticated_user,
    clear_authenticated_user,
    initialize_user_session,
)
from backend.modules.usuarios.session_token import create_session_token, parse_session_token

__all__ = [
    "AuthenticatedUser",
    "apply_authenticated_user",
    "authenticate_user",
    "clear_authenticated_user",
    "create_session_token",
    "initialize_user_session",
    "parse_session_token",
    "validate_active_session",
]
