"""Ponte para o monolito legado.

O objetivo deste modulo e manter compatibilidade enquanto a logica e
extraida gradualmente para a nova arquitetura.
"""

from importlib import import_module, reload
import sys


LEGACY_MODULE = "backend.auditoria_fiscal"


def run() -> None:
    """Executa o app legado dentro da nova estrutura."""
    if LEGACY_MODULE in sys.modules:
        reload(sys.modules[LEGACY_MODULE])
        return

    import_module(LEGACY_MODULE)
