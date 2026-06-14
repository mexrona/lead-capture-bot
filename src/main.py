import asyncio
import logging
import sys

from src.config.settings import get_settings
from src.fsm.storage.factory import create_fsm_storage
from src.telegram.bot import setup_app


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    storage = await create_fsm_storage(settings)
    container = setup_app(settings, storage)

    logger = logging.getLogger(__name__)
    logger.info("Lead Capture Bot started")

    try:
        await container.dispatcher.start_polling(container.bot)
    finally:
        await storage.close()
        await container.bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
