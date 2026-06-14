from aiogram.fsm.context import FSMContext

from src.domain.dto.lead_draft_dto import LeadDraftDTO

DRAFT_KEY = "draft"


async def get_draft(state: FSMContext) -> LeadDraftDTO:
    data = await state.get_data()
    return LeadDraftDTO.from_dict(data.get(DRAFT_KEY))


async def save_draft(state: FSMContext, draft: LeadDraftDTO) -> None:
    draft.touch()
    data = await state.get_data()
    data[DRAFT_KEY] = draft.to_dict()
    await state.set_data(data)


async def clear_draft(state: FSMContext) -> None:
    data = await state.get_data()
    data.pop(DRAFT_KEY, None)
    await state.set_data(data)


async def init_draft_from_user(
    state: FSMContext,
    *,
    telegram_id: int,
    username: str | None,
) -> LeadDraftDTO:
    draft = await get_draft(state)
    draft.telegram_id = telegram_id
    draft.username = username
    draft.is_editing = False
    draft.editing_field = None
    draft.processing = False
    await save_draft(state, draft)
    return draft
