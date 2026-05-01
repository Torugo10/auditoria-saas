"""Telas Streamlit do modulo de suporte."""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from backend.core.settings import get_settings
from backend.modules.suporte.service import (
    LogCallback,
    answer_ticket,
    close_ticket,
    create_support_ticket,
    get_ticket_statistics,
    get_user_email,
    list_admin_tickets,
    list_ticket_messages,
    list_user_tickets,
    reply_ticket_as_user,
)


STATUS_OPTIONS = ["ABERTO", "AGUARDANDO_ADMIN", "AGUARDANDO_USUARIO", "RESPONDIDO", "FECHADO"]
PRIORITY_OPTIONS = ["CRITICA", "ALTA", "MEDIA", "BAIXA"]
PRIORITY_ORDER = {"CRITICA": 1, "ALTA": 2, "MEDIA": 3, "BAIXA": 4}
SUPPORT_POLLING_INTERVAL = "8s"


def _support_polling_fragment(func):
    fragment = getattr(st, "fragment", None)
    if fragment is None:
        return func
    return fragment(run_every=SUPPORT_POLLING_INTERVAL)(func)


def _rerun_support_fragment() -> None:
    try:
        st.rerun(scope="fragment")
    except TypeError:
        st.rerun()
    except Exception as exc:
        if exc.__class__.__name__ == "StreamlitAPIException":
            st.rerun()
        raise


def render_admin_support_panel(
    *,
    database_url: str | None,
    database_path: str,
    admin_id: int,
    log_callback: LogCallback,
) -> None:
    """Renderiza a central de atendimento do administrador."""
    st.subheader("🎟️ Gerenciamento de Tickets de Suporte")
    _show_admin_flash_message()
    _render_admin_support_content(
        database_url=database_url,
        database_path=database_path,
        admin_id=admin_id,
        log_callback=log_callback,
    )


@_support_polling_fragment
def _render_admin_support_content(
    *,
    database_url: str | None,
    database_path: str,
    admin_id: int,
    log_callback: LogCallback,
) -> None:
    st.caption(f"Atualização automática a cada {SUPPORT_POLLING_INTERVAL}.")
    _show_admin_flash_message()

    stats = get_ticket_statistics(database_url=database_url, database_path=database_path)
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)

    with col_stat1:
        st.metric("📊 Total", stats["total"])
    with col_stat2:
        st.metric(
            "⏳ Abertos",
            stats["abertos"],
            delta=f"🔴 {stats['criticos']} críticos" if stats["criticos"] > 0 else "✅ OK",
        )
    with col_stat3:
        st.metric("✅ Respondidos", stats["respondidos"])
    with col_stat4:
        st.metric("🔒 Fechados", stats["fechados"])
    with col_stat5:
        if stats["criticos"] > 0:
            st.error(f"🔴 {stats['criticos']} Crítico(s)")
        else:
            st.success("✅ Sem críticos")

    st.divider()

    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        filtro_status_admin = st.multiselect(
            "Filtrar por Status:",
            STATUS_OPTIONS,
            default=[],
            placeholder="Todos",
            key="filtro_status_admin",
        )
    with col_filtro2:
        filtro_prioridade = st.multiselect(
            "Filtrar por Prioridade:",
            PRIORITY_OPTIONS,
            default=[],
            placeholder="Todas",
            key="filtro_prioridade",
        )
    with col_filtro3:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ["Data (Mais Recente)", "Prioridade", "Status"],
            key="ordenar_por",
        )

    st.divider()

    df_tickets = list_admin_tickets(database_url=database_url, database_path=database_path)
    if df_tickets.empty:
        st.info("📭 Nenhum ticket de suporte ainda.")
        return

    df_filtrado = df_tickets.copy()
    if filtro_status_admin:
        df_filtrado = df_filtrado[df_filtrado["status"].isin(filtro_status_admin)]
    if filtro_prioridade:
        df_filtrado = df_filtrado[df_filtrado["prioridade"].isin(filtro_prioridade)]

    if df_filtrado.empty:
        st.info("📭 Nenhum ticket encontrado com esses filtros.")
        return

    df_filtrado = _sort_admin_tickets(df_filtrado, ordenar_por)
    st.write(f"**Total de tickets encontrados:** {len(df_filtrado)}")

    for _, row in df_filtrado.iterrows():
        _render_admin_ticket_row(
            row=row,
            database_url=database_url,
            database_path=database_path,
            admin_id=admin_id,
            log_callback=log_callback,
        )


