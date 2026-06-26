from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.planner import planner_node
from app.agent.nodes.router import router_node
from app.agent.nodes.final_answer import final_answer_node


def build_agent_graph() -> StateGraph:
    """Build LangGraph StateGraph with ReAct loop."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("final_answer", final_answer_node)

    # Define flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")

    # Conditional: continue loop or finish
    graph.add_conditional_edges(
        "router",
        lambda state: "final_answer" if _should_finish(state) else "planner",
        {"planner": "planner", "final_answer": "final_answer"}
    )
    graph.add_edge("final_answer", END)

    return graph.compile()


def _should_finish(state: AgentState) -> bool:
    """Finish nếu đã có final answer hoặc vượt max iterations."""
    return (
        bool(state.get("final_answer"))
        or state.get("current_step", 0) >= state.get("max_iterations", 5)
    )


# Singleton compiled graph
agent_graph = build_agent_graph()