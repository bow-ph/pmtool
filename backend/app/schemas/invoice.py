from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvoiceBase(BaseModel):
    invoice_number: str
    user_id: int
    subscription_id: int
    total_amount: float
    pdf_path: Optional[str] = None
    status: str = "pending"

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    pdf_path: Optional[str] = None
    status: Optional[str] = None

class Invoice(InvoiceBase):
    id: int
    issue_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InvoiceResponse(Invoice):
    """Response model for invoice endpoints"""
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "invoice_number": "INV-2024-01-0001",
                "user_id": 1,
                "subscription_id": 1,
                "total_amount": 119.0,
                "pdf_path": "/invoices/2024/01/INV-2024-01-0001.pdf",
                "status": "paid",
                "issue_date": "2024-01-24T00:00:00Z",
                "created_at": "2024-01-24T00:00:00Z",
                "updated_at": None
            }
        }
