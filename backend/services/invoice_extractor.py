import re
import json
import requests
import pdfplumber


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path):
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:

        return "", str(e)

    return text.strip(), None


# ============================================================
# CONVERT AI VALUE TO SIMPLE STRING
# ============================================================

def clean_value(value):
    """
    Converts AI values into safe database-compatible strings.

    Examples:

    "Ravi Kumar"
        -> "Ravi Kumar"

    {"name": "Ravi Kumar"}
        -> "Ravi Kumar"

    {"customer_name": "Ravi Kumar"}
        -> "Ravi Kumar"

    ["Ravi Kumar"]
        -> "Ravi Kumar"

    None
        -> None
    """

    if value is None:
        return None

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    if isinstance(value, str):

        value = value.strip()

        return value if value else None

    # --------------------------------------------------------
    # DICTIONARY
    # --------------------------------------------------------

    if isinstance(value, dict):

        preferred_keys = [
            "name",
            "value",
            "text",
            "label",
            "customer_name",
            "vendor_name",
            "supplier_name",
            "company",
            "person"
        ]

        for key in preferred_keys:

            if key in value:

                cleaned = clean_value(
                    value.get(key)
                )

                if cleaned:
                    return cleaned

        return None

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    if isinstance(value, list):

        if not value:
            return None

        cleaned_items = []

        for item in value:

            cleaned = clean_value(item)

            if cleaned:
                cleaned_items.append(cleaned)

        if cleaned_items:

            return ", ".join(cleaned_items)

        return None

    # --------------------------------------------------------
    # NUMBER / OTHER
    # --------------------------------------------------------

    return str(value).strip() or None


# ============================================================
# LOCAL OLLAMA GENAI
# ============================================================

