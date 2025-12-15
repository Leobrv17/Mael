from app.models.billing import InvoiceStatus


def test_invoice_issue_locks_document(client):
    headers = {"Authorization": "Bearer test-token"}
    org_resp = client.post("/api/v1/organizations/", json={"name": "BillingOrg"}, headers=headers)
    org_id = org_resp.json()["id"]

    invoice_resp = client.post(
        "/api/v1/billing/invoices",
        json={
            "organization_id": org_id,
            "title": "Invoice A",
            "lines": [{"description": "Work", "quantity": 1, "unit_price": "100.00"}],
        },
        headers=headers,
    )
    invoice_id = invoice_resp.json()["id"]

    issue_resp = client.post(f"/api/v1/billing/invoices/{invoice_id}/issue", headers=headers)
    issued = issue_resp.json()
    assert issued["status"] == InvoiceStatus.ISSUED
    pdf_resp = client.get(f"/api/v1/billing/invoices/{invoice_id}/pdf", headers=headers)
    assert pdf_resp.status_code == 200
