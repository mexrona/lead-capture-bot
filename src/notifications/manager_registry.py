from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ManagerContact:
    chat_id: int
    name: str | None = None


class ManagerRegistry:
    """Routes notifications to managers. Single manager now, extensible later."""

    def __init__(self, default_chat_id: int) -> None:
        self._default_chat_id = default_chat_id

    def get_recipients(self, *, task_type: str | None = None) -> list[ManagerContact]:
        # Future: route by task_type, round-robin, schedule, etc.
        _ = task_type
        return [ManagerContact(chat_id=self._default_chat_id)]
