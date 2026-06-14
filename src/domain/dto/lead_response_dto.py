from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.lead import Lead


@dataclass(slots=True)
class LeadResponseDTO:
    id: UUID
    created_at: datetime
    telegram_id: int
    username: str | None
    name: str
    phone: str
    task_type: str
    budget: str
    deadline: str
    comment: str | None
    status: str
    source: str
    summary: str | None = None
    score: str | None = None

    @property
    def username_display(self) -> str:
        if not self.username:
            return "не указан"
        return self.username if self.username.startswith("@") else f"@{self.username}"

    @property
    def comment_display(self) -> str:
        return self.comment if self.comment else "—"

    @classmethod
    def from_lead(
        cls,
        lead: Lead,
        *,
        summary: str | None = None,
        score: str | None = None,
    ) -> "LeadResponseDTO":
        return cls(
            id=lead.id,
            created_at=lead.created_at,
            telegram_id=lead.telegram_id,
            username=lead.username,
            name=lead.name,
            phone=lead.phone,
            task_type=lead.task_type,
            budget=lead.budget,
            deadline=lead.deadline,
            comment=lead.comment,
            status=lead.status.value,
            source=lead.source,
            summary=summary,
            score=score,
        )
