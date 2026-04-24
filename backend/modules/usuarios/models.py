"""Modelos do dominio de usuarios."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    """Representa um usuario autenticado na aplicacao."""

    usuario_id: int
    tipo: str
    login: str
    cnpj_cpf: str | None = None
    perfil: str | None = None

