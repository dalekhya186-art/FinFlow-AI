import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


# ==========================================
# LOCAL OLLAMA GENAI
# ==========================================

def ask_local_genai(prompt):
    """
    Send reasoning request to local Ollama GenAI.
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        "No AI response received."
    )


# ==========================================
# MANAGER AGENT
# ==========================================

def manage_workflow(
    document_result,
    invoice_data,
    verification,
    category,
    workflow=None
):
    """
    FinFlow AI Manager Agent

    Coordinates:

    1. Document Agent
    2. Universal Extraction Agent
    3. Verification Agent
    4. Categorization Agent
    5. Customer History Agent
    6. Workflow Agent
    7. Manager Agent + Ollama GenAI

    Human approval always remains mandatory.
    """

    decision_log = []

    # ==========================================
    # SAFETY: DICTIONARY CHECKS
    # ==========================================

    if not isinstance(document_result, dict):
        document_result = {}

    if not isinstance(invoice_data, dict):
        invoice_data = {}

    if not isinstance(verification, dict):
        verification = {
            "status": "needs_review",
            "issues": [
                "Verification result unavailable."
            ]
        }

    if not isinstance(category, dict):
        category = {
            "category": "General Accounting",
            "confidence": "Low",
            "reason": "Category unavailable."
        }

    if not isinstance(workflow, dict):
        workflow = {
            "status": "ready_for_approval",
            "next_action": "Send document for human approval",
            "priority": "Normal",
            "category": category.get(
                "category",
                "General Accounting"
            ),
            "human_approval_required": True
        }

    # ==========================================
    # STEP 1: DOCUMENT AGENT
    # ==========================================

    document_status = document_result.get(
        "status",
        "success"
    )

    if document_status == "error":

        decision_log.append(
            "Document Agent failed."
        )

        return {
            "agent": "Manager Agent",
            "status": "error",
            "decision": "Stop workflow",
            "priority": "High",
            "reason": "Document processing failed.",
            "ai_reasoning": (
                "GenAI reasoning was skipped because "
                "document processing failed."
            ),
            "genai_status": "skipped",
            "human_approval_required": False,
            "decision_log": decision_log
        }

    decision_log.append(
        "Document Agent completed successfully."
    )

    # ==========================================
    # STEP 2: DOCUMENT TYPE
    # ==========================================

    document_type = invoice_data.get(
        "document_type",
        document_result.get(
            "possible_document_type",
            "accounting_document"
        )
    )

    document_title = invoice_data.get(
        "document_title",
        ""
    )

    decision_log.append(
        f"Document type identified: {document_type}"
    )

    if document_title:
        decision_log.append(
            f"Document title identified: {document_title}"
        )

    # ==========================================
    # STEP 3: EXTRACTION CHECK
    # ==========================================

    extraction_status = invoice_data.get(
        "extraction_status",
        "unknown"
    )

    if extraction_status == "failed":

        decision_log.append(
            "Universal Extraction Agent reported failure."
        )

    else:

        decision_log.append(
            "Universal Extraction Agent completed successfully."
        )

    # IMPORTANT:
    # No early return here.
    #
    # Manager Agent will still call Ollama
    # and explain the extraction problem.

    # ==========================================
    # STEP 4: VERIFICATION AGENT
    # ==========================================

    verification_status = verification.get(
        "status",
        "needs_review"
    )

    issues = verification.get(
        "issues",
        []
    )

    if verification_status == "needs_review":

        decision_log.append(
            "Verification Agent found issues. "
            "Human review will be required."
        )

    else:

        decision_log.append(
            "Verification Agent completed successfully."
        )

    # IMPORTANT:
    # NO RETURN HERE.
    #
    # Ollama must always receive the
    # verification result.

    # ==========================================
    # STEP 5: CATEGORIZATION AGENT
    # ==========================================

    selected_category = category.get(
        "category",
        "General Accounting"
    )

    decision_log.append(
        f"Categorization Agent selected: "
        f"{selected_category}"
    )

    # ==========================================
    # STEP 6: CUSTOMER HISTORY AGENT
    # ==========================================

    customer_history = invoice_data.get(
        "customer_history"
    )

    if isinstance(customer_history, dict):

        if customer_history.get(
            "customer_found"
        ):

            decision_log.append(
                "Customer History Agent found existing customer history."
            )

        else:

            decision_log.append(
                "Customer History Agent found no previous customer history."
            )

    elif customer_history:

        decision_log.append(
            "Customer History Agent returned customer data."
        )

    else:

        decision_log.append(
            "Customer History Agent data not available."
        )

    # ==========================================
    # STEP 7: WORKFLOW AGENT
    # ==========================================

    workflow_action = workflow.get(
        "next_action",
        "Send document for human approval"
    )

    workflow_priority = workflow.get(
        "priority",
        "Normal"
    )

    # ==========================================
    # FORCE HUMAN REVIEW WHEN REQUIRED
    # ==========================================

    if (
        verification_status == "needs_review"
        or extraction_status == "failed"
    ):

        workflow_action = (
            "Send to accountant review"
        )

        workflow_priority = "High"

        workflow["next_action"] = (
            workflow_action
        )

        workflow["priority"] = (
            workflow_priority
        )

        workflow["human_approval_required"] = True

    decision_log.append(
        f"Workflow Agent selected action: "
        f"{workflow_action}"
    )

    # ==========================================
    # STEP 8: PREPARE GENAI CONTEXT
    # ==========================================

    prompt = f"""
