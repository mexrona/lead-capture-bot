from abc import ABC, abstractmethod

from src.domain.dto.lead_response_dto import LeadResponseDTO


class INotificationService(ABC):
    @abstractmethod
    async def notify_managers(self, lead: LeadResponseDTO) -> None:
        """Send lead notification to all configured managers."""
