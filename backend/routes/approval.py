from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models.document import Document


router = APIRouter(
    prefix="/approval",
    tags=["Human Approval"]
)


class ApprovalRequest(BaseModel):
    document_name: str
    decision: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def approve_document(
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):

    decision = request.decision.lower().strip()


    # Find document
    document = db.query(Document).filter(
        Document.file_name == request.document_name
    ).order_by(
        Document.id.desc()
    ).first()


    # Document not found
    if not document:

        return {
            "status": "error",
            "message": "Document not found in database",
            "document": request.document_name
        }


    # Approve
    if decision == "approve":

        status = "approved"
        message = "Document approved by human"

        document.workflow_status = "approved"


    # Reject
    elif decision == "reject":

        status = "rejected"
        message = "Document rejected by human"

        document.workflow_status = "rejected"


    # Review
    elif decision == "review":

        status = "needs_review"
        message = "Document sent for further review"

        document.workflow_status = "needs_review"


    # Invalid decision
    else:

        return {
            "status": "error",
            "message": "Invalid decision. Use approve, reject, or review."
        }


    # Save change to database
    db.commit()
    db.refresh(document)


    return {
        "document": document.file_name,
        "document_id": document.id,
        "decision": decision,
        "status": status,
        "workflow_status": document.workflow_status,
        "message": message
    }
