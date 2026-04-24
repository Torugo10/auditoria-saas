"""Bootstrap da aplicacao.

Centraliza a inicializacao do projeto antes de delegar para os modulos.
"""

from backend.core.settings import get_settings
from backend.db.connection import ensure_sqlite_directory
from backend.modules.legacy import run as run_legacy_app


def bootstrap_streamlit_app() -> None:
    """Inicializa dependencias basicas e executa o app legado."""
    settings = get_settings()
    ensure_sqlite_directory(settings.database_path)
    run_legacy_app()

