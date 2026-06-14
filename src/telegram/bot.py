from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage

from src.app.container import AppContainer, build_container
from src.config.settings import Settings
from src.telegram.middlewares.error_handler import ErrorHandlerMiddleware, on_error
from src.telegram.middlewares.services import ServicesMiddleware
from src.telegram.routers import cancel, fallback, review, start, survey


def setup_app(settings: Settings, storage: BaseStorage) -> AppContainer:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=storage)
    container = build_container(settings, bot, dispatcher)

    dispatcher.errors.register(on_error)
    dispatcher.message.middleware(ServicesMiddleware(container))
    dispatcher.callback_query.middleware(ServicesMiddleware(container))
    dispatcher.message.middleware(ErrorHandlerMiddleware())
    dispatcher.callback_query.middleware(ErrorHandlerMiddleware())

    dispatcher.include_router(start.router)
    dispatcher.include_router(cancel.router)
    dispatcher.include_router(survey.router)
    dispatcher.include_router(review.router)
    dispatcher.include_router(fallback.router)

    return container
