import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

class WorkflowRunner:
    """Execute workflow with real-time WebSocket events"""
    
    def __init__(self, workflow_config: dict, websocket_manager=None):
        self.config = workflow_config
        self.websocket_manager = websocket_manager
        self.run_id = f"run_{datetime.now().timestamp()}"
        self.steps_result = []
    
    async def emit_event(self, event_type: str, data: dict):
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "WORKFLOW_STEP",
                "data": {
                    "eventType": event_type,
                    **data
                },
                "timestamp": datetime.now().timestamp()
            })
    
    async def execute_step(self, step: dict, inputs: dict, context: dict) -> dict:
        step_result = {
            "stepId": step["id"],
            "stepName": step["name"],
            "status": "running",
            "startedAt": datetime.now().timestamp()
        }
        
        await self.emit_event("STEP_START", {
            "stepId": step["id"],
            "stepName": step["name"]
        })
        
        try:
            if step["type"] == "tool":
                from ..services.tools import get_available_tools
                tools = get_available_tools()
                tool_name = step.get("toolName")
                
                if tool_name and tool_name in tools:
                    tool_args = step.get("toolArgs", {})
                    
                    for key, value in tool_args.items():
                        if isinstance(value, str):
                            if value.startswith("${inputs."):
                                var_name = value.replace("${inputs.", "").replace("}", "")
                                tool_args[key] = inputs.get(var_name)
                            elif value.startswith("${context."):
                                var_name = value.replace("${context.", "").replace("}", "")
                                tool_args[key] = context.get(var_name)
                    
                    await self.emit_event("TOOL_CALL", {
                        "stepId": step["id"],
                        "toolName": tool_name,
                        "arguments": tool_args
                    })
                    
                    result = await tools[tool_name].execute(**tool_args)
                    
                    step_result["output"] = result
                    step_result["status"] = "completed" if result.get("success", False) else "failed"
                    
                    await self.emit_event("TOOL_RESULT", {
                        "stepId": step["id"],
                        "toolName": tool_name,
                        "success": result.get("success", False)
                    })
                    
                    context[step.get("outputVar", f"step_{step['id']}")] = result
                else:
                    step_result["status"] = "skipped"
                    step_result["error"] = f"Tool {tool_name} not found"
            
            elif step["type"] == "condition":
                condition = step.get("condition", "")
                condition_result = self._evaluate_condition(condition, context)
                step_result["output"] = {"condition_result": condition_result}
                step_result["status"] = "completed"
            
            elif step["type"] == "output":
                output_var = step.get("outputVar")
                if output_var:
                    step_result["output"] = context.get(output_var)
                step_result["status"] = "completed"
            
        except Exception as e:
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            await self.emit_event("STEP_ERROR", {
                "stepId": step["id"],
                "error": str(e)
            })
        
        step_result["completedAt"] = datetime.now().timestamp()
        return step_result
    
    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        try:
            for key, value in context.items():
                condition = condition.replace(f"${{{key}}}", str(value))
            return eval(condition, {"__builtins__": {}}, {})
        except:
            return False
    
    async def execute(self, inputs: dict) -> dict:
        context = {"inputs": inputs}
        
        await self.emit_event("WORKFLOW_START", {
            "workflowId": self.config["id"],
            "workflowName": self.config["name"]
        })
        
        for step in self.config.get("steps", []):
            step_result = await self.execute_step(step, inputs, context)
            self.steps_result.append(step_result)
            
            if step_result["status"] == "failed" and step.get("onError") != "continue":
                break
        
        all_completed = all(s["status"] == "completed" for s in self.steps_result)
        
        await self.emit_event("WORKFLOW_COMPLETE", {
            "workflowId": self.config["id"],
            "success": all_completed,
            "stepsCount": len(self.steps_result)
        })
        
        return {
            "id": self.run_id,
            "workflowId": self.config["id"],
            "workflowName": self.config["name"],
            "status": "completed" if all_completed else "failed",
            "steps": self.steps_result,
            "startedAt": self.steps_result[0]["startedAt"] if self.steps_result else None,
            "completedAt": self.steps_result[-1]["completedAt"] if self.steps_result else None,
            "context": context
        }