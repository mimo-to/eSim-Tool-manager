from pathlib import Path
from datetime import datetime

def get_log_path() -> Path:
    log_dir = Path.home() / ".esim_tool_manager"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "esim_tm.log"

def log(action: str, target: str, status: str) -> None:
    path = get_log_path()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action} {target} {status}\n")

def read_last(n: int) -> list[str]:
    path = get_log_path()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.rstrip("\n") for line in lines[-n:]]
