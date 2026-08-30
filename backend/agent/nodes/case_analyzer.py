from agent.state import draft_state
from ai.llm import generate_json


def analyze_case(state: draft_state) -> draft_state:
    case_data = state["case_data"]

    prompt = f"""
You are the Case Analysis Agent for YEVRAH.

Analyze the supplied case data and convert it into structured facts
for downstream legal drafting agents.

IMPORTANT:
- Extract facts only from the supplied case data.
- Never invent names, dates, amounts, events, relationships, or documents.
- Do not draft the legal document.
- Do not rewrite the case as prose.
- Do not make unsupported legal conclusions.
- If information is absent, put it in missing_information.
- Preserve exact names, dates, amounts, and factual relationships.

Return ONLY valid JSON.

Required structure:

{{
    "parties": [],
    "relationships": [],
    "chronology": [],
    "agreements": [],
    "financials": [],
    "defaults": [],
    "communications": [],
    "legal_issues": [],
    "demands": [],
    "relief": [],
    "missing_information": []
}}

Extraction rules:

parties:
Identify each party, their role, and identifying information available.

relationships:
Describe the factual relationship between parties.

chronology:
List important events in chronological order. Include dates when available.

agreements:
Extract contracts, agreements, terms, obligations, and payment terms.

financials:
Extract amounts, invoices, payments, balances, interest, and other
financial facts.

defaults:
Extract alleged non-payment, breach, failure, delay, or other
non-performance.

communications:
Extract notices, letters, emails, demands, acknowledgements,
responses, and their dates.

legal_issues:
Identify legal issues explicitly raised by the supplied facts.
Do not invent legal issues.

demands:
Extract demands made by any party.

relief:
Extract the relief or outcome requested.

missing_information:
Identify information that appears necessary for drafting but is
not present in the case data.

CASE DATA:
{case_data}
"""

    case_facts = generate_json(prompt)

    return {
        **state,
        "case_facts": case_facts,
        "status": "case_analyzed",
    }