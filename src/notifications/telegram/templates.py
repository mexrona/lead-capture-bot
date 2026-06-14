from datetime import datetime
from zoneinfo import ZoneInfo

from src.domain.dto.lead_response_dto import LeadResponseDTO

DEFAULT_TZ = ZoneInfo("Europe/Moscow")


def format_manager_notification(lead: LeadResponseDTO) -> str:
    created_local = lead.created_at.astimezone(DEFAULT_TZ).strftime("%Y-%m-%d %H:%M")
    lines = [
        "🆕 <b>Новый лид</b>",
        "",
        f"<b>Имя:</b> {lead.name}",
        f"<b>Телефон:</b> {lead.phone}",
        f"<b>Telegram:</b> {lead.username_display}",
        f"<b>Тип задачи:</b> {lead.task_type}",
        f"<b>Бюджет:</b> {lead.budget}",
        f"<b>Срок:</b> {lead.deadline}",
        f"<b>Комментарий:</b> {lead.comment_display}",
        "",
        f"<b>Дата:</b> {created_local}",
        f"<b>ID:</b> <code>{lead.id}</code>",
    ]
    if lead.summary:
        lines.extend(["", f"<b>AI-саммари:</b> {lead.summary}"])
    if lead.score:
        lines.append(f"<b>Оценка:</b> {lead.score}")
    return "\n".join(lines)
