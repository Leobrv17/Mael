from fastapi import APIRouter

from app.api.routes import agenda, auth, billing, leads, notifications, organizations, projects, tickets

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(tickets.router, tags=["tickets"])
api_router.include_router(billing.router, tags=["billing"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(agenda.router, tags=["agenda"])
api_router.include_router(leads.router, tags=["public"], prefix="/public")
