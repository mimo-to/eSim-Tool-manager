import argparse
import json
import platform
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from src import registry, checker, installer, logger, health, repair, report, config, pip_checker, tui, snapshot, platform_mgr as pm

console = Console()
console = Console()

def is_fixed(res):
    return bool(res.get("installed")) and not bool(res.get("conflict")) and not bool(res.get("path_issue"))

def is_pkg_available(cmd_search):
    try:
        result = subprocess.run(cmd_search, capture_output=True, text=True, timeout=5)
        return result.returncode == 0 and result.stdout.strip()
    except Exception:
        return False

INSTALL_COMMANDS = {
    "ngspice": {
        "linux": "sudo apt install ngspice",
        "darwin": "brew install ngspice",
        "windows": {"choco": "choco install ngspice -y"}
    },
    "verilator": {
        "linux": "sudo apt install verilator",
        "darwin": "brew install verilator",
        "windows": None
    },
    "ghdl": {
        "linux": "sudo apt install ghdl",
        "darwin": "brew install ghdl",
        "windows": {"winget": "winget install --id ghdl.ghdl.ucrt64.mcode -e --silent"}
    },
    "kicad": {
        "windows": {
            "winget": "winget install --id KiCad.KiCad -e --silent",
            "choco": "choco install kicad -y"
        }
    }
}

MANUAL_LINKS = {
    "ngspice": "https://ngspice.sourceforge.io",
    "verilator": "https://www.veripool.org/verilator/",
    "ghdl": "https://ghdl.github.io/ghdl/",
}

def get_fix_command(tool_id, plat):
    cmd_data = INSTALL_COMMANDS.get(tool_id, {}).get(plat)
    if not cmd_data:
        return None
    
    if plat == "windows" and isinstance(cmd_data, dict):
        if shutil.which("winget") is not None and cmd_data.get("winget"):
            pkg_id = "KiCad.KiCad" if tool_id == "kicad" else tool_id
            if is_pkg_available(["winget", "search", "--id", pkg_id]):
                return cmd_data["winget"]
        if shutil.which("choco") is not None and cmd_data.get("choco"):
            if is_pkg_available(["choco", "search", tool_id]):
                return cmd_data["choco"]
        return None
    return cmd_data

def print_header():
    console.print(Panel("[bold cyan]eSim Tool Manager[/bold cyan]", expand=False))

def cmd_list(args):
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

def cmd_dashboard(args):
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

def cmd_repair(args):
    verbose = getattr(args, "verbose", False)
    dry_run = getattr(args, "dry_run", False)
    if verbose:
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

def cmd_report(args):
    print_header()
    path = report.generate()
    console.print(f"[bold green]Report saved at:[/bold green] {path}")

def cmd_check(args):
    tool_id = getattr(args, "tool", None)
    json_mode = getattr(args, "json", False)
    verbose = getattr(args, "verbose", False)
    if json_mode:
        verbose = False

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
        if verbose:
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
        if verbose:
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

def cmd_install(args):
    tool_id = getattr(args, "tool", None)
    print_header()
    r = registry.load()
    if not tool_id or tool_id not in r:
        console.print(f"[red]Error: Unknown tool '{tool_id}'[/red]")
        return
    console.print(f"Installing {tool_id}...")
    res = installer.install(tool_id, r[tool_id])
    if res["success"]:
        console.print(f"[green]✓ Successfully installed {tool_id}[/green]")
    else:
        console.print(f"[red]✗ Failed to install {tool_id}[/red]")

def cmd_update(args):
    tool_id = getattr(args, "tool", None)
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

def cmd_log(args):
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

def cmd_pkgs(args):
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

