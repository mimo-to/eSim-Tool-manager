import sys
from importlib import resources
from pathlib import Path
from src.logger import log as _log

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def load():
    # Load core tools
    with resources.files("src").joinpath("tools.toml").open("rb") as f:
        registry_data = tomllib.load(f)


    # Load custom tools from home directory
    custom_path = Path.home() / ".esim_tool_manager" / "custom_tools.toml"
    if custom_path.exists():
        try:
            with open(custom_path, "rb") as f:
                custom_data = tomllib.load(f)
            
            # Safe merge custom tools
            for key, data in custom_data.items():
                # 1. Prevent ID conflict
                if key in registry_data:
                    _log("REGISTRY", key, "WARNING_CONFLICT")
                    continue

                # 2. Validate required fields
                if "name" not in data or "check_cmd" not in data:
                    _log("REGISTRY", key, "WARNING_INVALID")
                    continue
                
                # 3. Default handling
                if "required" not in data:
                    data["required"] = False
                
                # 4. Insert safely
                registry_data[key] = data

        except Exception:
            _log("REGISTRY", "custom_tools.toml", "ERROR_PARSE")

    return registry_data
