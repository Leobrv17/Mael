from datetime import datetime

from pydantic import BaseModel

from app.models.core import GlobalRole


class UserBase(BaseModel):
    email: str
    name: str | None = None


class UserCreate(UserBase):
    firebase_uid: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgMembershipOut(BaseModel):
    id: int
    organization_id: int
    role: GlobalRole

    model_config = {"from_attributes": True}
