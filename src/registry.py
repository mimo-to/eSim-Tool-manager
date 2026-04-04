import sys
from importlib import resources

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def load():
    with resources.files("src").joinpath("tools.toml").open("rb") as f:
        return tomllib.load(f)
