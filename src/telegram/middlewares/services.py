from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.app.container import AppContainer


class ServicesMiddleware(BaseMiddleware):
    def __init__(self, container: AppContainer) -> None:
        self._container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["container"] = self._container
        data["lead_service"] = self._container.lead_service
        data["validation_service"] = self._container.validation_service
        data["nlp_service"] = self._container.nlp_service
        data["settings"] = self._container.settings
        return await handler(event, data)
