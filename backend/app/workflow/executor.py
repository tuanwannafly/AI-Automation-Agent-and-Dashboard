from app.workflow.parser import WorkflowConfig, WorkflowStep
from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
from jinja2 import Environment

jinja_env = Environment()


class WorkflowExecutor:
    def __init__(self, config: WorkflowConfig, inputs: dict):
        self.config = config
        self.inputs = inputs
        self.context: dict = {"inputs": inputs, "steps": {}}
        self.results: dict = {}

    async def run(self, emit_event=None) -> dict:
        """Execute workflow steps in order."""
        for step in self.config.steps:
            # Evaluate condition
            if step.condition:
                should_run = self._evaluate_condition(step.condition)
                if not should_run:
                    self.results[step.output_as] = None
                    continue

            # Emit event
            if emit_event:
                await emit_event({
                    "type": "WORKFLOW_STEP",
                    "step_id": step.id,
                    "description": step.description or step.tool,
                })

            # Execute step
            result = await self._execute_step(step)
            self.results[step.output_as] = result
            self.context["steps"][step.id] = {"output": result}

        # Collect outputs
        return {key: self.results.get(key) for key in self.config.outputs}

    def _evaluate_condition(self, condition: str) -> bool:
        try:
            template = jinja_env.from_string(f"{{{{ {condition} }}}}")
            result = template.render(**self.context)
            return result.strip().lower() not in ("false", "0", "none", "")
        except Exception:
            return True  # Default: run step

    def _render_template(self, text: str) -> str:
        if not text or "{{" not in text:
            return text
        try:
            template = jinja_env.from_string(text)
            return template.render(**self.context)
        except Exception as e:
            return text

    async def _execute_step(self, step: WorkflowStep) -> any:
        if step.tool == "code_executor":
            rendered_code = self._render_template(step.code)
            return await tool_registry.execute("code_executor", code=rendered_code)

        elif step.tool == "llm_call":
            rendered_prompt = self._render_template(step.prompt)
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": rendered_prompt}
            ]
            return await complete_groq(messages)

        elif step.tool == "rag_search":
            rendered_query = self._render_template(step.query or "")
            return await tool_registry.execute(
                "rag_search",
                query=rendered_query,
                collection=step.collection,
                top_k=step.top_k,
            )

        elif step.tool == "web_search":
            rendered_query = self._render_template(step.input.get("query", "") if step.input else "")
            return await tool_registry.execute("web_search", query=rendered_query)

        elif step.tool == "summarizer":
            rendered_text = self._render_template(step.input.get("text", "") if step.input else "")
            return await tool_registry.execute("summarizer", text=rendered_text)

        else:
            raise ValueError(f"Unknown tool: {step.tool}")