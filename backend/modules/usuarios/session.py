"""Utilitarios de sessao para o dominio de usuarios."""

from backend.core.session import initialize_session_state
from backend.modules.usuarios.models import AuthenticatedUser


def initialize_user_session(session_state) -> None:
    """Inicializa as chaves padrao da sessao."""
    initialize_session_state(session_state)


def apply_authenticated_user(session_state, user: AuthenticatedUser) -> None:
    """Grava os dados do usuario autenticado na sessao."""
    session_state.autenticado = True
    session_state.usuario = user.login
    session_state.tipo_usuario = user.tipo
    session_state.cnpj_cpf = user.cnpj_cpf
    session_state.perfil = user.perfil
    session_state.usuario_id = user.usuario_id


def clear_authenticated_user(session_state) -> None:
    """Limpa o estado autenticado da sessao."""
    session_state.autenticado = False
    session_state.usuario = None
    session_state.tipo_usuario = None
    session_state.cnpj_cpf = None
    session_state.perfil = None
    session_state.usuario_id = None

