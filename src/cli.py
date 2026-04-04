import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src import registry, checker, installer, logger, health, repair, report

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

def cmd_dashboard():
    r = registry.load()
    results = checker.check_all(r)
    h = health.compute(results)
    req_total = sum(1 for res in results if res["required"])
    req_inst = sum(1 for res in results if res["required"] and res["installed"])
    opt_total = sum(1 for res in results if not res["required"])
    opt_inst = sum(1 for res in results if not res["required"] and res["installed"])
    color = "green"
    if h["status"] == "Good":
        color = "yellow"
    elif h["status"] == "Partial":
        color = "orange3"
    elif h["status"] == "Critical":
        color = "red"
    console.print(Panel(f"[bold {color}]{h['score']}/100[/bold {color}]", title="System Health", expand=False))
    console.print(f"Status: [{color}]{h['status']}[/{color}]")
    console.print(f"Required: {req_inst}/{req_total}")
    console.print(f"Optional: {opt_inst}/{opt_total}")

def cmd_repair():
    s = repair.scan()
    if s["missing_required"]:
        console.print("[bold red]Missing Required:[/bold red]")
        for t in s["missing_required"]:
            console.print(f" - {t}")
    if s["missing_optional"]:
        console.print("[bold yellow]Missing Optional:[/bold yellow]")
        for t in s["missing_optional"]:
            console.print(f" - {t}")
    if not s["missing_required"] and not s["missing_optional"]:
        console.print("[green]✓ All tools present[/green]")
        return
    if console.input("\nProceed with repair? (y/n): ").lower() != 'y':
        return
    res = repair.repair_all()
    table = Table(title="Repair Results")
    table.add_column("Item")
    table.add_column("Result")
    for t in res["fixed"]:
        table.add_row(t, "[green]✓ Fixed[/green]")
    for t in res["failed"]:
        table.add_row(t, "[red]✗ Failed[/red]")
    for t in res["skipped"]:
        table.add_row(t, "[yellow]! Skipped[/yellow]")
    console.print(table)

def cmd_report():
    path = report.generate()
    console.print(f"[bold green]Report saved at:[/bold green] {path}")

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
    subparsers.add_parser("dashboard")
    subparsers.add_parser("repair")
    subparsers.add_parser("report")
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
    elif args.command == "dashboard":
        cmd_dashboard()
    elif args.command == "repair":
        cmd_repair()
    elif args.command == "report":
        cmd_report()
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
