import subprocess
from src.logger import log
import src.platform_mgr as pm

def install(tool_id: str, tool_data: dict) -> dict:
    pkg = tool_data.get(pm.pkg_key(), "")
    if not pkg:
        return {
            "id": tool_id,
            "name": tool_data.get("name", ""),
            "success": False
        }

    cmd = pm.install_cmd(pkg)
    success = False
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            success = True
    except Exception:
        pass

    if success:
        log("INSTALL", tool_id, "SUCCESS")
    else:
        log("INSTALL", tool_id, "FAILED")

    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "success": success
    }

def update(tool_id: str, tool_data: dict) -> dict:
    pkg = tool_data.get(pm.pkg_key(), "")
    if not pkg:
        return {
            "id": tool_id,
            "name": tool_data.get("name", ""),
            "success": False
        }

    cmd = pm.update_cmd(pkg)
    success = False
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            success = True
    except Exception:
        pass

    if success:
        log("UPDATE", tool_id, "SUCCESS")
    else:
        log("UPDATE", tool_id, "FAILED")

    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "success": success
    }

def install_all(registry_data: dict) -> list[dict]:
    results = []
    for tid, tdata in registry_data.items():
        results.append(install(tid, tdata))
    return results
