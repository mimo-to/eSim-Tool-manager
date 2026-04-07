<div align="center">

<h1>eSim Tool Manager</h1>

<p>
    <strong>Automated Tool Management System for eSim Environment</strong>
</p>

<p>
    An intelligent diagnostic and repair engine designed to automate the installation, 
    configuration, and monitoring of the eSim EDA toolchain.
    <br />
    <em>Built with Python, Rich, and Textual.</em>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Platforms">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/System_Health-Automated-orange" alt="Status">
</p>

<p>
    <a href="https://github.com/mimo-to/eSim-Tool-manager"><strong>Source Code</strong></a> • 
    <a href="design_document.md"><strong>Architecture Docs</strong></a> • 
    <a href="Project_outcomes/health_report.html"><strong>Sample Report</strong></a>
</p>

</div>
<br />

---

## Project Overview

The **eSim Tool Manager (esim-tm)** is a professional utility created to solve the "Dependency Hell" often associated with eSim environment setups. 

For students and electronics engineers, setting up EDA tools like Ngspice, Verilator, and GHDL involves complex PATH configurations and version-specific dependencies. **esim-tm** exists to eliminate these barriers by providing:

-   **Deterministic Diagnostics**: A "Single Command" system health check.
-   **Intelligent Repair**: An interactive assistant that understands platform-specific package managers (winget, choco, apt, pip).
-   **Version Awareness**: Automatic detection of outdated tools vs project requirements.
-   **Environment Stability**: Snapshotting your system state to detect breaking changes instantly.

---

## Key Features

-   **`esim-tm doctor`**: The primary diagnostic suite. It performs a deep-scan of system executables and Python packages, generating platform-aware fix commands.
-   **`esim-tm assist`**: A state-machine driven recovery system. It guides you through missing dependencies with a "one-click" auto-install or manual guidance loop.
-   **Intelligent Update Engine**: Uses semantic version normalization to ensure your installed tools meet the minimum architectural requirements.
-   **Snapshot & Diff**: Capture your entire environment state to a JSON file. Use `snapshot-diff` after a system update to find exactly what changed in your toolchain.
-   **CI-Ready JSON Output**: Use `--json` with any command for machine-readable diagnostics, ideal for integration into automated build pipelines.
-   **TUI Dashboard**: A modern, terminal-based interactive dashboard built with Textual for real-time monitoring of tool readiness.
-   **Platform Support**: Specialized logic for Windows (Winget/Choco) and Linux (Pip/Native) environments.

---

## Demo / Usage Flow

### 0. Prerequisite
Make sure Python (3.8+) is installed.

### 1. Install the Tool
Install globally using `pipx` (recommended):

```bash
python -m pip install pipx
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
```

This installs the `esim-tm` command on your system.

### 2. Full System Diagnostic
Run the doctor to analyze your system:

```bash
esim-tm doctor
```

### 3. Interactive Repair
Automatically fix missing or outdated tools:

```bash
esim-tm assist
```

### 4. Machine-Readable Health Check
Generate JSON output for automation or CI:

```bash
esim-tm check --json
```

### 5. Snapshot & Conflict Detection
Save and compare environment state:

```bash
esim-tm snapshot
esim-tm snapshot-diff
```

### 6. Professional Reporting
Generate an HTML diagnostic report:

```bash
esim-tm report
```

### 7. Interactive TUI Dashboard
Monitor system status visually:

```bash
esim-tm tui
```

---

## Command Reference

| Command | Description |
|--------|------------|
| `esim-tm doctor` | Full system diagnostic |
| `esim-tm assist` | Interactive repair assistant |
| `esim-tm check` | Dependency check |
| `esim-tm check --json` | Machine-readable output |
| `esim-tm install <tool>` | Install a specific tool |
| `esim-tm update` | Update installed tools |
| `esim-tm repair` | Auto-fix issues |
| `esim-tm snapshot` | Save environment state |
| `esim-tm snapshot-diff` | Detect environment changes |
| `esim-tm report` | Generate HTML report |
| `esim-tm tui` | Launch interactive dashboard |
| `esim-tm log` | View system logs |

---

## How It Works

The system follows a deterministic pipeline:

**User Command** → **CLI** → **Registry** → **Checker** → **Platform Manager** → **Installer** → **Logger** → **Output**

1.  **CLI**: Parses the user command and flags.
2.  **Registry**: Loads tool definitions from `tools.toml` and `custom_tools.toml`.
3.  **Checker**: Validates tool availability and extracts version strings.
4.  **Platform Manager**: Generates OS-specific installation and repair commands.
5.  **Installer**: Executes fixes using system package managers (winget, choco, apt).
6.  **Logger**: Records internal events to `esim_tm.log`.
7.  **Output**: Renders the final state via CLI (Rich), JSON, or TUI (Textual).

---

## Example Output

```bash
esim-tm doctor
✔ python3        Installed (3.11.5)
✖ ngspice        Not Found
→ Fix: winget install ngspice

✔ git            Installed
⚠ verilator      Outdated
→ Fix: sudo apt install verilator
```

---

## Requirements

-   **Python 3.8+**
-   **Supported Platforms**:
    -   **Windows**: winget / choco / pip
    -   **Linux**: apt / dnf / pip
    -   **macOS**: brew / pip

---

## System Architecture

The project follows a modular, parameter-driven architecture designed for zero global state.

| Module | Responsibility |
| :--- | :--- |
| **`checker.py`** | Diagnostic engine for executable detection. |
| **`health.py`** | Weighted scoring algorithm (Required * 0.7 + Optional * 0.3). |
| **`registry.py`** | Safe merging of core tools and user-defined `custom_tools.toml`. |
| **`platform_mgr.py`** | Normalizes OS-specific paths and manager logic. |
| **`version_utils.py`** | Normalizes non-standard version strings into comparable tuples. |

---

## Local Development Setup

For evaluators wishing to run from source without installation:

```bash
# Clone the repository
git clone https://github.com/mimo-to/eSim-Tool-manager.git
cd eSim-Tool-manager

# Install core UI dependencies
pip install rich textual tomli

# Run the entry point
python run.py doctor
```

---

**© 2026 eSim Tool Manager Project**