def cmd_doctor(args):
    verbose = getattr(args, "verbose", False)
    print_header()
    registry_data = registry.load()
    tool_results = checker.check_all(registry_data)
    
    if verbose:
        for res in tool_results:
            if not res.get("installed"):
                status = "Missing"
            elif res.get("conflict"):
                status = "Outdated"
            else:
                status = "OK"
            console.print(f"[dim]Checked: {res.get('name')} → {status}[/dim]")
            
    pkg_results = pip_checker.check_all()
    
    if verbose:
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

    plat = platform.system().lower()
    for res in tool_results:
        name = res.get("name", "Unknown Tool")
        installed = res.get("installed")
        path_issue = res.get("path_issue")
        conflict = res.get("conflict")
        req_label = "(Required)" if res.get("required") else "(Optional)"

        t_id = res.get("id")

        if not installed:
            tool_issues += 1
            console.print(f"[red]✗[/red] {name} — Not found {req_label}")
            
            t_data = registry_data.get(t_id) if t_id else None
            fix_cmd = None
            if t_data:
                pkg_id = t_data.get(pm.pkg_key())
                if pkg_id:
                    fix_cmd = " ".join(pm.install_cmd(pkg_id))
            
            if fix_cmd:
                console.print(f"    → Fix: {fix_cmd}")
            else:
                platform_cmd = get_fix_command(t_id, plat)
                link = MANUAL_LINKS.get(t_id)
                
                if platform_cmd:
                    console.print(f"    → Fix:\n      Run:\n      {platform_cmd}")
                    if link:
                        console.print(f"\n      Or install manually:\n      {link}")
                elif link:
                    console.print(f"    → Fix:\n      Install manually:\n      {link}")
                    console.print(f"      [dim]Search: install {name} {plat if plat != 'darwin' else 'macos'}[/dim]")
                    if plat == "windows":
                        if shutil.which("winget") is not None:
                            console.print(f"      [dim]Try: winget search {name.lower()}[/dim]")
                        if shutil.which("choco") is not None:
                            console.print(f"      [dim]Try: choco search {name.lower()}[/dim]")
                else:
                    console.print("    → Fix: Install manually (no package mapping found)")
                    if plat == "windows":
                        if shutil.which("winget") is not None:
                            console.print(f"      [dim]Try: winget search {name.lower()}[/dim]")
                        if shutil.which("choco") is not None:
                            console.print(f"      [dim]Try: choco search {name.lower()}[/dim]")
        elif path_issue:
            tool_issues += 1
            console.print(f"[yellow]![/yellow] {name} — Not in PATH {req_label}")
            console.print("    → Fix: Add tool to system PATH")
        elif conflict:
            tool_issues += 1
            console.print(f"[yellow]![/yellow] {name} — Outdated {req_label}")
            
            t_data = registry_data.get(t_id) if t_id else None
            fix_cmd = None
            if t_data:
                pkg_id = t_data.get(pm.pkg_key())
                if pkg_id:
                    fix_cmd = " ".join(pm.update_cmd(pkg_id))
            
            if fix_cmd:
                console.print(f"    → Fix: {fix_cmd}")
            else:
                platform_cmd = get_fix_command(t_id, plat)
                link = MANUAL_LINKS.get(t_id)
                
                if platform_cmd:
                    console.print(f"    → Fix:\n      Run:\n      {platform_cmd}")
                    if link:
                        console.print(f"\n      Or install manually:\n      {link}")
                elif link:
                    console.print(f"    → Fix:\n      Update manually:\n      {link}")
                    console.print(f"      [dim]Search: install {name} {plat if plat != 'darwin' else 'macos'}[/dim]")
                    if plat == "windows":
                        if shutil.which("winget") is not None:
                            console.print(f"      [dim]Try: winget search {name.lower()}[/dim]")
                        if shutil.which("choco") is not None:
                            console.print(f"      [dim]Try: choco search {name.lower()}[/dim]")
                else:
                    console.print("    → Fix: Update manually (no package mapping found)")
                    if plat == "windows":
                        if shutil.which("winget") is not None:
                            console.print(f"      [dim]Try: winget search {name.lower()}[/dim]")
                        if shutil.which("choco") is not None:
                            console.print(f"      [dim]Try: choco search {name.lower()}[/dim]")
        else:
            console.print(f"[green]✓[/green] {name} — OK {req_label}")

    console.print()
    console.print("[bold cyan]Python Packages[/bold cyan]")
    
    is_pipx = "pipx" in sys.prefix.lower()
    is_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    
    if is_pipx:
        console.print("[dim]Detected pipx environment — using pipx inject for package fixes[/dim]")
    elif is_venv:
        console.print("[dim]Detected virtual environment[/dim]")
    
    missing_pkgs = [pkg.get("name", "Unknown Package") for pkg in pkg_results if not pkg.get("installed") or not pkg.get("ok")]
    show_individual_fix = len(missing_pkgs) == 1
    
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
            if show_individual_fix:
                if is_pipx:
                    console.print(f"    → Fix: pipx inject esim-tool-manager {p_name}")
                else:
                    console.print(f"    → Fix: pip install {p_name}")
        elif not p_ok:
            pkg_issues += 1
            console.print(f"[yellow]![/yellow] {p_name} — Outdated")
            if show_individual_fix:
                if is_pipx:
                    console.print(f"    → Fix: pipx inject esim-tool-manager {p_name}")
                else:
                    console.print(f"    → Fix: pip install --upgrade {p_name}")

    if len(missing_pkgs) > 1:
        console.print()
        console.print("[bold yellow]Bulk Fix:[/bold yellow]")
        pkgs_str = " ".join(missing_pkgs)
        if is_pipx:
            console.print(f"pipx inject esim-tool-manager {pkgs_str}")
        else:
            console.print(f"pip install {pkgs_str}")

    if tool_issues == 0 and pkg_issues == 0:
        console.print("\nAll tools and packages are in a healthy state.")

    console.print()
    console.print(f"eSim Readiness: {health_data.get('score')}/100 ({health_data.get('status')})")

