import re

from src.config.constants import (
    BUDGET_OPTIONS,
    COMMENT_MAX_LENGTH,
    DEADLINE_OPTIONS,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    TASK_TYPES,
)
from src.config.settings import Settings
from src.services.nlp.base import INLPService
from src.services.nlp.noop import NoOpNLPService


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationService:
    PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")

    def validate_name(self, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < NAME_MIN_LENGTH:
            raise ValidationError(
                f"Имя слишком короткое. Минимум {NAME_MIN_LENGTH} символа."
            )
        if len(cleaned) > NAME_MAX_LENGTH:
            raise ValidationError(
                f"Имя слишком длинное. Максимум {NAME_MAX_LENGTH} символов."
            )
        return cleaned

    def validate_phone(self, value: str) -> str:
        cleaned = re.sub(r"[\s\-()]", "", value.strip())
        if cleaned.startswith("8") and len(cleaned) == 11:
            cleaned = "+7" + cleaned[1:]
        elif cleaned.startswith("7") and len(cleaned) == 11:
            cleaned = "+" + cleaned
        elif cleaned.isdigit() and len(cleaned) == 10:
            cleaned = "+7" + cleaned

        if not self.PHONE_PATTERN.match(cleaned):
            raise ValidationError(
                "Неверный формат телефона. Пример: +79991234567"
            )
        return cleaned

    def validate_comment(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if len(cleaned) > COMMENT_MAX_LENGTH:
            raise ValidationError(
                f"Комментарий слишком длинный. Максимум {COMMENT_MAX_LENGTH} символов."
            )
        return cleaned

    def validate_choice(self, key: str, options: dict[str, str]) -> str:
        if key not in options:
            raise ValidationError("Пожалуйста, выберите один из предложенных вариантов.")
        return options[key]

    def map_text_to_choice(self, text: str, options: dict[str, str]) -> str | None:
        normalized = text.strip().lower()
        for key, label in options.items():
            if normalized == label.lower() or normalized == key.lower():
                return key
        return None


def create_nlp_service(settings: Settings) -> INLPService:
    if settings.nlp_enabled:
        # Future: return OpenAI/Claude implementation
        raise NotImplementedError("NLP is enabled but no provider is configured yet.")
    return NoOpNLPService()
