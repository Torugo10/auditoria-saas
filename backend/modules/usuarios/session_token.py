"""Token assinado para restaurar sessao apos refresh do Streamlit."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from backend.modules.usuarios.models import AuthenticatedUser


def create_session_token(user: AuthenticatedUser, secret_key: str, ttl_seconds: int) -> str:
    expires_at = int(time.time()) + ttl_seconds
    payload = {
        "usuario_id": user.usuario_id,
        "tipo": user.tipo,
        "login": user.login,
        "cnpj_cpf": user.cnpj_cpf,
        "perfil": user.perfil,
        "exp": expires_at,
    }
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(encoded_payload, secret_key)
    return f"{encoded_payload}.{signature}"


def parse_session_token(token: str | None, secret_key: str | None) -> AuthenticatedUser | None:
    if not token or not secret_key or "." not in token:
        return None

    encoded_payload, signature = token.split(".", 1)
    expected_signature = _sign(encoded_payload, secret_key)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(_base64url_decode(encoded_payload))
    except (ValueError, TypeError):
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    return AuthenticatedUser(
        usuario_id=int(payload["usuario_id"]),
        tipo=str(payload["tipo"]),
        login=str(payload["login"]),
        cnpj_cpf=payload.get("cnpj_cpf"),
        perfil=payload.get("perfil"),
    )


def _sign(encoded_payload: str, secret_key: str) -> str:
    digest = hmac.new(secret_key.encode(), encoded_payload.encode(), hashlib.sha256).digest()
    return _base64url_encode(digest)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _base64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding).decode()
