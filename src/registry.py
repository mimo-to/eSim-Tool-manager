from importlib import resources
import tomllib

def load():
    with resources.files("src").joinpath("tools.toml").open("rb") as f:
        return tomllib.load(f)
