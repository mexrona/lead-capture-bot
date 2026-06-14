# Lead Capture Bot

Telegram-бот для квалификации входящих лидов. Собирает информацию от потенциального клиента, формирует карточку лида, сохраняет в Google Sheets и уведомляет менеджера в Telegram.

## Стек

- Python 3.12
- aiogram 3.x + FSM
- Google Sheets API (gspread)
- SQLite / PostgreSQL для FSM Storage
- Docker

## Быстрый старт (локально)

### 1. Клонирование и окружение

```bash
cd lead-capture-bot
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install pytest pytest-asyncio  # для тестов
```

### 2. Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Скопируйте токен в `.env`

### 3. Google Sheets

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите **Google Sheets API** и **Google Drive API**
3. Создайте Service Account и скачайте JSON-ключ
4. Положите ключ в `credentials/google-service-account.json`
5. Создайте Google Spreadsheet и дайте Service Account доступ (Editor)
6. Скопируйте ID таблицы из URL в `GOOGLE_SHEETS_SPREADSHEET_ID`

При первом сохранении лида бот автоматически создаст лист `Leads` с нужными колонками.

### 4. Конфигурация

```bash
cp .env.example .env
```

Заполните `.env`:

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен Telegram-бота |
| `MANAGER_CHAT_ID` | Chat ID менеджера для уведомлений |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | ID Google таблицы |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | Путь к JSON ключу Service Account |

**Как узнать MANAGER_CHAT_ID:** напишите боту [@userinfobot](https://t.me/userinfobot) или отправьте сообщение своему боту и откройте `https://api.telegram.org/bot<TOKEN>/getUpdates`.

### 5. Запуск

```bash
# из корня проекта
set PYTHONPATH=.   # Windows CMD
# $env:PYTHONPATH="."  # Windows PowerShell
# export PYTHONPATH=.  # Linux/macOS

python -m src.main
```

### 6. Тесты

```bash
pytest
```

## Docker (production)

```bash
cp .env.example .env
# Установите FSM_STORAGE=postgresql в .env

cd docker
docker compose up --build -d
```

В production-режиме FSM хранится в PostgreSQL. Лиды — в Google Sheets.

## Сценарий пользователя

1. `/start` → «Оставить заявку»
2. Тип задачи → Бюджет → Сроки (кнопки)
3. Имя → Телефон (текст)
4. Комментарий (текст или «Пропустить»)
5. Сводка → Подтвердить / Изменить / Отменить
6. Заявка сохраняется, менеджер получает уведомление

Команда `/cancel` отменяет заполнение на любом этапе.

## Архитектура

```
src/
├── telegram/       # Handlers, keyboards, messages
├── fsm/            # States, FSM storage
├── domain/         # Entities, DTOs
├── services/       # Business logic, validation, NLP stub
├── storage/        # ILeadRepository → Google Sheets
├── notifications/  # Manager notifications
├── integrations/   # External API clients
└── app/            # DI container
```

### Смена хранилища лидов

Реализуйте `ILeadRepository` и зарегистрируйте в `src/storage/factory.py`.

### AI (будущее)

Интерфейс `INLPService` в `src/services/nlp/base.py`. Сейчас используется `NoOpNLPService`. Включение: `NLP_ENABLED=true` (потребует реализации провайдера).

## Google Sheets Schema

| Колонка | Описание |
|---------|----------|
| id | UUID лида |
| created_at | ISO datetime |
| telegram_id | Telegram user ID |
| username | @username |
| name | Имя клиента |
| phone | Телефон |
| task_type | Тип задачи |
| budget | Бюджет |
| deadline | Срок |
| comment | Комментарий |
| status | new / contacted / ... |
| source | telegram_bot |

## Лицензия

MIT
