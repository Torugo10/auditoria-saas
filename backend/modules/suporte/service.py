"""Servicos do dominio de suporte."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

import pandas as pd

from backend.db.connection import connect_db, read_sql_query


LogCallback = Callable[[int, str, str, str, str], None]


def initialize_support_schema(*, database_url: str | None, database_path: str) -> None:
    """Cria a estrutura minima de tickets no backend disponivel."""
    conn = connect_db(database_url=database_url, database_path=database_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets_suporte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                usuario_login TEXT NOT NULL,
                usuario_email TEXT,
                tipo_problema TEXT NOT NULL,
                assunto TEXT NOT NULL,
                descricao TEXT NOT NULL,
                prioridade TEXT DEFAULT 'MEDIA',
                status TEXT DEFAULT 'ABERTO',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_resposta TIMESTAMP,
                resposta_admin TEXT,
                admin_id INTEGER,
                FOREIGN KEY(usuario_id) REFERENCES usuarios_finais(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                autor_tipo TEXT NOT NULL,
                autor_id INTEGER NOT NULL,
                mensagem TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ticket_id) REFERENCES tickets_suporte(id)
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO ticket_mensagens (ticket_id, autor_tipo, autor_id, mensagem, criado_em)
            SELECT id, 'usuario_final', usuario_id, descricao, data_criacao
            FROM tickets_suporte ticket
            WHERE NOT EXISTS (
                SELECT 1
                FROM ticket_mensagens mensagem
                WHERE mensagem.ticket_id = ticket.id
                  AND mensagem.autor_tipo = 'usuario_final'
                  AND mensagem.mensagem = ticket.descricao
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO ticket_mensagens (ticket_id, autor_tipo, autor_id, mensagem, criado_em)
            SELECT id, 'admin', COALESCE(admin_id, 0), resposta_admin, data_resposta
            FROM tickets_suporte ticket
            WHERE resposta_admin IS NOT NULL
              AND resposta_admin <> ''
              AND NOT EXISTS (
                  SELECT 1
                  FROM ticket_mensagens mensagem
                  WHERE mensagem.ticket_id = ticket.id
                    AND mensagem.autor_tipo = 'admin'
                    AND mensagem.mensagem = ticket.resposta_admin
              )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_support_ticket(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
    usuario_login: str,
    usuario_email: str,
    tipo_problema: str,
    assunto: str,
    descricao: str,
    prioridade: str = "MEDIA",
    log_callback: LogCallback | None = None,
) -> tuple[bool, str]:
    """Cria uma solicitacao de suporte para um usuario final."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tickets_suporte
            (usuario_id, usuario_login, usuario_email, tipo_problema, assunto, descricao, prioridade, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ABERTO')
            """,
            (
                usuario_id,
                usuario_login,
                usuario_email,
                tipo_problema,
                assunto,
                descricao,
                prioridade,
            ),
        )
        ticket_id = cursor.lastrowid
        _insert_ticket_message(
            cursor,
            ticket_id=ticket_id,
            autor_tipo="usuario_final",
            autor_id=usuario_id,
            mensagem=descricao,
        )
        conn.commit()
        conn.close()

        _log(
            log_callback,
            usuario_id,
            "usuario_final",
            "",
            "TICKET_SUPORTE_CRIADO",
            f"Ticket #{ticket_id} - {assunto}",
        )
        return True, f"✅ Ticket #{ticket_id} criado com sucesso! O administrador responderá em breve."
    except Exception as exc:
        return False, f"❌ Erro ao criar ticket: {str(exc)}"


def list_user_tickets(
    *,
    database_url: str | None,
    database_path: str,
    usuario_id: int,
) -> pd.DataFrame:
    """Lista os tickets abertos pelo usuario final."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        try:
            return read_sql_query(
                """
                SELECT id, tipo_problema, assunto, status, prioridade, data_criacao, resposta_admin
                FROM tickets_suporte
                WHERE usuario_id = ?
                ORDER BY data_criacao DESC
                """,
                conn,
                params=(usuario_id,),
            )
        finally:
            conn.close()
    except Exception:
        return pd.DataFrame()


def list_admin_tickets(*, database_url: str | None, database_path: str) -> pd.DataFrame:
    """Lista tickets para atendimento do administrador."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        try:
            return read_sql_query(
                """
                SELECT id, usuario_id, usuario_login, usuario_email, tipo_problema, assunto,
                       descricao, status, prioridade, data_criacao, data_resposta, resposta_admin
                FROM tickets_suporte
                ORDER BY
                    CASE prioridade
                        WHEN 'CRITICA' THEN 1
                        WHEN 'ALTA' THEN 2
                        WHEN 'MEDIA' THEN 3
                        WHEN 'BAIXA' THEN 4
                    END,
                    data_criacao DESC
                """,
                conn,
            )
        finally:
            conn.close()
    except Exception:
        return pd.DataFrame()


def answer_ticket(
    *,
    database_url: str | None,
    database_path: str,
    ticket_id: int,
    resposta_admin: str,
    admin_id: int,
    log_callback: LogCallback | None = None,
) -> tuple[bool, str]:
    """Registra a resposta do administrador para um ticket."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tickets_suporte
            SET status = 'AGUARDANDO_USUARIO', resposta_admin = ?, data_resposta = ?, admin_id = ?
            WHERE id = ?
            """,
            (resposta_admin, datetime.now(), admin_id, ticket_id),
        )
        _insert_ticket_message(
            cursor,
            ticket_id=ticket_id,
            autor_tipo="admin",
            autor_id=admin_id,
            mensagem=resposta_admin,
        )
        conn.commit()
        conn.close()

        _log(log_callback, admin_id, "admin", "", "TICKET_RESPONDIDO", f"Ticket #{ticket_id} respondido")
        return True, f"✅ Ticket #{ticket_id} respondido!"
    except Exception as exc:
        return False, f"❌ Erro ao responder: {str(exc)}"


def reply_ticket_as_user(
    *,
    database_url: str | None,
    database_path: str,
    ticket_id: int,
    usuario_id: int,
    mensagem: str,
    log_callback: LogCallback | None = None,
) -> tuple[bool, str]:
    """Adiciona uma resposta do usuario final em um ticket aberto."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM tickets_suporte WHERE id = ? AND usuario_id = ?",
            (ticket_id, usuario_id),
        )
        ticket = cursor.fetchone()
        if not ticket:
            conn.close()
            return False, "❌ Ticket não encontrado para este usuário."
        if ticket[0] == "FECHADO":
            conn.close()
            return False, "❌ Ticket fechado não permite novas respostas."

        _insert_ticket_message(
            cursor,
            ticket_id=ticket_id,
            autor_tipo="usuario_final",
            autor_id=usuario_id,
            mensagem=mensagem,
        )
        cursor.execute(
            """
            UPDATE tickets_suporte
            SET status = 'AGUARDANDO_ADMIN'
            WHERE id = ? AND usuario_id = ?
            """,
            (ticket_id, usuario_id),
        )
        conn.commit()
        conn.close()

        _log(log_callback, usuario_id, "usuario_final", "", "TICKET_USUARIO_RESPONDEU", f"Ticket #{ticket_id}")
        return True, f"✅ Resposta enviada no ticket #{ticket_id}."
    except Exception as exc:
        return False, f"❌ Erro ao responder ticket: {str(exc)}"


