from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.lead import Lead


@dataclass(slots=True)
class LeadStorageRowDTO:
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

    @classmethod
    def from_lead(cls, lead: Lead) -> "LeadStorageRowDTO":
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
        )

    def to_row(self, columns: list[str]) -> list[str]:
        data = {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "telegram_id": str(self.telegram_id),
            "username": self.username or "",
            "name": self.name,
            "phone": self.phone,
            "task_type": self.task_type,
            "budget": self.budget,
            "deadline": self.deadline,
            "comment": self.comment or "",
            "status": self.status,
            "source": self.source,
        }
        return [data[column] for column in columns]
