from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.domain.dto.lead_draft_dto import LeadDraftDTO
from src.fsm.states import LeadFormStates
from src.services.survey_service import get_draft, save_draft
from src.telegram.keyboards.inline import (
    back_cancel_keyboard,
    budget_keyboard,
    comment_keyboard,
    deadline_keyboard,
    format_review,
    review_keyboard,
    task_type_keyboard,
)
from src.telegram.messages import templates as msg

NEXT_STATE = {
    LeadFormStates.type_selection.state: LeadFormStates.budget_selection,
    LeadFormStates.budget_selection.state: LeadFormStates.deadline_selection,
    LeadFormStates.deadline_selection.state: LeadFormStates.name_input,
    LeadFormStates.name_input.state: LeadFormStates.contact_input,
    LeadFormStates.contact_input.state: LeadFormStates.comment_input,
    LeadFormStates.comment_input.state: LeadFormStates.review,
}

BACK_TRANSITIONS = {
    LeadFormStates.budget_selection.state: (
        LeadFormStates.type_selection,
        msg.ASK_TASK_TYPE,
        task_type_keyboard,
    ),
    LeadFormStates.deadline_selection.state: (
        LeadFormStates.budget_selection,
        msg.ASK_BUDGET,
        budget_keyboard,
    ),
    LeadFormStates.name_input.state: (
        LeadFormStates.deadline_selection,
        msg.ASK_DEADLINE,
        deadline_keyboard,
    ),
    LeadFormStates.contact_input.state: (
        LeadFormStates.name_input,
        msg.ASK_NAME,
        lambda: back_cancel_keyboard(),
    ),
    LeadFormStates.comment_input.state: (
        LeadFormStates.contact_input,
        msg.ASK_PHONE,
        lambda: back_cancel_keyboard(),
    ),
}


def resolve_state_from_draft(draft: LeadDraftDTO) -> LeadFormStates:
    if not draft.task_type:
        return LeadFormStates.type_selection
    if not draft.budget:
        return LeadFormStates.budget_selection
    if not draft.deadline:
        return LeadFormStates.deadline_selection
    if not draft.name:
        return LeadFormStates.name_input
    if not draft.phone:
        return LeadFormStates.contact_input
    if not draft.comment_step_done:
        return LeadFormStates.comment_input
    return LeadFormStates.review


async def complete_field(message: Message, state: FSMContext, draft: LeadDraftDTO) -> None:
    if draft.is_editing:
        draft.is_editing = False
        draft.editing_field = None
        await save_draft(state, draft)
        await state.set_state(LeadFormStates.review)
        await message.answer(
            format_review(draft),
            reply_markup=review_keyboard(),
            parse_mode="HTML",
        )
        return

    current = await state.get_state()
    next_state = NEXT_STATE.get(current, LeadFormStates.review)
    await state.set_state(next_state)
    await send_step_prompt(message, next_state, draft)


async def send_step_prompt(message: Message, step: LeadFormStates, draft: LeadDraftDTO) -> None:
    if step == LeadFormStates.budget_selection:
        await message.answer(msg.ASK_BUDGET, reply_markup=budget_keyboard())
    elif step == LeadFormStates.deadline_selection:
        await message.answer(msg.ASK_DEADLINE, reply_markup=deadline_keyboard())
    elif step == LeadFormStates.name_input:
        await message.answer(msg.ASK_NAME, reply_markup=back_cancel_keyboard())
    elif step == LeadFormStates.contact_input:
        await message.answer(msg.ASK_PHONE, reply_markup=back_cancel_keyboard())
    elif step == LeadFormStates.comment_input:
        await message.answer(msg.ASK_COMMENT, reply_markup=comment_keyboard())
    elif step == LeadFormStates.review:
        await message.answer(
            format_review(draft),
            reply_markup=review_keyboard(),
            parse_mode="HTML",
        )


async def go_back(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    transition = BACK_TRANSITIONS.get(current or "")
    if not transition:
        return
    next_state, text, keyboard_factory = transition
    await state.set_state(next_state)
    keyboard = keyboard_factory() if callable(keyboard_factory) else keyboard_factory()
    await message.answer(text, reply_markup=keyboard)


async def prompt_for_state(message: Message, state: FSMContext, draft: LeadDraftDTO) -> None:
    current = await state.get_state()
    if current == LeadFormStates.type_selection.state:
        await message.answer(msg.ASK_TASK_TYPE, reply_markup=task_type_keyboard())
    elif current == LeadFormStates.budget_selection.state:
        await message.answer(msg.ASK_BUDGET, reply_markup=budget_keyboard())
    elif current == LeadFormStates.deadline_selection.state:
        await message.answer(msg.ASK_DEADLINE, reply_markup=deadline_keyboard())
    elif current == LeadFormStates.name_input.state:
        await message.answer(msg.ASK_NAME, reply_markup=back_cancel_keyboard())
    elif current == LeadFormStates.contact_input.state:
        await message.answer(msg.ASK_PHONE, reply_markup=back_cancel_keyboard())
    elif current == LeadFormStates.comment_input.state:
        await message.answer(msg.ASK_COMMENT, reply_markup=comment_keyboard())
    elif current == LeadFormStates.review.state:
        await message.answer(
            format_review(draft),
            reply_markup=review_keyboard(),
            parse_mode="HTML",
        )
