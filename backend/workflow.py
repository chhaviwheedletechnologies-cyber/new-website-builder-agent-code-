from langgraph.graph import StateGraph, END
from state import OrchestratorState
from template_design import template_design_agent

workflow = StateGraph(OrchestratorState)
workflow.add_node("template_agent", template_design_agent)
workflow.add_edge("template_agent", END)
workflow.set_entry_point("template_agent")

app_workflow = workflow.compile()
