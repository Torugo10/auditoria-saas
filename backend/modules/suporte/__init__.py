"""Dominio de tickets e atendimento ao usuario."""

from backend.modules.suporte.service import (
    answer_ticket,
    close_ticket,
    create_support_ticket,
    get_ticket_statistics,
    get_user_email,
    initialize_support_schema,
    list_admin_tickets,
    list_ticket_messages,
    list_user_tickets,
    reply_ticket_as_user,
)
from backend.modules.suporte.ui import render_admin_support_panel, render_user_support_panel

__all__ = [
    "answer_ticket",
    "close_ticket",
    "create_support_ticket",
    "get_ticket_statistics",
    "get_user_email",
    "initialize_support_schema",
    "list_admin_tickets",
    "list_ticket_messages",
    "list_user_tickets",
    "reply_ticket_as_user",
    "render_admin_support_panel",
    "render_user_support_panel",
]
