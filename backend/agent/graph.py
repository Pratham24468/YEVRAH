from langgraph.graph import StateGraph, START, END

from agent.state import DraftState
from agent.nodes.case_analyzer import analyze_case
from agent.nodes.template_analyzer import analyze_template


builder = StateGraph(DraftState)

builder.add_node("case_analyzer", analyze_case)
builder.add_node("template_analyzer", analyze_template)

builder.add_edge(START, "case_analyzer")
builder.add_edge("case_analyzer", "template_analyzer")
builder.add_edge("template_analyzer", END)

graph = builder.compile()