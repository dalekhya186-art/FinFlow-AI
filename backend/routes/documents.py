from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os
import shutil
import ast

from database import SessionLocal

from models.document import Document
from models.customer import Customer
from models.transaction import Transaction

from agents.document_agent import process_document
from agents.customer_history_agent import find_customer_history
from services.invoice_extractor import extract_invoice_data
from agents.verification_agent import verify_invoice
from agents.categorization_agent import categorize_invoice
from agents.workflow_agent import create_workflow
from agents.manager_agent import manage_workflow


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================================
# DATABASE
# ==========================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ==========================================
# CLEAN CUSTOMER VALUE
# ==========================================

def clean_customer_value(value):

    if value is None:
        return ""

    if isinstance(value, dict):

        return (
            value.get("name")
            or value.get("customer_name")
            or value.get("client_name")
            or ""
        )

    value = str(value).strip()

    if not value:
        return ""

    if value.startswith("{") and value.endswith("}"):

        try:

            parsed = ast.literal_eval(value)

            if isinstance(parsed, dict):

                return (
                    parsed.get("name")
                    or parsed.get("customer_name")
                    or parsed.get("client_name")
                    or ""
                )

        except Exception:
            pass

    return value


# ==========================================
# CUSTOMER HELPER
# ==========================================

def find_or_create_customer(
    customer_name,
    customer_email,
    customer_phone,
    db
):

    customer_name = clean_customer_value(
        customer_name
    )

    customer_email = (
        str(customer_email).strip().lower()
        if customer_email
        else ""
    )

    customer_phone = (
        str(customer_phone).strip()
        if customer_phone
        else ""
    )

    customer = None

    # ======================================
    # SEARCH BY EMAIL
    # ======================================

    if customer_email:

        customer = db.query(
            Customer
        ).filter(
            Customer.email == customer_email
        ).first()

    # ======================================
    # SEARCH BY NAME
    # ======================================

    if not customer and customer_name:

        customer = db.query(
            Customer
        ).filter(
            Customer.name.ilike(
                customer_name
            )
        ).first()

    # ======================================
    # EXISTING CUSTOMER
    # ======================================

    if customer:

        if (
            customer_phone
            and not customer.phone
        ):

            customer.phone = customer_phone

        if (
            customer_email
            and not customer.email
        ):

            customer.email = customer_email

        db.commit()
        db.refresh(customer)

        return customer, "existing"

    # ======================================
    # NO CUSTOMER NAME
    # ======================================

    if not customer_name:

        return None, "not_available"

    # ======================================
    # CREATE CUSTOMER
    # ======================================

    new_customer = Customer(

        customer_id="TEMP",

        name=customer_name,

        email=(
            customer_email
            or None
        ),

        phone=(
            customer_phone
            or None
        )
    )

    db.add(
        new_customer
    )

    db.flush()

    new_customer.customer_id = (
        f"CUST-{new_customer.id:04d}"
    )

    db.commit()

    db.refresh(
        new_customer
    )

    return new_customer, "created"


# ==========================================
# DELETE OLD DOCUMENT DATA
# ==========================================

def delete_previous_document_data(db):

    """
    FinFlow AI keeps only ONE uploaded document.

    Old transactions are deleted first because
    they may reference old documents.

    Then all old documents are deleted.

    Customer records are NOT deleted.
    """

    # ======================================
    # DELETE OLD TRANSACTIONS
    # ======================================

    old_transactions = db.query(
        Transaction
    ).all()

    for transaction in old_transactions:

        db.delete(
            transaction
        )

    db.flush()


    # ======================================
    # DELETE OLD DOCUMENTS
    # ======================================

    old_documents = db.query(
        Document
    ).all()

    for document in old_documents:

        db.delete(
            document
        )

    db.flush()


    # ======================================
    # COMMIT DELETE
    # ======================================

    db.commit()


# ==========================================
# DELETE OLD UPLOAD FILES
# ==========================================

def delete_old_uploaded_files(
    keep_filename=None
):

    if not os.path.exists(
        UPLOAD_FOLDER
    ):

        return


    for filename in os.listdir(
        UPLOAD_FOLDER
    ):

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        # Only remove files
        if not os.path.isfile(
            file_path
        ):

            continue


        # Keep current file
        if (
            keep_filename
            and filename == keep_filename
        ):

            continue


        try:

            os.remove(
                file_path
            )

        except Exception as error:

            print(
                "Unable to delete old file:",
                filename,
                error
            )


