
import os


def process_document(file_path):
    """
    Document Agent

    Responsibilities:
    1. Check uploaded document
    2. Validate file type
    3. Collect basic document information
    4. Prepare document for the Extraction Agent
    """

    # -------------------------------------------------
    # 1. CHECK FILE PATH
    # -------------------------------------------------

    if not file_path:
        return {
            "status": "error",
            "agent": "Document Agent",
            "message": "No document provided."
        }


    # -------------------------------------------------
    # 2. CHECK FILE EXISTS
    # -------------------------------------------------

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "agent": "Document Agent",
            "message": "Document file not found."
        }


    # -------------------------------------------------
    # 3. BASIC FILE INFORMATION
    # -------------------------------------------------

    file_name = os.path.basename(
        file_path
    )

    extension = os.path.splitext(
        file_name
    )[1].lower()

    file_size = os.path.getsize(
        file_path
    )


    # -------------------------------------------------
    # 4. SUPPORTED DOCUMENT TYPES
    # -------------------------------------------------

    supported_extensions = [
        ".pdf"
    ]

    if extension not in supported_extensions:

        return {
            "status": "error",
            "agent": "Document Agent",
            "file_name": file_name,
            "file_type": extension,
            "message":
                "Unsupported document format."
        }


    # -------------------------------------------------
    # 5. BASIC FILE NAME SIGNALS
    #
    # These are only hints.
    # Final document classification is done
    # by the Universal Extraction Agent.
    # -------------------------------------------------

    file_name_lower = file_name.lower()

    possible_document_type = "Unknown"


    if "invoice" in file_name_lower:
        possible_document_type = "Invoice"

    elif "receipt" in file_name_lower:
        possible_document_type = "Receipt"

    elif "purchase" in file_name_lower:
        possible_document_type = "Purchase Order"

    elif "bill" in file_name_lower:
        possible_document_type = "Bill"

    elif "payment" in file_name_lower:
        possible_document_type = "Payment Document"

    elif "expense" in file_name_lower:
        possible_document_type = "Expense Document"

    elif "credit" in file_name_lower:
        possible_document_type = "Credit Note"

    elif "debit" in file_name_lower:
        possible_document_type = "Debit Note"

    elif "quotation" in file_name_lower:
        possible_document_type = "Quotation"

    elif "statement" in file_name_lower:
        possible_document_type = "Statement"

    elif "due" in file_name_lower:
        possible_document_type = "Due / Outstanding"


    # -------------------------------------------------
    # 6. RETURN DOCUMENT AGENT RESULT
    # -------------------------------------------------

    return {

        "status": "success",

        "agent":
            "Document Agent",

        "file_name":
            file_name,

        "file_path":
            file_path,

        "file_type":
            extension,

        "file_size":
            file_size,

        "possible_document_type":
            possible_document_type,

        "next_agent":
            "Universal Extraction Agent",

        "message":
            "Document received and prepared for analysis."
    }
