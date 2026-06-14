from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.config.constants import BUDGET_OPTIONS, DEADLINE_OPTIONS, TASK_TYPES
from src.fsm.states import LeadFormStates
from src.services.survey_service import get_draft, save_draft
from src.services.validation_service import ValidationError, ValidationService
from src.telegram.keyboards.inline import (
    CB_BACK,
    CB_BUDGET_PREFIX,
    CB_DEADLINE_PREFIX,
    CB_SKIP,
    CB_TASK_PREFIX,
    back_cancel_keyboard,
    comment_keyboard,
)
from src.telegram.navigation import complete_field, go_back

router = Router(name="survey")


@router.callback_query(F.data.startswith(CB_TASK_PREFIX), LeadFormStates.type_selection)
async def on_task_type(
    callback: CallbackQuery,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    await callback.answer()
    key = callback.data.removeprefix(CB_TASK_PREFIX)
    try:
        label = validation_service.validate_choice(key, TASK_TYPES)
    except ValidationError as exc:
        await callback.message.answer(exc.message)
        return

    draft = await get_draft(state)
    draft.task_type = label
    await save_draft(state, draft)
    await callback.message.edit_reply_markup(reply_markup=None)
    await complete_field(callback.message, state, draft)


@router.callback_query(F.data.startswith(CB_BUDGET_PREFIX), LeadFormStates.budget_selection)
async def on_budget(
    callback: CallbackQuery,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    await callback.answer()
    key = callback.data.removeprefix(CB_BUDGET_PREFIX)
    try:
        label = validation_service.validate_choice(key, BUDGET_OPTIONS)
    except ValidationError as exc:
        await callback.message.answer(exc.message)
        return

    draft = await get_draft(state)
    draft.budget = label
    await save_draft(state, draft)
    await callback.message.edit_reply_markup(reply_markup=None)
    await complete_field(callback.message, state, draft)


@router.callback_query(F.data.startswith(CB_DEADLINE_PREFIX), LeadFormStates.deadline_selection)
async def on_deadline(
    callback: CallbackQuery,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    await callback.answer()
    key = callback.data.removeprefix(CB_DEADLINE_PREFIX)
    try:
        label = validation_service.validate_choice(key, DEADLINE_OPTIONS)
    except ValidationError as exc:
        await callback.message.answer(exc.message)
        return

    draft = await get_draft(state)
    draft.deadline = label
    await save_draft(state, draft)
    await callback.message.edit_reply_markup(reply_markup=None)
    await complete_field(callback.message, state, draft)


@router.message(LeadFormStates.name_input, F.text)
async def on_name(
    message: Message,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    try:
        name = validation_service.validate_name(message.text or "")
    except ValidationError as exc:
        await message.answer(exc.message, reply_markup=back_cancel_keyboard())
        return

    draft = await get_draft(state)
    draft.name = name
    await save_draft(state, draft)
    await complete_field(message, state, draft)


@router.message(LeadFormStates.contact_input, F.text)
async def on_phone(
    message: Message,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    try:
        phone = validation_service.validate_phone(message.text or "")
    except ValidationError as exc:
        await message.answer(exc.message, reply_markup=back_cancel_keyboard())
        return

    draft = await get_draft(state)
    draft.phone = phone
    await save_draft(state, draft)
    await complete_field(message, state, draft)


@router.message(LeadFormStates.comment_input, F.text)
async def on_comment(
    message: Message,
    state: FSMContext,
    validation_service: ValidationService,
) -> None:
    try:
        comment = validation_service.validate_comment(message.text)
    except ValidationError as exc:
        await message.answer(exc.message, reply_markup=comment_keyboard())
        return

    draft = await get_draft(state)
    draft.comment = comment
    draft.comment_step_done = True
    await save_draft(state, draft)
    await complete_field(message, state, draft)


@router.callback_query(F.data == CB_SKIP, LeadFormStates.comment_input)
async def on_skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    draft = await get_draft(state)
    draft.comment = None
    draft.comment_step_done = True
    await save_draft(state, draft)
    await callback.message.edit_reply_markup(reply_markup=None)
    await complete_field(callback.message, state, draft)


@router.callback_query(F.data == CB_BACK)
async def on_back(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await go_back(callback.message, state)
