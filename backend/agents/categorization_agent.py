
def categorize_invoice(data):
    """
    Universal Categorization Agent

    Categorizes different accounting documents
    using information extracted by the
    Universal Extraction Agent.
    """

    # ==========================================
    # GET AVAILABLE INFORMATION
    # ==========================================

    document_type = str(
        data.get("document_type", "")
    ).lower()

    vendor = str(
        data.get("vendor", "")
    ).lower()

    supplier = str(
        data.get("supplier", "")
    ).lower()

    customer = str(
        data.get("customer", "")
    ).lower()

    payer = str(
        data.get("payer", "")
    ).lower()

    payee = str(
        data.get("payee", "")
    ).lower()

    description = str(
        data.get("description", "")
    ).lower()

    category_from_ai = str(
        data.get("category", "")
    ).lower()


    # ==========================================
    # COMBINE INFORMATION
    # ==========================================

    text = " ".join([
        document_type,
        vendor,
        supplier,
        customer,
        payer,
        payee,
        description,
        category_from_ai
    ])


    # ==========================================
    # PURCHASE / PROCUREMENT
    # ==========================================

    if any(word in text for word in [
        "purchase",
        "procurement",
        "purchase order",
        "purchase invoice",
        "po",
        "supplier order"
    ]):

        category = "Purchase / Procurement"


    # ==========================================
    # PAYMENT
    # ==========================================

    elif any(word in text for word in [
        "payment",
        "payment voucher",
        "payment receipt",
        "paid",
        "bank transfer",
        "upi payment",
        "transaction"
    ]):

        category = "Payment"


    # ==========================================
    # DUE / OUTSTANDING
    # ==========================================

    elif any(word in text for word in [
        "due",
        "outstanding",
        "balance due",
        "amount due",
        "overdue",
        "receivable",
        "payable"
    ]):

        category = "Due / Outstanding"


    # ==========================================
    # SALES / REVENUE
    # ==========================================

    elif any(word in text for word in [
        "sales",
        "sales invoice",
        "revenue",
        "customer invoice",
        "client invoice",
        "sale"
    ]):

        category = "Sales / Revenue"


    # ==========================================
    # TECHNOLOGY EXPENSE
    # ==========================================

    elif any(word in text for word in [
        "technology",
        "technologies",
        "software",
        "cloud",
        "computer",
        "it services",
        "saas",
        "web development",
        "software development",
        "hosting",
        "server"
    ]):

        category = "Technology Expense"


    # ==========================================
    # TRAVEL EXPENSE
    # ==========================================

    elif any(word in text for word in [
        "travel",
        "airlines",
        "flight",
        "hotel",
        "booking",
        "transport",
        "taxi",
        "cab",
        "bus",
        "train"
    ]):

        category = "Travel Expense"


    # ==========================================
    # OFFICE EXPENSE
    # ==========================================

    elif any(word in text for word in [
        "office",
        "stationery",
        "printer",
        "paper",
        "furniture",
        "supplies",
        "office supplies"
    ]):

        category = "Office Expense"


    # ==========================================
    # GENERAL EXPENSE
    # ==========================================

    elif any(word in text for word in [
        "expense",
        "expense report",
        "business expense",
        "reimbursement"
    ]):

        category = "General Expense"


    # ==========================================
    # TAX
    # ==========================================

    elif any(word in text for word in [
        "tax",
        "gst",
        "gstin",
        "tds",
        "tax invoice",
        "tax payment"
    ]):

        category = "Tax Related"


    # ==========================================
    # CREDIT / DEBIT ADJUSTMENT
    # ==========================================

    elif any(word in text for word in [
        "credit note",
        "debit note",
        "adjustment"
    ]):

        category = "Accounting Adjustment"


    # ==========================================
    # QUOTATION
    # ==========================================

    elif any(word in text for word in [
        "quotation",
        "quote",
        "price quotation"
    ]):

        category = "Quotation"


    # ==========================================
    # PROFORMA
    # ==========================================

    elif "proforma" in text:

        category = "Proforma / Preliminary"


    # ==========================================
    # RECEIPT
    # ==========================================

    elif "receipt" in text:

        category = "Receipt"


    # ==========================================
    # BANK / ACCOUNT STATEMENT
    # ==========================================

    elif any(word in text for word in [
        "bank statement",
        "account statement",
        "statement"
    ]):

        category = "Account Statement"


    # ==========================================
    # BILL
    # ==========================================

    elif "bill" in text:

        category = "Bills / Payables"


    # ==========================================
    # DEFAULT
    # ==========================================

    else:

        category = "General Accounting"


    # ==========================================
    # RETURN AGENT RESULT
    # ==========================================

    return {

        "agent":
            "Categorization Agent",

        "category":
            category,

        "confidence":
            "Suggested",

        "document_type":
            data.get(
                "document_type",
                "accounting_document"
            ),

        "reason":
            "Category selected from document type, parties, description and extracted accounting information."
    }
