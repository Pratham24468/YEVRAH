from langgraph.graph import StateGraph, START, END

from agent.state import draft_state
from agent.nodes.case_agent import analyze_case
from agent.nodes.template_agent import analyze_template
from agent.nodes.mismatch_guard import check_template_match
from agent.nodes.section_classifier import classify_sections
from agent.nodes.draft_synthesizer import synthesize_draft
from agent.nodes.structure_verifier import verify_structure
from agent.nodes.verifier_node import verify_facts


builder = StateGraph(draft_state)

builder.add_node("case_analyzer", analyze_case)
builder.add_node("template_analyzer", analyze_template)
builder.add_node("mismatch_guard", check_template_match)
builder.add_node("section_classifier", classify_sections)
builder.add_node("draft_synthesizer", synthesize_draft)
builder.add_node("structure_verifier", verify_structure)
builder.add_node("verifier_node", verify_facts)

# case_analyzer and template_analyzer are independent of each other and
# could fan out from START in parallel — left sequential for now since
# LangGraph's parallel-branch state merging adds complexity that isn't
# worth it until generation latency is actually a problem.
builder.add_edge(START, "case_analyzer")
builder.add_edge("case_analyzer", "template_analyzer")

# mismatch_guard is mechanical (no LLM call) and raises
# TemplateMismatchError if the loaded template doesn't plausibly fit
# the case — a hard stop before any LLM planning/synthesis work is
# wasted on a doomed generation.
builder.add_edge("template_analyzer", "mismatch_guard")
builder.add_edge("mismatch_guard", "section_classifier")

builder.add_edge("section_classifier", "draft_synthesizer")

# structure_verifier checks TEMPLATE ADHERENCE (did the draft follow
# the template's structure/document type) — a different question from
# verifier_node, which checks FACT ACCURACY (do the numbers/dates/
# names in the draft match case_facts). A draft can pass one and fail
# the other; both run, neither blocks — warnings surface to the caller.
builder.add_edge("draft_synthesizer", "structure_verifier")
builder.add_edge("structure_verifier", "verifier_node")
builder.add_edge("verifier_node", END)

graph = builder.compile()
