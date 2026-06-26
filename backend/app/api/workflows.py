from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from app.workflow.parser import parse_workflow_yaml, WorkflowConfig
from app.workflow.executor import WorkflowExecutor
from app.api.websocket import ws_manager
import uuid
from pathlib import Path

router = APIRouter()

# In-memory store (replace with DB in production)
workflow_store: dict[str, dict] = {}
run_store: dict[str, dict] = {}

# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "workflow" / "templates"


@router.post("/workflows")
async def upload_workflow(file: UploadFile = File(...)):
    """Upload a YAML workflow configuration."""
    content = await file.read()
    try:
        config = parse_workflow_yaml(content.decode())
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid YAML: {e}")

    workflow_id = str(uuid.uuid4())
    workflow_store[workflow_id] = {
        "id": workflow_id,
        "name": config.name,
        "config": config.model_dump(),
        "raw_yaml": content.decode(),
    }
    return {"workflow_id": workflow_id, "name": config.name}

from fastapi import APIRouter, HTTPException

router = APIRouter()

# In-memory workflow store
workflow_store: dict[str, dict] = {}
run_store: dict[str, dict] = {}


@router.get("/workflows")
async def list_workflows():
    """List all workflows."""
    return list(workflow_store.values())


@router.get("/workflows/templates")
async def list_templates():
    """List built-in workflow templates."""
    templates = []
    if TEMPLATES_DIR.exists():
        for yaml_file in TEMPLATES_DIR.glob("*.yaml"):
            with open(yaml_file) as f:
                content = yaml.safe_load(f)
                wf = content.get("workflow", content)
                templates.append({
                    "id": yaml_file.stem,
                    "name": wf.get("name", yaml_file.stem),
                    "description": wf.get("description", ""),
                    "filename": yaml_file.name,
                })
    return templates


@router.get("/workflows/templates/{template_id}")
async def get_template(template_id: str):
    """Get a built-in workflow template content."""
    template_file = TEMPLATES_DIR / f"{template_id}.yaml"
    if not template_file.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return {"content": template_file.read_text()}


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    inputs: dict,
    background_tasks: BackgroundTasks,
):
    """Run a workflow with given inputs."""
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")

    run_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    run_store[run_id] = {"status": "running", "session_id": session_id, "outputs": {}}

    config = WorkflowConfig(**workflow_store[workflow_id]["config"])
    executor = WorkflowExecutor(config, inputs)

    async def _run():
        try:
            outputs = await executor.run(
                emit_event=lambda e: ws_manager.send_event(session_id, e)
            )
            run_store[run_id]["status"] = "completed"
            run_store[run_id]["outputs"] = outputs
            await ws_manager.send_event(session_id, {"type": "DONE", "outputs": outputs})
        except Exception as e:
            run_store[run_id]["status"] = "failed"
            run_store[run_id]["error"] = str(e)
            await ws_manager.send_event(session_id, {"type": "ERROR", "message": str(e)})

    background_tasks.add_task(_run)

    return {"run_id": run_id, "session_id": session_id,
            "ws_url": f"ws://localhost:8000/ws/{session_id}"}
@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID."""
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_store[workflow_id]


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get run status and outputs."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_store[run_id]
    """Get run status by ID."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_store[run_id]
from fastapi import APIRouter

router = APIRouter()
