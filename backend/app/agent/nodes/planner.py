from app.agent.state import AgentState
from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
import json
import re

PLANNER_SYSTEM_PROMPT = """You are an AI agent planner. Given a user query and the available tools, create a step-by-step plan.

Available tools:
{tool_descriptions}

Rules:
1. Return ONLY a JSON array of steps
2. Each step: {{"step": int, "tool": "tool_name", "reason": "why", "input": {{...}}}}
3. Use "final_answer" as tool if no tools needed
4. Maximum 5 steps
5. Be efficient — don't use tools unnecessarily

Example:
[
  {{"step": 1, "tool": "web_search", "reason": "Need current info", "input": {{"query": "..."}}}},
  {{"step": 2, "tool": "summarizer", "reason": "Summarize results", "input": {{"text": "{{web_search_result}}"}}}}
]"""


async def planner_node(state: AgentState) -> AgentState:
    """Lên kế hoạch dựa trên query và tool descriptions."""
    messages = [
        {
            "role": "system",
            "content": PLANNER_SYSTEM_PROMPT.format(
                tool_descriptions=tool_registry.get_tool_descriptions()
            )
        },
        {
            "role": "user",
            "content": f"User query: {state['user_query']}\n\nPrevious steps completed: {state.get('current_step', 0)}\nTool results so far: {json.dumps(state.get('tool_results', []))}"
        }
    ]

    response = await complete_groq(messages, model="llama3-70b-8192")

    # Parse JSON plan
    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown code block
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        plan = json.loads(match.group()) if match else []

    return {
        **state,
        "plan": plan,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "THINKING", "content": f"Plan: {plan}", "step": state.get("current_step", 0)}
        ]
    }