from pydantic import BaseModel
from typing import List, Optional


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    vendor: Optional[str] = None
    subtotal: Optional[str] = None
    gst: Optional[str] = None
    total_amount: Optional[str] = None


class VerificationResult(BaseModel):
    status: str
    issues: List[str] = []


class CategoryResult(BaseModel):
    category: str
    confidence: str


class WorkflowResult(BaseModel):
    next_action: str
    priority: str
    category: str


class DocumentResult(BaseModel):
    status: str
    file_name: str
    file_type: str
    message: str


class DocumentResponse(BaseModel):
    document: DocumentResult
    invoice_data: InvoiceData
    verification: VerificationResult
    category: CategoryResult
    workflow: WorkflowResult