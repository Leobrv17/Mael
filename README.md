# Mael API

## Overview (English)
Mael is a FastAPI backend for a SaaS portfolio, client workspace, Scrum/Kanban project tracking, and billing. The service ships with Firebase authentication, PostgreSQL via SQLAlchemy/Alembic, and Docker support for quick local runs.

> Looking for French? See [README_FR.md](README_FR.md).

### Tech stack
- Python 3.12, FastAPI
- PostgreSQL with SQLAlchemy 2 (async) and Alembic migrations
- Firebase Authentication (ID Token)
- Docker + docker-compose

### Local setup
1. Copy `.env.example` to `.env` and adjust the values.
2. Run `docker-compose up --build`.
3. The API is available at `http://localhost:8000` with the Swagger UI served at `/docs`.

To start without Docker:
```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

### Migrations
```bash
alembic upgrade head
```

### Tests
```bash
pytest
```

### Authentication
All `/api/v1` routes (except those under `/public`) require an `Authorization: Bearer <idToken>` header validated via the Firebase Admin SDK. For tests, set `FIREBASE_EMULATED_UID` and use the token `test-token`.

### Key endpoints
See `documentation/en/routes.md` for a full route catalog. Highlights include:
- `GET /api/v1/me`: current profile
- `POST /api/v1/organizations/`: create an organization (creator becomes OWNER)
- `POST /api/v1/projects/`: create a project inside an organization
- `POST /api/v1/tickets/`: create a ticket
- `POST /api/v1/tickets/{id}/move`: move a ticket (starts/stops time tracking)
- `POST /api/v1/billing/invoices` + `/issue`: create and issue an invoice (embedded PDF)
- `GET /api/v1/notifications/`: in-app notifications
- `POST /api/v1/public/leads`: public leads with basic rate limiting

### Conventions
- Typed code (mypy-friendly), lint via ruff.
- JSON-structured logs.
- Automatic time tracking on IN_PROGRESS → DONE transitions.
- Invoices locked after issuance with generated PDFs (fpdf2).
- Legal mentions handled via the `legal_mentions` field and sequential numbers per organization.

### Compliance notes
- E-invoicing readiness through `e_invoicing_required_at` on `organizations`.
- `EmailOutbox` for asynchronous email delivery.
- CORS configurable through the `CORS_ORIGINS` environment variable.
