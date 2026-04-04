import subprocess
import re
from src.logger import log

def check_tool(tool_id: str, tool_data: dict) -> dict:
    cmd = tool_data.get("check_cmd", "")
    installed = False
    version = None
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            installed = True
            output = result.stdout + result.stderr
            match = re.search(tool_data.get("version_pattern", ""), output)
            if match:
                version = match.group(1)
            else:
                version = "unknown"
    except Exception:
        pass

    if installed:
        log("CHECK", tool_id, "FOUND")
    else:
        log("CHECK", tool_id, "NOT_FOUND")

    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "installed": installed,
        "version": version,
        "required": tool_data.get("required", False)
    }

def check_all(registry_data: dict) -> list[dict]:
    results = []
    for tid, tdata in registry_data.items():
        results.append(check_tool(tid, tdata))
    return results
