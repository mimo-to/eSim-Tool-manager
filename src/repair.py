import src.platform_mgr as pm
from src import checker, installer, registry

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
                
    return {
        "missing_required": missing_required,
        "missing_optional": missing_optional
    }

def repair_all() -> dict:
    data = scan()
    r = registry.load()
    fixed = []
    failed = []
    skipped = []
    
    for tool_id in data["missing_required"]:
        tool_data = r[tool_id]
        if not tool_data.get(pm.pkg_key()):
            skipped.append(tool_id)
            continue

        res = installer.install(tool_id, tool_data)
        if res["success"]:
            fixed.append(tool_id)
        else:
            failed.append(tool_id)
            
    return {"fixed": fixed, "failed": failed, "skipped": skipped}
