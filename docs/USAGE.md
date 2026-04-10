# Usage Workflows — eSim Tool Manager

> **Related:** [README](../README.md) · [Features](FEATURES.md) · [Architecture](ARCHITECTURE.md) · [Design Document](../design_document.md)

---

## Table of Contents

1. [Installation](#1-installation)
2. [First Run](#2-first-run)
3. [Workflow: Fresh Machine Setup](#3-workflow-fresh-machine-setup)
4. [Workflow: Recovering a Broken Environment](#4-workflow-recovering-a-broken-environment)
5. [Workflow: Routine Maintenance](#5-workflow-routine-maintenance)
6. [Workflow: CI/CD Pipeline Gating](#6-workflow-cicd-pipeline-gating)
7. [Workflow: Extended TUI Monitoring](#7-workflow-extended-tui-monitoring)
8. [Command Quick Reference](#8-command-quick-reference)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Installation

### Option A — pipx (recommended)

Installs `esim-tm` as an isolated global command. Does not interfere with any existing Python environment.

```bash
python -m pip install pipx
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
```

Verify:

```bash
esim-tm --help
```

### Option B — from source (for development or evaluation)

```bash
git clone https://github.com/mimo-to/eSim-Tool-manager.git
cd eSim-Tool-manager
pip install rich textual "tomli>=2.0.0"
python run.py --help
```

When running from source, replace `esim-tm` with `python run.py` in all commands below.

---

## 2. First Run

On the very first invocation, you will see:

```
Welcome to eSim Tool Manager

Run:
  esim-tm doctor

to check your system setup.
```

This message appears once. After that, every invocation goes directly to the requested command.

---

## 3. Workflow: Fresh Machine Setup

**Goal:** Go from a clean OS install to a working eSim environment.

```
Step 1: Diagnose
  esim-tm doctor

Step 2: Fix interactively
  esim-tm assist

Step 3: Verify
  esim-tm doctor

Step 4: Save a known-good baseline
  esim-tm snapshot
```

### Step-by-step

**Step 1 — Run the diagnostic**

```bash
esim-tm doctor
```

This shows you exactly what is missing, what is outdated, and what is misconfigured. Every problem comes with a suggested fix command tailored to your platform.

Read the output carefully before proceeding. If all required tools show `✓ OK`, you are done.

**Step 2 — Fix what's missing**

```bash
esim-tm assist
```

The assistant walks through each problem in sequence. For each tool:

- If your platform supports automatic installation, choose **Auto-install**
- If auto-install is not available, choose **Open installation guide** to open the official download page
- If you prefer step-by-step instructions in the terminal, choose **Manual steps**
- After installing anything, choose **Re-check** to confirm it worked before moving on

Example session for a missing Ngspice on Linux:

```
╭─ Tool Assistance (1/2) ─╮
│ Ngspice                  │
│ Status: Not found        │
╰──────────────────────────╯

  1. Auto-install (Try automatic repair)
  2. Open official installation guide in browser
  3. Show manual installation steps
  4. Re-check status now
  5. Skip this tool

Select an option: 1

Attempting auto-install for Ngspice...
Installing Ngspice via apt...
Installation attempted successfully (via apt).

Re-check status now? [y/n]: y
✓ Fixed! Tool is now healthy.
```

**Step 3 — Verify**

```bash
esim-tm doctor
```

You should see all required tools at `✓ OK` and a score of 100 (Excellent).

**Step 4 — Save baseline**

```bash
esim-tm snapshot
```

```
Snapshot saved → /home/user/.esim_tool_manager/snapshot.json
```

This records the current state. If anything breaks later, `snapshot-diff` will show exactly what changed.

---

## 4. Workflow: Recovering a Broken Environment

**Goal:** Restore a working state after something stopped working — after a system update, package purge, or accidental deletion.

```
Step 1: Identify what changed
  esim-tm snapshot-diff

Step 2a: Auto-fix (quick)
  esim-tm repair

Step 2b: Guided fix (thorough)
  esim-tm assist

Step 3: Verify
  esim-tm doctor

Step 4: Update baseline
  esim-tm snapshot
```

**Step 1 — See what broke**

```bash
esim-tm snapshot-diff
```

```
New Issues:
 - Ngspice (now Problem)
 - matplotlib (now Problem)

Fixed Issues:
 - (none)
```

This tells you exactly which tools were working before and have since broken, without requiring you to remember the previous state.

**Step 2a — Batch auto-fix**

```bash
esim-tm repair
```

```
┌─────────────────────────────────────────────┐
│              Repair Summary                 │
├─────────────────────────┬───────────────────┤
│ Missing Required        │ ngspice           │
└─────────────────────────┴───────────────────┘

Proceed with repair? [y/n]: y

 ngspice    Tool    ✓ Fixed
 matplotlib Python  ✓ Installed
```

**Step 2b — Guided fix (if auto-fix fails)**

```bash
esim-tm assist
```

Use this when automatic installation fails — it offers download links and manual steps as fallback paths.

---

## 5. Workflow: Routine Maintenance

**Goal:** Keep the environment healthy over time without breaking anything.

### Weekly check

```bash
esim-tm doctor
```

If the score drops or any `⚠ Outdated` entries appear, run:

```bash
esim-tm update
```

This updates all installed tools that have a newer version available.

### After a system update

```bash
esim-tm snapshot-diff
```

Compare against your last known-good snapshot. Address any new issues with `assist` or `repair`.

### Update the baseline after maintenance

```bash
esim-tm snapshot
```

---

## 6. Workflow: CI/CD Pipeline Gating

**Goal:** Block a CI build if the EDA environment is missing required tools.

```yaml
# .github/workflows/env-check.yml
name: Environment Check

on: [push, pull_request]

jobs:
  check-tools:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install esim-tm
        run: |
          pip install rich textual "tomli>=2.0.0"

      - name: Check required tools
        run: |
          python run.py check --json > health.json
          python - <<'EOF'
          import json, sys
          data = json.load(open("health.json"))
          missing = [t["name"] for t in data if t["required"] and not t["installed"]]
          if missing:
              print("Missing required tools:", missing)
              sys.exit(1)
          print("All required tools present.")
          EOF
```

### Using check output in a script

```bash
# Get the JSON
esim-tm check --json > health.json

# Count missing required tools
python -c "
import json
data = json.load(open('health.json'))
missing = [t for t in data if t['required'] and not t['installed']]
print(f'{len(missing)} required tools missing')
for t in missing:
    print(f'  - {t[\"name\"]}')
"
```

### Audit trail

All actions taken by `esim-tm` during a CI run are written to `~/.esim_tool_manager/esim_tm.log`. Review with:

```bash
esim-tm log
```

---

## 7. Workflow: Extended TUI Monitoring

**Goal:** Watch system state in real-time during a long development session.

```bash
esim-tm tui
```

The TUI opens to the Dashboard screen showing the overall health score. Use number keys to switch views:

| Key | View                  |
| --- | --------------------- |
| `1` | Health dashboard      |
| `2` | Tool status table     |
| `3` | Recent log entries    |
| `4` | Python package status |
| `q` | Quit                  |

Switching to any screen triggers a fresh live scan. If you install something in another terminal, switch away and back to any screen to see the updated status.

---

## 8. Command Quick Reference

```
DIAGNOSIS
  esim-tm doctor              Full diagnostic + health score
  esim-tm doctor --verbose    Verbose: show each tool as it is checked
  esim-tm check               Dependency table
  esim-tm check <tool>        Single tool check
  esim-tm check --json        Machine-readable output
  esim-tm list                All tools with install status
  esim-tm pkgs                Python package status
  esim-tm dashboard           Health score summary

REPAIR
  esim-tm assist              Interactive guided repair
  esim-tm repair              Batch auto-fix
  esim-tm repair --dry-run    Preview without executing
  esim-tm install <tool>      Install specific tool
  esim-tm update              Update all tools
  esim-tm update <tool>       Update specific tool

STATE
  esim-tm snapshot            Save current environment state
  esim-tm snapshot-diff       Compare current vs last snapshot

MONITORING
  esim-tm tui                 Interactive terminal dashboard
  esim-tm report              Generate HTML diagnostic report
  esim-tm log                 View last 20 log entries

HELP
  esim-tm setup               Full bootstrap (doctor + assist + verify)
  esim-tm setup-help          Show recommended workflow
  esim-tm --help              Global help
  esim-tm <command> --help    Command-specific help
```

---

## 9. Troubleshooting

### "No supported package manager found"

Your system does not have `apt`, `dnf`, `brew`, `winget`, or `choco` installed or on PATH.

- **Linux:** Confirm `which apt-get` or `which dnf` returns a path
- **macOS:** Install Homebrew: `https://brew.sh`
- **Windows:** Install winget (from Microsoft Store) or Chocolatey: `https://chocolatey.org`

Use the **Manual steps** option in `assist` as a fallback.

---

### Tool shows "Not in PATH" even after installing

The binary directory for the tool is not in your `$PATH` / `%PATH%`.

**Linux/macOS:**

```bash
# Find where the tool installed
which ngspice          # or: find / -name "ngspice" 2>/dev/null

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/tool/bin"
source ~/.bashrc
```

**Windows:**

1. Search for "Environment Variables" in the Start menu
2. Edit the `Path` variable under System variables
3. Add the directory containing the tool's `.exe`
4. Restart your terminal

Then run `esim-tm doctor` again to confirm the fix.

---

### `esim-tm` command not found after pipx install

```bash
# Check if pipx bin directory is on PATH
pipx ensurepath

# Then reload your shell
source ~/.bashrc   # or open a new terminal
```

---

### Python packages show missing but they are installed

This can happen when `esim-tm` is running in a different Python environment than where the packages are installed.

Check:

```bash
which python3
which esim-tm
python3 -c "import numpy; print(numpy.__version__)"
```

If the environments differ, install packages into the same environment as `esim-tm`, or use the pipx inject path shown in `doctor` output.

---

### Log file grows too large

The log file is at `~/.esim_tool_manager/esim_tm.log` and is append-only.

```bash
# Clear the log
> ~/.esim_tool_manager/esim_tm.log

# Or rotate it
mv ~/.esim_tool_manager/esim_tm.log ~/.esim_tool_manager/esim_tm.log.bak
```

---

### Running `esim-tm` in a script without interactive prompts

Use `--json` for machine-readable output. For repair without confirmation prompts, set `auto_confirm = true` in `~/.esim_tool_manager/config.toml`:

```toml
[general]
auto_confirm = true
```

Or use `repair` directly — it asks once for confirmation and proceeds.
