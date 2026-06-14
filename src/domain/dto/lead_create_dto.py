from dataclasses import dataclass


@dataclass(slots=True)
class LeadCreateDTO:
    telegram_id: int
    username: str | None
    name: str
    phone: str
    task_type: str
    budget: str
    deadline: str
    comment: str | None
    source: str
