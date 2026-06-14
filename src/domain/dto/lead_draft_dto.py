from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.config.constants import SOURCE_TELEGRAM_BOT


@dataclass
class LeadDraftDTO:
    """Temporary survey data stored in FSM context."""

    task_type: str | None = None
    budget: str | None = None
    deadline: str | None = None
    name: str | None = None
    phone: str | None = None
    comment: str | None = None
    comment_step_done: bool = False
    telegram_id: int | None = None
    username: str | None = None
    source: str = SOURCE_TELEGRAM_BOT
    is_editing: bool = False
    editing_field: str | None = None
    processing: bool = False
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        self.last_activity_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "budget": self.budget,
            "deadline": self.deadline,
            "name": self.name,
            "phone": self.phone,
            "comment": self.comment,
            "comment_step_done": self.comment_step_done,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "source": self.source,
            "is_editing": self.is_editing,
            "editing_field": self.editing_field,
            "processing": self.processing,
            "started_at": self.started_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "LeadDraftDTO":
        if not data:
            return cls()

        draft = cls(
            task_type=data.get("task_type"),
            budget=data.get("budget"),
            deadline=data.get("deadline"),
            name=data.get("name"),
            phone=data.get("phone"),
            comment=data.get("comment"),
            comment_step_done=bool(data.get("comment_step_done", False)),
            telegram_id=data.get("telegram_id"),
            username=data.get("username"),
            source=data.get("source", SOURCE_TELEGRAM_BOT),
            is_editing=bool(data.get("is_editing", False)),
            editing_field=data.get("editing_field"),
            processing=bool(data.get("processing", False)),
        )
        if started_at := data.get("started_at"):
            draft.started_at = datetime.fromisoformat(started_at)
        if last_activity := data.get("last_activity_at"):
            draft.last_activity_at = datetime.fromisoformat(last_activity)
        return draft

    def is_complete(self) -> bool:
        required = [self.task_type, self.budget, self.deadline, self.name, self.phone]
        return all(required) and self.telegram_id is not None