def render_user_support_panel(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
    usuario_login: str,
    log_callback: LogCallback,
) -> None:
    """Renderiza a area de suporte para usuario final."""
    st.header("🆘 Suporte ao Sistema")
    _show_user_flash_message()
    st.info(
        "💡 Abra uma solicitação de suporte e nossa equipe responderá dentro do painel. "
        "Você poderá acompanhar o status em tempo real."
    )

    tab_novo, tab_meus = st.tabs(["➕ Nova Solicitação", "📋 Meus Tickets"])

    with tab_novo:
        _render_new_ticket_form(
            database_url=database_url,
            database_path=database_path,
            usuario_id=usuario_id,
            usuario_login=usuario_login,
            log_callback=log_callback,
        )

    with tab_meus:
        _render_user_tickets(
            database_url=database_url,
            database_path=database_path,
            usuario_id=usuario_id,
            log_callback=log_callback,
        )


def _render_new_ticket_form(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
    usuario_login: str,
    log_callback: LogCallback,
) -> None:
    st.subheader("Abrir Nova Solicitação")

    with st.form("form_ticket_suporte"):
        tipo_problema = st.selectbox(
            "Tipo de Problema:",
            [
                "❓ Dúvida",
                "🐛 Bug/Erro",
                "🔧 Funcionalidade",
                "📋 Relatório",
                "🔐 Acesso",
                "⚡ Performance",
                "💾 Dados",
                "📞 Outro",
            ],
        )

        assunto = st.text_input(
            "Assunto (máx. 100 caracteres):",
            max_chars=100,
            placeholder="Ex: Erro ao fazer download do relatório",
        )

        descricao = st.text_area(
            "Descrição Detalhada:",
            height=200,
            placeholder=(
                "Descreva o problema com detalhes:\n"
                "- O que você estava fazendo?\n"
                "- Qual é o erro exato?\n"
                "- Quando ocorreu?"
            ),
            max_chars=2000,
        )

        col1, col2 = st.columns(2)
        with col1:
            prioridade = st.radio(
                "Prioridade:",
                ["🔴 CRÍTICA", "🟠 ALTA", "🟡 MÉDIA", "🟢 BAIXA"],
                horizontal=False,
            )
        with col2:
            st.info(
                "**Prioridades:**\n\n"
                "🔴 Crítica: Sistema inoperável\n\n"
                "🟠 Alta: Funcionalidade prejudicada\n\n"
                "🟡 Média: Incômodo menor\n\n"
                "🟢 Baixa: Dúvida/Sugestão"
            )

        prioridade_mapa = {
            "🔴 CRÍTICA": "CRITICA",
            "🟠 ALTA": "ALTA",
            "🟡 MÉDIA": "MEDIA",
            "🟢 BAIXA": "BAIXA",
        }

        if st.form_submit_button("📤 Enviar Solicitação", width="stretch"):
            if not all([assunto, descricao]):
                st.error("❌ Preencha todos os campos obrigatórios!")
                return

            email_usuario = get_user_email(
                database_url=database_url,
                database_path=database_path,
                usuario_id=usuario_id,
            )
            sucesso, mensagem = create_support_ticket(
                database_url=database_url,
                database_path=database_path,
                usuario_id=usuario_id,
                usuario_login=usuario_login,
                usuario_email=email_usuario,
                tipo_problema=tipo_problema,
                assunto=assunto,
                descricao=descricao,
                prioridade=prioridade_mapa[prioridade],
                log_callback=log_callback,
            )

            if sucesso:
                st.success(mensagem)
                st.balloons()
            else:
                st.error(mensagem)


