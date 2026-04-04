import src.platform_mgr as pm
from src import checker, installer, registry, pip_checker, logger
from rich.progress import Progress

def scan() -> dict:
    results = checker.check_all(registry.load())
    missing_required = []
    missing_optional = []
    
    for res in results:
        if not res["installed"]:
            if res["required"]:
                missing_required.append(res["id"])
            else:
                missing_optional.append(res["id"])
                
    missing_pkgs = pip_checker.missing()
    
    return {
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "missing_pkgs": missing_pkgs,
        "results": results
    }

def fix_pkgs(pkg_names):
    import subprocess
    import sys
    
    results = []
    
    with Progress() as progress:
        task = progress.add_task("Installing Python packages...", total=len(pkg_names))
        
        for name in pkg_names:
            print(f"Installing Python package: {name}...")
            
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "pip", "install", name],
                    text=True,
                    timeout=300
                )
                success = r.returncode == 0
            except subprocess.TimeoutExpired:
                print(f"Timeout installing {name}")
                success = False
            except KeyboardInterrupt:
                print(f"\nCancelled installation of {name}")
                success = False
                
            results.append({"name": name, "success": success})
            logger.log("PIP_INSTALL", name, success)
            progress.advance(task)
    
    return results

def repair_all() -> dict:
    scan_result = scan()
    r = registry.load()
    fixed = []
    failed = []
    skipped = []
    
    for tool_id in scan_result["missing_required"]:
        tool_data = r[tool_id]
        if not tool_data.get(pm.pkg_key()):
            skipped.append(tool_id)
            continue

        res = installer.install(tool_id, tool_data)
        if res["success"]:
            fixed.append(tool_id)
        else:
            failed.append(tool_id)
            
    tool_results = {"fixed": fixed, "failed": failed, "skipped": skipped}
    pkg_results = fix_pkgs(scan_result["missing_pkgs"])
    
    return {
        "tools": tool_results,
        "pkgs": pkg_results
    }
