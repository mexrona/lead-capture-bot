from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.fsm.states import LeadFormStates
from src.services.survey_service import clear_draft
from src.telegram.keyboards.inline import CB_CANCEL
from src.telegram.messages import templates as msg

router = Router(name="cancel")


async def _cancel_flow(message: Message, state: FSMContext) -> None:
    await clear_draft(state)
    await state.clear()
    await state.set_state(LeadFormStates.cancelled)
    await message.answer(msg.CANCELLED)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if not current or current in {
        LeadFormStates.idle.state,
        LeadFormStates.finish.state,
        LeadFormStates.cancelled.state,
    }:
        await message.answer("Нет активной заявки для отмены.")
        return
    await _cancel_flow(message, state)


@router.callback_query(F.data == CB_CANCEL)
async def callback_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    current = await state.get_state()
    if current == LeadFormStates.processing.state:
        await callback.message.answer(msg.ALREADY_PROCESSING)
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await _cancel_flow(callback.message, state)
