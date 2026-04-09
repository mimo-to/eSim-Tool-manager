<div align="center">

<h1>eSim Tool Manager</h1>

<p>
    <strong>Automated Tool Management System for eSim Environment</strong>
</p>

<p>
    <em>One command to diagnose, repair, and manage a complete eSim toolchain.</em>
    <br />
    Built with Python, Rich, and Textual.
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.9%2B-blue" alt="Python">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Platforms">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/System_Health-Automated-orange" alt="Status">
    <img src="https://img.shields.io/badge/FOSSEE-Requirement_Mapped-brightgreen" alt="FOSSEE">
</p>

<p>
    <a href="https://github.com/mimo-to/eSim-Tool-manager"><strong>Source Code</strong></a> • 
    <a href="design_document.md"><strong>Design Document</strong></a> • 
    <a href="docs/ARCHITECTURE.md"><strong>Architecture</strong></a>
</p>

</div>

---

> [!IMPORTANT]
> **Prerequisite**: Python 3.9+

## Why This Exists

Setting up a professional eSim environment requires multiple system tools (Ngspice, Verilator, GHDL), complex Python dependencies, and correct PATH configurations. This process is historically error-prone for students and engineers. **eSim Tool Manager** automates this entire lifecycle—from initial discovery to automated repair—ensuring a stable EDA environment with a single command.
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

## Core Command Reference

| Command | Purpose |
| :--- | :--- |
| `doctor` | Full system diagnostic and health check |
| `assist` | Guided repair assistant with auto-recheck |
| `repair` | Batch automated fix for required tools |
| `check --json` | Machine-readable health for CI/CD |
| `snapshot` | Capture environment state baseline |
| `tui` | Interactive visual dashboard |
| `report` | Generate professional HTML diagnostics |

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

## Why It Stands Out

-   **Full FOSSEE Compliance**: Explicitly implements all 6 core requirements (Install, Update, Config, Dependency, UI, Platform).
-   **Adaptive Installer**: Intelligently toggles between `winget`, `choco`, `apt`, `dnf`, and `brew` based on system availability.
-   **Deterministic Matching**: Uses strict keyword and word-boundary matching to prevent false-positive tool detection.
-   **Professional UX**: Seamlessly transitions between CLI, machine-readable JSON, and high-fidelity TUI dashboard.
-   **Engineering Depth**: Feature-rich version engine supporting tuple-based comparison for non-standard EDA version strings.

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
