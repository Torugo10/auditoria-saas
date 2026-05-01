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
    app_timezone: str
    secret_key: str | None
    session_ttl_seconds: int
    bootstrap_admin_login: str | None
    bootstrap_admin_password: str | None
    bootstrap_admin_email: str | None
    bootstrap_admin_name: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parent.parent
    project_root = backend_dir.parent
    _load_dotenv(project_root)
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
        app_timezone=os.getenv("APP_TIMEZONE", "America/Fortaleza"),
        secret_key=os.getenv("SECRET_KEY"),
        session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", str(60 * 60 * 24 * 7))),
        bootstrap_admin_login=os.getenv("BOOTSTRAP_ADMIN_LOGIN"),
        bootstrap_admin_password=os.getenv("BOOTSTRAP_ADMIN_PASSWORD"),
        bootstrap_admin_email=os.getenv("BOOTSTRAP_ADMIN_EMAIL"),
        bootstrap_admin_name=os.getenv("BOOTSTRAP_ADMIN_NAME"),
    )


def _load_dotenv(project_root: Path) -> None:
    env_path = project_root / ".env"

    try:
        from dotenv import load_dotenv
    except ImportError:
        _load_dotenv_without_dependency(env_path)
        return

    load_dotenv(env_path)


def _load_dotenv_without_dependency(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value