def close_ticket(
    *,
    database_url: str | None,
    database_path: str,
    ticket_id: int,
    admin_id: int,
    log_callback: LogCallback | None = None,
) -> tuple[bool, str]:
    """Fecha um ticket de suporte."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tickets_suporte
            SET status = 'FECHADO'
            WHERE id = ?
            """,
            (ticket_id,),
        )
        conn.commit()
        conn.close()

        _log(log_callback, admin_id, "admin", "", "TICKET_FECHADO", f"Ticket #{ticket_id} fechado")
        return True, f"✅ Ticket #{ticket_id} fechado!"
    except Exception as exc:
        return False, f"❌ Erro: {str(exc)}"


def get_ticket_statistics(*, database_url: str | None, database_path: str) -> dict[str, int]:
    """Calcula indicadores resumidos de atendimento."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tickets_suporte")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets_suporte WHERE status IN ('ABERTO', 'AGUARDANDO_ADMIN')")
        abertos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets_suporte WHERE status IN ('RESPONDIDO', 'AGUARDANDO_USUARIO')")
        respondidos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets_suporte WHERE status = 'FECHADO'")
        fechados = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM tickets_suporte WHERE prioridade = 'CRITICA' AND status IN ('ABERTO', 'AGUARDANDO_ADMIN')"
        )
        criticos = cursor.fetchone()[0]

        conn.close()
        return {
            "total": total,
            "abertos": abertos,
            "respondidos": respondidos,
            "fechados": fechados,
            "criticos": criticos,
        }
    except Exception:
        return {"total": 0, "abertos": 0, "respondidos": 0, "fechados": 0, "criticos": 0}


def get_user_email(*, database_url: str | None, database_path: str, usuario_id: int) -> str:
    """Busca o e-mail cadastrado do usuario final."""
    conn = connect_db(database_url=database_url, database_path=database_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM usuarios_finais WHERE id = ?", (usuario_id,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else "email_nao_informado@example.com"
    finally:
        conn.close()


def list_ticket_messages(
    *,
    database_url: str | None,
    database_path: str,
    ticket_id: int,
) -> pd.DataFrame:
    """Lista o historico de conversa de um ticket."""
    try:
        conn = connect_db(database_url=database_url, database_path=database_path)
        try:
            return read_sql_query(
                """
                SELECT id, ticket_id, autor_tipo, autor_id, mensagem, criado_em
                FROM ticket_mensagens
                WHERE ticket_id = ?
                ORDER BY criado_em ASC, id ASC
                """,
                conn,
                params=(ticket_id,),
            )
        finally:
            conn.close()
    except Exception:
        return pd.DataFrame()


def _insert_ticket_message(cursor, *, ticket_id: int, autor_tipo: str, autor_id: int, mensagem: str) -> None:
    cursor.execute(
        """
        INSERT INTO ticket_mensagens (ticket_id, autor_tipo, autor_id, mensagem)
        VALUES (?, ?, ?, ?)
        """,
        (ticket_id, autor_tipo, autor_id, mensagem),
    )


def _log(
    log_callback: LogCallback | None,
    usuario_id: int,
    tipo_usuario: str,
    cnpj_cpf: str,
    acao: str,
    dados_novos: str,
) -> None:
    if log_callback is not None:
        log_callback(usuario_id, tipo_usuario, cnpj_cpf, acao, dados_novos)
