from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.fsm.states import LeadFormStates
from src.services.survey_service import get_draft, init_draft_from_user
from src.telegram.keyboards.inline import begin_keyboard, resume_keyboard, task_type_keyboard
from src.telegram.messages import templates as msg
from src.telegram.navigation import prompt_for_state, resolve_state_from_draft

router = Router(name="start")


def _username_from_user(user) -> str | None:
    return user.username


async def _send_welcome(message: Message) -> None:
    await message.answer(msg.WELCOME, reply_markup=begin_keyboard())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    draft = await get_draft(state)
    current_state = await state.get_state()

    if current_state and current_state != LeadFormStates.idle.state and draft.task_type:
        await message.answer(msg.DRAFT_FOUND, reply_markup=resume_keyboard())
        return

    await state.clear()
    await state.set_state(LeadFormStates.idle)
    await _send_welcome(message)


@router.callback_query(lambda c: c.data == "begin_survey")
async def begin_survey(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    user = callback.from_user
    await init_draft_from_user(
        state,
        telegram_id=user.id,
        username=_username_from_user(user),
    )
    await state.set_state(LeadFormStates.type_selection)
    await callback.message.edit_text(msg.WELCOME)
    await callback.message.answer(msg.ASK_TASK_TYPE, reply_markup=task_type_keyboard())


@router.callback_query(lambda c: c.data == "resume_draft")
async def resume_draft(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    draft = await get_draft(state)
    next_state = resolve_state_from_draft(draft)
    await state.set_state(next_state)
    await callback.message.edit_text("Продолжаем заполнение заявки.")
    await prompt_for_state(callback.message, state, draft)


@router.callback_query(lambda c: c.data == "restart_draft")
async def restart_draft(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    user = callback.from_user
    await init_draft_from_user(
        state,
        telegram_id=user.id,
        username=_username_from_user(user),
    )
    await state.set_state(LeadFormStates.type_selection)
    await callback.message.edit_text(msg.WELCOME)
    await callback.message.answer(msg.ASK_TASK_TYPE, reply_markup=task_type_keyboard())
