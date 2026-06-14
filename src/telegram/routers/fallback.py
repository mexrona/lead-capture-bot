from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.config.constants import BUDGET_OPTIONS, DEADLINE_OPTIONS, TASK_TYPES
from src.fsm.states import LeadFormStates
from src.services.nlp.base import INLPService
from src.services.survey_service import get_draft, save_draft
from src.services.validation_service import ValidationService
from src.telegram.keyboards.inline import (
    back_cancel_keyboard,
    budget_keyboard,
    comment_keyboard,
    deadline_keyboard,
    task_type_keyboard,
)
from src.telegram.messages import templates as msg

router = Router(name="fallback")

CHOICE_STATES = {
    LeadFormStates.type_selection.state: (TASK_TYPES, "task_type"),
    LeadFormStates.budget_selection.state: (BUDGET_OPTIONS, "budget"),
    LeadFormStates.deadline_selection.state: (DEADLINE_OPTIONS, "deadline"),
}


@router.message(
    F.text,
    StateFilter(
        LeadFormStates.type_selection,
        LeadFormStates.budget_selection,
        LeadFormStates.deadline_selection,
    ),
)
async def fallback_choice_text(
    message: Message,
    state: FSMContext,
    validation_service: ValidationService,
    nlp_service: INLPService,
) -> None:
    current = await state.get_state()
    options, field_name = CHOICE_STATES[current]
    text = message.text or ""

    mapped_key = validation_service.map_text_to_choice(text, options)
    if mapped_key is None:
        parsed = await nlp_service.parse_user_message(text, current or "")
        if parsed.mapped_value and parsed.mapped_value in options:
            mapped_key = parsed.mapped_value

    if mapped_key is None:
        await message.answer(msg.INVALID_CHOICE, reply_markup=_keyboard_for_state(current))
        return

    draft = await get_draft(state)
    setattr(draft, field_name, options[mapped_key])
    await save_draft(state, draft)

    from src.telegram.navigation import complete_field

    await complete_field(message, state, draft)


@router.callback_query()
async def fallback_unknown_callback(callback: CallbackQuery) -> None:
    await callback.answer("Используйте кнопки на клавиатуре.", show_alert=False)


def _keyboard_for_state(state: str):
    if state == LeadFormStates.type_selection.state:
        return task_type_keyboard()
    if state == LeadFormStates.budget_selection.state:
        return budget_keyboard()
    return deadline_keyboard()
