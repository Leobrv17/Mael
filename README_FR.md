# Mael API

## Présentation
Mael est un backend FastAPI pour un SaaS de portfolio, un espace client, le suivi de projets Scrum/Kanban et la facturation. Il utilise Firebase pour l'authentification, PostgreSQL via SQLAlchemy/Alembic et se lance facilement avec Docker.

> Version principale en anglais : consultez le fichier [README.md](README.md).

### Pile technique
- Python 3.12, FastAPI
- PostgreSQL avec SQLAlchemy 2 (async) et migrations Alembic
- Authentification Firebase (ID Token)
- Docker + docker-compose

### Lancement local
1. Copier `.env.example` en `.env` et ajuster les valeurs.
2. Lancer `docker-compose up --build`.
3. L'API est accessible sur `http://localhost:8000` avec la Swagger UI sur `/docs`.

Démarrage sans Docker :
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

### Authentification
Toutes les routes `/api/v1` (sauf celles sous `/public`) exigent un en-tête `Authorization: Bearer <idToken>` vérifié via le SDK Firebase Admin. En test, définir `FIREBASE_EMULATED_UID` et utiliser le jeton `test-token`.

### Principaux endpoints
Consultez `documentation/fr/routes.md` pour l'inventaire complet. En résumé :
- `GET /api/v1/me` : profil courant
- `POST /api/v1/organizations/` : créer une organisation (le créateur devient OWNER)
- `POST /api/v1/projects/` : créer un projet dans une organisation
- `POST /api/v1/tickets/` : créer un ticket
- `POST /api/v1/tickets/{id}/move` : déplacer un ticket (démarre/arrête le suivi du temps)
- `POST /api/v1/billing/invoices` + `/issue` : créer et émettre une facture (PDF intégré)
- `GET /api/v1/notifications/` : notifications in-app
- `POST /api/v1/public/leads` : leads publics avec un rate limiting simple

### Conventions
- Code typé (compatible mypy), lint avec ruff.
- Logs structurés en JSON.
- Suivi du temps automatique lors des transitions IN_PROGRESS → DONE.
- Factures verrouillées après émission et PDF généré (fpdf2).
- Mentions légales via le champ `legal_mentions` et numérotation séquentielle par organisation.

### Notes de conformité
- Préparation à la facturation électronique via `e_invoicing_required_at` sur `organizations`.
- `EmailOutbox` pour l'envoi d'emails de manière asynchrone.
- CORS configurables avec la variable d'environnement `CORS_ORIGINS`.
