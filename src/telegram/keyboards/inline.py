from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config.constants import BUDGET_OPTIONS, DEADLINE_OPTIONS, TASK_TYPES
from src.domain.dto.lead_draft_dto import LeadDraftDTO

CB_BEGIN = "begin_survey"
CB_BACK = "back"
CB_CANCEL = "cancel"
CB_SKIP = "skip"
CB_CONFIRM = "confirm"
CB_EDIT = "edit"
CB_RESUME = "resume_draft"
CB_RESTART = "restart_draft"

CB_TASK_PREFIX = "task:"
CB_BUDGET_PREFIX = "budget:"
CB_DEADLINE_PREFIX = "deadline:"
CB_EDIT_PREFIX = "edit:"


def _options_keyboard(
    options: dict[str, str],
    prefix: str,
    *,
    show_back: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in options.items():
        builder.button(text=label, callback_data=f"{prefix}{key}")
    builder.adjust(1)
    if show_back:
        builder.row(
            _back_button(),
            _cancel_button(),
        )
    else:
        builder.row(_cancel_button())
    return builder.as_markup()


def _back_button():
    from aiogram.types import InlineKeyboardButton

    return InlineKeyboardButton(text="⬅️ Назад", callback_data=CB_BACK)


def _cancel_button():
    from aiogram.types import InlineKeyboardButton

    return InlineKeyboardButton(text="❌ Отменить", callback_data=CB_CANCEL)


def begin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Оставить заявку", callback_data=CB_BEGIN)
    builder.adjust(1)
    return builder.as_markup()


def resume_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Продолжить", callback_data=CB_RESUME)
    builder.button(text="🔄 Начать заново", callback_data=CB_RESTART)
    builder.adjust(1)
    return builder.as_markup()


def task_type_keyboard() -> InlineKeyboardMarkup:
    return _options_keyboard(TASK_TYPES, CB_TASK_PREFIX)


def budget_keyboard() -> InlineKeyboardMarkup:
    return _options_keyboard(BUDGET_OPTIONS, CB_BUDGET_PREFIX, show_back=True)


def deadline_keyboard() -> InlineKeyboardMarkup:
    return _options_keyboard(DEADLINE_OPTIONS, CB_DEADLINE_PREFIX, show_back=True)


def comment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустить", callback_data=CB_SKIP)
    builder.row(_back_button(), _cancel_button())
    return builder.as_markup()


def back_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(_back_button(), _cancel_button())
    return builder.as_markup()


def review_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=CB_CONFIRM)
    builder.button(text="✏️ Изменить", callback_data=CB_EDIT)
    builder.button(text="❌ Отменить", callback_data=CB_CANCEL)
    builder.adjust(1)
    return builder.as_markup()


def edit_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Тип задачи", callback_data=f"{CB_EDIT_PREFIX}task_type")
    builder.button(text="Бюджет", callback_data=f"{CB_EDIT_PREFIX}budget")
    builder.button(text="Сроки", callback_data=f"{CB_EDIT_PREFIX}deadline")
    builder.button(text="Имя", callback_data=f"{CB_EDIT_PREFIX}name")
    builder.button(text="Телефон", callback_data=f"{CB_EDIT_PREFIX}phone")
    builder.button(text="Комментарий", callback_data=f"{CB_EDIT_PREFIX}comment")
    builder.button(text="⬅️ Назад к сводке", callback_data=f"{CB_EDIT_PREFIX}back")
    builder.adjust(2, 2, 2, 1)
    builder.row(_cancel_button())
    return builder.as_markup()


def format_review(draft: LeadDraftDTO) -> str:
    username = draft.username or "не указан"
    if username != "не указан" and not username.startswith("@"):
        username = f"@{username}"

    comment = draft.comment if draft.comment else "—"
    lines = [
        "<b>Проверьте данные заявки:</b>",
        "",
        f"<b>Тип задачи:</b> {draft.task_type}",
        f"<b>Бюджет:</b> {draft.budget}",
        f"<b>Срок:</b> {draft.deadline}",
        f"<b>Имя:</b> {draft.name}",
        f"<b>Телефон:</b> {draft.phone}",
        f"<b>Telegram:</b> {username}",
        f"<b>Комментарий:</b> {comment}",
        "",
        "Если всё верно — нажмите «Подтвердить».",
    ]
    return "\n".join(lines)
