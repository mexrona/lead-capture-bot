"""Shared constants: button labels and survey options."""

SOURCE_TELEGRAM_BOT = "telegram_bot"

# Task types
TASK_TYPES: dict[str, str] = {
    "website": "Разработка сайта",
    "telegram_bot": "Telegram-бот",
    "mobile_app": "Мобильное приложение",
    "design": "Дизайн",
    "other": "Другое",
}

# Budget ranges
BUDGET_OPTIONS: dict[str, str] = {
    "up_to_500": "до $500",
    "500_2000": "$500–2000",
    "2000_5000": "$2000–5000",
    "5000_plus": "$5000+",
    "discuss": "Обсудим",
}

# Deadline ranges
DEADLINE_OPTIONS: dict[str, str] = {
    "urgent": "Срочно (до 2 нед.)",
    "1_month": "1 месяц",
    "2_3_months": "2–3 месяца",
    "3_plus": "3+ месяца",
    "flexible": "Гибко",
}

# Validation limits
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 100
COMMENT_MAX_LENGTH = 1000

# Google Sheets column order
SHEETS_COLUMNS: list[str] = [
    "id",
    "created_at",
    "telegram_id",
    "username",
    "name",
    "phone",
    "task_type",
    "budget",
    "deadline",
    "comment",
    "status",
    "source",
]
