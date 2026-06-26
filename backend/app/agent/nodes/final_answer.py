from app.agent.state import AgentState
from app.llm.groq import complete_groq
import json

FINAL_ANSWER_PROMPT = """You are an AI assistant. Based on the research and tool results below, provide a comprehensive, helpful answer to the user's question.

Be concise, accurate, and cite sources when available."""


async def final_answer_node(state: AgentState) -> AgentState:
    """Tổng hợp tất cả results thành câu trả lời cuối cùng."""
    if state.get("final_answer"):
        return state  # Already set by router

    context = f"""
User Query: {state['user_query']}

Tool Results:
{json.dumps(state.get('tool_results', []), indent=2, ensure_ascii=False)}
"""

    messages = [
        {"role": "system", "content": FINAL_ANSWER_PROMPT},
        {"role": "user", "content": context}
    ]

    final = await complete_groq(messages)

    return {
        **state,
        "final_answer": final,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "DONE", "content": "Final answer generated"}
        ]
    }