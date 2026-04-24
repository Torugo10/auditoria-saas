"""Ponte para o monolito legado.

O objetivo deste modulo e manter compatibilidade enquanto a logica e
extraida gradualmente para a nova arquitetura.
"""

from importlib import import_module


LEGACY_MODULE = "backend.auditoria_fiscal"


def run() -> None:
    """Executa o app legado dentro da nova estrutura."""
    import_module(LEGACY_MODULE)