def ask_local_ai(text):

    prompt = f"""
You are the Universal Accounting Document Extraction Agent
of FinFlow AI.

Your job is to analyze ANY accounting or financial document.

The document may be:

1. Invoice
2. Sales Invoice
3. Purchase Invoice
4. Receipt
5. Payment Receipt
6. Bill
7. Due Notice
8. Outstanding Notice
9. Purchase Order
10. Expense Document
11. Payment Voucher
12. Credit Note
13. Debit Note
14. Tax / GST Document
15. Bank Statement
16. Quotation
17. Proforma Invoice
18. Account Statement
19. Sales Document
20. Other Accounting Document

IMPORTANT:

Do NOT assume the document is an invoice.

First identify the actual document type from the document content.

Then extract meaningful accounting information.

Do not invent information.

If information is not available, return null.

If multiple items exist, put them inside the items array.

Return ONLY valid JSON.


============================================================
VENDOR AND CUSTOMER IDENTIFICATION
============================================================

You MUST distinguish Vendor/Supplier from Customer/Buyer.

VENDOR / SUPPLIER:

The person or organization providing products or services.

Look for:

- Vendor
- Supplier
- Seller
- From
- Supplied By
- Service Provider
- Issued By
- Seller Name


CUSTOMER / BUYER:

The person or organization purchasing products or services.

Look for:

- Customer
- Customer Name
- Client
- Buyer
- Buyer Name
- Bill To
- Billed To
- Sold To
- Ship To
- Purchaser
- Consignee
- Account Name
- Customer Details
- Customer Information


CRITICAL RULES:

1. Vendor and Customer are DIFFERENT roles.

2. NEVER copy vendor name into customer.

3. NEVER copy supplier name into customer.

4. If only vendor/supplier information exists,
   customer MUST be null.

5. If customer information exists,
   extract the actual customer.

6. If customer name exists but email/phone does not exist,
   return the available customer name and null for missing fields.

7. If customer email or phone exists but customer name
   is not available, do not invent a customer name.

8. Do not guess customer information.

9. Do not use filename to invent customer information.

10. Do not use vendor name as fallback customer.

11. For purchase documents:

    Supplier/Vendor = seller/provider.

    Customer/Buyer = organization/person purchasing.

12. For sales documents:

    Seller/Vendor = organization/person selling.

    Customer/Buyer = organization/person purchasing.

13. For receipts:

    Payer may be customer.

    Payee may be vendor/business.

14. For payment documents:

    Payer and Payee must be extracted separately.

15. If there is no customer information,
    customer MUST remain null.


============================================================
STRICT OUTPUT TYPE RULES
============================================================

These fields MUST ALWAYS be simple strings or null:

vendor
supplier
customer
customer_email
customer_phone
payer
payee
document_type
document_title
document_number
invoice_number
purchase_order_number
receipt_number
date
invoice_date
due_date
currency
subtotal
tax
gst
discount
total_amount
paid_amount
due_amount
payment_status
payment_method
category
gst_number
description
account_number
transaction_date
other_information

IMPORTANT:

DO NOT return an object/dictionary for these fields.

Correct example:

"vendor": "ABC Technologies Pvt Ltd"

Wrong example:

"vendor": {{
    "name": "ABC Technologies Pvt Ltd",
    "description": "Vendor"
}}

Correct example:

"customer": "Ravi Kumar"

Wrong example:

"customer": {{
    "name": "Ravi Kumar",
    "email": "ravi.kumar@example.com"
}}

If unavailable:

"customer": null


============================================================
OUTPUT FORMAT
============================================================

Return exactly this JSON structure:

{{
    "document_type": null,
    "document_title": null,
    "document_number": null,
    "invoice_number": null,
    "purchase_order_number": null,
    "receipt_number": null,
    "date": null,
    "invoice_date": null,
    "due_date": null,
    "vendor": null,
    "supplier": null,
    "customer": null,
    "customer_email": null,
    "customer_phone": null,
    "payer": null,
    "payee": null,
    "currency": null,
    "subtotal": null,
    "tax": null,
    "gst": null,
    "discount": null,
    "total_amount": null,
    "paid_amount": null,
    "due_amount": null,
    "payment_status": null,
    "payment_method": null,
    "items": [],
    "category": null,
    "gst_number": null,
    "description": null,
    "account_number": null,
    "transaction_date": null,
    "other_information": null
}}


============================================================
DOCUMENT TYPE RULES
============================================================

If it is a receipt:

document_type = "Receipt"

If it is a purchase order:

document_type = "Purchase Order"

If it is a due or outstanding notice:

document_type = "Due / Outstanding"

If it is a credit note:

document_type = "Credit Note"

If it is a debit note:

document_type = "Debit Note"

If it is a payment voucher:

document_type = "Payment Voucher"

If it is an expense report:

document_type = "Expense Document"

If it is a quotation:

document_type = "Quotation"

If it is a proforma invoice:

document_type = "Proforma Invoice"

If it is a bank statement:

document_type = "Bank Statement"

If it is a sales invoice:

document_type = "Sales Invoice"

If it is a purchase invoice:

document_type = "Purchase Invoice"

If it is a normal invoice:

document_type = "Invoice"

Never assume every document is an invoice.


============================================================
EXTRACTION RULES
============================================================

Extract:

- document information
- vendor/supplier information
- customer/buyer information
- payer/payee information
- payment information
- due information
- tax/GST information
- item information
- accounting amounts
- dates
- document numbers

Do not calculate missing values.

Do not create fake customer information.

Do not create fake vendor information.

Do not create fake amounts.

Do not create fake dates.


============================================================
ITEM STRUCTURE
============================================================

For items use:

[
    {{
        "name": null,
        "description": null,
        "quantity": null,
        "unit_price": null,
        "amount": null
    }}
]


============================================================
DOCUMENT TEXT
============================================================

{text}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        ai_response = data.get(
            "response",
            ""
        )

        if not ai_response:

            return None

        # ----------------------------------------------------
        # REMOVE POSSIBLE MARKDOWN JSON FENCES
        # ----------------------------------------------------

        ai_response = ai_response.strip()

        if ai_response.startswith("```json"):

            ai_response = ai_response[7:]

        elif ai_response.startswith("```"):

            ai_response = ai_response[3:]

        if ai_response.endswith("```"):

            ai_response = ai_response[:-3]

        ai_response = ai_response.strip()

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        result = json.loads(
            ai_response
        )

        return result

    except requests.exceptions.ConnectionError as e:

        print(
            "Ollama connection error:",
            e
        )

        return None

    except requests.exceptions.Timeout as e:

        print(
            "Ollama timeout:",
            e
        )

        return None

    except json.JSONDecodeError as e:

        print(
            "Invalid JSON returned by Ollama:",
            e
        )

        return None

    except Exception as e:

        print(
            "Universal AI extraction error:",
            e
        )

        return None


# ============================================================
# RULE-BASED UNIVERSAL FALLBACK
# ============================================================

def basic_fallback_extraction(text):

    lower_text = text.lower()

    # --------------------------------------------------------
    # FIND FUNCTION
    # --------------------------------------------------------

    def find(pattern):

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

        return None


    # --------------------------------------------------------
    # DOCUMENT TYPE
    # --------------------------------------------------------

    document_type = "Other Accounting Document"

    if "purchase order" in lower_text:

        document_type = "Purchase Order"

    elif "credit note" in lower_text:

        document_type = "Credit Note"

    elif "debit note" in lower_text:

        document_type = "Debit Note"

    elif "payment voucher" in lower_text:

        document_type = "Payment Voucher"

    elif (
        "payment receipt" in lower_text
        or re.search(r"\breceipt\b", lower_text)
    ):

        document_type = "Receipt"

    elif (
        "due notice" in lower_text
        or "outstanding notice" in lower_text
        or "amount due" in lower_text
        or "outstanding amount" in lower_text
    ):

        document_type = "Due / Outstanding"

    elif (
        "expense report" in lower_text
        or "expense document" in lower_text
    ):

        document_type = "Expense Document"

    elif (
        "quotation" in lower_text
        or re.search(r"\bquote\b", lower_text)
    ):

        document_type = "Quotation"

    elif "proforma invoice" in lower_text:

        document_type = "Proforma Invoice"

    elif "bank statement" in lower_text:

        document_type = "Bank Statement"

    elif "sales invoice" in lower_text:

        document_type = "Sales Invoice"

    elif "purchase invoice" in lower_text:

        document_type = "Purchase Invoice"

    elif "invoice" in lower_text:

        document_type = "Invoice"

    elif re.search(r"\bbill\b", lower_text):

        document_type = "Bill"


    # --------------------------------------------------------
    # DOCUMENT NUMBERS
    # --------------------------------------------------------

    document_number = find(
        r"(?:Document Number|Document No|Document #)"
        r"\s*[:\-]?\s*(\S+)"
    )

    invoice_number = find(
        r"(?:Invoice Number|Invoice No|Invoice #)"
        r"\s*[:\-]?\s*(\S+)"
    )

    purchase_order_number = find(
        r"(?:Purchase Order Number|Purchase Order No|PO Number|PO No)"
        r"\s*[:\-]?\s*(\S+)"
    )

    receipt_number = find(
        r"(?:Receipt Number|Receipt No|Receipt #)"
        r"\s*[:\-]?\s*(\S+)"
    )


    # --------------------------------------------------------
    # DATES
    # --------------------------------------------------------

    date = find(
        r"(?:Date|Invoice Date|Bill Date|Receipt Date)"
        r"\s*[:\-]?\s*([^\n]+)"
    )

    invoice_date = find(
        r"(?:Invoice Date|Bill Date)"
        r"\s*[:\-]?\s*([^\n]+)"
    )

    due_date = find(
        r"(?:Due Date|Payment Due Date)"
        r"\s*[:\-]?\s*([^\n]+)"
    )


    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer = find(
        r"(?:Customer Name|Customer|Client|Buyer Name|Buyer)"
        r"\s*[:\-]\s*([^\n]+)"
    )

    if not customer:

        customer = find(
            r"(?:Bill To|Billed To|Sold To|Purchaser|Consignee)"
            r"\s*[:\-]?\s*([^\n]+)"
        )


    # --------------------------------------------------------
    # CUSTOMER EMAIL
    # --------------------------------------------------------

    customer_email = find(
        r"(?:Customer Email|Buyer Email|Client Email|Email)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"
    )


    # --------------------------------------------------------
    # CUSTOMER PHONE
    # --------------------------------------------------------

    customer_phone = find(
        r"(?:Customer Phone|Buyer Phone|Phone|Mobile)"
        r"\s*[:\-]?\s*"
        r"([0-9+\-\s]{10,})"
    )


    # --------------------------------------------------------
    # VENDOR
    # --------------------------------------------------------

    vendor = find(
        r"(?:Vendor|Supplier|Seller|Service Provider)"
        r"\s*[:\-]\s*([^\n]+)"
    )


    # --------------------------------------------------------
    # SUPPLIER
    # --------------------------------------------------------

    supplier = find(
        r"(?:Supplier)"
        r"\s*[:\-]\s*([^\n]+)"
    )


    # --------------------------------------------------------
    # VENDOR != CUSTOMER
    # --------------------------------------------------------

    if customer and vendor:

        if customer.strip().lower() == vendor.strip().lower():

            customer = None

    if customer and supplier:

        if customer.strip().lower() == supplier.strip().lower():

            customer = None


    # --------------------------------------------------------
    # AMOUNTS
    # --------------------------------------------------------

    subtotal = find(
        r"(?:Subtotal|Sub Total|Taxable Value)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )

    tax = find(
        r"(?:Tax|Tax Amount)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )

    gst = find(
        r"(?:GST|GST Amount)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )

    total_amount = find(
        r"(?:Grand Total|Total Amount|Total)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )

    paid_amount = find(
        r"(?:Paid Amount|Amount Paid|Paid)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )

    due_amount = find(
        r"(?:Due Amount|Amount Due|Balance Due|Outstanding Amount)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"([\d,]+(?:\.\d+)?)"
    )


    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment_method = find(
        r"(?:Payment Method|Payment Mode|Mode of Payment)"
        r"\s*[:\-]?\s*([^\n]+)"
    )

    payment_status = find(
        r"(?:Payment Status|Status)"
        r"\s*[:\-]\s*([^\n]+)"
    )


    # --------------------------------------------------------
    # GST NUMBER
    # --------------------------------------------------------

    gst_number = find(
        r"(?:GSTIN|GST Number|GST No)"
        r"\s*[:\-]?\s*([A-Z0-9]+)"
    )


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = find(
        r"(?:Description|Particulars)"
        r"\s*[:\-]?\s*([^\n]+)"
    )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = "General Accounting"

    if document_type in [
        "Purchase Order",
        "Purchase Invoice"
    ]:

        category = "Purchase / Procurement"

    elif document_type in [
        "Receipt",
        "Payment Receipt",
        "Payment Voucher"
    ]:

        category = "Payment"

    elif document_type == "Due / Outstanding":

        category = "Due / Outstanding"

    elif document_type == "Sales Invoice":

        category = "Sales / Revenue"

    elif document_type == "Expense Document":

        category = "General Accounting"

    elif document_type in [
        "Credit Note",
        "Debit Note"
    ]:

        category = "Accounting Adjustment"

    elif document_type == "Tax / GST Document":

        category = "Tax Related"


    # --------------------------------------------------------
    # RETURN FALLBACK RESULT
    # --------------------------------------------------------

    return {

        "document_type": document_type,

        "document_title": None,

        "document_number": document_number,

        "invoice_number": invoice_number,

        "purchase_order_number":
            purchase_order_number,

        "receipt_number":
            receipt_number,

        "date":
            date,

        "invoice_date":
            invoice_date,

        "due_date":
            due_date,

        "vendor":
            vendor,

        "supplier":
            supplier,

        "customer":
            customer,

        "customer_email":
            customer_email,

        "customer_phone":
            customer_phone,

        "payer":
            None,

        "payee":
            None,

        "currency":
            "INR",

        "subtotal":
            subtotal,

        "tax":
            tax,

        "gst":
            gst,

        "discount":
            None,

        "total_amount":
            total_amount,

        "paid_amount":
            paid_amount,

        "due_amount":
            due_amount,

        "payment_status":
            payment_status,

        "payment_method":
            payment_method,

        "items":
            [],

        "category":
            category,

        "gst_number":
            gst_number,

        "description":
            description,

        "account_number":
            None,

        "transaction_date":
            date,

        "other_information":
            None
    }


# ============================================================
# NORMALIZE RESULT
# ============================================================

def normalize_result(data):

    if not data:
        return None

    if not isinstance(data, dict):
        return None


    # --------------------------------------------------------
    # DATABASE / AGENT STRING FIELDS
    # --------------------------------------------------------

    scalar_fields = [

        "document_type",
        "document_title",
        "document_number",
        "invoice_number",
        "purchase_order_number",
        "receipt_number",

        "date",
        "invoice_date",
        "due_date",

        "vendor",
        "supplier",

        "customer",
        "customer_email",
        "customer_phone",

        "payer",
        "payee",

        "currency",

        "subtotal",
        "tax",
        "gst",
        "discount",

        "total_amount",
        "paid_amount",
        "due_amount",

        "payment_status",
        "payment_method",

        "category",

        "gst_number",
        "description",
        "account_number",

        "transaction_date",

        "other_information"
    ]


    for field in scalar_fields:

        data[field] = clean_value(
            data.get(field)
        )


    # --------------------------------------------------------
    # DEFAULT DOCUMENT TYPE
    # --------------------------------------------------------

    if not data.get("document_type"):

        data["document_type"] = (
            "Other Accounting Document"
        )


    # --------------------------------------------------------
    # DATE COMPATIBILITY
    # --------------------------------------------------------

    if not data.get("date"):

        data["date"] = data.get(
            "invoice_date"
        )

    if not data.get("invoice_date"):

        data["invoice_date"] = data.get(
            "date"
        )


    # --------------------------------------------------------
    # VENDOR COMPATIBILITY
    # --------------------------------------------------------

    if not data.get("vendor"):

        data["vendor"] = clean_value(
            data.get("supplier")
        )


    # --------------------------------------------------------
    # DOCUMENT NUMBER
    # --------------------------------------------------------

    if not data.get("document_number"):

        data["document_number"] = (

            data.get("invoice_number")

            or data.get(
                "purchase_order_number"
            )

            or data.get(
                "receipt_number"
            )
        )


    # --------------------------------------------------------
    # INVOICE NUMBER
    # --------------------------------------------------------

    if not data.get("invoice_number"):

        if data.get("document_type") in [

            "Invoice",
            "Sales Invoice",
            "Purchase Invoice"

        ]:

            data["invoice_number"] = (
                data.get("document_number")
            )


    # --------------------------------------------------------
    # CUSTOMER DEFAULTS
    # --------------------------------------------------------

    if "customer" not in data:

        data["customer"] = None

    if "customer_email" not in data:

        data["customer_email"] = None

    if "customer_phone" not in data:

        data["customer_phone"] = None


    # --------------------------------------------------------
    # VENDOR != CUSTOMER SAFETY CHECK
    # --------------------------------------------------------

    vendor = data.get("vendor")
    supplier = data.get("supplier")
    customer = data.get("customer")


    if customer:

        customer_text = (
            str(customer)
            .strip()
            .lower()
        )


        if vendor:

            if customer_text == str(
                vendor
            ).strip().lower():

                data["customer"] = None


        if supplier:

            if customer_text == str(
                supplier
            ).strip().lower():

                data["customer"] = None


    # --------------------------------------------------------
    # ITEMS
    # --------------------------------------------------------

    if not isinstance(
        data.get("items"),
        list
    ):

        data["items"] = []


    # --------------------------------------------------------
    # CLEAN ITEM VALUES
    # --------------------------------------------------------

    cleaned_items = []

    for item in data["items"]:

        if not isinstance(item, dict):

            continue

        cleaned_item = {

            "name":
                clean_value(
                    item.get("name")
                ),

            "description":
                clean_value(
                    item.get("description")
                ),

            "quantity":
                clean_value(
                    item.get("quantity")
                ),

            "unit_price":
                clean_value(
                    item.get("unit_price")
                ),

            "amount":
                clean_value(
                    item.get("amount")
                )
        }

        cleaned_items.append(
            cleaned_item
        )

    data["items"] = cleaned_items


    # --------------------------------------------------------
    # CURRENCY DEFAULT
    # --------------------------------------------------------

    if not data.get("currency"):

        data["currency"] = "INR"


    # --------------------------------------------------------
    # RETURN CLEAN DATA
    # --------------------------------------------------------

    return data


# ============================================================
# MAIN UNIVERSAL EXTRACTION FUNCTION
# ============================================================

def extract_invoice_data(file_path):

    """
    Universal Accounting Document Extraction Agent.

    Pipeline:

    PDF
      ↓
    Text Extraction
      ↓
    Local Ollama GenAI
      ↓
    Document Type Detection
      ↓
    Vendor / Customer Role Detection
      ↓
    Universal Field Extraction
      ↓
    Normalization
      ↓
    FinFlow Agents
    """


    # --------------------------------------------------------
    # PDF TEXT EXTRACTION
    # --------------------------------------------------------

    text, error = extract_pdf_text(
        file_path
    )


    # --------------------------------------------------------
    # PDF ERROR
    # --------------------------------------------------------

    if error:

        print(
            "PDF extraction error:",
            error
        )

        return {

            "document_type":
                "Unknown",

            "extraction_status":
                "error",

            "error":
                error
        }


    # --------------------------------------------------------
    # NO TEXT
    # --------------------------------------------------------

    if not text:

        return {

            "document_type":
                "Unknown",

            "extraction_status":
                "failed",

            "message":
                "No readable text found in PDF."
        }


    print(
        "Extracted PDF text length:",
        len(text)
    )


    # ========================================================
    # STEP 1 — OLLAMA GENAI
    # ========================================================

    ai_data = ask_local_ai(
        text
    )


    # ========================================================
    # STEP 2 — AI SUCCESS
    # ========================================================

    if ai_data:

        result = normalize_result(
            ai_data
        )


        if result:

            result["extraction_status"] = (
                "ai_extracted"
            )

            result["source"] = (
                "Ollama Llama 3.2"
            )


            print(
                "Extraction source: Ollama Llama 3.2"
            )

            print(
                "Detected document type:",
                result.get(
                    "document_type"
                )
            )

            print(
                "Detected vendor:",
                result.get(
                    "vendor"
                )
            )

            print(
                "Detected customer:",
                result.get(
                    "customer"
                )
            )

            print(
                "Detected customer email:",
                result.get(
                    "customer_email"
                )
            )

            print(
                "Detected customer phone:",
                result.get(
                    "customer_phone"
                )
            )


            return result


    # ========================================================
    # STEP 3 — FALLBACK
    # ========================================================

    print(
        "Ollama unavailable or invalid response."
    )

    print(
        "Using universal rule-based fallback."
    )


    result = basic_fallback_extraction(
        text
    )


    result = normalize_result(
        result
    )


    result["extraction_status"] = (
        "fallback_extracted"
    )

    result["source"] = (
        "Universal Rule-based Extraction"
    )


    return result