def cmd_snapshot(args):
    r = registry.load()
    tools = checker.check_all(r)
    pkgs = pip_checker.check_all()

    snapshot.save_snapshot(tools, pkgs)
    path = Path.home() / ".esim_tool_manager" / "snapshot.json"
    console.print(f"Snapshot saved → {path}")

def cmd_snapshot_diff(args):
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

def cmd_setup_help(args):
    print_header()
    
    console.print("[bold cyan]1. Getting Started[/bold cyan]")
    console.print("   • [bold]esim-tm doctor[/bold]        → Run full diagnostics")
    console.print("   • [bold]esim-tm assist[/bold]        → Interactive guided fix")
    console.print("   • [bold]esim-tm repair[/bold]        → Auto-fix missing items")
    
    console.print("\n[bold cyan]2. Monitoring & State[/bold cyan]")
    console.print("   • [bold]esim-tm snapshot[/bold]      → Save current state")
    console.print("   • [bold]esim-tm snapshot-diff[/bold] → Identify changes since last snapshot")
    console.print("   • [bold]esim-tm dashboard[/bold]     → View readiness score")
    
    console.print("\n[bold cyan]3. Typical Workflow[/bold cyan]")
    console.print("   [dim]doctor[/dim] → [dim]assist[/dim] → [dim]snapshot[/dim] (baseline) → [dim]snapshot-diff[/dim] (monitor)")
    console.print("\nFor more details, run commands with [bold]--help[/bold]")


DOWNLOAD_LINKS = {
    "python3": "https://www.python.org/downloads/",
    "pip": "https://pip.pypa.io/en/stable/installation/",
    "git": "https://git-scm.com/downloads",
    "ngspice": "https://ngspice.sourceforge.io/download.html",
    "kicad": "https://www.kicad.org/download/",
    "verilator": "https://verilator.org/guide/latest/install.html",
    "ghdl": "https://github.com/ghdl/ghdl/releases"
}

INSTALL_STEPS = {
    "python3": [
        "Go to python.org/downloads",
        "Download the latest Windows installer",
        "IMPORTANT: Check 'Add Python to PATH' before clicking Install",
        "Complete installation and restart terminal"
    ],
    "pip": [
        "Download get-pip.py from bootstrap.pypa.io/get-pip.py",
        "Run: python get-pip.py",
        "Verify with: pip --version"
    ],
    "git": [
        "Download the Windows installer from git-scm.com",
        "Run the installer and accept default options",
        "Restart terminal to enable 'git' command"
    ],
    "ngspice": [
        "Visit the Ngspice download page on SourceForge",
        "Download the latest Windows binary (e.g., ngspice-42_64.zip)",
        "Extract it to c:\\ngspice",
        "Add c:\\ngspice\\bin to your system PATH"
    ],
    "verilator": [
        "Download the latest release or use WSL/Cygwin",
        "Follow the official guide to build/install",
        "Ensure 'verilator' command is accessible in PATH"
    ],
    "ghdl": [
        "Download the msys2 or llvm binary for Windows",
        "Extract/Install to a known directory",
        "Add the install directory to your PATH"
    ],
    "kicad": [
        "Download the 64-bit installer from the official website",
        "Run the installer and follow the wizard (default settings recommended)",
        "Check 'Add KiCad to PATH' if prompted, or verify manually"
    ]
}


