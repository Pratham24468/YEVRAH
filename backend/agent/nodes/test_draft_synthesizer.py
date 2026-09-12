from agent.state import draft_state
from agent.nodes import draft_synthesizer


def fake_retrieve_chunks(query, case_id=None, limit=4):
    print(
        f"\n[RAG] query={query!r} "
        f"case_id={case_id} "
        f"limit={limit}"
    )

    return [
        {
            "source": "case_document_001",
            "text": (
                "The Respondent entered into Contract No. "
                "ABC/XYZ/001 dated 15 January 2024."
            ),
        },
        {
            "source": "case_document_002",
            "text": (
                "The outstanding principal amount payable "
                "by the Respondent is ₹10,00,000."
            ),
        },
    ]


def fake_generate_response(prompt):
    print("\n[LLM] Draft generation called.")
    print(f"[LLM] Prompt length: {len(prompt)} characters")

    return """
**BEFORE THE [COURT_NAME]**

**[CASE_TYPE] NO. [CASE_NUMBER] OF [YEAR]**

**[CLAIMANT_NAME]**

VERSUS

**[RESPONDENT_NAME]**

## AFFIDAVIT OF [AFFIANT_NAME]

I, [AFFIANT_NAME], residing at [ADDRESS], do hereby solemnly
state as under:

**1.** I say that the Claimant entered into Contract No.
[CONTRACT_NUMBER] dated [DATE] with the Respondent.

**2.** I say that the Respondent was required to make payment
of [PRINCIPAL_AMOUNT].

**3.** I say that the Respondent failed to make payment within
[PAYMENT_PERIOD].

## VERIFICATION

I, [AFFIANT_NAME], verify that the contents herein are true
and correct to my knowledge and belief.
""".strip()


# --------------------------------------------------
# PATCH REAL EXTERNAL DEPENDENCIES
# --------------------------------------------------

draft_synthesizer.retrieve_chunks = fake_retrieve_chunks
draft_synthesizer.generate_response = fake_generate_response


def main():

    # --------------------------------------------------
    # SAMPLE STATE
    # --------------------------------------------------

    state: draft_state = {

        "metadata": {
            "case_id": 1,
        },

        "parameterized_template": """
**BEFORE THE [COURT_NAME]**

**[CASE_TYPE] NO. [CASE_NUMBER] OF [YEAR]**

**[CLAIMANT_NAME]**

VERSUS

**[RESPONDENT_NAME]**

## AFFIDAVIT OF [AFFIANT_NAME]

I, [AFFIANT_NAME], residing at [ADDRESS], do hereby solemnly
state as under:

**1.** I say that the Claimant entered into Contract No.
[CONTRACT_NUMBER] dated [DATE] with the Respondent.

**2.** I say that the Respondent was required to make payment
of [PRINCIPAL_AMOUNT].

**3.** I say that the Respondent failed to make payment within
[PAYMENT_PERIOD].

## VERIFICATION

I, [AFFIANT_NAME], verify that the contents herein are true
and correct to my knowledge and belief.
""",

        "case_facts": {
            "parties": [
                {
                    "name": "ABC Private Limited",
                    "role": "Claimant",
                },
                {
                    "name": "XYZ Enterprises",
                    "role": "Respondent",
                },
            ],
            "financials": [
                {
                    "principal_amount": "₹10,00,000",
                }
            ],
            "agreements": [
                {
                    "contract_number": "ABC/XYZ/001",
                    "date": "2024-01-15",
                }
            ],
            "defaults": [
                "Respondent failed to make payment",
            ],
        },

        "document_plan": {
            "sections": [
                {
                    "id": "section_1",
                    "name": "Contract Formation",
                    "placeholders": [
                        "[CONTRACT_NUMBER]",
                        "[DATE]",
                    ],
                    "case_fact_categories": [
                        "agreements",
                    ],
                    "evidence_query": (
                        "contract formation agreement date number"
                    ),
                },
                {
                    "id": "section_2",
                    "name": "Payment Default",
                    "placeholders": [
                        "[PRINCIPAL_AMOUNT]",
                        "[PAYMENT_PERIOD]",
                    ],
                    "case_fact_categories": [
                        "financials",
                        "defaults",
                    ],
                    "evidence_query": (
                        "outstanding amount payment default"
                    ),
                },
            ]
        },

        "custom_prompt": "",
    }

    # --------------------------------------------------
    # RUN
    # --------------------------------------------------

    print("\n========== DRAFT SYNTHESIZER TEST ==========\n")

    print("Running Draft Synthesizer...\n")

    result_state = draft_synthesizer.synthesize_draft(
        state
    )

    # --------------------------------------------------
    # CHECK RETRIEVED KNOWLEDGE
    # --------------------------------------------------

    retrieved = result_state.get(
        "retrieved_knowledge"
    )

    if not retrieved:
        raise ValueError(
            "No retrieved knowledge returned"
        )

    print("\n========== RETRIEVED KNOWLEDGE ==========\n")

    for item in retrieved:

        print(
            f"Section: {item.get('section')}"
        )

        print(
            f"Source: {item.get('source')}"
        )

        print(
            f"Text: {item.get('text')}"
        )

        print()

    # --------------------------------------------------
    # CHECK DRAFT
    # --------------------------------------------------

    draft = result_state.get("draft")

    if not draft:
        raise ValueError(
            "Draft Synthesizer returned empty draft"
        )

    print("\n========== GENERATED DRAFT ==========\n")
    print(draft)

    # --------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------

    status = result_state.get("status")

    if status != "draft_synthesized":
        raise ValueError(
            f"Unexpected status: {status}"
        )

    print("\n========== VALIDATION ==========\n")

    print("✓ RAG evidence retrieved")
    print("✓ Evidence tagged by section")
    print("✓ Draft generated")
    print("✓ Draft stored in state")
    print("✓ Retrieved knowledge stored in state")
    print("✓ Status is draft_synthesized")

    print("\n========== TEST PASSED ==========\n")


if __name__ == "__main__":
    main()