from langgraph.graph import StateGraph, START, END

from agent.state import draft_state
from agent.nodes.case_agent import analyze_case
from agent.nodes.template_agent import analyze_template
from agent.nodes.mismatch_guard import check_template_match
from agent.nodes.section_classifier import classify_sections
from agent.nodes.draft_synthesizer import synthesize_draft
from agent.nodes.structure_verifier import verify_structure
from agent.nodes.verifier_node import verify_facts
from agent.nodes.repair_agent import repair_draft
from agent.nodes.patch_agent import apply_repair_patches


builder = StateGraph(draft_state)

builder.add_node("case_analyzer", analyze_case)
builder.add_node("template_analyzer", analyze_template)
builder.add_node("mismatch_guard", check_template_match)
builder.add_node("section_classifier", classify_sections)
builder.add_node("draft_synthesizer", synthesize_draft)
builder.add_node("structure_verifier", verify_structure)
builder.add_node("verifier_node", verify_facts)
builder.add_node("repair_agent", repair_draft)
builder.add_node("patch_engine", apply_repair_patches)

builder.add_edge(START, "case_analyzer")
builder.add_edge("case_analyzer", "template_analyzer")
builder.add_edge("template_analyzer", "mismatch_guard")
builder.add_edge("mismatch_guard", "section_classifier")
builder.add_edge("section_classifier", "draft_synthesizer")
builder.add_edge("draft_synthesizer", "structure_verifier")
builder.add_edge("structure_verifier", "verifier_node")
builder.add_edge("verifier_node", "repair_agent")
builder.add_edge("repair_agent", "patch_engine")
builder.add_edge("patch_engine", END)

graph = builder.compile()