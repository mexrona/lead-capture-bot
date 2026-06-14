import json
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder, KeyBuilder, StateType, StorageKey


class Base(DeclarativeBase):
    pass


class FSMRecord(Base):
    __tablename__ = "fsm_states"

    key: Mapped[str] = mapped_column(String(512), primary_key=True)
    state: Mapped[str | None] = mapped_column(String(256), nullable=True)
    data: Mapped[str] = mapped_column(Text, default="{}")


class SQLAlchemyStorage(BaseStorage):
    """FSM storage backed by SQLite or PostgreSQL via SQLAlchemy."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        key_builder: KeyBuilder | None = None,
    ) -> None:
        self._engine = engine
        self._session_factory = async_sessionmaker(engine, expire_on_commit=False)
        self._key_builder = key_builder or DefaultKeyBuilder()

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def resolve_key(self, key: StorageKey) -> str:
        return self._key_builder.build(key)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        record_key = self.resolve_key(key)
        async with self._session_factory() as session:
            record = await session.get(FSMRecord, record_key)
            if record is None:
                record = FSMRecord(key=record_key, state=None, data="{}")
                session.add(record)
            record.state = state.state if hasattr(state, "state") else state
            await session.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        record_key = self.resolve_key(key)
        async with self._session_factory() as session:
            record = await session.get(FSMRecord, record_key)
            return record.state if record else None

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        record_key = self.resolve_key(key)
        async with self._session_factory() as session:
            record = await session.get(FSMRecord, record_key)
            if record is None:
                record = FSMRecord(key=record_key, state=None, data="{}")
                session.add(record)
            record.data = json.dumps(data, ensure_ascii=False)
            await session.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        record_key = self.resolve_key(key)
        async with self._session_factory() as session:
            record = await session.get(FSMRecord, record_key)
            if record is None or not record.data:
                return {}
            return json.loads(record.data)

    async def close(self) -> None:
        await self._engine.dispose()

    async def clear(self, key: StorageKey) -> None:
        record_key = self.resolve_key(key)
        async with self._session_factory() as session:
            record = await session.get(FSMRecord, record_key)
            if record:
                await session.delete(record)
                await session.commit()

    async def wait_closed(self) -> None:
        return None


def create_sql_engine(dsn: str) -> AsyncEngine:
    return create_async_engine(dsn, echo=False)
