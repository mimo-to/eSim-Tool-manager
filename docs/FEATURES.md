# Features — eSim Tool Manager

> **Related:** [README](../README.md) · [Architecture](ARCHITECTURE.md) · [Usage Workflows](USAGE.md) · [Design Document](../design_document.md)

---

## Table of Contents

- [Features — eSim Tool Manager](#features--esim-tool-manager)
  - [Table of Contents](#table-of-contents)
  - [1. Doctor — Full System Diagnostic](#1-doctor--full-system-diagnostic)
  - [2. Assist — Interactive Repair](#2-assist--interactive-repair)
  - [3. Repair — Batch Auto-Fix](#3-repair--batch-auto-fix)
  - [4. Health Scoring](#4-health-scoring)
  - [5. Check — Dependency Audit](#5-check--dependency-audit)
  - [6. Snapshot — Environment Regression Detection](#6-snapshot--environment-regression-detection)
  - [7. TUI Dashboard](#7-tui-dashboard)
  - [8. HTML Report](#8-html-report)
  - [9. Logging](#9-logging)
  - [10. Custom Tool Registry](#10-custom-tool-registry)
  - [11. CI/CD Integration](#11-cicd-integration)
  - [12. Cross-Platform Package Management](#12-cross-platform-package-management)

---

## 1. Doctor — Full System Diagnostic

```bash
esim-tm doctor
esim-tm doctor --verbose
```

The `doctor` command is the primary entry point for diagnosing an eSim environment. It performs a full scan in a single pass and produces an annotated, color-coded report.

**What it checks:**

| Category        | What                                                                           |
| --------------- | ------------------------------------------------------------------------------ |
| System tools    | All tools in the registry — whether present, in PATH, and at the right version |
| Python packages | All required Python dependencies via `importlib.metadata`                      |
| Health score    | Weighted readiness score (0–100)                                               |
| Fix commands    | Platform-specific one-liner for each problem, auto-detected                    |

**Output structure:**

```
Tools
✓ Python 3   — OK  (Required)
✓ pip        — OK  (Required)
✗ Ngspice    — Not found  (Required)
    → Fix: sudo apt-get install -y ngspice
⚠ Verilator  — Outdated  (Optional)
    → Fix: sudo apt-get upgrade -y verilator
! Git         — Not in PATH  (Required)
    → Fix: Add tool to system PATH

Python Packages
✓ numpy      — OK
✗ pyqt5      — Not found
    → Fix: pip install pyqt5

Bulk Fix:
pip install pyqt5 pyserial

eSim Readiness: 68/100 (Partial)
```

**Verbose mode** (`--verbose`) prints each tool and package as it is checked, showing intermediate state before the final table.

**Environment detection:** The fix commands shown for Python packages adapt to the detected environment:

- `pipx` environment → `pipx inject esim-tool-manager <package>`
- virtualenv → plain `pip install`
- Multiple missing packages → bulk fix command instead of per-package lines

---

## 2. Assist — Interactive Repair

```bash
esim-tm assist
```

`assist` is a guided repair session. It walks through every problematic tool one at a time, offering contextual options for each.

**Menu per tool:**

```
╭─ Tool Assistance (2/4) ─╮
│ Ngspice                  │
│ Status: Not found        │
╰──────────────────────────╯

  1. Auto-install (Try automatic repair)
  2. Open official installation guide in browser
  3. Show manual installation steps
  4. Re-check status now
  5. Skip this tool
  a. Skip all remaining tools
  q. Quit assistant
```

**What each option does:**

| Option       | Behaviour                                                                                                         |
| ------------ | ----------------------------------------------------------------------------------------------------------------- |
| Auto-install | Runs the full search-validate-install pipeline. Shows which package manager was used. Prompts for re-check after. |
| Open guide   | Calls `webbrowser.open()` with the official download/install URL for the tool.                                    |
| Manual steps | Prints a numbered, platform-specific install walkthrough inline.                                                  |
| Re-check     | Runs a live check right now. If now healthy, marks the tool as fixed and advances.                                |
| Skip         | Marks this tool as skipped, advances to the next.                                                                 |
| Skip all     | Marks all remaining tools as skipped and jumps to summary.                                                        |

**PATH hint:** When a tool shows `path_issue=True` (installed but not in PATH), a contextual hint is displayed before the menu:

```
💡 Hint: The tool appears to be installed but your terminal can't find it.
   Try adding its folder to your system PATH variable.
```

**Guaranteed summary:** Regardless of how the session ends — normal completion, skip-all, or Ctrl+C — the final summary always prints:

```
╔══════════════════════════╗
║ Assistant Summary Report ║
╚══════════════════════════╝

✓ SUCCESSFULLY INSTALLED / FIXED
  • Ngspice
  • Git

⚠ SKIPPED DURING ASSIST
  • Verilator

✗ REMAINING ISSUES
  (none)

Use 'esim-tm doctor' to verify all system dependencies.
```

---

## 3. Repair — Batch Auto-Fix

```bash
esim-tm repair
esim-tm repair --dry-run
```

`repair` is the non-interactive counterpart to `assist`. It scans the system, presents a summary of what needs fixing, asks for confirmation, then attempts automated fixes for everything at once.

**Dry run mode** prints what would be done without executing anything.

**What it fixes:**

- Missing required tools (automatic install via best available manager)
- Missing optional tools (listed but attempted)
- Missing Python packages (via `pip install`)

**Output:**

```
┌─────────────────────────────────────────────┐
│              Repair Summary                 │
├─────────────────────────┬───────────────────┤
│ Missing Required        │ ngspice, git      │
│ Missing Optional        │ verilator         │
└─────────────────────────┴───────────────────┘

Proceed with repair? [y/n]: y

┌────────────┬────────┬───────────────┐
│ Item       │ Type   │ Result        │
├────────────┼────────┼───────────────┤
│ ngspice    │ Tool   │ ✓ Fixed       │
│ git        │ Tool   │ ✗ Failed      │
│ verilator  │ Tool   │ ! Skipped     │
│ pyqt5      │ Python │ ✓ Installed   │
└────────────┴────────┴───────────────┘
```

A tool is skipped (not failed) when no package mapping exists for it in the registry for the current platform.

---

## 4. Health Scoring

```bash
esim-tm dashboard
```

The health score is a single number (0–100) reflecting the current state of the entire toolchain.

**Formula:**

```
score = (required_ok / required_total × 70)
      + (optional_ok / optional_total × 30)
```

A tool contributes to `_ok` only if it is installed, in PATH, and at or above the minimum version. PATH problems and version conflicts are treated as failures.

| Score | Status                              |
| ----- | ----------------------------------- |
| 100   | Excellent — full readiness          |
| 70–99 | Good — required tools healthy       |
| 40–69 | Partial — required tools missing    |
| 0–39  | Critical — toolchain non-functional |

The score appears at the bottom of every `doctor` run and is the primary metric in the `dashboard` and `tui` views.

---

## 5. Check — Dependency Audit

```bash
esim-tm check
esim-tm check ngspice
esim-tm check --json
esim-tm check ngspice --json
```

`check` is a lighter version of `doctor` — no health score, no fix commands, just a status table.

The `--json` flag outputs machine-readable results to stdout:

```json
[
  {
    "id": "ngspice",
    "name": "Ngspice",
    "installed": false,
    "path_issue": false,
    "version": null,
    "required": true,
    "min_version": "37",
    "conflict": false
  },
  ...
]
```

This output is stable across versions and designed for scripting and CI integration.

---

## 6. Snapshot — Environment Regression Detection

```bash
esim-tm snapshot
esim-tm snapshot-diff
```

**Snapshot** captures the complete tool + package state to `~/.esim_tool_manager/snapshot.json` with a timestamp.

**Snapshot-diff** compares the current live state against the last saved snapshot and shows what changed:

```
New Issues:
 - Verilator (now Problem)
 - matplotlib (now Problem)

Fixed Issues:
 - Ngspice (now OK)
```

Use this after a system update to immediately identify what broke. The intended workflow:

```bash
# After verifying everything works:
esim-tm snapshot

# Next week, after a system update:
esim-tm snapshot-diff
```

---

## 7. TUI Dashboard

```bash
esim-tm tui
```

A full-screen terminal UI with four views:

| Key | Screen    | Content                                                            |
| --- | --------- | ------------------------------------------------------------------ |
| `1` | Dashboard | Health score, required/optional counts                             |
| `2` | Tools     | DataTable of all tracked tools with status, version, conflict flag |
| `3` | Logs      | Last 10 log entries                                                |
| `4` | Packages  | DataTable of all Python packages                                   |
| `q` | —         | Quit                                                               |

Each screen performs a live scan when mounted, so switching tabs gives you a fresh read.

The Tools screen groups entries by required/optional with section headers:

```
 Tool         Status   Version  Required  Conflict
─────────────────────────────────────────────────
 Required Tools
 Python 3     ✓ OK     3.11.5   Yes
 pip          ✓ OK     23.2     Yes
 Ngspice      ✗ Missing —       Yes
─────────────────────────────────────────────────
 Optional Tools
 KiCad        ✓ OK     8.0.3    No
 Verilator    ✓ OK     5.026    No
```

---

## 8. HTML Report

```bash
esim-tm report
```

Generates a self-contained HTML file at `~/.esim_tool_manager/health_report.html`.

The report uses a GitHub-dark color scheme and includes:

- Health score badge (color-coded green/yellow/red)
- Required / optional / Python package counts
- Full tool status table with version and required columns
- Full Python package table
- Timestamp

The output path is printed after generation so it can be opened directly or attached to a report.

---

## 9. Logging

```bash
esim-tm log
```

All diagnostic and installation actions are logged to `~/.esim_tool_manager/esim_tm.log` with timestamps.

Format:

```
[2026-04-10 14:23:01] CHECK ngspice FOUND
[2026-04-10 14:23:02] CHECK verilator NOT_FOUND
[2026-04-10 14:23:10] INSTALL ngspice SUCCESS (via apt)
[2026-04-10 14:23:15] UPDATE kicad FAILED
[2026-04-10 14:23:16] REGISTRY custom_tools.toml WARNING_INVALID
```

The `log` command shows the last 20 entries with color coding:

- Green → `SUCCESS`, `FOUND`
- Red → `FAILED`
- Yellow → `ATTEMPT`

---

## 10. Custom Tool Registry

Drop a `custom_tools.toml` file at `~/.esim_tool_manager/custom_tools.toml` to add tools outside the core registry.

**Minimal entry:**

```toml
[openroad]
name      = "OpenROAD"
check_cmd = "openroad -version"
```

**Full entry:**

```toml
[openroad]
name        = "OpenROAD"
check_cmd   = "openroad -version"
required    = false
min_version = "2.0"
apt_pkg     = "openroad"
dnf_pkg     = "openroad"
brew_pkg    = "openroad"
version_pattern = "(\\d+\\.\\d+)"
homepage    = "https://openroad.readthedocs.io"
```

Custom tools participate in all commands — `doctor`, `assist`, `check`, health scoring, snapshots, and the TUI.

**Merge rules:**

- ID already exists in core registry → skipped (logged as `WARNING_CONFLICT`)
- `name` or `check_cmd` absent → skipped (logged as `WARNING_INVALID`)
- `required` absent → defaults to `false`

---

## 11. CI/CD Integration

`esim-tm check --json` produces stable JSON suitable for use in pipelines:

```yaml
# GitHub Actions example
- name: Verify EDA environment
  run: |
    pip install rich textual "tomli>=2.0.0"
    python run.py check --json > health.json
    python - <<'EOF'
    import json, sys
    data = json.load(open("health.json"))
    missing = [t["name"] for t in data if t["required"] and not t["installed"]]
    if missing:
        print(f"Missing required tools: {missing}")
        sys.exit(1)
    EOF
```

The JSON schema is documented in [ARCHITECTURE.md — Data Structures](ARCHITECTURE.md#4-data-structures).

---

## 12. Cross-Platform Package Management

`platform_mgr.py` detects all available package managers at runtime and provides a unified command interface. No configuration is needed.

| Platform              | Detected Managers | Priority |
| --------------------- | ----------------- | -------- |
| Linux (Debian/Ubuntu) | `apt`             | 1st      |
| Linux (Fedora/RHEL)   | `dnf`             | 1st      |
| macOS                 | `brew`            | 1st      |
| Windows               | `winget`          | 1st      |
| Windows               | `choco`           | 2nd      |

When multiple managers are available (e.g., Windows with both winget and choco), the installer tries them in order until one succeeds.

The `tools.toml` registry stores per-manager package names:

```toml
[ngspice]
apt_pkg    = "ngspice"
dnf_pkg    = "ngspice"
brew_pkg   = "ngspice"
choco_pkg  = "ngspice"
winget_pkg = ""          # empty = not available via winget
```

An empty `winget_pkg` causes the installer to skip winget for that tool and fall through to the next manager or manual steps.
