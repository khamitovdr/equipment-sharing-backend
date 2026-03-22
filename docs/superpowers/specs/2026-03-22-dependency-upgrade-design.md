# Dependency Upgrade Design — Full Modernization

**Date:** 2026-03-22
**Approach:** Layered Phases — sequential commits on one branch

## Decisions

- **Python:** 3.11 -> 3.13
- **Pydantic:** v1 -> v2 (full migration, no compatibility shims)
- **python-jose:** Remove, replace with PyJWT
- **Rocketry:** Remove entirely (user will add cron jobs later). `init_equipment_categories_db_table` called directly in startup. Deferred file cleanup (`files_signals.py`) converted to `asyncio.create_task`.
- **Sentry:** Remove entirely (user will re-add later)
- **Aerich migrations:** Clean slate — delete and regenerate (requires DB volume reset)
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
- `app/db_signals/files_signals.py`: remove Rocketry imports (`from app.scheduler import app as scheduler`, `session = scheduler.session`). Remove `@scheduler.task()` decorator from `delete_file_if_unused`. Replace the Rocketry task dispatch in `file_post_save` with `asyncio.create_task(delete_file_if_unused(...))`.
- `app/main.py`: remove Rocketry imports (`from app import scheduler`), remove Sentry imports (`import sentry_sdk`, `sentry_sdk.init(...)`). Call `await init_equipment_categories_db_table()` directly in startup event after `init_db(app)`. Remove `scheduler.start()` / `scheduler.stop()` calls.
- `app/config.py`: remove `sentry_dsn` field
- `project/requirements.txt`: remove `rocketry` and `sentry-sdk[fastapi]`
- `.env` / `example.env`: remove `SENTRY_DSN` line

**Risk:** Low

## Phase 3: Pydantic v2 + pydantic-settings + Tortoise ORM + Aerich + FastAPI + httpx

This is the core migration. Must be a single atomic commit because FastAPI 0.95 does not support Pydantic v2 — the framework and data layer must move together.

### Dependency changes (`project/requirements.txt`)
- `pydantic[email]` 1.10 -> 2.12+
- Add `pydantic-settings` (new package, `BaseSettings` moved out of pydantic core)
- `tortoise-orm` 0.19 -> 0.24+
- `aerich` 0.7 -> 0.9
- `asyncpg` 0.27 -> 0.30+
- `fastapi` 0.95 -> 0.135+
- `uvicorn[standard]` 0.20 -> 0.34+
- `httpx` 0.23 -> 0.28+ (in `project/requirements-dev.txt`)

### Code changes

**`app/config.py`:**
- `from pydantic import BaseSettings` -> `from pydantic_settings import BaseSettings`
- `AnyUrl` import stays in `pydantic`
- All optional fields need explicit typing: `str = None` -> `str | None = None`

**Schema files — validator migration:**

Files with validators requiring migration:
- `app/schemas/users.py` — 5 validators:
  - `check_phone`: `@validator("phone")` -> `@field_validator("phone")` with `@classmethod`
  - `check_password`: `@validator("password")` -> `@field_validator("password")` with `@classmethod`
  - `check_organization_inn`: uses `values` dict for cross-field validation (`values.get("is_owner")`). Convert to `@model_validator(mode="after")` since it depends on other fields.
  - `UserUpdateSchema.check_password`: override, same pattern
  - `UserUpdateSchema.check_new_password`: uses `values.get("password")` for cross-field validation. Convert to `@model_validator(mode="after")`.
- `app/schemas/reviews.py` — 1 validator:
  - `rating_must_be_in_range`: `@validator("rating")` -> `@field_validator("rating")` with `@classmethod`

Files needing typing cleanup (no validators, but `str or None` / `str = None` patterns):
- `app/schemas/organizations.py` — `str or None = None` -> `str | None = None`
- `app/schemas/equipment.py` — `str = None` -> `str | None = None` for optional fields
- `app/schemas/orders.py` — `date = None` -> `date | None = None` for optional fields

Files with no changes needed:
- `app/schemas/auth.py` — clean BaseModel, already uses `str | None = None`
- `app/schemas/requisites.py` — clean BaseModel
- `app/schemas/notifications.py` — only `pydantic_queryset_creator`, no custom schemas with validators
- `app/schemas/files.py` — only `pydantic_model_creator`

