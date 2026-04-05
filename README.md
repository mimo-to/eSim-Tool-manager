# eSim Tool Manager
**A cross-platform CLI tool to detect, fix, and monitor eSim development environments.**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![CI](https://github.com/mimo-to/eSim-Tool-manager/actions/workflows/ci.yml/badge.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

### One Glance Summary
**Detect → Fix → Monitor eSim environments in one CLI**

| Status | Meaning |
|--------|---------|
| ✓ OK | Working correctly |
| ✗ Missing | Not installed |
| ! Outdated | Needs update |

The eSim Tool Manager provides a unified interface to ensure your electronic simulation tools and Python dependencies are correctly installed, configured on your PATH, and ready for use.

---

## Install in one line

```bash
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
```

---


## Problem vs. Solution

### The Problem
Setting up a complete eSim environment (Ngspice, KiCad, Verilator, etc.) is error-prone. Manual installation leads to:
- **Version mismatches** between tools.
- **PATH configuration errors** that break simulations.
- **Missing Python dependencies** required for analysis.
- **Fragmented workflows** using multiple package managers (pip, winget, apt).

### The Solution
eSim Tool Manager automates the "sanity check" process. It provides:
- **One-command diagnostics** (`doctor`).
- **Automated repairs** for missing tools.
- **Environment baselining** (`snapshot`) to detect unwanted system changes.

---

## Who is this for?

- **Students**: Set up your eSim environment in minutes without manual troubleshooting.
- **Developers**: Manage complex toolchains and ensure consistency across development machines.
- **Contributors**: Rapidly identify and fix environment bottlenecks before committing 
  code.

---

## Zero Config Start

Get started instantly—no setup required:
- **No configuration files** needed to begin.
- **No environment variables** to set manually.
- **Works out of the box** on Windows, Linux, and macOS.

Simply run:
```bash
python run.py doctor
```

---

## Quick Demo Flow (30 sec)

1. **Diagnose**: `python run.py doctor` (Find out what's missing)
2. **Fix**: `python run.py repair --dry-run` (Preview the automated fixes)
3. **Baseline**: `python run.py snapshot` (Save your known-good state)
4. **Monitor**: `python run.py snapshot-diff` (Check for system regressions)

---

## Command Table (Quick Reference)

| Command         | Purpose                                     |
|-----------------|---------------------------------------------|
| `doctor`        | Full system diagnostics and health scoring. |
| `repair`        | Automated fix for missing tools/packages.   |
| `snapshot`      | Save current environment state to JSON.    |
| `snapshot-diff` | Compare current state vs. saved snapshot.  |
| `list`          | Quick overview of all registered tools.     |
| `setup-help`    | Interactive onboarding and workflow guide.  |

---

## Safe Operations

Built for engineering reliability:
- **Dry-Run Support**: Preview every repair action before it modifies your system.
- **JSON-Safe Output**: All diagnostic data can be exported to machine-readable JSON for automation.
- **Non-Destructive**: The tool never deletes system files or modifies your PATH without explicit registry instructions.

---

## Example Output

**Example output from real system (`doctor`):**

```text
Tools
✗ Ngspice — Not found (Required)
    → Fix: Install manually (no package mapping found)
✗ KiCad — Not found (Optional)
✓ Python 3 — OK (Required)
✓ pip — OK (Required)
✓ Git — OK (Required)

Python Packages
✓ numpy — OK
✓ matplotlib — OK
✗ pyqt5 — Not found
    → Fix: pip install pyqt5

eSim Readiness: 52/100 (Partial)
```

---

## Key Highlights

- **Prioritized Health Engine**: Differentiates between critical `Required` tools and `Optional` enhancements.
- **Rich TUI**: Beautiful, high-contrast terminal interface for clear visibility.
- **State Tracking**: Detect when a system update or manual uninstallation breaks your toolchain.
- **Extensibility**: Add your own custom tools via a simple `custom_tools.toml` file.

---

## Architecture Overview

The tool is split into five core modules to ensure stability and extensibility:
- **Registry**: Central source of truth for tool definitions.
- **Checker**: Hardened detection logic for binary versions and PATHs.
- **Installer**: Executes repairs via ecosystem-native package managers.
- **Snapshot**: Manages JSON-based environment persistence.
- **CLI**: The interface layer for user interaction and global flags.

*For details, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).*

---

## Why This Stands Out

Unlike generic system checkers, eSim Tool Manager is specifically tuned for the **Electronic Simulation ecosystem**. It understands the nuances of simulation dependencies, supports additive diagnostics via `--verbose`, and is designed to be automation-ready for high-stakes development teams.

---

*Detailed documentation can be found in the [docs/](docs/) directory.*
