import argparse
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from src import registry, checker, installer, logger, health, repair, report, config, pip_checker, tui, snapshot, platform_mgr as pm

console = Console()
_args = None

def is_verbose():
    return _args and getattr(_args, "verbose", False) and "--json" not in sys.argv

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
    if is_verbose():
        console.print("[dim]Analyzing system state...[/dim]")
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

def cmd_check(tool_id, json_mode=False):
    if not json_mode:
        print_header()
    r = registry.load()
    if tool_id:
        if tool_id not in r:
            if not json_mode:
                console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
            else:
                print(json.dumps({"error": f"Unknown tool '{tool_id}'"}, indent=2))
            return
        
        t_data = r[tool_id]
        if is_verbose():
            console.print(f"[dim]Command: {t_data.get('check_cmd')}[/dim]")
            
        res = checker.check_tool(tool_id, t_data)
        if json_mode:
            print(json.dumps([res], indent=2))
            return
        installed = "[green]✓ Installed[/green]" if res["installed"] else "[red]✗ Not Installed[/red]"
        version = res["version"] if res["version"] else "—"
        console.print(f"{res['name']}: {installed} (Version: {version})")
    else:
        results = checker.check_all(r)
        if is_verbose():
            for res in results:
                if not res.get("installed"):
                    status = "Missing"
                elif res.get("conflict"):
                    status = "Outdated"
                else:
                    status = "OK"
                console.print(f"[dim]Checked: {res.get('name')} → {status}[/dim]")
        
        if json_mode:
            print(json.dumps(results, indent=2))
            return
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
        if "SUCCESS" in line:
            console.print(line, style="green")
        elif "FOUND" in line:
            console.print(line, style="green")
        elif "FAILED" in line:
            console.print(line, style="red")
        elif "ATTEMPT" in line:
            console.print(line, style="yellow")
        else:
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

def cmd_doctor():
    print_header()
    registry_data = registry.load()
    tool_results = checker.check_all(registry_data)
    
    if is_verbose():
        for res in tool_results:
            if not res.get("installed"):
                status = "Missing"
            elif res.get("conflict"):
                status = "Outdated"
            else:
                status = "OK"
            console.print(f"[dim]Checked: {res.get('name')} → {status}[/dim]")
            
    pkg_results = pip_checker.check_all()
    
    if is_verbose():
        for pkg in pkg_results:
            if not pkg.get("installed"):
                p_status = "Missing"
            elif not pkg.get("ok"):
                p_status = "Outdated"
            else:
                p_status = "OK"
            console.print(f"[dim]Verified package: {pkg.get('name')} → {p_status}[/dim]")
            
    health_data = health.compute(tool_results)

    tool_issues = 0
    pkg_issues = 0

    console.print("[bold cyan]Tools[/bold cyan]")

    for res in tool_results:
        name = res.get("name", "Unknown Tool")
        installed = res.get("installed")
        path_issue = res.get("path_issue")
        conflict = res.get("conflict")
        req_label = "(Required)" if res.get("required") else "(Optional)"

        if not installed:
            tool_issues += 1
            console.print(f"[red]✗[/red] {name} — Not found {req_label}")
            t_id = res.get("id")
            t_data = registry_data.get(t_id) if t_id else None
            fix_cmd = None
            if t_data:
                pkg_id = t_data.get(pm.pkg_key())
                if pkg_id:
                    fix_cmd = " ".join(pm.install_cmd(pkg_id))
            
            if fix_cmd:
                console.print(f"    → Fix: {fix_cmd}")
            else:
                console.print("    → Fix: Install manually (no package mapping found)")
        elif path_issue:
            tool_issues += 1
            console.print(f"[yellow]![/yellow] {name} — Not in PATH {req_label}")
            console.print("    → Fix: Add tool to system PATH")
        elif conflict:
            tool_issues += 1
            console.print(f"[yellow]![/yellow] {name} — Outdated {req_label}")
            t_id = res.get("id")
            t_data = registry_data.get(t_id) if t_id else None
            fix_cmd = None
            if t_data:
                pkg_id = t_data.get(pm.pkg_key())
                if pkg_id:
                    fix_cmd = " ".join(pm.update_cmd(pkg_id))
            
            if fix_cmd:
                console.print(f"    → Fix: {fix_cmd}")
            else:
                console.print("    → Fix: Update manually (no package mapping found)")
        else:
            console.print(f"[green]✓[/green] {name} — OK {req_label}")

    console.print()
    console.print("[bold cyan]Python Packages[/bold cyan]")
    for pkg in pkg_results:
        p_name = pkg.get("name", "Unknown Package")
        p_installed = pkg.get("installed")
        p_ok = pkg.get("ok")
        p_ver = pkg.get("version")

        if p_installed and p_ok:
            console.print(f"[green]✓[/green] {p_name} — OK")
        elif not p_installed or p_ver is None:
            pkg_issues += 1
            console.print(f"[red]✗[/red] {p_name} — Not found")
            console.print(f"    → Fix: pip install {p_name}")
        elif not p_ok:
            pkg_issues += 1
            console.print(f"[yellow]![/yellow] {p_name} — Outdated")
            console.print(f"    → Fix: pip install --upgrade {p_name}")

    if tool_issues == 0 and pkg_issues == 0:
        console.print("\nAll tools and packages are in a healthy state.")

    console.print()
    console.print(f"eSim Readiness: {health_data.get('score')}/100 ({health_data.get('status')})")

