from typing import Any
from typing_extensions import TypedDict


class draft_state(TypedDict):

    # Orginal Input
    case_data: Any
    template: Any
    custom_prompt: str
    status: str
    metadata: dict[str, Any]

    # Agent-processed Understanding
    case_facts: dict
    parameterized_template: str

    # Later Stages
    document_plan: dict
    retrieved_knowledge: list[dict]
    draft: str
    review: dict
    structural_warnings: list[str]
    verification_warnings: list[dict]

    # Control
    current_section: int
    revision_count: int
