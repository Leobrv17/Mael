from datetime import datetime

from pydantic import BaseModel

from app.models.core import GlobalRole


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationOut(OrganizationBase):
    id: int
    e_invoicing_required_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgMembership(BaseModel):
    id: int
    user_id: int
    role: GlobalRole

    model_config = {"from_attributes": True}
