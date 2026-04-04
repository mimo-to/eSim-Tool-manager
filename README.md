# eSim Tool Manager

Cross-platform CLI tool to manage, verify, update, and repair eSim EDA dependencies with intelligent automation.

## Features

- **Automated Tool Installation**: Full cross-platform support for `apt`, `dnf`, `brew`, and `winget`.
- **Intelligent Dependency Checking**: Real-time verification of installed tools with regex-based version extraction.
- **Improved Update System**: Version-aware logic that compares installed versions against requirements to bypass redundant updates.
- **Persistent User Configuration**: Customizable behavior via `~/.esim_tool_manager/config.toml` (auto-confirm, update-optional).
- **Automated Repair Workflows**: Scans systems for missing required dependencies and offers a one-click recovery.
- **Health Scoring Dashboard**: Quantifies system readiness with a real-time health score (0-100).
- **HTML Audit Reporting**: Generates sleek, dark-themed system health reports for offline diagnostic sharing.
- **Professional CLI Interface**: Powered by `rich` for crisp, color-coded tables and status panels.

## Why This Tool?

Unlike generic installation scripts, the eSim Tool Manager provides a professional maintenance layer:
- **Efficiency**: Avoids unnecessary updates using smart version tuple comparison logic.
- **Safety**: Prioritizes automated repair workflows over simple error reporting to ensure a working EDA environment.
- **Visibility**: Offers a diagnostic dashboard and health score to ensure system readiness at a glance.

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/eSim-Tool-manager.git
    cd eSim-Tool-manager
    ```

2.  **Setup Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

| Command | Description |
| :--- | :--- |
| `python run.py list` | List all tools in the registry and their installation status. |
| `python run.py check` | Run focused installation and version verification on all tools. |
| `python run.py dashboard` | View system health score and tool status in a polished panel. |
| `python run.py update` | Perform a version-aware bulk update of all installed tools. |
| `python run.py repair` | Scan and automatically restore missing required dependencies. |
| `python run.py report` | Generate an HTML diagnostic report of your system's health. |
| `python run.py log` | Inspect recent activity and subprocess execution logs. |

## Configuration

The system persists user preferences in `~/.esim_tool_manager/config.toml`:

```toml
[general]
auto_confirm = false  # Set to true to skip repair confirmation prompts
log_level = "INFO"

[update]
update_optional = false # Set to true to include optional tools in bulk updates
```

## How the Update Engine Works

The eSim Tool Manager uses a deterministic and safe update strategy:
1.  **Version Normalization**: Converts version strings (`3.11.9`) into comparable integer tuples using `re.findall(r'\d+', ...)`.
2.  **Tuple Comparison**: Normalizes tuple lengths (e.g., `(3, 8)` vs `(3, 8, 1)` becomes `(3, 8, 0)` vs `(3, 8, 1)`) for accurate relative positioning.
3.  **Intelligent Skip**: If your installed version is already `min_version` or higher, the tool reports "Already up-to-date" and skips the expensive subprocess call.

## Project Structure

-   `src/registry.py`: TOML-driven master tool database logic.
-   `src/installer.py`: Core orchestration for installs and version-aware updates.
-   `src/checker.py`: Subprocess-based verification engine with regex extraction.
-   `src/platform_mgr.py`: Cross-platform abstraction layer for package managers.
-   `src/repair.py`: Logic for automated dependency recovery workflows.
-   `src/report.py`: Offline HTML diagnostic report generator.
-   `src/health.py`: Scoring algorithms for system readiness calculations.
-   `src/config.py`: Safe, persistent user configuration management.
-   `src/cli.py`: Professional subcommand-based interface.

## Design Highlights

-   **Modular Architecture**: Clean separation of concerns between verification, installation, and reporting.
-   **No Hardcoding**: All tool metadata, version patterns, and dependencies are externalized in `tools.toml`.
-   **Cross-Platform Ease**: Automatically maps tools to specific package managers (`apt`, `brew`, etc.) based on OS.
-   **Failure-Safe Execution**: Subprocess calls include timeouts and isolated execution to prevent system hangs.
