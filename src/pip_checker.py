import importlib.metadata
import re
from src.version_utils import is_outdated

ESIM_PYTHON_DEPS = {
    "numpy": ">=1.20",
    "scipy": ">=1.7",
    "matplotlib": ">=3.4",
    "pyqt5": ">=5.15",
    "pyserial": ">=3.5",
    "requests": ">=2.25",
    "Pillow": ">=8.0",
}

def check_pkg(name, min_ver):
    installed = False
    version = None
    ok = False
    try:
        version = importlib.metadata.version(name)
        installed = True
        
        min_clean = re.sub(r'[>=<]', '', min_ver)
        ok = not is_outdated(version, min_clean) if version else False
    except importlib.metadata.PackageNotFoundError:
        pass
        
    return {
        "name": name,
        "installed": installed,
        "version": version,
        "ok": ok
    }

def check_all():
    return [check_pkg(name, ver) for name, ver in ESIM_PYTHON_DEPS.items()]

def missing():
    results = check_all()
    return [r["name"] for r in results if not r["installed"] or not r["ok"]]
