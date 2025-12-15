from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from fpdf import FPDF
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Invoice, InvoiceLine, InvoiceStatus, Quote, QuoteLine, QuoteStatus


async def next_document_number(session: AsyncSession, model: type[Invoice | Quote], org_id: int) -> str:
    result = await session.execute(
        select(model.number).where(model.organization_id == org_id, model.number.is_not(None)).order_by(model.number.desc())
    )
    last = result.scalars().first()
    if last and "-" in last:
        year, seq = last.split("-")
        next_seq = int(seq) + 1
    else:
        year = datetime.utcnow().year
        next_seq = 1
    return f"{year}-{next_seq:04d}"


def build_invoice_pdf(invoice: Invoice) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice {invoice.number}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Status: {invoice.status}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Title: {invoice.title}", ln=True, align="L")
    for line in invoice.lines:
        pdf.cell(200, 10, txt=f"{line.description} - {line.quantity} x {line.unit_price}", ln=True)
    return pdf.output(dest="S").encode("latin1")


async def issue_invoice(session: AsyncSession, invoice: Invoice) -> Invoice:
    if invoice.locked:
        return invoice
    invoice.status = InvoiceStatus.ISSUED
    invoice.issue_date = datetime.utcnow()
    invoice.number = invoice.number or await next_document_number(session, Invoice, invoice.organization_id)
    pdf_bytes = build_invoice_pdf(invoice)
    invoice.pdf_blob = pdf_bytes
    invoice.pdf_checksum = sha256(pdf_bytes).hexdigest()
    invoice.pdf_content_type = "application/pdf"
    invoice.locked = True
    await session.flush()
    return invoice


async def accept_quote(session: AsyncSession, quote: Quote, ip: str | None, user_id: int | None) -> Quote:
    quote.status = QuoteStatus.ACCEPTED
    quote.accepted_at = datetime.utcnow()
    quote.accepted_by_ip = ip
    quote.accepted_by_user = user_id
    await session.flush()
    return quote
