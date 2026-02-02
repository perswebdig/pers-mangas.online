<!-- Copilot instructions for AI coding agents working on this repo -->
# Guidance for AI coding agents

This project is a FastAPI-based web app that proxies MangaDex and serves Jinja2 HTML templates. Use these focused instructions to be immediately productive.

- **Big picture:** The app is a monolith combining a FastAPI JSON API proxy to MangaDex and server-rendered pages using Jinja2 templates. Backend code lives at [main.py](main.py) (routes, auth, API proxy) and data models are defined in [models.py](models.py) (canonical) and partially duplicated in [main.py](main.py) as runtime models.

- **Data & DB patterns:**
  - Database access uses SQLAlchemy `SessionLocal` from [database.py](database.py) or the inline `SessionLocal` in [main.py](main.py). Prefer `models.py` for schema changes and migration targets.
  - The project supports either SQLite (local dev) or PostgreSQL (production) via `DATABASE_URL` in `.env`.
  - `Base.metadata.create_all(...)` is called from `main.py` on startup; migrations live in `migrations/` and alembic is in `requirements.txt`.

- **Auth & session:**
  - Authentication uses JWT tokens set as an `access_token` cookie. Inspect `create_access_token()` and `get_current_user()` in [main.py](main.py).
  - Passwords hashed with `passlib` (`bcrypt`). Look for `get_password_hash()` and `verify_password()`.

- **API integration patterns:**
  - External calls to MangaDex use `httpx.AsyncClient` (see `/api/mangadex/*` endpoints in [main.py](main.py)). These calls typically set `verify=False` and have a short timeout — preserve existing error handling semantics when editing.
  - Caching of MangaDex data can be stored in `models.Manga`, `Chapter`, and related tables when adding persistence.

- **Templates & static:**
  - Server-rendered pages use Jinja2 templates under [templates/](templates/) and static assets under [static/](static/). Site configuration (colors, ad scripts, footer text) is persisted in `SiteConfig` and injected into templates via `get_site_config()`.

- **Admin & ads:**
  - Admin endpoints require `user.is_admin` checks (see `admin_personalizar` and `/api/admin/config`). Ad scripts are stored in `SiteConfig` fields (`ad_header_script`, etc.). Be careful when editing how scripts are stored/displayed to avoid XSS regressions.

- **Developer workflows:**
  - Local run (development):
    - Create a venv and install with `pip install -r requirements.txt`.
    - Copy `.env.example` to `.env` and set `DATABASE_URL` and `SECRET_KEY`.
    - Run the app: `python main.py` (starts uvicorn) or `uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
  - DB initialization: tables are auto-created on startup, or use `python init_db.py` for PostgreSQL seed (note: `init_db.py` contains a broken `os.getenv(...)` key and should be used carefully).
  - Migrations: use Alembic in `migrations/` for schema changes; prefer editing `models.py` then generating migration.

- **Project-specific gotchas discovered:**
  - There are duplicate `User`/`SiteConfig` definitions between `models.py` and `main.py`. For schema and migrations, treat `models.py` as canonical and align `main.py` where safe.
  - `init_db.py` attempts to read a DB URL using `os.getenv("postgresql://...")` which is incorrect; prefer using `DATABASE_URL` from `.env` or `database.py` helpers.
  - `database.py` sets `poolclass=NullPool` intentionally; maintain this when changing DB engine configuration.

- **When editing code:**
  - Preserve the use of `get_db()` dependency and `SessionLocal` patterns to avoid leaking sessions. Update both `database.py` and callers if you change the session creation.
  - Keep template/context keys stable: routes pass `request`, `user`, and `config` into templates — do not rename these without updating templates in `templates/`.
  - When modifying external API calls, keep `httpx.AsyncClient` usage and timeouts consistent; tests and user flows assume asynchronous endpoints.

- **Files worth inspecting for context:**
  - [main.py](main.py) — entrypoint, routes, auth, API proxy
  - [models.py](models.py) — canonical ORM models for migrations
  - [database.py](database.py) — DB engine/session config
  - [init_db.py](init_db.py) — helper to seed DB (has quirks)
  - `templates/` and `static/` — UI patterns and theme variables

If anything is unclear or you want me to prefer a different source-of-truth (for example, move models fully into `models.py` and remove duplicates), say so and I will update this guidance.
