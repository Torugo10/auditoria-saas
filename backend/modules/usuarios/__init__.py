"""Dominio de autenticacao, perfis e gestao de usuarios."""

from backend.modules.usuarios.models import AuthenticatedUser
from backend.modules.usuarios.service import authenticate_user, validate_active_session
from backend.modules.usuarios.session import (
    apply_authenticated_user,
    clear_authenticated_user,
    initialize_user_session,
)

__all__ = [
    "AuthenticatedUser",
    "apply_authenticated_user",
    "authenticate_user",
    "clear_authenticated_user",
    "initialize_user_session",
    "validate_active_session",
]
