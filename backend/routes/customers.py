from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.customer import Customer
from models.transaction import Transaction

from agents.customer_history_agent import (
    find_customer_history
)

import ast


# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# CLEAN OLD CUSTOMER DATA
# ==========================================

def clean_legacy_customer(customer, db):

    """
    Fixes old customer records where the complete
    dictionary was accidentally stored inside name.

    Example old value:

    {
        'name': 'Ravi Kumar',
        'email': 'ravi.kumar@example.com',
        'phone': '9876543210'
    }

    It will become:

    name  = Ravi Kumar
    email = ravi.kumar@example.com
    phone = 9876543210
    """

    if not customer.name:

        return False

    name_value = str(customer.name).strip()

    # ------------------------------------------
    # Only try parsing dictionary-like strings
    # ------------------------------------------

    if not (
        name_value.startswith("{")
        and name_value.endswith("}")
    ):

        return False

    try:

        data = ast.literal_eval(name_value)

    except Exception:

        return False

    if not isinstance(data, dict):

        return False

    changed = False

    # ------------------------------------------
    # NAME
    # ------------------------------------------

    real_name = (
        data.get("name")
        or data.get("customer")
        or data.get("customer_name")
        or data.get("client")
        or data.get("buyer")
        or data.get("buyer_name")
        or data.get("account_name")
    )

    if real_name:

        real_name = str(real_name).strip()

        if real_name:

            customer.name = real_name
            changed = True

    # ------------------------------------------
    # EMAIL
    # ------------------------------------------

    real_email = (
        data.get("email")
        or data.get("customer_email")
        or data.get("buyer_email")
        or data.get("client_email")
    )

    if real_email:

        real_email = str(real_email).strip().lower()

        if real_email:

            customer.email = real_email
            changed = True

    # ------------------------------------------
    # PHONE
    # ------------------------------------------

    real_phone = (
        data.get("phone")
        or data.get("customer_phone")
        or data.get("buyer_phone")
        or data.get("mobile")
    )

    if real_phone:

        real_phone = str(real_phone).strip()

        if real_phone:

            customer.phone = real_phone
            changed = True

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

    if changed:

        db.commit()
        db.refresh(customer)

    return changed


# ==========================================
# CONVERT CUSTOMER TO RESPONSE
# ==========================================

def customer_to_dict(customer):

    return {

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

        "created_at":
            customer.created_at
    }


# ==========================================
# GET ALL CUSTOMERS
# ==========================================

@router.get("/")
def get_customers(
    db: Session = Depends(get_db)
):

    customers = db.query(
        Customer
    ).order_by(
        Customer.id.desc()
    ).all()

    result = []

    for customer in customers:

        # Fix old malformed records
        clean_legacy_customer(
            customer,
            db
        )

        result.append(
            customer_to_dict(customer)
        )

    return {

        "total":
            len(result),

        "customers":
            result
    }


# ==========================================
# SEARCH CUSTOMER
# ==========================================

@router.get("/search")
def search_customer(
    q: str,
    db: Session = Depends(get_db)
):

    search_text = q.strip()

    if not search_text:

        return {

            "total": 0,

            "customers": []
        }

    # ------------------------------------------
    # First clean legacy records
    # ------------------------------------------

    all_customers = db.query(
        Customer
    ).all()

    for customer in all_customers:

        clean_legacy_customer(
            customer,
            db
        )

    # ------------------------------------------
    # Search
    # ------------------------------------------

    customers = db.query(
        Customer
    ).filter(

        (Customer.customer_id.ilike(
            f"%{search_text}%"
        ))

        |

        (Customer.name.ilike(
            f"%{search_text}%"
        ))

        |

        (Customer.email.ilike(
            f"%{search_text}%"
        ))

        |

        (Customer.phone.ilike(
            f"%{search_text}%"
        ))

    ).order_by(
        Customer.id.desc()
    ).all()

    result = []

    for customer in customers:

        result.append(
            customer_to_dict(customer)
        )

    return {

        "total":
            len(result),

        "customers":
            result
    }


# ==========================================
# CUSTOMER HISTORY
# ==========================================

@router.get("/{customer_id}/history")
def get_customer_history(
    customer_id: str,
    db: Session = Depends(get_db)
):

    customer = db.query(
        Customer
    ).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:

        return {

            "status":
                "error",

            "message":
                "Customer not found",

            "customer_id":
                customer_id,

            "history":
                []
        }

    # ------------------------------------------
    # Clean old record if required
    # ------------------------------------------

    clean_legacy_customer(
        customer,
        db
    )

    history = find_customer_history(

        customer_name=
            customer.name,

        customer_id=
            customer.customer_id,

        db=
            db
    )

    return history


# ==========================================
# CUSTOMER TRANSACTIONS
# ==========================================

@router.get("/{customer_id}/transactions")
def get_customer_transactions(
    customer_id: str,
    db: Session = Depends(get_db)
):

    customer = db.query(
        Customer
    ).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:

        return {

            "status":
                "error",

            "message":
                "Customer not found",

            "transactions":
                []
        }

    # ------------------------------------------
    # Clean old record if required
    # ------------------------------------------

    clean_legacy_customer(
        customer,
        db
    )

    transactions = db.query(
        Transaction
    ).filter(
        Transaction.customer_id == customer_id
    ).order_by(
        Transaction.id.desc()
    ).all()

    result = []

    for transaction in transactions:

        result.append({

            "id":
                transaction.id,

            "document_id":
                transaction.document_id,

            "transaction_type":
                transaction.transaction_type,

            "document_number":
                transaction.document_number,

            "amount":
                transaction.amount,

            "paid_amount":
                transaction.paid_amount,

            "due_amount":
                transaction.due_amount,

            "payment_status":
                transaction.payment_status,

            "transaction_date":
                transaction.transaction_date,

            "created_at":
                transaction.created_at
        })

    return {

        "status":
            "success",

        "customer": {

            "customer_id":
                customer.customer_id,

            "name":
                customer.name,

            "email":
                customer.email,

            "phone":
                customer.phone
        },

        "total_transactions":
            len(result),

        "transactions":
            result
    }
