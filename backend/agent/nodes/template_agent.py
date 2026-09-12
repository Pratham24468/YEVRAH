from agent.state import draft_state
from ai.llm import generate_general_response


def build_template_prompt(markdown_content: str) -> str:
    return f"""
You are YEVRAH's Template Agent.

Convert the supplied legal document Markdown into a reusable
PARAMETERIZED MARKDOWN TEMPLATE.

The supplied Markdown is the reference document.

Preserve the reference document's:

- structure
- section order
- headings
- paragraph structure
- numbering
- tables
- wording patterns
- formatting
- bold
- italic
- underline
- alignment
- indentation
- spacing
- Markdown/Pandoc attributes
- HTML formatting
- other Markdown syntax

Replace case-specific information with meaningful semantic
placeholders.

Examples:

Party names → [CLAIMANT_NAME], [RESPONDENT_NAME]
Person names → [PERSON_NAME]
Addresses → [ADDRESS]
Dates → [DATE]
Case numbers → [CASE_NUMBER]
Application numbers → [APPLICATION_NUMBER]
Amounts → [AMOUNT]
Principal amounts → [PRINCIPAL_AMOUNT]
Interest amounts → [INTEREST_AMOUNT]
Contract numbers → [CONTRACT_NUMBER]
Invoice numbers → [INVOICE_NUMBER]
Quantities → [QUANTITY]
Exhibit references → [EXHIBIT_REFERENCE]

Use more specific placeholders when the role of the information
is clear.

For example:

[CLAIMANT_NAME]
[RESPONDENT_NAME]
[AFFIANT_NAME]
[ADVOCATE_NAME]
[COURT_NAME]
[APPLICATION_NUMBER]
[PRINCIPAL_AMOUNT]
[INTEREST_AMOUNT]

Keep reusable legal wording intact.

Example:

I say that the Respondents failed and neglected to make payment of
Rs.1,02,68,072/-.

becomes:

I say that the Respondents failed and neglected to make payment of
[PRINCIPAL_AMOUNT].

Keep the original drafting style and sentence construction.

Preserve tables as tables.

Replace case-specific table values with appropriate placeholders
while retaining the table's structure, columns, rows, numbering,
alignment, and formatting.

The resulting template should show YEVRAH where each piece of future
case information belongs while retaining the drafting pattern of the
reference document.

The output itself must be a Markdown template.

Return ONLY the completed parameterized Markdown template.

REFERENCE MARKDOWN:

{markdown_content}
"""


def compile_template(markdown_content: str) -> str:
    if not markdown_content:
        raise ValueError("Template has no markdown_content")

    prompt = build_template_prompt(markdown_content)

    result = generate_general_response(prompt)

    if not result:
        raise ValueError(
            "Template Agent returned empty compiled template"
        )

    return result.strip()


def analyze_template(state: draft_state) -> draft_state:
    template = state["template"]

    markdown_content = getattr(
        template,
        "markdown_content",
        None,
    )

    if not markdown_content:
        raise ValueError(
            "Template has no markdown_content"
        )

    parameterized_template = compile_template(
        markdown_content
    )

    return {
        **state,
        "parameterized_template": parameterized_template,
        "status": "template_compiled",
    }