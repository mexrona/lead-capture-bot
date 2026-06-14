from abc import ABC, abstractmethod

from src.domain.entities.lead import Lead
from src.services.nlp.models import LeadScore, ParsedMessage, PartialLeadData


class INLPService(ABC):
    """Abstract NLP/AI service. FSM does not depend on this interface."""

    @abstractmethod
    async def parse_user_message(self, text: str, current_state: str) -> ParsedMessage:
        """Map free-text input to a button choice for the current FSM state."""

    @abstractmethod
    async def extract_lead_data(self, text: str) -> PartialLeadData:
        """Extract structured lead fields from a single free-form message."""

    @abstractmethod
    async def generate_lead_summary(self, lead: Lead) -> str:
        """Generate a short manager-facing summary."""

    @abstractmethod
    async def score_lead(self, lead: Lead) -> LeadScore:
        """Score lead quality/priority."""
