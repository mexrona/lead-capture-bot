import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import ErrorEvent, TelegramObject

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Unhandled error while processing update")
            raise


async def on_error(event: ErrorEvent) -> None:
    logger.exception(
        "Dispatcher error for update %s",
        event.update.update_id,
        exc_info=event.exception,
    )
