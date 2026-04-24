"""Estado de sessao padrao da aplicacao Streamlit."""

DEFAULT_SESSION_STATE = {
    "autenticado": False,
    "usuario": None,
    "tipo_usuario": None,
    "cnpj_cpf": None,
    "perfil": None,
    "usuario_id": None,
}


def initialize_session_state(session_state) -> None:
    """Preenche apenas as chaves ausentes."""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in session_state:
            session_state[key] = value

