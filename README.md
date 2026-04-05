# eSim Tool Manager
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![CI](https://github.com/mimo-to/eSim-Tool-manager/actions/workflows/ci.yml/badge.svg)
Automated CLI & TUI tool for managing eSim dependencies across platforms.

## Supported Platforms
- Windows
- Linux
- macOS

## Requirements
- Python 3.9+
- [pipx](https://github.com/pypa/pipx) (recommended)

## Quick Start

Install globally using [pipx](https://github.com/pypa/pipx) (recommended):

```bash
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
esim-tm tui
```

No cloning. No virtual environments. Works instantly.

This installs the tool globally with no virtual environment setup.

**Requires pipx:**
`pip install pipx`

---

### **Overview**
Setting up an eSim development environment is a complex, error-prone process involving dozens of platform-specific tools and Python dependencies. The **eSim Tool Manager** transforms this into a 30-second automated check, providing a production-grade interface for detection, repair, and reporting.

---

### **Key Features**
- **Cross-Platform Support**: Seamless operation on Windows, Linux, and macOS.
- **Intelligent Dependency Checking**: Real-time validation of system binaries and PATH variables.
- **Automated Repair System**: One-command restoration of missing environment tools.
- **Python Package Validation**: Deep-dive checks for internal Python dependency alignment.
- **Interactive TUI Dashboard**: High-fidelity terminal interface built with Textual.
- **Health Scoring System**: Weighted metrics (0-100) to prioritize critical vs. optional tools.
- **Shareable Reports**: Generates professional, dark-themed HTML diagnostic reports.
- **CI/CD Integration**: Automated testing pipeline via GitHub Actions.

## Why This Stands Out
- **Implements 5 out of 6 core requirements** (minimum required: 2)
- **Version-aware intelligent update system** (tuple-based parsing and comparison)
- **Full Textual TUI** with multiple interactive screens
- **HTML report generation** with professional styling and conflict detection
- **Auto-repair system** with safe dry-run support
- **Python dependency checker** that extends beyond system tools
- **Cross-platform support** covering Linux, Windows, and macOS
- **GitHub Actions CI** with multi-version Python testing


---

### **Usage**

#### **CLI Commands**
| Command | Action |
| :--- | :--- |
| `python run.py list` | Detailed table of installed tools and versions. |
| `python run.py dashboard` | View system health score and tool categorization. |
| `python run.py repair` | Automatically install or update missing tools. |
| `python run.py report` | Generate a detailed HTML diagnostic report. |
| `python run.py pkgs` | Validate the Python environment and internal packages. |

Run `python run.py list` to view real-time tool status on your system.

#### **Terminal User Interface (TUI)**
Launch the immersive dashboard with:
```bash
esim-tm tui
```
**Navigation Keys:**
- `1`: Dashboard (System Health Overview)
- `2`: Tools (Categorized Required/Optional List)
- `3`: Logs (Action Audit History)
- `4`: Packages (Python Environment Status)
- `q`: Quit

---

## Detailed Usage Guide

This guide helps you understand how to use the eSim Tool Manager effectively, whether you are a first-time user or a pro.

### A. Quick Example (FAST START)

If you just installed the tool and want to verify your system immediately:

```bash
# 1. Install globally
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git

# 2. Check your status
esim-tm dashboard

# 3. Enter the interactive TUI
esim-tm tui
```

### B. Command Breakdown (CORE PART)

The tool provides a rich set of CLI commands for every scenario.

#### `esim-tm list`
Displays a detailed table of all registered tools, their installation status, and detected versions.

- **Use when:** You need a quick birds-eye view of your environment.
- **Example:** `esim-tm list`

#### `esim-tm check`
Runs a deep-dive scan of your system to verify tool presence and connectivity.

- **Use when:** You suspect a tool is missing or misconfigured in your PATH.
- **Example:** `esim-tm check`

#### `esim-tm dashboard`
Shows your overall **System Health Score** (0-100) and a summary of required/optional tools.

- **Use when:** You want a high-level "pass/fail" check of your setup.
- **Example:** `esim-tm dashboard`

#### `esim-tm repair`
Automatically attempts to fix issues by installing or updating missing dependencies.

- **Use when:** You have missing tools and want the manager to fix them.
- **Example:** `esim-tm repair`

#### `esim-tm update`
Checks for updates to existing tools and performs upgrades where safe.

- **Use when:** You want to ensure you are on the latest verified versions.
- **Example:** `esim-tm update`

#### `esim-tm pkgs`
Validates the internal Python environment and ensures essential libraries (NumPy, SciPy, etc.) are at correct versions.

- **Use when:** CLI tools are working but you encounter Python import errors.
- **Example:** `esim-tm pkgs`

#### `esim-tm report`
Generates a professional, dark-themed HTML diagnostic report.

- **Use when:** You need to share your environment state with colleagues or support.
- **Example:** `esim-tm report`

#### `esim-tm log`
Displays the last 20 actions performed by the tool (installs, checks, repairs).

- **Use when:** You need to audit what changes the tool made to your system.
- **Example:** `esim-tm log`

#### `esim-tm tui`
Launches the full interactive terminal interface.

- **Use when:** You want a modern, mouse-free environment for monitoring.
- **Example:** `esim-tm tui`

### C. Arguments & Flags

#### `--dry-run`
Can be used with the `repair` command to preview what changes **would** be made without actually modifying your system.

- **Why it's useful:** It's a "safety first" feature that lets you see which commands will be executed.
- **Example:** `esim-tm repair --dry-run`

### D. Typical Workflows

#### 1. First-time Setup
New to the project? Follow this flow:
1. `esim-tm check` (See what's missing)
2. `esim-tm repair` (Let the manager fix it)

#### 2. Regular Maintenance
Keep your environment healthy:
1. `esim-tm dashboard` (Rapid health check)
2. `esim-tm update` (Upgrade tools)

#### 3. Debugging Issues
Something feels wrong? Use this combo:
1. `esim-tm repair --dry-run` (Analyze proposed fixes)
2. `esim-tm log` (Check for past failures)

### E. Output Explanation

When you run a command, you will see structured output:
- **Green (✓ OK):** The tool is found and functioning correctly.
- **Red (✗ Missing):** The tool is either not installed or not in your system PATH.
- **Yellow (! Outdated):** The tool is installed but does not meet the minimum version required.

### F. TUI Guide

The TUI (Terminal User Interface) is divided into four main sections:
1. **Dashboard (Key 1):** Real-time health score and status overview.
2. **Tools (Key 2):** A searchable table of all system binaries.
3. **Logs (Key 3):** An audit trail of recent operations.
4. **Packages (Key 4):** Status of the internal Python dependency stack.

### G. Tips (PRO TOUCH)

- **Use pipx:** Installing via `pipx` ensures the Tool Manager doesn't conflict with other projects.
- **Safety First:** Always run `repair --dry-run` if you are on a restricted or sensitive machine.
- **Healthy Habit:** Check your `dashboard` once a week to ensure no environmental drift.

---

### **Project Structure**
- `src/`: Core implementation (logic, TUI, CLI engine).
- `tests/`: Unit test suite covering registry, health, and platform logic.
- `.github/`: CI/CD workflow configuration for automated testing.
- `tools.toml`: Centralized registry for tool metadata.

---

### **Testing & CI**
Quality is maintained through a dedicated test suite using Python's `unittest` framework.
- **Run Tests Locally**: `python -m unittest discover tests`
- **Automated CI**: Every push or PR triggers the `ci.yml` workflow on GitHub Actions to ensure cross-environment stability.


---

## Manual Installation (Optional)

This method is only needed for development or contribution.

```bash
# Clone the repository
git clone https://github.com/mimo-to/eSim-Tool-manager.git

# Navigate to project directory
cd eSim-Tool-manager

# Install dependencies
pip install -r requirements.txt
```
