from app.agent.state import AgentState
from app.agent.tools.registry import tool_registry
from jinja2 import Template


async def router_node(state: AgentState) -> AgentState:
    """Thực thi tool hiện tại trong plan."""
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {**state, "final_answer": "No more steps to execute."}

    step = plan[current_step]
    tool_name = step.get("tool", "")
    tool_input = step.get("input", {})

    # Resolve template variables từ previous results
    resolved_input = _resolve_templates(tool_input, state.get("tool_results", []))

    if tool_name == "final_answer":
        # Không cần gọi tool, chuyển sang final answer node
        return {**state, "final_answer": resolved_input.get("content", "")}

    # Execute tool
    try:
        result = await tool_registry.execute(tool_name, **resolved_input)
        success = True
        error = None
    except Exception as e:
        result = str(e)
        success = False
        error = str(e)

    tool_call_record = {
        "step": current_step,
        "tool": tool_name,
        "input": resolved_input,
        "output": result,
        "success": success,
    }

    return {
        **state,
        "tool_calls": state.get("tool_calls", []) + [tool_call_record],
        "tool_results": state.get("tool_results", []) + [result],
        "current_step": current_step + 1,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "TOOL_USE", "tool": tool_name, "result_preview": str(result)[:200]}
        ],
        "error": error,
    }


def _resolve_templates(input_dict: dict, previous_results: list) -> dict:
    """Thay thế {{step_N_result}} bằng actual results."""
    resolved = {}
    for key, value in input_dict.items():
        if isinstance(value, str) and "{{" in value:
            for i, result in enumerate(previous_results):
                value = value.replace(f"{{{{step_{i}_result}}}}", str(result))
        resolved[key] = value
    return resolved


async def router_node(state: AgentState) -> AgentState:
    """Router node - to be implemented in Phase 3."""
    return state
