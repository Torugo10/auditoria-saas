"""Configuracoes centralizadas da aplicacao."""

from dataclasses import dataclass
from functools import lru_cache
import getpass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    backend_dir: Path
    database_path: str
    database_url: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parent.parent
    project_root = backend_dir.parent
    database_url = (
        os.getenv("LOCAL_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or f"postgresql://{getpass.getuser()}@localhost/auditoria"
    )

    return Settings(
        project_root=project_root,
        backend_dir=backend_dir,
        database_path=os.getenv("DATABASE_PATH", "/tmp/auditoria_multi_tenant.db"),
        database_url=database_url,
    )
