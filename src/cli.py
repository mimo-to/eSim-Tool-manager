import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from src import registry, checker, installer, logger, health, repair, report, config, pip_checker, tui

console = Console()

def print_header():
    console.print(Panel("[bold cyan]eSim Tool Manager[/bold cyan]", expand=False))

def cmd_list():
    print_header()
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
    print_header()
    r = registry.load()
    results = checker.check_all(r)
    h = health.compute(results)
    
    color = "green"
    if h["status"] == "Good":
        color = "yellow"
    elif h["status"] == "Partial":
        color = "orange3"
    elif h["status"] == "Critical":
        color = "red"
    console.print(Panel(f"[bold {color}]{h['score']}/100[/bold {color}]", title="System Health", expand=False))
    console.print(f"Status: [{color}]{h['status']}[/{color}]")
    console.print(f"Required: {h['required_installed']}/{h['required_total']}")
    console.print(f"Optional: {h['optional_installed']}/{h['optional_total']}")

def cmd_repair(dry_run=False):
    print_header()

    scan = repair.scan()

    missing_required = scan.get("missing_required", [])
    missing_optional = scan.get("missing_optional", [])

    if not missing_required and not missing_optional:
        console.print("[bold green]✓ No issues found. System is healthy.[/bold green]")
        return

    table = Table(title="Repair Summary", box=box.ROUNDED)
    table.add_column("Category")
    table.add_column("Items")

    if missing_required:
        table.add_row(
            "[red]Missing Required[/red]",
            ", ".join(missing_required)
        )

    if missing_optional:
        table.add_row(
            "[yellow]Missing Optional[/yellow]",
            ", ".join(missing_optional)
        )

    console.print(table)

    if dry_run:
        console.print("\n[yellow bold]Dry run — no changes will be made.[/yellow bold]")
        return
    auto_conf = config.get("general.auto_confirm", False)
    if not auto_conf:
        from rich.prompt import Confirm
        if not Confirm.ask("Proceed with repair?"):
            return
    with console.status("[bold green]Repairing system dependencies...[/bold green]", spinner="dots"):
        res = repair.repair_all()
    t = Table(title="Repair Results", box=box.ROUNDED)
    t.add_column("Item", style="bold")
    t.add_column("Type")
    t.add_column("Result")

    for name in res["tools"]["fixed"]:
        t.add_row(name, "Tool", "[green]✓ Fixed[/green]")
    for name in res["tools"]["failed"]:
        t.add_row(name, "Tool", "[red]✗ Failed[/red]")
    for name in res["tools"]["skipped"]:
        t.add_row(name, "Tool", "[yellow]! Skipped[/yellow]")

    for p in res.get("pkgs", []):
        status = "[green]✓ Installed[/green]" if p["success"] else "[red]✗ Failed[/red]"
        t.add_row(p["name"], "Python", status)

    console.print(t)

def cmd_report():
    print_header()
    path = report.generate()
    console.print(f"[bold green]Report saved at:[/bold green] {path}")

def cmd_check(tool_id):
    print_header()
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
    print_header()
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
    print_header()
    r = registry.load()
    if tool_id:
        if tool_id not in r:
            console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
            return
        console.print(f"Updating {tool_id}...")
        res = installer.update(tool_id, r[tool_id])
        if res["success"]:
            console.print(f"[green]✓ Successfully updated {tool_id}[/green]")
        else:
            console.print(f"[red]✗ Failed to update {tool_id}[/red]")
    else:
        res = installer.update_all(r)
        table = Table(title="Update Results")
        table.add_column("Tool")
        table.add_column("Result")
        table.add_column("Detail")
        for t in res["updated"]:
            table.add_row(t, "[green]✓ Updated[/green]", "")
        for t in res["failed"]:
            table.add_row(t, "[red]✗ Failed[/red]", "")
        for t in res["skipped"]:
            table.add_row(t["name"], "[yellow]! Skipped[/yellow]", t["reason"])
        console.print(table)

def cmd_log():
    print_header()
    lines = logger.read_last(20)
    console.rule("[bold cyan]Last 20 Logs[/bold cyan]")
    for line in lines:
        console.print(line)

def cmd_pkgs():
    print_header()
    results = pip_checker.check_all()
    
    t = Table(title="Python Package Dependencies", box=box.ROUNDED)
    t.add_column("Package", style="bold")
    t.add_column("Status")
    t.add_column("Version")

    for r in results:
        status = "[green]✓ OK[/green]" if r["ok"] else "[red]✗ Missing[/red]"
        ver = r["version"] or "[dim]—[/dim]"
        t.add_row(r["name"], status, ver)

    console.print(t)

def main():
    parser = argparse.ArgumentParser(description="eSim Tool Manager")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list")
    subparsers.add_parser("dashboard")
    p_repair = subparsers.add_parser("repair")
    p_repair.add_argument("--dry-run", action="store_true")
    subparsers.add_parser("report")
    p_check = subparsers.add_parser("check")
    p_check.add_argument("tool", nargs="?", default=None)
    p_install = subparsers.add_parser("install")
    p_install.add_argument("tool")
    p_update = subparsers.add_parser("update")
    p_update.add_argument("tool", nargs="?", default=None)
    subparsers.add_parser("log")
    subparsers.add_parser("pkgs")
    subparsers.add_parser("tui")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list()
    elif args.command == "dashboard":
        cmd_dashboard()
    elif args.command == "repair":
        cmd_repair(args.dry_run)
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
    elif args.command == "pkgs":
        cmd_pkgs()
    elif args.command == "tui":
        tui.run()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
