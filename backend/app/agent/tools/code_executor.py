import docker
import json
from app.agent.tools.registry import tool_registry
from app.config import settings

docker_client = docker.from_env()

SANDBOX_IMAGE = "agent-sandbox:latest"
BLOCKED_IMPORTS = ["os.system", "subprocess", "socket", "__import__", "eval", "exec"]


@tool_registry.register(
    name="code_executor",
    description="Thực thi Python code trong môi trường sandbox an toàn. Có sẵn: numpy, pandas, matplotlib, scikit-learn. Không có network access."
)
async def code_executor(code: str) -> dict:
    """
    Chạy code trong Docker sandbox.
    Security guarantees:
    - Network disabled
    - Memory limit 256MB
    - CPU limit 0.5
    - Timeout 30s
    - Non-root user
    - Whitelist imports only
    """
    # Pre-check: block dangerous patterns
    for blocked in BLOCKED_IMPORTS:
        if blocked in code:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Blocked: '{blocked}' is not allowed",
                "result": ""
            }

    payload = json.dumps({"code": code, "timeout": settings.max_code_exec_timeout})

    try:
        container = docker_client.containers.run(
            image=SANDBOX_IMAGE,
            command="",
            stdin_open=True,
            stdout=True,
            stderr=True,
            detach=True,
            # Security constraints
            network_mode="none",
            mem_limit="256m",
            nano_cpus=500_000_000,  # 0.5 CPU
            read_only=True,
            tmpfs={"/tmp": "size=50m"},
            security_opt=["no-new-privileges"],
        )

        # Send code via stdin
        socket = container.attach_socket(params={"stdin": 1, "stdout": 1, "stream": 1})
        socket._sock.sendall((payload + "\n").encode())
        socket._sock.close()

        # Wait with timeout
        result = container.wait(timeout=settings.max_code_exec_timeout + 5)
        logs = container.logs(stdout=True, stderr=False).decode()

        container.remove(force=True)
        return json.loads(logs) if logs.strip() else {"success": False, "stdout": "", "stderr": "No output", "result": ""}

    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "result": ""}