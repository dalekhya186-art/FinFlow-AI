
from sqlalchemy.orm import Session

from models.customer import Customer
from models.transaction import Transaction


def find_customer_history(
    customer_name,
    customer_id,
    db: Session
):
    """
    Customer History Agent

    Finds an existing customer and retrieves
    their complete transaction history.
    """

    customer = None

    # ==========================================
    # STEP 1: SEARCH BY CUSTOMER ID
    # ==========================================

    if customer_id:

        customer = db.query(
            Customer
        ).filter(
            Customer.customer_id == customer_id
        ).first()

    # ==========================================
    # STEP 2: SEARCH BY CUSTOMER NAME
    # ==========================================

    if not customer and customer_name:

        customer = db.query(
            Customer
        ).filter(
            Customer.name.ilike(
                customer_name.strip()
            )
        ).first()

    # ==========================================
    # STEP 3: CUSTOMER NOT FOUND
    # ==========================================

    if not customer:

        return {
            "status": "new_customer",
            "customer_found": False,
            "message": "Customer not found",
            "history": []
        }

    # ==========================================
    # STEP 4: GET TRANSACTION HISTORY
    # ==========================================

    transactions = db.query(
        Transaction
    ).filter(
        Transaction.customer_id
        == customer.customer_id
    ).order_by(
        Transaction.id.desc()
    ).all()

    history = []

    total_amount = 0.0
    total_paid = 0.0
    total_due = 0.0

    for transaction in transactions:

        # ------------------------------
        # Amount
        # ------------------------------

        amount = 0.0

        if transaction.amount:

            try:

                amount = float(
                    str(
                        transaction.amount
                    )
                    .replace(",", "")
                    .replace("₹", "")
                )

            except ValueError:

                amount = 0.0

        # ------------------------------
        # Paid Amount
        # ------------------------------

        paid_amount = 0.0

        if transaction.paid_amount:

            try:

                paid_amount = float(
                    str(
                        transaction.paid_amount
                    )
                    .replace(",", "")
                    .replace("₹", "")
                )

            except ValueError:

                paid_amount = 0.0

        # ------------------------------
        # Due Amount
        # ------------------------------

        due_amount = 0.0

        if transaction.due_amount:

            try:

                due_amount = float(
                    str(
                        transaction.due_amount
                    )
                    .replace(",", "")
                    .replace("₹", "")
                )

            except ValueError:

                due_amount = 0.0

        total_amount += amount
        total_paid += paid_amount
        total_due += due_amount

        history.append({

            "id": transaction.id,

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
                transaction.transaction_date

        })

    # ==========================================
    # STEP 5: RETURN CUSTOMER + HISTORY
    # ==========================================

    return {

        "status":
            "existing_customer",

        "customer_found":
            True,

        "customer": {

            "id":
                customer.id,

            "customer_id":
                customer.customer_id,

            "name":
                customer.name,

            "email":
                customer.email,

            "phone":
                customer.phone

        },

        "summary": {

            "total_transactions":
                len(history),

            "total_amount":
                total_amount,

            "total_paid":
                total_paid,

            "total_due":
                total_due

        },

        "history":
            history
    }
