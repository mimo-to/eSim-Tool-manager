import argparse
from rich.console import Console
from rich.table import Table
from src import registry, checker, installer, logger

console = Console()

def cmd_list():
    r = registry.load()
    results = checker.check_all(r)
    table = Table(title="Installed Tools")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Installed", justify="center")
    table.add_column("Version", justify="center")
    table.add_column("Required", justify="center")
    for res in results:
        installed = "[green]✓[/green]" if res["installed"] else "[red]✗[/red]"
        version = res["version"] if res["version"] else "—"
        required = "Required" if res["required"] else "Optional"
        table.add_row(res["name"], installed, version, required)
    console.print(table)

def cmd_check(tool_id):
    r = registry.load()
    if tool_id:
        if tool_id not in r:
            console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
            return
        res = checker.check_tool(tool_id, r[tool_id])
        installed = "[green]✓ Installed[/green]" if res["installed"] else "[red]✗ Not Installed[/red]"
        version = res["version"] if res["version"] else "—"
        console.print(f"{res['name']}: {installed} (Version: {version})")
    else:
        results = checker.check_all(r)
        table = Table(title="Dependency Check")
        table.add_column("Tool", style="cyan")
        table.add_column("Status")
        for res in results:
            status = "[green]✓ OK[/green]" if res["installed"] else "[red]✗ Missing[/red]"
            table.add_row(res["name"], status)
        console.print(table)

def cmd_install(tool_id):
    r = registry.load()
    if tool_id not in r:
        console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
        return
    console.print(f"Installing {tool_id}...")
    res = installer.install(tool_id, r[tool_id])
    if res["success"]:
        console.print(f"[green]✓ Successfully installed {tool_id}[/green]")
    else:
        console.print(f"[red]✗ Failed to install {tool_id}[/red]")

def cmd_update(tool_id):
    r = registry.load()
    if tool_id not in r:
        console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
        return
    console.print(f"Updating {tool_id}...")
    res = installer.update(tool_id, r[tool_id])
    if res["success"]:
        console.print(f"[green]✓ Successfully updated {tool_id}[/green]")
    else:
        console.print(f"[red]✗ Failed to update {tool_id}[/red]")

def cmd_log():
    lines = logger.read_last(20)
    console.rule("[bold cyan]Last 20 Logs[/bold cyan]")
    for line in lines:
        console.print(line)

def main():
    parser = argparse.ArgumentParser(description="eSim Tool Manager")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list")
    p_check = subparsers.add_parser("check")
    p_check.add_argument("tool", nargs="?", default=None)
    p_install = subparsers.add_parser("install")
    p_install.add_argument("tool")
    p_update = subparsers.add_parser("update")
    p_update.add_argument("tool")
    subparsers.add_parser("log")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list()
    elif args.command == "check":
        cmd_check(args.tool)
    elif args.command == "install":
        cmd_install(args.tool)
    elif args.command == "update":
        cmd_update(args.tool)
    elif args.command == "log":
        cmd_log()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