# ==========================================
# UPLOAD DOCUMENT
# ==========================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # ======================================
    # 1. SAVE NEW FILE
    # ======================================

    safe_filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # ======================================
    # 2. DELETE PREVIOUS DOCUMENT DATA
    # ======================================

    delete_previous_document_data(
        db
    )


    # ======================================
    # 3. DELETE OLD PHYSICAL FILES
    # ======================================

    delete_old_uploaded_files(
        keep_filename=safe_filename
    )


    # ======================================
    # 4. DOCUMENT AGENT
    # ======================================

    document_result = process_document(
        file_path
    )

    if not isinstance(
        document_result,
        dict
    ):

        document_result = {

            "status":
                "success"

        }


    # ======================================
    # 5. AI EXTRACTION
    # ======================================

    invoice_data = extract_invoice_data(
        file_path
    )

    if not isinstance(
        invoice_data,
        dict
    ):

        invoice_data = {

            "document_type":
                "Unknown",

            "extraction_status":
                "failed",

            "customer":
                None,

            "vendor":
                None,

            "total_amount":
                None,

            "message":
                "Document information could not be extracted."

        }


    # ======================================
    # 6. CUSTOMER INFORMATION
    # ======================================

    customer_name = (

        invoice_data.get(
            "customer"
        )

        or invoice_data.get(
            "customer_name"
        )

        or invoice_data.get(
            "client"
        )

    )


    customer_email = (

        invoice_data.get(
            "customer_email"
        )

        or invoice_data.get(
            "email"
        )

    )


    customer_phone = (

        invoice_data.get(
            "customer_phone"
        )

        or invoice_data.get(
            "phone"
        )

    )


    # ======================================
    # 7. CUSTOMER
    # ======================================

    customer, customer_action = (
        find_or_create_customer(
            customer_name,
            customer_email,
            customer_phone,
            db
        )
    )


    # ======================================
    # 8. CUSTOMER HISTORY
    # ======================================

    if customer:

        customer_history = (
            find_customer_history(
                customer_name=customer.name,
                customer_id=customer.customer_id,
                db=db
            )
        )

    else:

        customer_history = {

            "status":
                "not_available",

            "customer_found":
                False,

            "history":
                []

        }


    # ======================================
    # 9. ADD CUSTOMER CONTEXT
    # ======================================

    invoice_data[
        "customer_history"
    ] = customer_history


    if customer:

        invoice_data[
            "customer_id"
        ] = customer.customer_id


    # ======================================
    # 10. VERIFICATION
    # ======================================

    verification = verify_invoice(
        invoice_data
    )

    if not isinstance(
        verification,
        dict
    ):

        verification = {

            "agent":
                "Verification Agent",

            "status":
                "needs_review",

            "document_type":
                invoice_data.get(
                    "document_type",
                    "Unknown"
                ),

            "issues": [

                "Verification Agent returned no result."

            ],

            "checks_performed":
                [],

            "message":
                "Document requires accountant review."

        }


    # ======================================
    # 11. CATEGORIZATION
    # ======================================

    category = categorize_invoice(
        invoice_data
    )

    if not isinstance(
        category,
        dict
    ):

        category = {

            "agent":
                "Categorization Agent",

            "category":
                "General Accounting",

            "confidence":
                "Low",

            "document_type":
                invoice_data.get(
                    "document_type",
                    "Unknown"
                ),

            "reason":
                "Categorization Agent returned no result."

        }


    # ======================================
    # 12. WORKFLOW
    # ======================================

    workflow = create_workflow(
        verification,
        category
    )

    if not isinstance(
        workflow,
        dict
    ):

        workflow = {

            "agent":
                "Workflow Agent",

            "status":
                "needs_review",

            "document_type":
                invoice_data.get(
                    "document_type",
                    "Unknown"
                ),

            "next_action":
                "Send document for accountant review",

            "priority":
                "High",

            "category":
                category.get(
                    "category",
                    "General Accounting"
                ),

            "issues":
                verification.get(
                    "issues",
                    []
                ),

            "human_approval_required":
                True,

            "workflow_reason":
                "Workflow Agent returned no result."

        }


    # ======================================
    # 13. MANAGER AGENT + OLLAMA
    # ======================================

    manager = manage_workflow(

        document_result,

        invoice_data,

        verification,

        category,

        workflow

    )


    # ======================================
    # 14. SAFETY CHECK
    # ======================================

    if not isinstance(
        manager,
        dict
    ):

        manager = {

            "agent":
                "Manager Agent",

            "status":
                "needs_review",

            "decision":
                "Send to accountant review",

            "priority":
                "High",

            "document_type":
                invoice_data.get(
                    "document_type",
                    "Unknown"
                ),

            "category":
                category.get(
                    "category",
                    "General Accounting"
                ),

            "reason":
                "Manager Agent returned no result.",

            "ai_reasoning":
                "GenAI Manager reasoning unavailable.",

            "genai_status":
                "unavailable",

            "verification":
                verification,

            "categorization":
                category,

            "workflow":
                workflow,

            "customer_history":
                customer_history,

            "human_approval_required":
                True,

            "decision_log": [

                "Manager Agent returned no result."

            ]

        }


    # ======================================
    # 15. VALUES
    # ======================================

    invoice_number = invoice_data.get(
        "invoice_number"
    )


    document_number = (

        invoice_data.get(
            "document_number"
        )

        or invoice_number

        or invoice_data.get(
            "receipt_number"
        )

        or invoice_data.get(
            "purchase_order_number"
        )

    )


    vendor = invoice_data.get(
        "vendor"
    )


    total_amount = invoice_data.get(
        "total_amount"
    )


    category_name = category.get(
        "category",
        "General Accounting"
    )


    verification_status = verification.get(
        "status",
        "needs_review"
    )


    workflow_status = manager.get(
        "decision",
        workflow.get(
            "next_action",
            "Pending Human Approval"
        )
    )


    document_type = invoice_data.get(
        "document_type",
        "accounting_document"
    )


    # ======================================
    # 16. CREATE NEW DOCUMENT
    # ======================================

    document = Document(

        file_name=safe_filename,

        invoice_number=invoice_number,

        vendor=vendor,

        total_amount=total_amount,

        category=category_name,

        verification_status=(
            verification_status
        ),

        workflow_status=(
            workflow_status
        )

    )


    db.add(
        document
    )

    db.commit()

    db.refresh(
        document
    )


    # ======================================
    # 17. ACTION
    # ======================================

    action = "created"

    message = (
        "New document saved as the current document"
    )


    # ======================================
    # 18. TRANSACTION
    # ======================================

    transaction_result = None


    if customer:

        payment_status = (
            invoice_data.get(
                "payment_status"
            )
        )


        if not payment_status:

            payment_status = (
                "Pending Approval"
            )


        transaction = Transaction(

            customer_id=(
                customer.customer_id
            ),

            document_id=(
                document.id
            ),

            transaction_type=(
                document_type
            ),

            document_number=(
                document_number
            ),

            amount=(
                invoice_data.get(
                    "total_amount"
                )
            ),

            paid_amount=(
                invoice_data.get(
                    "paid_amount"
                )
            ),

            due_amount=(
                invoice_data.get(
                    "due_amount"
                )
            ),

            payment_status=(
                payment_status
            ),

            transaction_date=(

                invoice_data.get(
                    "date"
                )

                or invoice_data.get(
                    "invoice_date"
                )

                or invoice_data.get(
                    "transaction_date"
                )

            )

        )


        db.add(
            transaction
        )

        db.commit()

        db.refresh(
            transaction
        )


        transaction_result = {

            "id":
                transaction.id,

            "action":
                "created",

            "customer_id":
                customer.customer_id

        }


    # ======================================
    # 19. CUSTOMER RESPONSE
    # ======================================

    customer_response = None


    if customer:

        customer_response = {

            "id":
                customer.id,

            "customer_id":
                customer.customer_id,

            "name":
                customer.name,

            "email":
                customer.email,

            "phone":
                customer.phone,

            "action":
                customer_action

        }


    # ======================================
    # 20. FINAL RESPONSE
    # ======================================

    return {

        "document":
            document_result,

        "invoice_data":
            invoice_data,

        "customer":
            customer_response,

        "customer_history":
            customer_history,

        "verification":
            verification,

        "category":
            category,

        "workflow":
            workflow,

        "manager_agent":
            manager,

        "database": {

            "id":
                document.id,

            "action":
                action,

            "message":
                message,

            "transaction":
                transaction_result

        }

    }


# ==========================================
# GET CURRENT DOCUMENT
# ==========================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = db.query(
        Document
    ).order_by(
        Document.id.desc()
    ).all()


    result = []


    for document in documents:

        result.append({

            "id":
                document.id,

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
                document.verification_status,

            "workflow_status":
                document.workflow_status

        })


    return {

        "total":
            len(result),

        "documents":
            result

    }