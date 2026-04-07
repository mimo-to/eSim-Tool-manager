import json
import datetime
from pathlib import Path
from src.logger import log as _log

def save_snapshot(tools, pkgs):
    path = Path.home() / ".esim_tool_manager"
    path.mkdir(parents=True, exist_ok=True)
    file = path / "snapshot.json"
    
    data = {
        "tools": tools,
        "packages": pkgs,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        _log("SNAPSHOT", "save", "ERROR")

def load_snapshot():
    file = Path.home() / ".esim_tool_manager" / "snapshot.json"
    if not file.exists():
        return None
    
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        _log("SNAPSHOT", "load", "ERROR")
        return None

def get_diff(old, current_tools, current_pkgs):
    def is_problem(res):
        # A tool is a problem if not installed or has a conflict
        # A package is a problem if not installed or ok is False
        # checker results use 'conflict', pip_checker results use 'ok'
        if "conflict" in res:
            return (not res.get("installed")) or res.get("conflict")
        else:
            return (not res.get("installed")) or (not res.get("ok"))

    # Map by name for comparison
    old_tools = {r.get("name"): r for r in old.get("tools", [])}
    old_pkgs = {r.get("name"): r for r in old.get("packages", [])}
    
    new_tools = {r.get("name"): r for r in current_tools}
    new_pkgs = {r.get("name"): r for r in current_pkgs}
    
    new_issues = []
    fixed_issues = []
    
    # Compare tools
    for name, curr in new_tools.items():
        prev = old_tools.get(name)
        if prev:
            prev_issue = is_problem(prev)
            curr_issue = is_problem(curr)
            
            if not prev_issue and curr_issue:
                new_issues.append(f"{name} (now Problem)")
            elif prev_issue and not curr_issue:
                fixed_issues.append(f"{name} (now OK)")
                
    # Compare packages
    for name, curr in new_pkgs.items():
        prev = old_pkgs.get(name)
        if prev:
            prev_issue = is_problem(prev)
            curr_issue = is_problem(curr)
            
            if not prev_issue and curr_issue:
                new_issues.append(f"{name} (now Problem)")
            elif prev_issue and not curr_issue:
                fixed_issues.append(f"{name} (now OK)")
                
    return {
        "new_issues": new_issues,
        "fixed_issues": fixed_issues
    }