@_support_polling_fragment
def _render_user_tickets(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
    log_callback: LogCallback,
) -> None:
    st.subheader("Meus Tickets de Suporte")
    st.caption(f"Atualização automática a cada {SUPPORT_POLLING_INTERVAL}.")
    _show_user_flash_message()

    df_meus_tickets = list_user_tickets(
        database_url=database_url,
        database_path=database_path,
        usuario_id=usuario_id,
    )

    if df_meus_tickets.empty:
        st.info("📭 Você ainda não abriu nenhum ticket de suporte.")
        return

    filtro_status = st.selectbox(
        "Filtrar por Status:",
        ["Todos", *STATUS_OPTIONS],
        key="filtro_status_usuario",
    )

    if filtro_status != "Todos":
        df_filtrado = df_meus_tickets[df_meus_tickets["status"] == filtro_status]
    else:
        df_filtrado = df_meus_tickets

    if df_filtrado.empty:
        st.info(f"📭 Nenhum ticket com status '{filtro_status}'")
        return

    for _, row in df_filtrado.iterrows():
        emoji_status = _status_icon(row["status"])
        emoji_prio = _priority_icon(row["prioridade"])

        with st.expander(f"{emoji_status} #{row['id']} - {row['assunto']} {emoji_prio}"):
            st.write(f"**Tipo:** {row['tipo_problema']}")
            st.write(f"**Status:** {_status_label(row['status'])}")
            st.write(f"**Prioridade:** {row['prioridade']}")
            st.write(f"**Criado em:** {_format_datetime(row['data_criacao'])}")

            st.divider()
            _render_ticket_messages(
                row=row,
                database_url=database_url,
                database_path=database_path,
            )

            if row["status"] != "FECHADO":
                st.divider()
                _render_user_reply_form(
                    ticket_id=int(row["id"]),
                    usuario_id=usuario_id,
                    database_url=database_url,
                    database_path=database_path,
                    log_callback=log_callback,
                )


def _render_ticket_messages(*, row, database_url: str | None, database_path: str) -> None:
    messages = list_ticket_messages(
        database_url=database_url,
        database_path=database_path,
        ticket_id=int(row["id"]),
    )

    if messages.empty:
        st.markdown("**Conversa:**")
        st.info(row["descricao"])
        resposta_admin = row.get("resposta_admin")
        if resposta_admin is not None and not pd.isna(resposta_admin) and resposta_admin:
            st.success(resposta_admin)
        return

    st.markdown("**Conversa:**")
    for _, message in messages.iterrows():
        autor_tipo = message["autor_tipo"]
        criado_em = _format_datetime(message["criado_em"])
        if autor_tipo == "admin":
            st.success(f"**Admin** · {criado_em}\n\n{message['mensagem']}")
        else:
            st.info(f"**Usuário** · {criado_em}\n\n{message['mensagem']}")


def _render_user_reply_form(
    *,
    ticket_id: int,
    usuario_id: int,
    database_url: str | None,
    database_path: str,
    log_callback: LogCallback,
) -> None:
    reply_key = _ticket_reply_widget_key("usuario", ticket_id)
    with st.form(f"form_resposta_usuario_{ticket_id}"):
        mensagem = st.text_area(
            "Responder ao suporte:",
            height=120,
            placeholder="Digite sua resposta ou complemento para o atendimento...",
            key=reply_key,
        )
        if st.form_submit_button("Enviar resposta", width="stretch"):
            _handle_user_reply(
                ticket_id=ticket_id,
                usuario_id=usuario_id,
                mensagem=mensagem,
                database_url=database_url,
                database_path=database_path,
                log_callback=log_callback,
            )