def cmd_assist(args):
    """Interactive assistant for tool installation."""
    registry_data = registry.load()
    plat = platform.system().lower()
    
    # Discovery phase
    all_res = checker.check_all(registry_data)
    problematic_results = [res for res in all_res if not is_fixed(res)]
    
    if not problematic_results:
        console.print("[bold green]✓ All tools are healthy! No assistance needed.[/bold green]")
        return

    # Initial Snapshot (Locked Set)
    initial_tools = {str(res["id"]).strip().lower() for res in problematic_results}
    installed_tools = set()
    skipped_tools = set()
    
    print_header()
    console.print(f"Found {len(initial_tools)} tool(s) requiring attention.\n")
    
    try:
        # Outer Loop: Process one tool at a time
        for tool_id in sorted(list(initial_tools)):
            if tool_id in (installed_tools | skipped_tools):
                continue
                
            tool_data = registry_data.get(tool_id)
            if not tool_data:
                skipped_tools.add(tool_id)
                continue
                
            # Real-time state check per tool turn
            res = checker.check_tool(tool_id, tool_data)
            if is_fixed(res):
                installed_tools.add(tool_id)
                continue
                
            attempts = 0
            max_attempts = 5
            path_hint_shown = False
            
            # Inner Loop: Menu for current tool
            while True:
                # Refresh state inside inner loop if needed
                res = checker.check_tool(tool_id, tool_data)
                if is_fixed(res):
                    if tool_id not in (installed_tools | skipped_tools):
                        installed_tools.add(tool_id)
                    break # to next tool
                
                status_str = "[red]Not found[/red]"
                if res.get("path_issue"):
                    status_str = "[yellow]Installed but not in PATH[/yellow]"
                elif res.get("conflict"):
                    status_str = "[red]Version conflict / Dirty install[/red]"
                
                console.print(Panel(
                    f"[bold]{res['name']}[/bold]\nStatus: {status_str}",
                    title=f"Tool Assistance ({sorted(list(initial_tools)).index(tool_id) + 1}/{len(initial_tools)})",
                    expand=False
                ))
                
                if res.get("path_issue") and not path_hint_shown:
                    console.print("[dim]💡 Hint: The tool appears to be installed but your terminal can't find it. Try adding its folder to your system PATH variable.[/dim]\n")
                    path_hint_shown = True

                # Dynamic Menu
                options = []
                idx = 1
                
                # 1. Auto-install (if available)
                has_auto = tool_data.get("install_cmd") or (plat == "windows" and tool_data.get("winget_pkg"))
                if has_auto:
                    options.append((str(idx), "[green]Auto-install[/green] (Try automatic repair)"))
                    auto_idx = str(idx)
                    idx += 1
                else:
                    auto_idx = None
                
                # 2. Download page / Installation Guide
                download_url = DOWNLOAD_LINKS.get(tool_id)
                label_text = "Open official [bold]installation guide[/bold] in browser"
                
                if not download_url:
                    download_url = tool_data.get("homepage")
                    label_text = "Open official [bold]homepage[/bold] in browser"
                
                if download_url:
                    options.append((str(idx), label_text))
                    download_idx = str(idx)
                    idx += 1
                else:
                    download_idx = None
                
                # 3. Manual Steps
                if tool_id in INSTALL_STEPS:
                    options.append((str(idx), "Show [bold]manual installation steps[/bold]"))
                    steps_idx = str(idx)
                    idx += 1
                else:
                    steps_idx = None
                
                recheck_idx = str(idx)
                options.append((recheck_idx, "Re-check status now"))
                idx += 1
                
                skip_idx = str(idx)
                options.append((skip_idx, "Skip this tool"))
                
                options.append(("a", "Skip [bold]all[/bold] remaining tools"))
                options.append(("q", "Quit assistant"))
                
                for key, label in options:
                    console.print(f"  {key}. {label}")
                
                choice = input("\nSelect an option: ").strip().lower()
                
                if choice == auto_idx and auto_idx:
                    console.print(f"\nAttempting auto-install for {res['name']}...")
                    try:
                        success = installer.install_tool(tool_id, tool_data)
                        if success:
                            console.print("[green]Installation attempted successfully.[/green]")
                        else:
                            console.print("[yellow]Auto-install was not successful or not available.[/yellow]")
                    except Exception as e:
                        console.print(f"[red]Auto-install failed with error: {e}[/red]")
                        success = False
                    
                    console.print("\n[bold]Re-check recommended to verify health.[/bold]")
                    from rich.prompt import Confirm
                    if Confirm.ask("Re-check status now?"):
                        res = checker.check_tool(tool_id, tool_data)
                        if is_fixed(res):
                            console.print("[bold green]✓ Fixed! Tool is now healthy.[/bold green]")
                            if tool_id not in (installed_tools | skipped_tools):
                                installed_tools.add(tool_id)
                            break
                        else:
                            console.print("[red]✗ Still not detected or unhealthy.[/red]")
                
                elif choice == download_idx and download_idx:
                    console.print(f"Opening: {download_url}")
                    webbrowser.open(download_url)
                
                elif choice == steps_idx and steps_idx:
                    steps = INSTALL_STEPS[tool_id]
                    console.print(f"\n[bold underline]Manual Steps for {res['name']}:[/bold underline]")
                    for i, step in enumerate(steps, 1):
                        console.print(f"  {i}. {step}")
                    console.print("")
                
                elif choice == recheck_idx:
                    attempts += 1
                    console.print("\nRe-checking status...")
                    res = checker.check_tool(tool_id, tool_data)
                    if is_fixed(res):
                        console.print("[bold green]✓ Fixed![/bold green]")
                        if tool_id not in (installed_tools | skipped_tools):
                            installed_tools.add(tool_id)
                        break
                    else:
                        console.print(f"[red]✗ Still not detected.[/red] (Attempt {attempts}/{max_attempts})")
                        if attempts >= max_attempts:
                            console.print("[yellow]Maximum re-check attempts reached for this tool.[/yellow]")
                            if tool_id not in (installed_tools | skipped_tools):
                                skipped_tools.add(tool_id)
                            break
                            
                elif choice == skip_idx:
                    if tool_id not in (installed_tools | skipped_tools):
                        skipped_tools.add(tool_id)
                    break
                    
                elif choice == "a":
                    # Skip all remaining tools including current
                    to_skip = initial_tools - installed_tools - skipped_tools
                    skipped_tools.update(to_skip)
                    console.print(f"\nSkipping all remaining {len(to_skip)} tool(s)...")
                    return # Exit outer loop via return to trigger finally
                    
                elif choice == "q":
                    console.print("\nExiting assistant...")
                    return # Exit outer loop via return to trigger finally
                    
                else:
                    console.print("[red]Invalid choice. Try again.[/red]")
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    finally:
        # 1. ENFORCE HIGH-CONFIDENCE DISJOINT PARTITION
        final_installed = installed_tools.copy()
        final_skipped = skipped_tools.copy()
        final_remaining = initial_tools - final_installed - final_skipped
        
        # PROVE INTEGRITY
        assert final_installed.isdisjoint(final_skipped), "Internal state error"
        
        # 2. CATEGORIZED SUMMARY
        console.print(Panel(
            "[bold cyan]Assistant Summary Report[/bold cyan]",
            box=box.DOUBLE,
            expand=False
        ))
        
        # Installed
        console.print("\n[bold green]✓ SUCCESSFULLY INSTALLED / FIXED[/bold green]")
        if final_installed:
            for tid in sorted(list(final_installed)):
                name = registry_data.get(tid, {}).get("name", tid)
                console.print(f"  • {name}")
        else:
            console.print("  (none)")
            
        # Skipped
        console.print("\n[bold yellow]⚠ SKIPPED DURING ASSIST[/bold yellow]")
        if final_skipped:
            for tid in sorted(list(final_skipped)):
                name = registry_data.get(tid, {}).get("name", tid)
                console.print(f"  • {name}")
        else:
            console.print("  (none)")
            
        # Remaining
        console.print("\n[bold red]✗ REMAINING ISSUES[/bold red]")
        if final_remaining:
            for tid in sorted(list(final_remaining)):
                name = registry_data.get(tid, {}).get("name", tid)
                console.print(f"  • {name}")
        else:
            console.print("  (none)")
            
        console.print("\n[dim]Use 'esim-tm doctor' to verify all system dependencies.[/dim]\n")

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
    subparsers.add_parser("assist", parents=[parent_parser])
    
    args = parser.parse_args()
    
    dispatch = {
        "list": cmd_list,
        "dashboard": cmd_dashboard,
        "repair": cmd_repair,
        "report": cmd_report,
        "check": cmd_check,
        "install": cmd_install,
        "update": cmd_update,
        "log": cmd_log,
        "pkgs": cmd_pkgs,
        "tui": tui.run,
        "doctor": cmd_doctor,
        "snapshot": cmd_snapshot,
        "snapshot-diff": cmd_snapshot_diff,
        "setup-help": cmd_setup_help,
        "assist": cmd_assist,
    }
    
    cmd = dispatch.get(args.command)
    if not cmd:
        parser.print_help()
        return
        
    cmd(args)

if __name__ == "__main__":
    main()
