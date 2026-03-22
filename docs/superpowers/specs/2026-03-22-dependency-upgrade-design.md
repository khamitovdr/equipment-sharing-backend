# Dependency Upgrade Design — Full Modernization

**Date:** 2026-03-22
**Approach:** Layered Phases — sequential commits on one branch

## Decisions

- **Python:** 3.11 -> 3.13
- **Pydantic:** v1 -> v2 (full migration, no compatibility shims)
- **python-jose:** Remove, replace with PyJWT
- **Rocketry:** Remove entirely (user will add cron jobs later). `init_equipment_categories_db_table` called directly in startup.
- **Sentry:** Remove entirely (user will re-add later)
- **Aerich migrations:** Clean slate — delete and regenerate
- **pytest-lazy-fixture:** Replace with `pytest-lazy-fixtures`

## Phase 1: Python 3.13 + Dockerfile + Infrastructure

**Files changed:**
- `project/Dockerfile`: `python:3.11-slim-bookworm` -> `python:3.13-slim-bookworm`
- `.python-version`: update to `3.13`
- `project/pyproject.toml`: `target-version = ["py313"]`

**Risk:** Low

## Phase 2: Remove Rocketry + Sentry

**Files changed:**
- Delete `app/scheduler.py`
- `app/services/equipment.py`: remove `@scheduler.task()` decorator and Rocketry import. Function becomes a plain `async def`.
- `app/main.py`: remove Rocketry imports (`from app import scheduler`), remove Sentry imports (`import sentry_sdk`, `sentry_sdk.init(...)`). Call `await init_equipment_categories_db_table()` directly in startup event after `init_db(app)`.
- `app/config.py`: remove `sentry_dsn` field
- `requirements.txt`: remove `rocketry` and `sentry-sdk[fastapi]`

**Risk:** Low

## Phase 3: Pydantic v2 + pydantic-settings + Tortoise ORM + Aerich

This is the core migration. Must be a single atomic commit.

### Dependency changes
- `pydantic[email]` 1.10 -> 2.12+
- Add `pydantic-settings` (new package)
- `tortoise-orm` 0.19 -> 0.24+
- `aerich` 0.7 -> 0.9
- `asyncpg` 0.27 -> 0.30+

### Code changes

**`app/config.py`:**
- `from pydantic import BaseSettings` -> `from pydantic_settings import BaseSettings`
- `AnyUrl` import stays in `pydantic`

**Schema files (9 files):**
- `@validator("field")` -> `@field_validator("field")` with `@classmethod`
- `@validator("field", always=True)` -> `@field_validator("field", mode="before")`
- Validator signature: `(cls, v, values)` -> `(cls, v, info)` where `info.data` replaces `values`
- `from pydantic import validator` -> `from pydantic import field_validator`
- Clean up `str or None = None` to `str | None = None`

Affected files:
- `app/schemas/users.py` — 5 validators to migrate
- `app/schemas/reviews.py` — 1 validator to migrate
- `app/schemas/auth.py` — no validators, just BaseModel (no change)
- `app/schemas/organizations.py` — no validators (no change beyond import cleanup)
- `app/schemas/equipment.py` — no validators (no change)
- `app/schemas/orders.py` — no validators (no change)
- `app/schemas/requisites.py` — no validators (no change)
- `app/schemas/notifications.py` — no validators (no change)
- `app/schemas/files.py` — no validators (no change)

**CRUD files (`.dict()` -> `.model_dump()`):**
- `app/crud/users.py` — 2 calls: `.dict()`, `.dict(exclude_unset=True)`
- `app/crud/organizations.py` — 3 calls: `.dict()`, `.dict()`, `.dict()`
- `app/crud/equipment.py` — 2 calls: `.dict(exclude_unset=True)`, `.dict(exclude_unset=True)`
- `app/crud/orders.py` — 1 call: `.dict(exclude_unset=True)`

**`app/models/notifications.py`:**
- Has `from pydantic import BaseModel` for notification content schemas. No change needed.

**`app/_init_models.py`:**
- Still required with Tortoise ORM 0.24 for `pydantic_model_creator` to resolve relations. No change.

**Risk:** High — most invasive phase, touches ~15 files

## Phase 4: FastAPI Modernization

### Dependency changes
- `fastapi` 0.95 -> 0.135+
- `uvicorn[standard]` 0.20 -> 0.34+
- `httpx` 0.23 -> 0.28+

### Code changes

**`app/main.py`:**
- Replace `@app.on_event("startup")` / `@app.on_event("shutdown")` with lifespan context manager:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(app)
    await init_equipment_categories_db_table()
    yield

app = FastAPI(lifespan=lifespan)
```

**`app/db.py`:**
- Verify `register_tortoise` works with lifespan pattern in Tortoise ORM 0.24+

**`project/tests/conftest.py`:**
- httpx 0.28: `AsyncClient(app=app, ...)` -> `AsyncClient(transport=ASGITransport(app=app), ...)`
- `from httpx import ASGITransport`
- Affects all fixtures creating `AsyncClient` (~5 fixtures)

**Risk:** Medium

## Phase 5: python-jose -> PyJWT

### Dependency changes
- Remove `python-jose[cryptography]`
- Add `PyJWT`

### Code changes

**`app/services/auth.py`:**
- `from jose import JWTError, jwt` -> `import jwt` and `from jwt.exceptions import InvalidTokenError`
- `except JWTError:` -> `except InvalidTokenError:`
- `jwt.encode()` and `jwt.decode()` — same API for HS256

**Risk:** Low

## Phase 6: Dev Tools

### Dependency changes
- `pytest` 7.2 -> 8+
- `pytest-lazy-fixture` -> `pytest-lazy-fixtures` (different package)
- `black` 23 -> 25+
- `flake8` 6.0 -> 7+
- `isort` 5.12 -> 6+
- `pytest-cov` 4.0 -> 6+
- `requests` 2.28 -> 2.32+

### Code changes

**`project/tests/test_users.py`:**
- `pytest.lazy_fixture("name")` -> `lf("name")` with `from pytest_lazy_fixtures import lf`
- 6 occurrences

**`project/tests/test_organizations.py`:**
- `pytest.lazy_fixture("name")` -> `lf("name")` with `from pytest_lazy_fixtures import lf`
- 3 occurrences

**Risk:** Low

## Phase 7: Remaining Minor Upgrades

### Dependency changes (version bumps only, no code changes expected)
- `aiohttp` 3.8 -> 3.11+
- `Pillow` 10.0 -> 11+
- `python-docx` 0.8 -> 1.1+
- `python-multipart` 0.0.6 -> 0.0.20+
- `passlib[bcrypt]` 1.7 -> 1.7 (no major update)
- `bcrypt` 4.0 -> 4.2+
- `dadata` 21.10 -> 21.10 (no major update)
- `gunicorn` 20.1 -> 23+
- `yookassa` 2.4 -> 3+

**Risk:** Low

## Phase 8: Clean Slate Migrations + `.cursorrules` Update

### Migrations
- Delete `project/migrations/` directory
- Run `aerich init-db` to regenerate

### `.cursorrules`
- Python 3.13
- Pydantic v2 syntax patterns
- Remove Rocketry, Sentry from tech stack
- python-jose -> PyJWT
- `_init_models.py` still required
