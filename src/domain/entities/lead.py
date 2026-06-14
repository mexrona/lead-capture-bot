from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.enums.lead_status import LeadStatus


@dataclass(slots=True)
class Lead:
    """Domain entity representing a persisted lead."""

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
    status: LeadStatus
    source: str
