## Стек

| Компонент | Выбор |
|---|---|
| Язык | Python 3.11 |
| Пакетный менеджер | [uv](https://docs.astral.sh/uv/) + `pyproject.toml` / `uv.lock` |
| Web | FastAPI + Uvicorn |
| Валидация | Pydantic v2 |
| БД | SQLite + SQLAlchemy 2.0 (ORM) |
| Конфигурация | `pydantic-settings` + `.env` |
| Тесты | pytest + httpx |

## Быстрый старт

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

### Конфигурация

Настройки читаются из `.env` (файл в `.gitignore`, шаблон — `.env.example`).
Приоритет: переменные окружения → `.env` → дефолты в `app/config.py`.

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./bookings.db` | Строка подключения SQLAlchemy |
| `DEBUG` | `false` | Режим отладки FastAPI |
| `APP_TITLE` | `Restaurant Booking API` | Заголовок в Swagger |

### Тесты

```bash
uv run pytest -q
```

## API

Все маршруты имеют версионированный префикс `/api/v1`.

| Метод | Путь | Успех | Описание |
|---|---|---|---|
| POST | `/api/v1/bookings` | 201 | Создать бронь (`status=active`) |
| GET | `/api/v1/bookings?date=YYYY-MM-DD` | 200 | Список броней, фильтр по дате опционален |
| GET | `/api/v1/bookings/{id}` | 200 | Бронь по id |
| DELETE | `/api/v1/bookings/{id}` | 200 | Отменить бронь (`status=cancelled`) |

### Поля брони

| Поле | Тип | Правило |
|---|---|---|
| `name` | str | 2–50 символов |
| `phone` | str | `+7` и ровно 10 цифр |
| `booking_date` | date | от сегодня до +30 дней включительно |
| `booking_time` | time | целый час с 12:00 до 22:00 |
| `guests` | int | 1–10 |

### Ошибки

| Ситуация | Код | Тело |
|---|---|---|
| Невалидные данные | 422 | Стандартный ответ FastAPI |
| Бронь не найдена | 404 | `{"detail": "Booking not found"}` |
| Слот занят активной бронью | 409 | `{"detail": "Slot is already booked"}` |

### Примеры

```bash
# Создать бронь
curl -X POST http://127.0.0.1:8000/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Петров",
    "phone": "+79991234567",
    "booking_date": "2026-12-15",
    "booking_time": "19:00",
    "guests": 2
  }'

# Список за дату
curl "http://127.0.0.1:8000/api/v1/bookings?date=2026-12-15"

# Получить бронь
curl http://127.0.0.1:8000/api/v1/bookings/1

# Отменить бронь
curl -X DELETE http://127.0.0.1:8000/api/v1/bookings/1
```

## Структура проекта

```
app/
├── main.py                    # сборка FastAPI: lifespan, роутер, обработчики
├── api.py                     # агрегатор роутеров с префиксом /api/v1
├── config.py                  # настройки из .env
├── db.py                      # engine, SessionLocal, Base, get_db
└── booking/                   # модуль предметной области «брони»
    ├── router.py              # HTTP-слой
    ├── schemas.py             # BookingCreate, BookingOut + валидация
    ├── models.py              # ORM-модель и частичный уникальный индекс
    ├── repository.py          # доступ к данным
    ├── usecases.py            # бизнес-сценарии
    ├── mapper.py              # BookingModel → BookingOut
    ├── exceptions.py          # BookingNotFound, SlotAlreadyBooked
    └── errors.py              # исключения → HTTP 404/409
tests/
├── conftest.py                # in-memory SQLite, override get_db
└── test_bookings.py
```

## Принятые решения

- **Слои** (`routers` → `usecases` → `repositories`): HTTP-слой тонкий, бизнес-сценарии
  не знают про FastAPI, SQL — только в репозитории.
- **Версионирование API**: все маршруты группируются под версии `/api/v1` через
  агрегатор `app/api.py`. Модуль `app/booking` не знает о версии — он определяет
  только ресурсные пути (`/bookings` и т.д.), а префикс накладывается сверху.
- **Доменные исключения вместо `HTTPException`**: use case бросает `BookingNotFound` /
  `SlotAlreadyBooked`, а `app/booking/errors.py` переводит их в 404/409 с нужными
  сообщениями.
- **Явный маппер `BookingModel → BookingOut`**: ORM-модель не покидает приложение,
  роутер возвращает схему ответа, аннотации совпадают с фактическим типом.
- **Уникальность слота на уровне БД**: частичный уникальный индекс
  `(booking_date, booking_time) WHERE status='active'` гарантирует одно активное
  бронирование даже при гонке запросов; use case дополнительно проверяет слот и
  превращает `IntegrityError` в `SlotAlreadyBooked` (409).
- **Валидация в схемах Pydantic**: правила даты и времени описаны рядом с полями,
  а невалидные данные автоматически дают 422 в стандартном формате FastAPI.
- **Отмена идемпотентна**: повторный `DELETE` возвращает 200 и ту же бронь со
  `status=cancelled`; запись не удаляется и продолжает быть видна в списке.
- **SQLite выбран осознанно**: задание не требует PostgreSQL, а SQLAlchemy
  позволяет позже заменить хранилище без изменения сервисов и роутов.

## Что доделал бы при наличии времени

- Alembic для миграций вместо `create_all()`.
- Пагинация и фильтр по статусу в `GET /bookings`.
- Ограничение частоты запросов и аутентификацию для админских операций.
- Docker-образ и CI (ruff + pytest) на GitHub Actions.