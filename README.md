# SaaS Backend (FastAPI + PostgreSQL)

Backend pour site vitrine + espace client + gestion de projets Scrum/Kanban + facturation.

## Stack
- Python 3.12, FastAPI
- PostgreSQL + SQLAlchemy 2.0 (async) + Alembic
- Firebase Authentication (ID Token)
- Docker + docker-compose

## Démarrage local
1. Copier `.env.example` vers `.env` et ajuster les valeurs.
2. Lancer `docker-compose up --build`.
3. L'API est disponible sur `http://localhost:8000` avec documentation OpenAPI intégrée.

Pour un lancement sans Docker :
```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Migrations
```bash
alembic upgrade head
```

## Tests
```bash
pytest
```

## Authentification
Toutes les routes `/api/v1` (sauf `/public`) nécessitent un header `Authorization: Bearer <idToken>` vérifié via Firebase Admin SDK. En test, définir `FIREBASE_EMULATED_UID` et utiliser le token `test-token`.

## Principaux endpoints
- `GET /api/v1/me` : profil courant
- `POST /api/v1/organizations/` : créer une organisation (membre devient OWNER)
- `POST /api/v1/projects/` : créer un projet dans une organisation
- `POST /api/v1/tickets/` : créer un ticket
- `POST /api/v1/tickets/{id}/move` : déplacer un ticket (démarre/arrête le time tracking)
- `POST /api/v1/billing/invoices` + `/issue` : créer et émettre une facture (PDF embarqué)
- `GET /api/v1/notifications/` : notifications in-app
- `POST /api/v1/public/leads` : leads publics avec rate-limiting simple

## Conventions
- Code typé (mypy-friendly), lint via ruff.
- Logs structurés JSON.
- Time tracking automatique lors des transitions IN_PROGRESS → DONE.
- Factures verrouillées après émission et PDF généré (fpdf2).
- Mentions légales : champ `legal_mentions` prévu + ajout automatique de numéro séquentiel par organisation.

## Notes conformité
- Prévoit e-invoicing via `e_invoicing_required_at` dans `organizations`.
- EmailOutbox pour envoi asynchrone sans bloquer les requêtes.
- CORS configurables via env `CORS_ORIGINS`.