**CRUD files (`.dict()` -> `.model_dump()`):**
- `app/crud/users.py` — 2 calls: `.dict()`, `.dict(exclude_unset=True)`
- `app/crud/organizations.py` — 3 calls: `.dict()`, `.dict()`, `.dict()`
- `app/crud/equipment.py` — 2 calls: `.dict(exclude_unset=True)`
- `app/crud/orders.py` — 1 call: `.dict(exclude_unset=True)`

**`app/main.py` — lifespan migration:**
- Replace `@app.on_event("startup")` / `@app.on_event("shutdown")` with lifespan context manager
- Pass `lifespan` into `FastAPI(...)` inside `create_application()`:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    init_db(app)
    await init_equipment_categories_db_table()
    yield
    # shutdown (nothing needed currently)

def create_application() -> FastAPI:
    application = FastAPI(title="Equipment sharing service", lifespan=lifespan)
    # ... routers, middleware ...
    return application
```

**`app/db.py` — Tortoise + lifespan:**
- Verify `register_tortoise` from `tortoise.contrib.fastapi` works with the lifespan pattern. If not, switch to Tortoise's `RegisterTortoise` async context manager inside lifespan.

**`project/tests/conftest.py` — httpx 0.28:**
- `AsyncClient(app=app, ...)` -> `AsyncClient(transport=ASGITransport(app=app), ...)`
- `from httpx import ASGITransport`
- Affects ~5 fixtures that create `AsyncClient`

**Tortoise ORM notes:**
- `_init_models.py` pattern is still required with Tortoise ORM 0.24+ for `pydantic_model_creator` to resolve relations. No change.
- `meta_override=EquipmentPydanticMeta` in `app/schemas/equipment.py`: verify this pattern still works with Tortoise 0.24+ Pydantic v2 integration. May need adjustment to align with `model_config` / `ConfigDict`.

**`app/models/notifications.py`:**
- Has `from pydantic import BaseModel` for notification content schemas. No change needed (BaseModel import path unchanged in v2).

**Risk:** High — most invasive phase, touches ~20 files. Largest single commit.

## Phase 4: python-jose -> PyJWT

### Dependency changes (`project/requirements.txt`)
- Remove `python-jose[cryptography]`
- Add `PyJWT`

### Code changes

**`app/services/auth.py`:**
- `from jose import JWTError, jwt` -> `import jwt` and `from jwt.exceptions import PyJWTError`
- `except JWTError:` -> `except PyJWTError:` (broad catch, equivalent to jose's `JWTError`)
- `jwt.encode()` and `jwt.decode()` — same API for HS256

**Risk:** Low

## Phase 5: Dev Tools

### Dependency changes (`project/requirements-dev.txt`)
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

## Phase 6: Remaining Minor Upgrades

### Dependency changes (`project/requirements.txt`, version bumps)
- `aiohttp` 3.8 -> 3.11+
- `Pillow` 10.0 -> 11+
- `python-docx` 0.8 -> 1.1+
- `python-multipart` 0.0.6 -> 0.0.20+
- `passlib[bcrypt]` 1.7 -> 1.7 (no major update available, stays)
- `bcrypt` 4.0 -> 4.2+
- `dadata` 21.10 -> 21.10 (no major update, stays)
- `gunicorn` 20.1 -> 23+
- `yookassa` 2.4 -> 3+

**Note:** These are listed as "minor" but some may have breaking changes (especially YooKassa 3+, Gunicorn 23, Pillow 11, python-docx 1.1). Each should be verified against its changelog. If code changes are needed, they will be addressed during implementation.

**passlib/bcrypt note:** passlib is effectively unmaintained. Verify that `passlib[bcrypt]` + `bcrypt 4.2` work together correctly. Test: create user, hash password, login. If compatibility issues arise, consider switching to direct `bcrypt` usage.

**Risk:** Low-Medium (depending on YooKassa, passlib/bcrypt interactions)

## Phase 7: Clean Slate Migrations + `.cursorrules` Update

### Migrations
- Delete `project/migrations/` directory
- Reset DB: `docker compose down -v` to clear PostgreSQL volume and Aerich state
- Run `aerich init-db` to regenerate initial migration from current models

### `.cursorrules`
- Python 3.13
- Pydantic v2 syntax patterns (`@field_validator`, `@model_validator`, `.model_dump()`, `pydantic_settings`)
- Remove Rocketry, Sentry from tech stack
- python-jose -> PyJWT
- `_init_models.py` still required
- Update commands reference if needed
