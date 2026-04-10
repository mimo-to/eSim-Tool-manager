import subprocess
import re
import shutil
from src.logger import log

from src.version_utils import is_outdated

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
            timeout=30
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

    min_version = tool_data.get("min_version", "")
    conflict = False
    if installed and version and version != "unknown" and min_version:
        conflict = is_outdated(version, min_version)

    # Extract base command for PATH checking
    try:
        base_cmd = tool_data.get("check_cmd", "").split()[0] if tool_data.get("check_cmd") else None
        in_path = shutil.which(base_cmd) is not None if base_cmd else False
    except Exception:
        in_path = False

    path_issue = bool(installed and not in_path)

    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "installed": installed,
        "path_issue": path_issue,
        "version": version,
        "required": tool_data.get("required", False),
        "min_version": min_version,
        "conflict": conflict
    }

def check_all(registry_data: dict) -> list[dict]:
    results = []
    for tid, tdata in registry_data.items():
        results.append(check_tool(tid, tdata))
    return results
