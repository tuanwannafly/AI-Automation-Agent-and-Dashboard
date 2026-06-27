import os
import json
import yaml
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from typing import List
from ..core.config import settings

router = APIRouter()

WORKFLOWS_DIR = settings.WORKFLOWS_DIR
TEMPLATES_DIR = os.path.join(WORKFLOWS_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

_builtin_templates = [
    {
        "id": "cv_analysis",
        "name": "CV Analysis Pipeline",
        "description": "Analyze CV/resume and extract key information",
        "category": "HR",
        "config": {
            "id": "cv_analysis",
            "name": "CV Analysis Pipeline",
            "version": "1.0.0",
            "steps": [
                {"id": "1", "name": "Extract Text", "type": "tool", "toolName": "file_parser"},
                {"id": "2", "name": "Extract Skills", "type": "tool", "toolName": "code_executor"},
                {"id": "3", "name": "Summary", "type": "output"}
            ],
            "inputs": [
                {"name": "cv_file", "type": "string", "required": True}
            ]
        }
    },
    {
        "id": "web_research",
        "name": "Web Research Agent",
        "description": "Research a topic using web search",
        "category": "Research",
        "config": {
            "id": "web_research",
            "name": "Web Research Agent",
            "version": "1.0.0",
            "steps": [
                {"id": "1", "name": "Search Web", "type": "tool", "toolName": "web_search"},
                {"id": "2", "name": "Summarize", "type": "tool", "toolName": "code_executor"}
            ],
            "inputs": [
                {"name": "topic", "type": "string", "required": True}
            ]
        }
    },
    {
        "id": "data_analysis",
        "name": "Data Analysis Pipeline",
        "description": "Analyze data and generate insights",
        "category": "Analytics",
        "config": {
            "id": "data_analysis",
            "name": "Data Analysis Pipeline",
            "version": "1.0.0",
            "steps": [
                {"id": "1", "name": "Load Data", "type": "tool", "toolName": "code_executor"},
                {"id": "2", "name": "Analyze", "type": "tool", "toolName": "code_executor"},
                {"id": "3", "name": "Visualize", "type": "tool", "toolName": "code_executor"}
            ],
            "inputs": [
                {"name": "data", "type": "string", "required": True}
            ]
        }
    }
]

@router.get("/templates")
async def list_templates():
    return JSONResponse(content={
        "success": True,
        "data": {"templates": _builtin_templates}
    })

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    for template in _builtin_templates:
        if template["id"] == template_id:
            return JSONResponse(content={
                "success": True,
                "data": template["config"]
            })
    raise HTTPException(status_code=404, detail="Template not found")

@router.post("/")
async def create_workflow(file: UploadFile = File(...)):
    if not file.filename.endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Only YAML files are allowed")
    
    try:
        content = await file.read()
        config = yaml.safe_load(content)
        
        workflow_id = f"wf_{uuid4()}"
        config["id"] = workflow_id
        
        file_path = os.path.join(WORKFLOWS_DIR, f"{workflow_id}.yaml")
        async with aiofiles.open(file_path, "w") as f:
            await f.write(yaml.dump(config))
        
        return JSONResponse(content={
            "success": True,
            "data": config
        })
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")

@router.get("/")
async def list_workflows():
    workflows = []
    if os.path.exists(WORKFLOWS_DIR):
        for filename in os.listdir(WORKFLOWS_DIR):
            if filename.endswith((".yaml", ".yml")):
                file_path = os.path.join(WORKFLOWS_DIR, filename)
                async with aiofiles.open(file_path, "r") as f:
                    content = await f.read()
                    config = yaml.safe_load(content)
                    workflows.append(config)
    
    return JSONResponse(content={
        "success": True,
        "data": {"workflows": workflows}
    })

class WorkflowExecutor:
    def __init__(self, config: dict):
        self.config = config
        self.run_id = f"run_{uuid4()}"
        self.steps_result = []
    
    async def execute(self, inputs: dict) -> dict:
        from ..services.tools import get_available_tools
        tools = get_available_tools()
        
        for step in self.config.get("steps", []):
            step_result = {
                "stepId": step["id"],
                "stepName": step["name"],
                "status": "running",
                "startedAt": datetime.now().timestamp()
            }
            
            try:
                if step["type"] == "tool" and step.get("toolName") in tools:
                    tool_args = step.get("toolArgs", {})
                    for key, value in tool_args.items():
                        if isinstance(value, str) and value.startswith("${inputs."):
                            var_name = value.replace("${inputs.", "").replace("}", "")
                            tool_args[key] = inputs.get(var_name)
                    
                    result = await tools[step["toolName"]].execute(**tool_args)
                    step_result["output"] = result
                    step_result["status"] = "completed" if result.get("success") else "failed"
                else:
                    step_result["status"] = "skipped"
                
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)
            
            step_result["completedAt"] = datetime.now().timestamp()
            self.steps_result.append(step_result)
        
        return {
            "id": self.run_id,
            "workflowId": self.config["id"],
            "status": "completed" if all(s["status"] != "failed" for s in self.steps_result) else "failed",
            "steps": self.steps_result,
            "startedAt": self.steps_result[0]["startedAt"] if self.steps_result else None,
            "completedAt": self.steps_result[-1]["completedAt"] if self.steps_result else None
        }

@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: str, inputs: dict = {}):
    workflow = None
    for template in _builtin_templates:
        if template["id"] == workflow_id:
            workflow = template["config"]
            break
    
    if not workflow:
        file_path = os.path.join(WORKFLOWS_DIR, f"{workflow_id}.yaml")
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                workflow = yaml.safe_load(content)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    executor = WorkflowExecutor(workflow)
    result = await executor.execute(inputs)
    
    return JSONResponse(content={
        "success": True,
        "data": result
    })

@router.get("/runs/{run_id}")
async def get_run_status(run_id: str):
    return JSONResponse(content={
        "success": True,
        "data": {"id": run_id, "status": "completed", "steps": []}
    })