# Transcription API

Async REST API for managing audio transcription jobs. Built with FastAPI, SQLAlchemy 2 (async), PostgreSQL, and JWT auth.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2 (asyncpg) |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| Migrations | Alembic |
| Package manager | uv |

## Quickstart

**1. Clone and configure:**
```bash
cp .env.example .env
# edit .env — set JWT_SECRET to a real secret
```

**2. Start the database:**
```bash
docker compose up -d db
```

**3. Run migrations:**
```bash
uv run alembic upgrade head
```

**4. Start the server:**
```bash
uv run fastapi dev app/main.py
```

API docs available at `http://localhost:8000/docs`

## Run with Docker**

```bash
docker compose up --build
```

## API

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | — | Register a new user |
| POST | `/auth/token` | — | Login, get JWT |
| GET | `/users/me` | JWT | Current user profile |
| POST | `/jobs/` | JWT | Submit a transcription job |
| GET | `/jobs/` | JWT | List jobs (paginated) |
| GET | `/jobs/{id}` | JWT | Get job by ID |
| PATCH | `/jobs/{id}/status` | JWT | Update job status |
| DELETE | `/jobs/{id}` | JWT | Soft-delete a job |
| GET | `/healthcheck` | — | Health + DB ping |

## Example flow

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -d 'username=you@example.com&password=yourpassword' \
  | jq -r .access_token)

# Submit a job
curl -X POST http://localhost:8000/jobs/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"language":"en","audio_url":"https://example.com/audio.mp3","file_ext":"mp3","priority":1}'
```

## Project structure

```
app/
  auth.py          # password hashing, JWT utilities
  config.py        # settings (pydantic-settings)
  database.py      # engine + session factory
  dependencies.py  # get_db, get_current_user, PaginationParams
  main.py          # FastAPI app + routers
  models/          # SQLAlchemy models
  routes/          # auth, jobs, users
  schemas/         # Pydantic schemas
migrations/        # Alembic migrations
tests/             # pytest test suite
```
