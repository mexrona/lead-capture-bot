import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.domain.dto.lead_create_dto import LeadCreateDTO
from src.domain.dto.lead_draft_dto import LeadDraftDTO
from src.domain.dto.lead_response_dto import LeadResponseDTO
from src.domain.entities.lead import Lead
from src.domain.enums.lead_status import LeadStatus
from src.notifications.telegram.notifier import notify_with_retry
from src.notifications.interfaces.notification_service import INotificationService
from src.services.nlp.base import INLPService
from src.services.validation_service import ValidationError, ValidationService
from src.storage.interfaces.lead_repository import ILeadRepository

logger = logging.getLogger(__name__)


class LeadSaveError(Exception):
    """Raised when lead persistence fails."""


@dataclass(slots=True)
class LeadCreatedResult:
    lead: Lead
    response: LeadResponseDTO


class LeadService:
    def __init__(
        self,
        repository: ILeadRepository,
        notification_service: INotificationService,
        validation_service: ValidationService,
        nlp_service: INLPService,
    ) -> None:
        self._repository = repository
        self._notification_service = notification_service
        self._validation = validation_service
        self._nlp = nlp_service

    def build_create_dto(self, draft: LeadDraftDTO) -> LeadCreateDTO:
        if not draft.is_complete():
            raise ValidationError("Не все обязательные поля заполнены.")

        return LeadCreateDTO(
            telegram_id=draft.telegram_id,  # type: ignore[arg-type]
            username=draft.username,
            name=draft.name,  # type: ignore[arg-type]
            phone=draft.phone,  # type: ignore[arg-type]
            task_type=draft.task_type,  # type: ignore[arg-type]
            budget=draft.budget,  # type: ignore[arg-type]
            deadline=draft.deadline,  # type: ignore[arg-type]
            comment=draft.comment,
            source=draft.source,
        )

    def _to_entity(self, dto: LeadCreateDTO) -> Lead:
        return Lead(
            id=uuid4(),
            created_at=datetime.now(UTC),
            telegram_id=dto.telegram_id,
            username=dto.username,
            name=dto.name,
            phone=dto.phone,
            task_type=dto.task_type,
            budget=dto.budget,
            deadline=dto.deadline,
            comment=dto.comment,
            status=LeadStatus.NEW,
            source=dto.source,
        )

    async def _save_with_retry(self, lead: Lead, *, max_attempts: int = 3) -> Lead:
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return await self._repository.save(lead)
            except Exception as exc:
                last_error = exc
                logger.exception(
                    "Lead save attempt %s/%s failed for telegram_id=%s",
                    attempt,
                    max_attempts,
                    lead.telegram_id,
                )
                if attempt < max_attempts:
                    await asyncio.sleep(1.0 * attempt)
        raise LeadSaveError("Не удалось сохранить заявку.") from last_error

    async def create_lead(self, draft: LeadDraftDTO) -> LeadCreatedResult:
        create_dto = self.build_create_dto(draft)
        lead = self._to_entity(create_dto)
        lead = await self._save_with_retry(lead)

        summary = await self._nlp.generate_lead_summary(lead)
        score_result = await self._nlp.score_lead(lead)
        score = score_result.label if score_result.value > 0 else None

        response = LeadResponseDTO.from_lead(
            lead,
            summary=summary or None,
            score=score,
        )

        try:
            await notify_with_retry(self._notification_service, response)
        except NotificationDeliveryError:
            logger.error(
                "Lead %s saved but manager notification failed — will require manual follow-up",
                lead.id,
            )

        return LeadCreatedResult(lead=lead, response=response)
