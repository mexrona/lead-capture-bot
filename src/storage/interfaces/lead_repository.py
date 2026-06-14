from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.lead import Lead
from src.domain.enums.lead_status import LeadStatus


class ILeadRepository(ABC):
    @abstractmethod
    async def save(self, lead: Lead) -> Lead:
        """Persist a new lead and return it."""

    @abstractmethod
    async def update_status(self, lead_id: UUID, status: LeadStatus) -> None:
        """Update lead status (for future CRM sync)."""
