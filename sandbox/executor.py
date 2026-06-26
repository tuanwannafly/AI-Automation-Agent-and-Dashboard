import sys
import json
import io
import contextlib
import signal


def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")


def run_code(code: str, timeout: int = 30) -> dict:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    local_vars = {}

    try:
        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stderr_capture):
            exec(code, {"__builtins__": __builtins__}, local_vars)
        return {
            "success": True,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "result": str(local_vars.get("result", "")),
        }
    except TimeoutError:
        return {"success": False, "stdout": "", "stderr": "TIMEOUT", "result": ""}
    except Exception as e:
        return {"success": False, "stdout": stdout_capture.getvalue(),
                "stderr": str(e), "result": ""}
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    result = run_code(payload["code"], payload.get("timeout", 30))
    print(json.dumps(result))