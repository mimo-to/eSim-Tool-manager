from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Vertical
from src import checker, health, logger, registry, pip_checker

class DashboardScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        results = checker.check_all(registry.load())
        h = health.compute(results)
        
        yield Vertical(
            Static("System Health", classes="title"),
            Static(f"{h['score']}/100", classes="score"),
            Static(f"Status: {h['status']}"),
            Static(f"Required: {h['required_installed']}/{h['required_total']}"),
            Static(f"Optional: {h['optional_installed']}/{h['optional_total']}"),
            Static("Press 1: Dashboard | 2: Tools | 3: Logs | 4: Packages | q: Quit", id="hints")
        )
        yield Footer()

class ToolsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="tools_table")
        yield Footer()

    def on_mount(self) -> None:
        reg = registry.load()
        results = checker.check_all(reg)
        table = self.query_one("#tools_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("Tool", "Status", "Version", "Required", "Conflict")

        if not results:
            table.add_row("No tools found", "", "", "", "")
            return

        results = sorted(results, key=lambda r: not r["required"])
        last_req = None

        for r in results:
            if r["required"] != last_req:
                header = "Required Tools" if r["required"] else "Optional Tools"
                table.add_row("", "", "", "", "")
                table.add_row(header, "", "", "", "")
                last_req = r["required"]

            status = "✓ OK" if r["installed"] else "✗ Missing"
            version = r.get("version") if r.get("version") else "—"
            required = "Yes" if r["required"] else "No"
            conflict = "⚠" if r.get("conflict") else ""

            table.add_row(
                r["name"],
                status,
                version,
                required,
                conflict
            )

class LogsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        logs = logger.read_last(10)
        yield Vertical(
            Static("Recent Logs", classes="title"),
            Static("\n".join(logs) if logs else "No logs available")
        )
        yield Footer()

class PackagesScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="pkgs_table")
        yield Footer()

    def on_mount(self) -> None:
        results = pip_checker.check_all()
        table = self.query_one("#pkgs_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("Package", "Status", "Version")

        if not results:
            table.add_row("No packages found", "", "")
            return

        results = sorted(results, key=lambda r: not r["ok"])
        last_ok = None

        for r in results:
            if r["ok"] != last_ok:
                header = "Installed Packages" if r["ok"] else "Missing Packages"
                table.add_row("", "", "")
                table.add_row(f"{header}", "", "")
                last_ok = r["ok"]

            status = "✓ OK" if r["ok"] else "✗ Missing"
            version = r.get("version") if r.get("version") else "—"

            table.add_row(
                r["name"],
                status,
                version
            )

class ToolManagerApp(App):
    CSS = """
    .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    .score {
        text-align: center;
        text-style: bold;
        color: green;
    }
    #hints {
        text-align: center;
        opacity: 0.6;
        margin-top: 2;
    }
    """

    SCREENS = {
        "dashboard": DashboardScreen,
        "tools": ToolsScreen,
        "logs": LogsScreen,
        "packages": PackagesScreen
    }

    BINDINGS = [
        Binding("1", "show_dashboard", "Dashboard"),
        Binding("2", "show_tools", "Tools"),
        Binding("4", "show_packages", "Packages"),
        Binding("3", "show_logs", "Logs"),
        Binding("q", "quit", "Quit")
    ]

    def on_mount(self):
        self.push_screen("dashboard")

    def action_show_dashboard(self):
        self.switch_screen("dashboard")

    def action_show_tools(self):
        self.switch_screen("tools")

    def action_show_logs(self):
        self.switch_screen("logs")

    def action_show_packages(self):
        self.switch_screen("packages")

def run():
    ToolManagerApp().run()

if __name__ == "__main__":
    run()
