
def create_workflow(verification, category):
    """
    Universal Workflow Agent

    Decides the next workflow action based on:
    1. Verification result
    2. Document type
    3. Accounting category

    Human approval always remains the final decision.
    """

    # ==========================================
    # GET AGENT RESULTS
    # ==========================================

    verification_status = verification.get(
        "status",
        "needs_review"
    )

    issues = verification.get(
        "issues",
        []
    )

    selected_category = category.get(
        "category",
        "General Accounting"
    )

    document_type = category.get(
        "document_type",
        "accounting_document"
    )


    document_type_lower = str(
        document_type
    ).lower()


    # ==========================================
    # IF VERIFICATION FAILED
    # ==========================================

    if (
        verification_status != "verified"
        or issues
    ):

        return {

            "agent":
                "Workflow Agent",

            "status":
                "needs_review",

            "document_type":
                document_type,

            "next_action":
                "Send document for accountant review",

            "priority":
                "High",

            "category":
                selected_category,

            "issues":
                issues,

            "human_approval_required":
                True,

            "workflow_reason":
                "Verification found issues that require human review."
        }


    # ==========================================
    # VERIFIED DOCUMENT
    # ==========================================

    action = (
        "Send document for human approval"
    )

    priority = "Normal"

    workflow_reason = (
        "Document passed automated verification."
    )


    # ==========================================
    # DOCUMENT-SPECIFIC WORKFLOW
    # ==========================================

    # ------------------------------------------
    # PURCHASE ORDER
    # ------------------------------------------

    if (
        "purchase order"
        in document_type_lower
        or document_type_lower == "po"
    ):

        action = (
            "Send purchase order for approval"
        )

        workflow_reason = (
            "Purchase order is verified and "
            "requires human approval before processing."
        )


    # ------------------------------------------
    # RECEIPT
    # ------------------------------------------

    elif "receipt" in document_type_lower:

        action = (
            "Send receipt for payment confirmation"
        )

        workflow_reason = (
            "Receipt information is verified "
            "and requires human confirmation."
        )


    # ------------------------------------------
    # PAYMENT
    # ------------------------------------------

    elif "payment" in document_type_lower:

        action = (
            "Send payment document for approval"
        )

        workflow_reason = (
            "Payment information is verified "
            "and requires human approval."
        )


    # ------------------------------------------
    # DUE / OUTSTANDING
    # ------------------------------------------

    elif (
        "due" in document_type_lower
        or "outstanding" in document_type_lower
    ):

        priority = "High"

        action = (
            "Send outstanding amount for review"
        )

        workflow_reason = (
            "Outstanding financial information "
            "requires human review."
        )


    # ------------------------------------------
    # EXPENSE
    # ------------------------------------------

    elif "expense" in document_type_lower:

        action = (
            "Send expense document for approval"
        )

        workflow_reason = (
            "Expense information is verified "
            "and requires human approval."
        )


    # ------------------------------------------
    # CREDIT NOTE
    # ------------------------------------------

    elif "credit note" in document_type_lower:

        action = (
            "Send credit note for approval"
        )

        workflow_reason = (
            "Credit adjustment requires human approval."
        )


    # ------------------------------------------
    # DEBIT NOTE
    # ------------------------------------------

    elif "debit note" in document_type_lower:

        action = (
            "Send debit note for approval"
        )

        workflow_reason = (
            "Debit adjustment requires human approval."
        )


    # ------------------------------------------
    # QUOTATION
    # ------------------------------------------

    elif "quotation" in document_type_lower:

        action = (
            "Send quotation for review"
        )

        workflow_reason = (
            "Quotation is ready for human review "
            "before acceptance."
        )


    # ------------------------------------------
    # STATEMENT
    # ------------------------------------------

    elif "statement" in document_type_lower:

        action = (
            "Send statement for accountant review"
        )

        workflow_reason = (
            "Statement information is verified "
            "and should be reviewed by an accountant."
        )


    # ------------------------------------------
    # INVOICE
    # ------------------------------------------

    elif "invoice" in document_type_lower:

        action = (
            "Send invoice for human approval"
        )

        workflow_reason = (
            "Invoice passed automated verification "
            "and requires human approval."
        )


    # ==========================================
    # RETURN WORKFLOW RESULT
    # ==========================================

    return {

        "agent":
            "Workflow Agent",

        "status":
            "ready_for_approval",

        "document_type":
            document_type,

        "next_action":
            action,

        "priority":
            priority,

        "category":
            selected_category,

        "issues":
            issues,

        "human_approval_required":
            True,

        "workflow_reason":
            workflow_reason
    }

