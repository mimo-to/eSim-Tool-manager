import subprocess
from src.logger import log as logger_log
from src import platform_mgr as pm, config, constants
from src.version_utils import is_outdated

def _is_pkg_match(output: str, pkg: str) -> bool:
    """Deterministic package name matching logic."""
    if not output:
        return False
    
    pkg = pkg.lower()
    for line in output.lower().splitlines():
        line = line.strip()
        # 1. Exact match
        if line == pkg:
            return True
        # 2. Prefix match (with common separators)
        if line.startswith(pkg + " ") or line.startswith(pkg + "/") or line.startswith(pkg + "-"):
            return True
        # 3. Word boundary match (handles winget KiCad.KiCad etc.)
        words = line.replace("/", " ").replace("-", " ").replace(".", " ").split()
        if pkg in words:
            return True
        # 4. Fallback for dot-names (match first part or full segments)
        if "." in pkg:
            pkg_base = pkg.split(".")[0]
            if pkg_base in words:
                return True
            
    return False

def install(tool_id: str, tool_data: dict) -> dict:
    """Legacy helper: installs a tool and returns success status."""
    result = install_tool(tool_id, tool_data)
    return {
        "id": tool_id,
        "name": tool_data.get("name", ""),
        "success": result["success"]
    }

def update(tool_id: str, tool_data: dict) -> dict:
    """Updates a tool using the first available manager."""
    managers = pm.get_available_managers()
    manual_link = constants.MANUAL_LINKS.get(tool_id, constants.DOWNLOAD_LINKS.get(tool_id, ""))
    
    if not managers:
        return {"success": False, "reason": "no_package_manager", "manual": manual_link}

    success = False
    used_manager = None
    
    for manager in managers:
        pkg = tool_data.get(f"{manager}_pkg") or tool_data.get("pkg_name") or tool_id
        cmd = pm.update_cmd(pkg, manager=manager)
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            combined_output = (res.stdout or "") + (res.stderr or "")
            if res.returncode == 0 and not any(kw in combined_output.lower() for kw in ["error", "failed", "not found"]):
                success = True
                used_manager = manager
                break
        except Exception:
            continue

    if success:
        logger_log("UPDATE", tool_id, f"SUCCESS (via {used_manager})")
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

        if not res["required"] and not upd_opt:
            skipped.append({"name": res["name"], "reason": "Optional tool"})
            continue
            
        logger_log("UPDATE", t_id, "ATTEMPT")
        res_upd = update(t_id, t_data)
        if res_upd["success"]:
            updated.append(res["name"])
        else:
            failed.append(res["name"])
            
    return {
        "updated": updated,
        "failed": failed,
        "skipped": skipped
    }

def install_all(registry_data: dict) -> list[dict]:
    results = []
    for tid, tdata in registry_data.items():
        res = install_tool(tid, tdata)
        results.append({
            "id": tid,
            "name": tdata.get("name", ""),
            "success": res["success"]
        })
    return results

def install_tool(tool_id, tool_data):
    """
    Adaptive installation system that tries multiple managers.
    Returns: {success: bool, reason: str, manager: str, manual: str}
    """
    managers = pm.get_available_managers()
    manual_link = constants.MANUAL_LINKS.get(tool_id, constants.DOWNLOAD_LINKS.get(tool_id, ""))
    
    if not managers:
        return {
            "success": False,
            "reason": "no_package_manager",
            "manager": None,
            "manual": manual_link
        }

    tried_any_manager = False
    
    for manager in managers:
        pkg = tool_data.get(f"{manager}_pkg") or tool_data.get("pkg_name") or tool_id
        
        # 1. Search Phase (Silent)
        try:
            s_cmd = pm.search_cmd(manager, pkg)
            s_res = subprocess.run(s_cmd, capture_output=True, text=True, timeout=10)
            s_output = (s_res.stdout or "") + (s_res.stderr or "")
            if not _is_pkg_match(s_output, pkg):
                # Optionally print internal diagnostic for testing:
                # print(f"Tool {pkg} not available in {manager}, trying next...")
                continue
        except subprocess.TimeoutExpired:
            print(f"Search timed out for {manager}, skipping...")
            continue
        except Exception:
            continue

        tried_any_manager = True
        
        # 2. Install Phase (Visible)
        print(f"Installing {tool_data.get('name', tool_id)} via {manager}...")
        try:
            i_cmd = pm.install_cmd(pkg, manager=manager)
            i_res = subprocess.run(i_cmd, capture_output=True, text=True, timeout=300) # Increased timeout for slow installs
            i_output = (i_res.stdout or "") + (i_res.stderr or "")
            
            # 3. Success Normalization
            if i_res.returncode == 0 and not any(kw in i_output.lower() for kw in ["error", "failed", "not found"]):
                logger_log("INSTALL", tool_id, f"SUCCESS (via {manager})")
                return {
                    "success": True, 
                    "reason": None, 
                    "manager": manager, 
                    "manual": manual_link
                }
        except subprocess.TimeoutExpired:
            print(f"Installation timed out for {manager}.")
        except Exception:
            pass

    # If we get here, all managers failed
    reason = "install_failed" if tried_any_manager else "not_found_in_manager"
    logger_log("INSTALL", tool_id, f"FAILED ({reason})")
    
    return {
        "success": False,
        "reason": reason,
        "manager": None,
        "manual": manual_link
    }
