import importlib.metadata
import re

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
        
        v_match = re.search(r'(\d+)', version)
        m_match = re.search(r'(\d+)', min_ver)
        
        if v_match and m_match:
            v_major = int(v_match.group(1))
            m_major = int(m_match.group(1))
            if v_major >= m_major:
                ok = True
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
