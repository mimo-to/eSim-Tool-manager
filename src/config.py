from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

def get_path():
    p = Path.home() / ".esim_tool_manager" / "config.toml"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def save(data):
    p = get_path()
    content = f"""[general]
auto_confirm = {str(data['general']['auto_confirm']).lower()}
log_level = "{data['general']['log_level']}"

[update]
auto_update = {str(data['update']['auto_update']).lower()}
update_optional = {str(data['update']['update_optional']).lower()}
"""
    with open(p, "w") as f:
        f.write(content)

def load():
    p = get_path()
    if not p.exists():
        d = {
            "general": {"auto_confirm": False, "log_level": "INFO"},
            "update": {"auto_update": False, "update_optional": False}
        }
        save(d)
        return d
    with open(p, "rb") as f:
        return tomllib.load(f)

def get(key, default=None):
    data = load()
    parts = key.split(".")
    for part in parts:
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            return default
    return data
