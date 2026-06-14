import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.config.settings import Settings
from src.fsm.states import LeadFormStates
from src.services.lead_service import LeadSaveError, LeadService
from src.services.survey_service import clear_draft, get_draft, save_draft
from src.telegram.keyboards.inline import (
    CB_CONFIRM,
    CB_EDIT,
    CB_EDIT_PREFIX,
    back_cancel_keyboard,
    budget_keyboard,
    comment_keyboard,
    deadline_keyboard,
    edit_menu_keyboard,
    format_review,
    review_keyboard,
    task_type_keyboard,
)
from src.telegram.messages import templates as msg

logger = logging.getLogger(__name__)

router = Router(name="review")

EDIT_FIELD_STATES = {
    "task_type": (LeadFormStates.type_selection, msg.ASK_TASK_TYPE, task_type_keyboard),
    "budget": (LeadFormStates.budget_selection, msg.ASK_BUDGET, budget_keyboard),
    "deadline": (LeadFormStates.deadline_selection, msg.ASK_DEADLINE, deadline_keyboard),
    "name": (LeadFormStates.name_input, msg.ASK_NAME, lambda: back_cancel_keyboard()),
    "phone": (LeadFormStates.contact_input, msg.ASK_PHONE, lambda: back_cancel_keyboard()),
    "comment": (LeadFormStates.comment_input, msg.ASK_COMMENT, comment_keyboard),
}


@router.callback_query(F.data == CB_EDIT, LeadFormStates.review)
async def on_edit_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(LeadFormStates.edit_menu)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите поле для изменения:",
        reply_markup=edit_menu_keyboard(),
    )


@router.callback_query(F.data.startswith(CB_EDIT_PREFIX), LeadFormStates.edit_menu)
async def on_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    field = callback.data.removeprefix(CB_EDIT_PREFIX)

    if field == "back":
        draft = await get_draft(state)
        await state.set_state(LeadFormStates.review)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            format_review(draft),
            reply_markup=review_keyboard(),
            parse_mode="HTML",
        )
        return

    if field not in EDIT_FIELD_STATES:
        await callback.message.answer("Неизвестное поле.")
        return

    draft = await get_draft(state)
    draft.is_editing = True
    draft.editing_field = field
    await save_draft(state, draft)

    next_state, text, keyboard_factory = EDIT_FIELD_STATES[field]
    await state.set_state(next_state)
    await callback.message.edit_reply_markup(reply_markup=None)
    keyboard = keyboard_factory() if callable(keyboard_factory) else keyboard_factory()
    await callback.message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == CB_CONFIRM, LeadFormStates.review)
async def on_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    lead_service: LeadService,
    settings: Settings,
) -> None:
    await callback.answer()
    draft = await get_draft(state)

    if draft.processing:
        await callback.message.answer(msg.ALREADY_PROCESSING)
        return

    draft.processing = True
    await save_draft(state, draft)
    await state.set_state(LeadFormStates.processing)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(msg.PROCESSING)

    try:
        await lead_service.create_lead(draft)
    except LeadSaveError as exc:
        logger.exception("Lead save failed: %s", exc)
        draft.processing = False
        await save_draft(state, draft)
        await state.set_state(LeadFormStates.review)
        await callback.message.answer(msg.SAVE_FAILED, reply_markup=review_keyboard())
        return
    except Exception:
        logger.exception("Unexpected error while creating lead")
        draft.processing = False
        await save_draft(state, draft)
        await state.set_state(LeadFormStates.review)
        await callback.message.answer(msg.SAVE_FAILED, reply_markup=review_keyboard())
        return

    await clear_draft(state)
    await state.set_state(LeadFormStates.finish)

    phone_line = (
        f"📞 {settings.manager_contact_phone}\n"
        if settings.manager_contact_phone
        else ""
    )
    telegram_line = (
        f"💬 {settings.manager_contact_telegram}\n"
        if settings.manager_contact_telegram
        else ""
    )
    success_text = msg.SUCCESS.format(
        manager_name=settings.manager_contact_name,
        phone_line=phone_line,
        telegram_line=telegram_line,
    )
    await callback.message.answer(success_text)
