from dataclasses import dataclass

from aiogram import Bot, Dispatcher

from src.config.settings import Settings
from src.notifications.manager_registry import ManagerRegistry
from src.notifications.telegram.notifier import TelegramNotificationService
from src.services.lead_service import LeadService
from src.services.nlp.base import INLPService
from src.services.validation_service import ValidationService, create_nlp_service
from src.storage.factory import create_lead_repository
from src.storage.interfaces.lead_repository import ILeadRepository


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    bot: Bot
    dispatcher: Dispatcher
    lead_service: LeadService
    validation_service: ValidationService
    nlp_service: INLPService
    lead_repository: ILeadRepository


def build_container(settings: Settings, bot: Bot, dispatcher: Dispatcher) -> AppContainer:
    validation_service = ValidationService()
    nlp_service = create_nlp_service(settings)
    lead_repository = create_lead_repository(settings)
    manager_registry = ManagerRegistry(default_chat_id=settings.manager_chat_id)
    notification_service = TelegramNotificationService(bot, manager_registry)
    lead_service = LeadService(
        repository=lead_repository,
        notification_service=notification_service,
        validation_service=validation_service,
        nlp_service=nlp_service,
    )
    return AppContainer(
        settings=settings,
        bot=bot,
        dispatcher=dispatcher,
        lead_service=lead_service,
        validation_service=validation_service,
        nlp_service=nlp_service,
        lead_repository=lead_repository,
    )
