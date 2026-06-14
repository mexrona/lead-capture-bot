from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.config.constants import SOURCE_TELEGRAM_BOT
from src.domain.dto.lead_draft_dto import LeadDraftDTO
from src.domain.entities.lead import Lead
from src.domain.enums.lead_status import LeadStatus
from src.notifications.interfaces.notification_service import INotificationService
from src.services.lead_service import LeadService
from src.services.nlp.noop import NoOpNLPService
from src.services.validation_service import ValidationService
from src.storage.interfaces.lead_repository import ILeadRepository


@pytest.fixture
def complete_draft() -> LeadDraftDTO:
    return LeadDraftDTO(
        task_type="Разработка сайта",
        budget="до $500",
        deadline="1 месяц",
        name="Иван Петров",
        phone="+79991234567",
        comment="Нужен лендинг",
        telegram_id=123456,
        username="ivanpetrov",
        comment_step_done=True,
        source=SOURCE_TELEGRAM_BOT,
    )


@pytest.mark.asyncio
async def test_create_lead_success(complete_draft: LeadDraftDTO) -> None:
    saved_lead = Lead(
        id=uuid4(),
        created_at=datetime.now(UTC),
        telegram_id=123456,
        username="ivanpetrov",
        name="Иван Петров",
        phone="+79991234567",
        task_type="Разработка сайта",
        budget="до $500",
        deadline="1 месяц",
        comment="Нужен лендинг",
        status=LeadStatus.NEW,
        source=SOURCE_TELEGRAM_BOT,
    )

    repository = AsyncMock(spec=ILeadRepository)
    repository.save = AsyncMock(return_value=saved_lead)

    notification_service = AsyncMock(spec=INotificationService)
    notification_service.notify_managers = AsyncMock()

    service = LeadService(
        repository=repository,
        notification_service=notification_service,
        validation_service=ValidationService(),
        nlp_service=NoOpNLPService(),
    )

    result = await service.create_lead(complete_draft)

    repository.save.assert_awaited_once()
    notification_service.notify_managers.assert_awaited_once()
    assert result.lead.name == "Иван Петров"
    assert result.response.phone == "+79991234567"
