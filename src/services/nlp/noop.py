from src.domain.entities.lead import Lead
from src.services.nlp.base import INLPService
from src.services.nlp.models import LeadScore, ParsedMessage, PartialLeadData


class NoOpNLPService(INLPService):
    """Default stub: AI disabled, bot works unchanged."""

    async def parse_user_message(self, text: str, current_state: str) -> ParsedMessage:
        _ = text, current_state
        return ParsedMessage()

    async def extract_lead_data(self, text: str) -> PartialLeadData:
        _ = text
        return PartialLeadData()

    async def generate_lead_summary(self, lead: Lead) -> str:
        _ = lead
        return ""

    async def score_lead(self, lead: Lead) -> LeadScore:
        _ = lead
        return LeadScore(label="unknown", value=0.0)