def _handle_user_reply(
    *,
    ticket_id: int,
    usuario_id: int,
    mensagem: str,
    database_url: str | None,
    database_path: str,
    log_callback: LogCallback,
) -> None:
    if not mensagem.strip():
        st.error("❌ Digite uma resposta.")
        return

    sucesso, msg = reply_ticket_as_user(
        database_url=database_url,
        database_path=database_path,
        ticket_id=ticket_id,
        usuario_id=usuario_id,
        mensagem=mensagem,
        log_callback=log_callback,
    )
    if sucesso:
        _reset_ticket_reply_widget("usuario", ticket_id)
        _flash_user_message(msg)
        return
    st.error(msg)


def _render_admin_ticket_row(
    *,
    row,
    database_url: str | None,
    database_path: str,
    admin_id: int,
    log_callback: LogCallback,
) -> None:
    emoji_status = _status_icon(row["status"])
    emoji_prio = _priority_icon(row["prioridade"])

    with st.expander(f"{emoji_status} #{row['id']} - {row['assunto']} {emoji_prio} - {row['usuario_login']}"):
        col_det1, col_det2 = st.columns([2, 1])

        with col_det1:
            st.write(f"**👤 Usuário:** {row['usuario_login']}")
            st.write(f"**📧 E-mail:** {row['usuario_email']}")
            st.write(f"**📝 Tipo:** {row['tipo_problema']}")
            st.write(f"**📊 Prioridade:** {row['prioridade']}")
            st.write(f"**📅 Criado em:** {_format_datetime(row['data_criacao'])}")

            if row["status"] in ("RESPONDIDO", "AGUARDANDO_USUARIO"):
                st.write(f"**✅ Respondido em:** {_format_datetime(row['data_resposta'])}")

        with col_det2:
            st.write(f"**Status:** {_status_label(row['status'])}")
            if row["status"] in ("ABERTO", "AGUARDANDO_ADMIN"):
                st.error("⏳ Pendente")
            elif row["status"] in ("RESPONDIDO", "AGUARDANDO_USUARIO"):
                st.info("✅ Aguardando usuário")
            else:
                st.success("🔒 Fechado")

        st.divider()
        _render_ticket_messages(
            row=row,
            database_url=database_url,
            database_path=database_path,
        )

        st.divider()

        if row["status"] != "FECHADO":
            _render_admin_answer_form(
                row=row,
                database_url=database_url,
                database_path=database_path,
                admin_id=admin_id,
                log_callback=log_callback,
            )


def _render_admin_answer_form(
    *,
    row,
    database_url: str | None,
    database_path: str,
    admin_id: int,
    log_callback: LogCallback,
) -> None:
    reply_key = _ticket_reply_widget_key("admin", int(row["id"]))
    with st.form(f"form_resposta_{row['id']}"):
        resposta = st.text_area(
            "Sua Resposta:",
            height=150,
            placeholder="Digite a resposta para o usuário...",
            key=reply_key,
        )

        col_resp1, col_resp2, col_resp3 = st.columns(3)

        with col_resp1:
            if st.form_submit_button("✅ Responder", width="stretch"):
                _handle_answer(
                    row["id"],
                    resposta,
                    database_url,
                    database_path,
                    admin_id,
                    log_callback,
                    close_after=False,
                )

        with col_resp2:
            if st.form_submit_button("🔒 Responder & Fechar", width="stretch"):
                _handle_answer(
                    row["id"],
                    resposta,
                    database_url,
                    database_path,
                    admin_id,
                    log_callback,
                    close_after=True,
                )

        with col_resp3:
            if st.form_submit_button("❌ Fechar sem Responder", width="stretch"):
                sucesso, msg = close_ticket(
                    database_url=database_url,
                    database_path=database_path,
                    ticket_id=row["id"],
                    admin_id=admin_id,
                    log_callback=log_callback,
                )
                if sucesso:
                    _reset_ticket_reply_widget("admin", int(row["id"]))
                    _flash_admin_message(msg)
                    return
                st.error(msg)


