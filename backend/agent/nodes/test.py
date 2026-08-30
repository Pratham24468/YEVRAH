from agent.nodes.case_analyzer import analyze_case

state = {
    "case_data": {
        "title": "Money Recovery",
        "plaintiff": "Aarav Industrial Supplies Pvt. Ltd.",
        "defendant": "Zenith Engineering Works",
        "facts": """
Aarav Industrial Supplies Pvt. Ltd. supplied industrial electrical
components to Zenith Engineering Works.

The goods were supplied between 12 February 2026 and 28 March 2026.

The total value of the goods supplied was ₹8,74,500.

The Defendant made a partial payment of ₹2,00,000 on 15 April 2026.

An outstanding principal amount of ₹6,74,500 remained payable.

The Plaintiff sent a written demand dated 20 May 2026.

The Defendant acknowledged receipt of the demand but did not make payment.

The Plaintiff sent a legal notice dated 5 June 2026 demanding payment.

No payment was received after the legal notice.

The Plaintiff claims interest at 12% per annum from 15 April 2026
until realisation.

        """
    },

    "template": None,
    "custom_prompt": "",
    "metadata": {},

    "case_facts": {},
    "template_blueprint": {},
    "document_plan": {},
    "retrieved_knowledge": [],
    "draft": "",
    "review": {},

    "current_section": 0,
    "revision_count": 0,
    "status": "started",
}

result = analyze_case(state)

print(result["case_facts"])