You are the Manager Agent of FinFlow AI.

FinFlow AI is an AI-powered accounting
operations and agentic workflow automation
platform.

You coordinate multiple specialized agents.

Your job is to reason over their results and
recommend the safest next workflow action.

IMPORTANT RULES:

- Do not invent information.
- Do not make final accounting decisions.
- Do not make final tax decisions.
- Do not make final legal decisions.
- Do not make final financial decisions.
- Human approval must remain mandatory.
- If verification has issues, recommend
  accountant review.
- If extraction failed, recommend
  accountant review.
- Explain why the recommended action is needed.
- Consider all agent outputs together.
- If agents disagree, clearly mention it.

==========================================
DOCUMENT AGENT
==========================================

{document_result}


==========================================
EXTRACTION AGENT
==========================================

{invoice_data}


==========================================
VERIFICATION AGENT
==========================================

{verification}


==========================================
CATEGORIZATION AGENT
==========================================

{category}


==========================================
CUSTOMER HISTORY AGENT
==========================================

{customer_history}


==========================================
WORKFLOW AGENT
==========================================

{workflow}


==========================================
MANAGER TASK
==========================================

Analyze all the above agent outputs.

Identify:

1. Document type
2. Important extracted information
3. Verification issues
4. Accounting category
5. Customer history relevance
6. Workflow recommendation
7. Missing or suspicious information
8. Safest next action
9. Why human approval is required

==========================================
RESPONSE FORMAT
==========================================

Document Type:
Recommendation:
Priority:
Reason:
Concerns:
Agent Coordination:
Human Approval:

Keep the response clear and concise.
"""

    # ==========================================
    # STEP 9: OLLAMA GENAI
    # ==========================================

    try:

        ai_reasoning = ask_local_genai(
            prompt
        )

        if not ai_reasoning:
            ai_reasoning = (
                "Ollama returned an empty response."
            )

            genai_status = "empty"

            decision_log.append(
                "Ollama returned an empty response."
            )

        else:

            genai_status = "success"

            decision_log.append(
                "Manager Agent used local Ollama "
                "GenAI for workflow reasoning."
            )

    except Exception as e:

        ai_reasoning = (
            "Local Ollama GenAI is currently "
            "unavailable. The workflow recommendation "
            "is based on the specialized agent results."
        )

        genai_status = "unavailable"

        decision_log.append(
            "Local Ollama GenAI unavailable. "
            "Rule-based workflow recommendation used."
        )

    # ==========================================
    # STEP 10: HUMAN APPROVAL
    # ==========================================

    decision_log.append(
        "Human approval required before final action."
    )

    # ==========================================
    # FINAL RESULT
    # ==========================================

    return {

        "agent":
            "Manager Agent",

        "status":
            "ready_for_approval",

        "decision":
            workflow_action,

        "priority":
            workflow_priority,

        "document_type":
            document_type,

        "category":
            selected_category,

        "reason":
            "Agent team completed automated "
            "analysis and workflow reasoning.",

        "ai_reasoning":
            ai_reasoning,

        "genai_status":
            genai_status,

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

        "decision_log":
            decision_log
    }