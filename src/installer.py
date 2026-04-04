import subprocess
from src.logger import log as logger_log
from src import platform_mgr as pm, config
from src.version_utils import is_outdated

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
        logger_log("INSTALL", tool_id, "SUCCESS")
    else:
        logger_log("INSTALL", tool_id, "FAILED")

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
        logger_log("UPDATE", tool_id, "SUCCESS")
    else:
        logger_log("UPDATE", tool_id, "FAILED")

    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "success": success
    }

def update_all(registry_data, check_results=None):
    if check_results is None:
        from src import checker as _checker
        check_results = _checker.check_all(registry_data)
    upd_opt = config.get("update.update_optional", False)
    
    updated, failed, skipped = [], [], []
    
    for res in check_results:
        t_id = res["id"]
        t_data = registry_data[t_id]
        
        if not res["installed"]:
            skipped.append({"name": res["name"], "reason": "Not installed"})
            continue
            
        if res["version"] == "unknown":
            skipped.append({"name": res["name"], "reason": "Unstable version"})
            continue
            
        min_v = t_data.get("min_version", "")
        if res["version"] and min_v:
            if not is_outdated(res["version"], min_v):
                skipped.append({"name": res["name"], "reason": "Already up-to-date"})
                continue

        pkg_key = pm.pkg_key()
        pkg = t_data.get(pkg_key, "")
        if not pkg:
            skipped.append({"name": res["name"], "reason": "No package"})
            continue
            
        if not res["required"] and not upd_opt:
            skipped.append({"name": res["name"], "reason": "Optional tool"})
            continue
            
        logger_log("UPDATE", t_id, "ATTEMPT")
        res_upd = update(t_id, t_data)
        if res_upd["success"]:
            logger_log("UPDATE", t_id, "SUCCESS")
            updated.append(res["name"])
        else:
            logger_log("UPDATE", t_id, "FAILED")
            failed.append(res["name"])
            
    return {
        "updated": updated,
        "failed": failed,
        "skipped": skipped
    }

def install_all(registry_data: dict) -> list[dict]:
    results = []
    for tid, tdata in registry_data.items():
        results.append(install(tid, tdata))
    return results
