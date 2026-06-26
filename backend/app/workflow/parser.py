import yaml
from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal, Any
from app.models.workflow import WorkflowConfig


def parse_workflow_yaml(yaml_content: str) -> WorkflowConfig:
    """Parse and validate YAML workflow configuration."""
    data = yaml.safe_load(yaml_content)
    workflow_data = data.get("workflow", data)  # Support both root-level and nested
    return WorkflowConfig(**workflow_data)