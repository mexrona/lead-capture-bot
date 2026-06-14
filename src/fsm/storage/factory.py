from pathlib import Path

from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from src.config.settings import Settings
from src.fsm.storage.sql_storage import SQLAlchemyStorage, create_sql_engine


async def create_fsm_storage(settings: Settings) -> BaseStorage:
    if settings.fsm_storage == "memory":
        return MemoryStorage()

    if settings.fsm_storage == "sqlite":
        db_path = Path(settings.fsm_sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        dsn = f"sqlite+aiosqlite:///{db_path.as_posix()}"
        engine = create_sql_engine(dsn)
        storage = SQLAlchemyStorage(engine)
        await storage.create_tables()
        return storage

    if settings.fsm_storage == "postgresql":
        engine = create_sql_engine(settings.postgres_dsn)
        storage = SQLAlchemyStorage(engine)
        await storage.create_tables()
        return storage

    raise ValueError(f"Unsupported FSM storage: {settings.fsm_storage}")
