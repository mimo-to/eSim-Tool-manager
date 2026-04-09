import platform
import shutil

def get_os() -> str:
    system = platform.system()
    if system == "Linux":
        return "linux"
    if system == "Windows":
        return "windows"
    if system == "Darwin":
        return "macos"
    raise RuntimeError(f"Unsupported platform: {system}")

def get_available_managers() -> list[str]:
    """Detect all available package managers for the current platform."""
    os_name = get_os()
    managers = []
    
    if os_name == "linux":
        if shutil.which("apt-get"):
            managers.append("apt")
        if shutil.which("dnf"):
            managers.append("dnf")
    elif os_name == "macos":
        if shutil.which("brew"):
            managers.append("brew")
    elif os_name == "windows":
        if shutil.which("winget"):
            managers.append("winget")
        if shutil.which("choco"):
            managers.append("choco")
            
    return managers

def get_pkg_manager() -> str:
    """Legacy helper: returns the primary package manager or raises error."""
    managers = get_available_managers()
    if not managers:
        os_name = get_os()
        if os_name == "linux":
            raise RuntimeError("Unsupported Linux distribution")
        if os_name == "macos":
            raise RuntimeError("Homebrew not found. Install from https://brew.sh")
        if os_name == "windows":
            raise RuntimeError("winget/choco not found. Please install a package manager.")
    return managers[0]

def pkg_key() -> str:
    """Returns the dictionary key for the primary package manager."""
    try:
        return f"{get_pkg_manager()}_pkg"
    except RuntimeError:
        return "pkg_name" # Fallback if no manager

def search_cmd(manager: str, pkg: str) -> list[str]:
    """Return command to search for a package in the specified manager."""
    if manager == "apt":
        return ["apt-cache", "search", pkg]
    if manager == "dnf":
        return ["dnf", "search", pkg]
    if manager == "brew":
        return ["brew", "search", pkg]
    if manager == "winget":
        return ["winget", "search", pkg]
    if manager == "choco":
        return ["choco", "search", pkg]
    return []

def install_cmd(pkg: str, manager: str = None) -> list[str]:
    """Return command to install a package using the specified or primary manager."""
    pm = manager or get_pkg_manager()
    if pm == "apt":
        return ["sudo", "apt-get", "install", "-y", pkg]
    if pm == "dnf":
        return ["sudo", "dnf", "install", "-y", pkg]
    if pm == "brew":
        return ["brew", "install", pkg]
    if pm == "winget":
        return ["winget", "install", "--id", pkg, "-e", "--silent"]
    if pm == "choco":
        return ["choco", "install", "-y", pkg]
    raise RuntimeError(f"Unsupported package manager: {pm}")

def update_cmd(pkg: str, manager: str = None) -> list[str]:
    """Return command to update a package using the specified or primary manager."""
    pm = manager or get_pkg_manager()
    if pm == "apt":
        return ["sudo", "apt-get", "upgrade", "-y", pkg]
    if pm == "dnf":
        return ["sudo", "dnf", "upgrade", "-y", pkg]
    if pm == "brew":
        return ["brew", "upgrade", pkg]
    if pm == "winget":
        return ["winget", "upgrade", "--id", pkg, "-e"]
    if pm == "choco":
        return ["choco", "upgrade", "-y", pkg]
    raise RuntimeError(f"Unsupported package manager: {pm}")
