from dataclasses import dataclass


@dataclass(slots=True)
class ParsedMessage:
    intent: str | None = None
    mapped_value: str | None = None
    confidence: float = 0.0


@dataclass(slots=True)
class PartialLeadData:
    task_type: str | None = None
    budget: str | None = None
    deadline: str | None = None
    name: str | None = None
    phone: str | None = None
    comment: str | None = None


@dataclass(slots=True)
class LeadScore:
    label: str
    value: float
    details: str | None = None
