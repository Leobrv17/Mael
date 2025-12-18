# Routes API Mael (Français)

Langue principale : français

## Vérification publique
- **GET `/health`** — Retourne `{ "status": "ok" }` pour confirmer l'accessibilité de Mael.

## API authentifiée (`/api/v1`)
Toutes les routes ci-dessous requièrent `Authorization: Bearer <idToken>` validé par Firebase Admin.

### Authentification
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| GET | `/api/v1/me` | Récupère le profil de l'utilisateur authentifié. |

### Organisations
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/organizations/` | Crée une organisation ; le créateur reçoit le rôle OWNER. |
| GET | `/api/v1/organizations/` | Liste toutes les organisations. |
| DELETE | `/api/v1/organizations/{org_id}` | Supprime une organisation si le demandeur est OWNER/ADMIN. |

### Projets
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/projects/` | Crée un projet dans une organisation. |
| GET | `/api/v1/projects/` | Liste tous les projets. |
| POST | `/api/v1/projects/{project_id}/members` | Ajoute un membre à un projet avec le rôle indiqué. |
| POST | `/api/v1/projects/{project_id}/sprints` | Crée un sprint pour un projet. |

### Tickets
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/tickets/` | Crée un ticket dans une colonne du projet. |
| POST | `/api/v1/tickets/{ticket_id}/move` | Déplace un ticket vers une autre colonne et lance le suivi du temps. |
| POST | `/api/v1/tickets/{ticket_id}/comments` | Ajoute un commentaire à un ticket. |
| GET | `/api/v1/tickets/{ticket_id}/time` | Liste les segments de temps enregistrés pour un ticket. |

### Facturation
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/billing/quotes` | Crée un devis avec ses lignes. |
| POST | `/api/v1/billing/quotes/{quote_id}/accept` | Accepte un devis et met à jour son état. |
| POST | `/api/v1/billing/invoices` | Crée une facture avec ses lignes. |
| POST | `/api/v1/billing/invoices/{invoice_id}/issue` | Émet une facture (la verrouille et génère le PDF). |
| GET | `/api/v1/billing/invoices/{invoice_id}/pdf` | Récupère l'empreinte du PDF de facture stocké. |

### Notifications
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| GET | `/api/v1/notifications/` | Liste les notifications de l'utilisateur courant. |
| POST | `/api/v1/notifications/{notification_id}/read` | Marque une notification comme lue. |

### Agenda
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/agenda/` | Crée un événement d'agenda. |
| GET | `/api/v1/agenda/` | Liste les événements d'agenda de l'utilisateur courant. |

### Leads publics (`/api/v1/public`)
| Méthode | Chemin | Objectif |
| --- | --- | --- |
| POST | `/api/v1/public/leads/` | Accepte une demande de lead public avec un rate limiting simple. |