def _handle_answer(
    ticket_id: int,
    resposta: str,
    database_url: str | None,
    database_path: str,
    admin_id: int,
    log_callback: LogCallback,
    *,
    close_after: bool,
) -> None:
    if not resposta.strip():
        st.error("❌ Digite uma resposta!")
        return

    sucesso, msg = answer_ticket(
        database_url=database_url,
        database_path=database_path,
        ticket_id=ticket_id,
        resposta_admin=resposta,
        admin_id=admin_id,
        log_callback=log_callback,
    )
    if not sucesso:
        st.error(msg)
        return

    if not close_after:
        _reset_ticket_reply_widget("admin", ticket_id)
        _flash_admin_message(msg)
        return

    sucesso2, msg2 = close_ticket(
        database_url=database_url,
        database_path=database_path,
        ticket_id=ticket_id,
        admin_id=admin_id,
        log_callback=log_callback,
    )
    if sucesso2:
        _reset_ticket_reply_widget("admin", ticket_id)
        _flash_admin_message(f"{msg}\n{msg2}")
    else:
        st.error(msg2)


def _flash_admin_message(message: str) -> None:
    st.session_state.flash_suporte_admin = message
    _rerun_support_fragment()


def _show_admin_flash_message() -> None:
    message = st.session_state.pop("flash_suporte_admin", None)
    if message:
        st.success(message)


def _flash_user_message(message: str) -> None:
    st.session_state.flash_suporte_usuario = message
    _rerun_support_fragment()


def _show_user_flash_message() -> None:
    message = st.session_state.pop("flash_suporte_usuario", None)
    if message:
        st.success(message)


def _ticket_reply_widget_key(author: str, ticket_id: int) -> str:
    version_key = f"suporte_reply_version_{author}_{ticket_id}"
    version = st.session_state.get(version_key, 0)
    return f"suporte_reply_{author}_{ticket_id}_{version}"


def _reset_ticket_reply_widget(author: str, ticket_id: int) -> None:
    version_key = f"suporte_reply_version_{author}_{ticket_id}"
    st.session_state[version_key] = st.session_state.get(version_key, 0) + 1


def _sort_admin_tickets(df_tickets: pd.DataFrame, ordenar_por: str) -> pd.DataFrame:
    if ordenar_por == "Prioridade":
        df_tickets["ordem_prioridade"] = df_tickets["prioridade"].map(PRIORITY_ORDER).fillna(99)
        return df_tickets.sort_values(["ordem_prioridade", "data_criacao"], ascending=[True, False])
    if ordenar_por == "Status":
        return df_tickets.sort_values(["status", "data_criacao"], ascending=[True, False])
    return df_tickets.sort_values("data_criacao", ascending=False)


def _status_icon(status: str) -> str:
    if status in ("ABERTO", "AGUARDANDO_ADMIN"):
        return "⏳"
    if status in ("RESPONDIDO", "AGUARDANDO_USUARIO"):
        return "✅"
    return "🔒"


def _status_label(status: str) -> str:
    labels = {
        "ABERTO": "Aberto",
        "AGUARDANDO_ADMIN": "Aguardando admin",
        "AGUARDANDO_USUARIO": "Aguardando usuário",
        "RESPONDIDO": "Respondido",
        "FECHADO": "Fechado",
    }
    return labels.get(status, status)


def _priority_icon(prioridade: str) -> str:
    if prioridade == "CRITICA":
        return "🔴"
    if prioridade == "ALTA":
        return "🟠"
    if prioridade == "MEDIA":
        return "🟡"
    return "🟢"


def _format_datetime(value) -> str:
    if value is None or pd.isna(value):
        return "-"

    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return str(value)

    timezone = ZoneInfo(get_settings().app_timezone)
    return timestamp.tz_convert(timezone).strftime("%d/%m/%Y %H:%M")
