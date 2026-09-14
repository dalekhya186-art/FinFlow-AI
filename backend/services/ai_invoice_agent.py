import os
from openai import OpenAI


def analyze_invoice_with_ai(invoice_data):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "OPENAI_API_KEY is not configured"
        }

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an AI accounting operations assistant.

Analyze the following invoice information.

Invoice Number: {invoice_data.get("invoice_number")}
Invoice Date: {invoice_data.get("invoice_date")}
Vendor: {invoice_data.get("vendor")}
Subtotal: {invoice_data.get("subtotal")}
GST: {invoice_data.get("gst")}
Total Amount: {invoice_data.get("total_amount")}

Provide:
1. A short invoice summary
2. Expense category suggestion
3. Important accounting checks
4. Possible issues or risks
5. Recommended next workflow action

Do not make final accounting, tax, or legal decisions.
The final decision must remain with a human accountant.
"""

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        return {
            "status": "success",
            "ai_analysis": response.output_text
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
