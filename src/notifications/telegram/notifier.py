import asyncio
import logging

from aiogram import Bot

from src.domain.dto.lead_response_dto import LeadResponseDTO
from src.notifications.interfaces.notification_service import INotificationService
from src.notifications.manager_registry import ManagerRegistry
from src.notifications.telegram.templates import format_manager_notification

logger = logging.getLogger(__name__)


class TelegramNotificationService(INotificationService):
    def __init__(self, bot: Bot, manager_registry: ManagerRegistry) -> None:
        self._bot = bot
        self._manager_registry = manager_registry

    async def notify_managers(self, lead: LeadResponseDTO) -> None:
        text = format_manager_notification(lead)
        recipients = self._manager_registry.get_recipients(task_type=lead.task_type)

        errors: list[Exception] = []
        for recipient in recipients:
            try:
                await self._bot.send_message(
                    chat_id=recipient.chat_id,
                    text=text,
                    parse_mode="HTML",
                )
            except Exception as exc:
                logger.exception(
                    "Failed to notify manager chat_id=%s for lead %s",
                    recipient.chat_id,
                    lead.id,
                )
                errors.append(exc)

        if errors:
            raise NotificationDeliveryError(
                f"Failed to deliver notification for lead {lead.id}"
            ) from errors[0]


class NotificationDeliveryError(Exception):
    """Raised when manager notification could not be delivered."""


async def notify_with_retry(
    service: INotificationService,
    lead: LeadResponseDTO,
    *,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            await service.notify_managers(lead)
            return
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Notification attempt %s/%s failed for lead %s",
                attempt,
                max_attempts,
                lead.id,
            )
            if attempt < max_attempts:
                await asyncio.sleep(delay_seconds * attempt)
    if last_error:
        raise last_error
