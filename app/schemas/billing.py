from datetime import datetime
from decimal import Decimal
from typing import Sequence

from pydantic import BaseModel, Field

from app.models.billing import InvoiceStatus, QuoteStatus


class QuoteLineCreate(BaseModel):
    description: str
    quantity: int = Field(ge=1)
    unit_price: Decimal


class QuoteCreate(BaseModel):
    organization_id: int
    title: str
    valid_until: datetime | None = None
    lines: list[QuoteLineCreate]


class QuoteOut(BaseModel):
    id: int
    number: str | None
    organization_id: int
    title: str
    status: QuoteStatus
    valid_until: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceLineCreate(BaseModel):
    description: str
    quantity: int = Field(ge=1)
    unit_price: Decimal


class InvoiceCreate(BaseModel):
    organization_id: int
    title: str
    lines: list[InvoiceLineCreate]


class InvoiceOut(BaseModel):
    id: int
    number: str | None
    organization_id: int
    title: str
    status: InvoiceStatus
    issue_date: datetime | None
    locked: bool

    model_config = {"from_attributes": True}
