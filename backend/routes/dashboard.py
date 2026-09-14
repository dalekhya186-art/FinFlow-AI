from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.document import Document


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# Database connection
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db)
):

    # Total documents
    total_documents = db.query(
        Document
    ).count()


    # Verified documents
    verified_documents = db.query(
        Document
    ).filter(
        Document.verification_status == "verified"
    ).count()


    # Documents needing review
    pending_documents = db.query(
        Document
    ).filter(
        Document.verification_status == "needs_review"
    ).count()


    # Total amount
    documents = db.query(
        Document
    ).all()

    total_amount = 0

    for document in documents:

        if document.total_amount:

            try:
                amount = float(
                    document.total_amount
                    .replace(",", "")
                    .replace("₹", "")
                )

                total_amount += amount

            except ValueError:
                pass


    # Recent documents
    recent_documents = db.query(
        Document
    ).order_by(
        Document.id.desc()
    ).limit(5).all()


    recent_data = []

    for document in recent_documents:

        recent_data.append({

            "id": document.id,

            "file_name":
                document.file_name,

            "invoice_number":
                document.invoice_number,

            "vendor":
                document.vendor,

            "total_amount":
                document.total_amount,

            "category":
                document.category,

            "verification_status":
                document.verification_status

        })


    return {

        "total_documents":
            total_documents,

        "verified_documents":
            verified_documents,

        "pending_documents":
            pending_documents,

        "total_amount":
            total_amount,

        "recent_documents":
            recent_data

    }