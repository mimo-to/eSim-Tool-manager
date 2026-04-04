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

def get_pkg_manager() -> str:
    os_name = get_os()
    if os_name == "linux":
        if shutil.which("apt-get"):
            return "apt"
        if shutil.which("dnf"):
            return "dnf"
        raise RuntimeError("Unsupported Linux distribution")
    if os_name == "macos":
        if shutil.which("brew"):
            return "brew"
        raise RuntimeError("Homebrew not found. Install from https://brew.sh")
    if os_name == "windows":
        if shutil.which("winget"):
            return "winget"
        raise RuntimeError("winget not found. Update Windows or install App Installer from Microsoft Store")
    raise RuntimeError(f"Unsupported platform: {os_name}")

def pkg_key() -> str:
    return f"{get_pkg_manager()}_pkg"

def install_cmd(pkg: str) -> list[str]:
    pm = get_pkg_manager()
    if pm == "apt":
        return ["sudo", "apt-get", "install", "-y", pkg]
    if pm == "dnf":
        return ["sudo", "dnf", "install", "-y", pkg]
    if pm == "brew":
        return ["brew", "install", pkg]
    if pm == "winget":
        return ["winget", "install", "--id", pkg, "-e", "--silent"]
    raise RuntimeError(f"Unsupported package manager: {pm}")

def update_cmd(pkg: str) -> list[str]:
    pm = get_pkg_manager()
    if pm == "apt":
        return ["sudo", "apt-get", "upgrade", "-y", pkg]
    if pm == "dnf":
        return ["sudo", "dnf", "upgrade", "-y", pkg]
    if pm == "brew":
        return ["brew", "upgrade", pkg]
    if pm == "winget":
        return ["winget", "upgrade", "--id", pkg, "-e"]
    raise RuntimeError(f"Unsupported package manager: {pm}")
