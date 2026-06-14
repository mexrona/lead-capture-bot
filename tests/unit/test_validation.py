import pytest

from src.services.validation_service import ValidationError, ValidationService


@pytest.fixture
def validation_service() -> ValidationService:
    return ValidationService()


def test_validate_name_ok(validation_service: ValidationService) -> None:
    assert validation_service.validate_name("Иван") == "Иван"


def test_validate_name_too_short(validation_service: ValidationService) -> None:
    with pytest.raises(ValidationError):
        validation_service.validate_name("А")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+79991234567", "+79991234567"),
        ("89991234567", "+79991234567"),
        ("9991234567", "+79991234567"),
    ],
)
def test_validate_phone_ok(
    validation_service: ValidationService,
    raw: str,
    expected: str,
) -> None:
    assert validation_service.validate_phone(raw) == expected


def test_validate_phone_invalid(validation_service: ValidationService) -> None:
    with pytest.raises(ValidationError):
        validation_service.validate_phone("abc")


def test_map_text_to_choice(validation_service: ValidationService) -> None:
    options = {"website": "Разработка сайта"}
    assert validation_service.map_text_to_choice("Разработка сайта", options) == "website"
