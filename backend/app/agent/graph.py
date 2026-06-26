from langgraph.graph import StateGraph, END
from app.agent.state import AgentState


def build_agent_graph() -> StateGraph:
    """Build LangGraph StateGraph with placeholder nodes."""
    graph = StateGraph(AgentState)

    # Add placeholder nodes - will be implemented in Phase 3
    graph.add_node("planner", lambda state: state)
    graph.add_node("router", lambda state: state)
    graph.add_node("final_answer", lambda state: state)

    # Define flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")
    graph.add_edge("router", "final_answer")
    graph.add_edge("final_answer", END)

    return graph.compile()


# Singleton compiled graph
agent_graph = build_agent_graph()