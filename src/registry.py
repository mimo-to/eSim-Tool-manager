import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def load() -> dict:
    path = Path(__file__).parent.parent / "tools.toml"
    with open(path, "rb") as f:
        return tomllib.load(f)