def cmd_snapshot():
    r = registry.load()
    tools = checker.check_all(r)
    pkgs = pip_checker.check_all()

    snapshot.save_snapshot(tools, pkgs)
    path = Path.home() / ".esim_tool_manager" / "snapshot.json"
    console.print(f"Snapshot saved → {path}")

def cmd_snapshot_diff():
    old = snapshot.load_snapshot()

    if not old:
        console.print("No snapshot found. Run 'snapshot' first.")
        return

    r = registry.load()
    tools = checker.check_all(r)
    pkgs = pip_checker.check_all()

    diff = snapshot.get_diff(old, tools, pkgs)

    if diff["new_issues"]:
        console.print("[red]New Issues:[/red]")
        for t in diff["new_issues"]:
            console.print(f" - {t}")

    if diff["fixed_issues"]:
        console.print("[green]Fixed Issues:[/green]")
        for t in diff["fixed_issues"]:
            console.print(f" - {t}")

    if not diff["new_issues"] and not diff["fixed_issues"]:
        console.print("No changes detected")

def cmd_setup_help():
    print_header()
    
    console.print("[bold cyan]1. Getting Started[/bold cyan]")
    console.print("   • [bold]esim-tm doctor[/bold] (or python run.py [bold]doctor[/bold]) → Run full diagnostics")
    console.print("   • [bold]esim-tm repair[/bold] (or python run.py [bold]repair[/bold]) → Auto-fix missing items")
    console.print("   • [bold]esim-tm dashboard[/bold] (or python run.py [bold]dashboard[/bold]) → View readiness score")
    
    console.print("\n[bold cyan]2. Common Commands[/bold cyan]")
    console.print("   • [bold]list[/bold]          → Show status of all registered tools")
    console.print("   • [bold]check[/bold]         → Detailed check for a specific tool")
    console.print("   • [bold]pkgs[/bold]          → Check Python package dependencies")
    console.print("   • [bold]snapshot[/bold] (or python run.py [bold]snapshot[/bold])     → Save current state")
    console.print("   • [bold]snapshot-diff[/bold] → Identify changes since last snapshot")
    
    console.print("\n[bold cyan]3. Typical Workflow[/bold cyan]")
    console.print("   [dim]doctor[/dim] → [dim]repair[/dim] → [dim]snapshot[/dim] (baseline) → [dim]snapshot-diff[/dim] (monitor)")
    console.print("\nFor more details, run commands with [bold]--help[/bold]")

def check_first_run():
    # Skip onboarding if JSON mode is requested to keep output clean
    if "--json" in sys.argv:
        return

    flag_path = Path.home() / ".esim_tool_manager" / "first_run.flag"
    if not flag_path.exists():
        console.print("\n[bold cyan]Welcome to eSim Tool Manager[/bold cyan]\n")
        console.print("Run:")
        console.print("  [bold]esim-tm doctor[/bold]\n")
        console.print("to check your system setup.\n")
        
        # Ensure directory exists and create the flag file
        flag_path.parent.mkdir(parents=True, exist_ok=True)
        flag_path.touch()

def main():
    check_first_run()
    
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--verbose", action="store_true")
    
    parser = argparse.ArgumentParser(description="eSim Tool Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("list", parents=[parent_parser])
    subparsers.add_parser("dashboard", parents=[parent_parser])
    
    p_repair = subparsers.add_parser("repair", parents=[parent_parser])
    p_repair.add_argument("--dry-run", action="store_true")
    
    subparsers.add_parser("report", parents=[parent_parser])
    
    p_check = subparsers.add_parser("check", parents=[parent_parser])
    p_check.add_argument("tool", nargs="?", default=None)
    p_check.add_argument("--json", action="store_true")
    
    p_install = subparsers.add_parser("install", parents=[parent_parser])
    p_install.add_argument("tool")
    
    p_update = subparsers.add_parser("update", parents=[parent_parser])
    p_update.add_argument("tool", nargs="?", default=None)
    
    subparsers.add_parser("log", parents=[parent_parser])
    subparsers.add_parser("pkgs", parents=[parent_parser])
    subparsers.add_parser("tui", parents=[parent_parser])
    subparsers.add_parser("doctor", parents=[parent_parser])
    subparsers.add_parser("snapshot", parents=[parent_parser])
    subparsers.add_parser("snapshot-diff", parents=[parent_parser])
    subparsers.add_parser("setup-help", parents=[parent_parser])
    
    global _args
    _args = parser.parse_args()
    args = _args
    
    if args.command == "list":
        cmd_list()
    elif args.command == "dashboard":
        cmd_dashboard()
    elif args.command == "repair":
        cmd_repair(args.dry_run)
    elif args.command == "report":
        cmd_report()
    elif args.command == "check":
        cmd_check(args.tool, args.json)
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
    elif args.command == "doctor":
        cmd_doctor()
    elif args.command == "snapshot":
        cmd_snapshot()
    elif args.command == "snapshot-diff":
        cmd_snapshot_diff()
    elif args.command == "setup-help":
        cmd_setup_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
