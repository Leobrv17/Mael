# Mael API Routes (English)

Primary language: English

## Public healthcheck
- **GET `/health`** — Returns `{ "status": "ok" }` to confirm Mael is reachable.

## Authenticated API (`/api/v1`)
All routes below require `Authorization: Bearer <idToken>` validated by Firebase Admin.

### Authentication
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/me` | Retrieve the currently authenticated user profile. |

### Organizations
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/organizations/` | Create an organization; creator is granted OWNER role. |
| GET | `/api/v1/organizations/` | List all organizations. |
| DELETE | `/api/v1/organizations/{org_id}` | Delete an organization if the requester is OWNER/ADMIN. |

### Projects
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/projects/` | Create a project within an organization. |
| GET | `/api/v1/projects/` | List all projects. |
| POST | `/api/v1/projects/{project_id}/members` | Add a member to a project with the given role. |
| POST | `/api/v1/projects/{project_id}/sprints` | Create a sprint for a project. |

### Tickets
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/tickets/` | Create a ticket in a project column. |
| POST | `/api/v1/tickets/{ticket_id}/move` | Move a ticket to another column and trigger time tracking. |
| POST | `/api/v1/tickets/{ticket_id}/comments` | Add a comment to a ticket. |
| GET | `/api/v1/tickets/{ticket_id}/time` | List recorded time segments for a ticket. |

### Billing
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/billing/quotes` | Create a quote with line items. |
| POST | `/api/v1/billing/quotes/{quote_id}/accept` | Accept a quote and mark it accordingly. |
| POST | `/api/v1/billing/invoices` | Create an invoice with line items. |
| POST | `/api/v1/billing/invoices/{invoice_id}/issue` | Issue an invoice (locks it and generates PDF). |
| GET | `/api/v1/billing/invoices/{invoice_id}/pdf` | Retrieve the stored invoice PDF checksum. |

### Notifications
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/notifications/` | List notifications for the current user. |
| POST | `/api/v1/notifications/{notification_id}/read` | Mark a notification as read. |

### Agenda
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/agenda/` | Create an agenda event. |
| GET | `/api/v1/agenda/` | List agenda events for the current user. |

### Public leads (`/api/v1/public`)
| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/public/leads/` | Accept a public lead submission with basic rate limiting. |
