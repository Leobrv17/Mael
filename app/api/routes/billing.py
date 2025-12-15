from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.billing import Invoice, InvoiceLine, InvoiceStatus, Quote, QuoteLine, QuoteStatus
from app.schemas.billing import InvoiceCreate, InvoiceOut, QuoteCreate, QuoteOut
from app.schemas.common import Message
from app.services.billing import accept_quote, issue_invoice, next_document_number

router = APIRouter(prefix="/billing")


@router.post("/quotes", response_model=QuoteOut)
async def create_quote(
    payload: QuoteCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> QuoteOut:
    quote = Quote(
        organization_id=payload.organization_id,
        title=payload.title,
        valid_until=payload.valid_until,
    )
    session.add(quote)
    await session.flush()
    for line in payload.lines:
        session.add(QuoteLine(quote_id=quote.id, **line.model_dump()))
    await session.commit()
    await session.refresh(quote)
    return quote


@router.post("/quotes/{quote_id}/accept", response_model=QuoteOut)
async def accept_quote_endpoint(
    quote_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> QuoteOut:
    quote = await session.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    await accept_quote(session, quote, ip="0.0.0.0", user_id=current_user.id)
    await session.commit()
    await session.refresh(quote)
    return quote


@router.post("/invoices", response_model=InvoiceOut)
async def create_invoice(
    payload: InvoiceCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvoiceOut:
    invoice = Invoice(organization_id=payload.organization_id, title=payload.title)
    session.add(invoice)
    await session.flush()
    for line in payload.lines:
        session.add(InvoiceLine(invoice_id=invoice.id, **line.model_dump()))
    await session.commit()
    await session.refresh(invoice)
    return invoice


@router.post("/invoices/{invoice_id}/issue", response_model=InvoiceOut)
async def issue_invoice_endpoint(
    invoice_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> InvoiceOut:
    invoice = await session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    await issue_invoice(session, invoice)
    await session.commit()
    await session.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    invoice = await session.get(Invoice, invoice_id)
    if not invoice or not invoice.pdf_blob:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF unavailable")
    return Message(message=invoice.pdf_checksum or "missing")
