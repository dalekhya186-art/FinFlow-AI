
def safe_number(value):
    """
    Convert amount values safely into float.
    """

    if value is None:
        return None

    try:
        value = str(value)

        value = value.replace(",", "")
        value = value.replace("₹", "")
        value = value.replace("Rs.", "")
        value = value.replace("Rs", "")
        value = value.replace("INR", "")
        value = value.replace("$", "")
        value = value.strip()

        return float(value)

    except (ValueError, TypeError):
        return None


def verify_invoice(data):
    """
    Universal Verification Agent

    Supports different accounting documents:

    Invoice
    Sales Invoice
    Purchase Invoice
    Bill
    Receipt
    Payment
    Purchase Order
    Due / Outstanding
    Expense
    Payment Voucher
    Credit Note
    Debit Note
    Quotation
    Proforma Invoice
    Bank Statement
    Account Statement
    Other accounting documents
    """

    issues = []

    # ==========================================
    # EMPTY DATA CHECK
    # ==========================================

    if not data:

        return {
            "agent": "Verification Agent",
            "status": "needs_review",
            "document_type": "Unknown",
            "issues": [
                "No document information extracted"
            ]
        }


    # ==========================================
    # DOCUMENT TYPE
    # ==========================================

    document_type = (
        data.get("document_type")
        or "Unknown"
    )

    document_type_lower = str(
        document_type
    ).lower().strip()


    # ==========================================
    # COMMON INFORMATION
    # ==========================================

    document_number = (
        data.get("document_number")
        or data.get("invoice_number")
        or data.get("receipt_number")
        or data.get("purchase_order_number")
    )


    has_date = (
        data.get("date")
        or data.get("invoice_date")
        or data.get("transaction_date")
    )


    has_amount = (
        data.get("total_amount")
        or data.get("paid_amount")
        or data.get("due_amount")
    )


    has_party = (
        data.get("vendor")
        or data.get("supplier")
        or data.get("customer")
        or data.get("payer")
        or data.get("payee")
    )


    # ==========================================
    # INVOICE
    # ==========================================

    if "invoice" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing invoice/document number"
            )


        if not has_date:

            issues.append(
                "Missing invoice date"
            )


        if not has_party:

            issues.append(
                "Missing vendor, supplier or customer"
            )


        if not data.get("total_amount"):

            issues.append(
                "Missing invoice total amount"
            )


    # ==========================================
    # BILL
    # ==========================================

    elif "bill" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing bill/document number"
            )


        if not has_date:

            issues.append(
                "Missing bill date"
            )


        if not has_party:

            issues.append(
                "Missing vendor or supplier"
            )


        if not data.get("total_amount"):

            issues.append(
                "Missing bill amount"
            )


    # ==========================================
    # PURCHASE ORDER
    # ==========================================

    elif (
        "purchase order" in document_type_lower
        or document_type_lower == "po"
    ):

        if not (
            data.get("purchase_order_number")
            or document_number
        ):

            issues.append(
                "Missing purchase order number"
            )


        if not has_date:

            issues.append(
                "Missing purchase order date"
            )


        if not (
            data.get("supplier")
            or data.get("vendor")
        ):

            issues.append(
                "Missing supplier information"
            )


        if not has_amount:

            issues.append(
                "Missing purchase order amount"
            )


    # ==========================================
    # RECEIPT
    # ==========================================

    elif "receipt" in document_type_lower:

        if not (
            data.get("receipt_number")
            or document_number
        ):

            issues.append(
                "Missing receipt number"
            )


        if not has_date:

            issues.append(
                "Missing receipt date"
            )


        if not has_amount:

            issues.append(
                "Missing receipt amount"
            )


    # ==========================================
    # PAYMENT
    # ==========================================

    elif (
        "payment" in document_type_lower
        or "payment voucher" in document_type_lower
    ):

        if not has_date:

            issues.append(
                "Missing payment date"
            )


        if not has_amount:

            issues.append(
                "Missing payment amount"
            )


        if not has_party:

            issues.append(
                "Missing payer or payee information"
            )


    # ==========================================
    # DUE / OUTSTANDING
    # ==========================================

    elif (
        "due" in document_type_lower
        or "outstanding" in document_type_lower
    ):

        if not data.get("due_amount"):

            issues.append(
                "Missing due amount"
            )


        if not data.get("due_date"):

            issues.append(
                "Missing due date"
            )


        if not has_party:

            issues.append(
                "Missing customer or vendor information"
            )


    # ==========================================
    # EXPENSE
    # ==========================================

    elif "expense" in document_type_lower:

        if not has_date:

            issues.append(
                "Missing expense date"
            )


        if not has_amount:

            issues.append(
                "Missing expense amount"
            )


        if not data.get("description"):

            issues.append(
                "Expense description is missing"
            )


    # ==========================================
    # CREDIT NOTE
    # ==========================================

    elif "credit note" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing credit note number"
            )


        if not has_date:

            issues.append(
                "Missing credit note date"
            )


        if not has_amount:

            issues.append(
                "Missing credit note amount"
            )


        if not has_party:

            issues.append(
                "Missing customer or vendor information"
            )


    # ==========================================
    # DEBIT NOTE
    # ==========================================

    elif "debit note" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing debit note number"
            )


        if not has_date:

            issues.append(
                "Missing debit note date"
            )


        if not has_amount:

            issues.append(
                "Missing debit note amount"
            )


        if not has_party:

            issues.append(
                "Missing customer or vendor information"
            )


    # ==========================================
    # QUOTATION
    # ==========================================

    elif "quotation" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing quotation number"
            )


        if not has_date:

            issues.append(
                "Missing quotation date"
            )


        if not has_party:

            issues.append(
                "Missing supplier or customer information"
            )


        if not has_amount:

            issues.append(
                "Missing quotation amount"
            )


    # ==========================================
    # PROFORMA INVOICE
    # ==========================================

    elif "proforma" in document_type_lower:

        if not document_number:

            issues.append(
                "Missing proforma invoice number"
            )


        if not has_date:

            issues.append(
                "Missing proforma invoice date"
            )


        if not has_party:

            issues.append(
                "Missing customer or vendor information"
            )


        if not has_amount:

            issues.append(
                "Missing proforma amount"
            )


    # ==========================================
    # BANK STATEMENT
    # ==========================================

    elif "bank statement" in document_type_lower:

        if not has_date:

            issues.append(
                "Statement date or transaction date missing"
            )


        if not data.get("account_number"):

            issues.append(
                "Bank account number not identified"
            )


    # ==========================================
    # ACCOUNT STATEMENT
    # ==========================================

    elif "statement" in document_type_lower:

        if not has_date:

            issues.append(
                "Statement date could not be identified"
            )


    # ==========================================
    # OTHER ACCOUNTING DOCUMENT
    # ==========================================

    else:

        # Do not force invoice-specific fields
        # on unknown documents.

        if not has_date:

            issues.append(
                "Document date could not be identified"
            )


        if not has_amount:

            issues.append(
                "Financial amount could not be identified"
            )


    # ==========================================
    # AMOUNT VERIFICATION
    # ==========================================

    subtotal = safe_number(
        data.get("subtotal")
    )

    gst = safe_number(
        data.get("gst")
    )

    tax = safe_number(
        data.get("tax")
    )

    total = safe_number(
        data.get("total_amount")
    )

    discount = safe_number(
        data.get("discount")
    )


    # ==========================================
    # SUBTOTAL + GST - DISCOUNT = TOTAL
    # ==========================================

    if (
        subtotal is not None
        and gst is not None
        and total is not None
    ):

        calculated_total = (
            subtotal
            + gst
        )

        if discount is not None:

            calculated_total -= discount


        if abs(
            calculated_total - total
        ) > 0.01:

            issues.append(
                "Subtotal + GST does not match total amount"
            )


    # ==========================================
    # SUBTOTAL + TAX - DISCOUNT = TOTAL
    # ==========================================

    elif (
        subtotal is not None
        and tax is not None
        and total is not None
    ):

        calculated_total = (
            subtotal
            + tax
        )

        if discount is not None:

            calculated_total -= discount


        if abs(
            calculated_total - total
        ) > 0.01:

            issues.append(
                "Subtotal + tax does not match total amount"
            )


    # ==========================================
    # PAID + DUE = TOTAL
    # ==========================================

    paid = safe_number(
        data.get("paid_amount")
    )

    due = safe_number(
        data.get("due_amount")
    )


    if (
        paid is not None
        and due is not None
        and total is not None
    ):

        calculated_total = (
            paid + due
        )


        if abs(
            calculated_total - total
        ) > 0.01:

            issues.append(
                "Paid amount + due amount does not match total amount"
            )


    # ==========================================
    # FINAL STATUS
    # ==========================================

    if issues:

        status = "needs_review"

        message = (
            "Document requires accountant review."
        )

    else:

        status = "verified"

        message = (
            "Document passed automated verification."
        )


    # ==========================================
    # RETURN AGENT RESULT
    # ==========================================

    return {

        "agent":
            "Verification Agent",

        "status":
            status,

        "document_type":
            document_type,

        "issues":
            issues,

        "checks_performed": [

            "Document type validation",

            "Document number validation",

            "Date validation",

            "Party information validation",

            "Amount validation",

            "Accounting amount consistency",

            "Document-specific validation"

        ],

        "message":
            message
    }
