from fastapi import APIRouter, HTTPException

router = APIRouter()

# In-memory workflow store
workflow_store: dict[str, dict] = {}
run_store: dict[str, dict] = {}


@router.get("/workflows")
async def list_workflows():
    """List all workflows."""
    return list(workflow_store.values())


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow by ID."""
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_store[workflow_id]


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get run status by ID."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_store[run_id]