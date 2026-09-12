from langgraph.graph import StateGraph, START, END

from agent.state import draft_state
from agent.nodes.case_agent import analyze_case
from agent.nodes.template_agent import analyze_template
from agent.nodes.section_classifier import classify_sections
from agent.nodes.draft_synthesizer import synthesize_draft


builder = StateGraph(draft_state)

builder.add_node("case_analyzer", analyze_case)
builder.add_node("template_analyzer", analyze_template)
builder.add_node("section_classifier", classify_sections)
builder.add_node("draft_synthesizer", synthesize_draft)

# case_analyzer and template_analyzer are independent of each other and
# could fan out from START in parallel — left sequential for now since
# LangGraph's parallel-branch state merging adds complexity that isn't
# worth it until generation latency is actually a problem.
builder.add_edge(START, "case_analyzer")
builder.add_edge("case_analyzer", "template_analyzer")
builder.add_edge("template_analyzer", "section_classifier")
builder.add_edge("section_classifier", "draft_synthesizer")
builder.add_edge("draft_synthesizer", END)

graph = builder.compile()