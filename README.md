<div align="center">

<br />

<h1>eSim Tool Manager</h1>

<p><strong>Diagnose. Repair. Monitor. One command for your entire EDA toolchain.</strong></p>

<p><em>Built with Python · Rich · Textual</em></p>

<br />

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org) [![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=flat-square)](https://github.com/mimo-to/eSim-Tool-manager) [![CI](https://img.shields.io/badge/CI-Passing-238636?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/mimo-to/eSim-Tool-manager/actions) [![Code Style](https://img.shields.io/badge/Style-PEP8-informational?style=flat-square)](https://peps.python.org/pep-0008/)

<br />

[**Quickstart**](#quickstart) · [**Commands**](#command-reference) · [**Architecture**](docs/ARCHITECTURE.md) · [**Design**](design_document.md) · [**Features**](docs/FEATURES.md) · [**Workflows**](docs/USAGE.md)

<br />

</div>

---

## The Problem

Setting up an EDA environment by hand is painful. You need the right versions of Ngspice, Verilator, GHDL, KiCad, and a specific set of Python packages — all on different platforms with conflicting PATH behaviours and non-standard version strings. A single misconfigured tool silently breaks simulation runs.

`esim-tm` is a purpose-built manager that handles the entire lifecycle: discovery, installation, version validation, repair, and regression detection. It works on Linux, Windows, and macOS without changing how you work.

---

## What It Does

```
esim-tm doctor
```

```
┌─────────────────────────────┐
│      eSim Tool Manager      │
└─────────────────────────────┘

Tools
✓ Python 3      — OK  (Required)   v3.11.5
✓ pip           — OK  (Required)   v23.2
✓ Git           — OK  (Required)   v2.42.0
✗ Ngspice       — Not found  (Required)
    → Fix: sudo apt-get install -y ngspice
⚠ Verilator     — Outdated  (Optional)
    → Fix: sudo apt-get upgrade -y verilator

Python Packages
✓ numpy         — OK
✓ matplotlib    — OK
✗ pyqt5         — Not found
    → Fix: pip install pyqt5

eSim Readiness: 71/100 (Good)
```

---

## Quickstart

**Prerequisites:** Python 3.9+

### Install via pipx (recommended)

```bash
python -m pip install pipx
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
```

### Install from source

```bash
git clone https://github.com/mimo-to/eSim-Tool-manager.git
cd eSim-Tool-manager
pip install rich textual "tomli>=2.0.0"
python run.py doctor
```

### First run

```bash
# 1. Check what's broken
esim-tm doctor

# 2. Fix it interactively
esim-tm assist

# 3. Save a baseline snapshot
esim-tm snapshot

# 4. Next time — see what changed
esim-tm snapshot-diff
```

---

## Command Reference

| Command                  | What it does                                                    |
| ------------------------ | --------------------------------------------------------------- |
| `esim-tm doctor`         | Full system diagnostic — tools + Python packages + health score |
| `esim-tm assist`         | Interactive step-by-step repair assistant                       |
| `esim-tm repair`         | Batch auto-fix for all missing required tools                   |
| `esim-tm check`          | Dependency status table                                         |
| `esim-tm check --json`   | Machine-readable JSON output for CI/CD                          |
| `esim-tm install <tool>` | Install a specific tool by ID                                   |
| `esim-tm update`         | Update all installed tools                                      |
| `esim-tm update <tool>`  | Update a specific tool                                          |
| `esim-tm snapshot`       | Save current environment state to disk                          |
| `esim-tm snapshot-diff`  | Compare current state against last snapshot                     |
| `esim-tm report`         | Generate a full HTML diagnostic report                          |
| `esim-tm tui`            | Open the interactive terminal dashboard                         |
| `esim-tm list`           | Show all tracked tools with install status                      |
| `esim-tm pkgs`           | Show Python package dependency status                           |
| `esim-tm log`            | View last 20 log entries                                        |
| `esim-tm dashboard`      | Show health score summary                                       |
| `esim-tm setup`          | Full environment bootstrap (doctor + assist + verify)           |
| `esim-tm setup-help`     | Show recommended command workflow                               |

---

## How the Pipeline Works

Every command follows the same deterministic execution path:

```
User Input
    │
    ▼
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────────┐
│   CLI   │────▶│ Registry │────▶│ Checker │────▶│ Version Utils│
│(Argparse│     │(TOML +   │     │(subprocess     │(Tuple-based  │
│ Dispatch│     │ custom)  │     │ + shutil)│     │ semver parse)│
└─────────┘     └──────────┘     └─────────┘     └──────────────┘
                                                         │
                    ┌────────────────────────────────────┘
                    ▼
             ┌────────────┐     ┌──────────────┐     ┌──────────┐
             │   Health   │────▶│Platform Mgr  │────▶│Installer │
             │  Scoring   │     │(winget/apt/  │     │(search + │
             │ (weighted) │     │ brew/dnf)    │     │ install) │
             └────────────┘     └──────────────┘     └──────────┘
                    │                                      │
                    ▼                                      ▼
             ┌────────────┐                         ┌────────┐
             │   Output   │                         │ Logger │
             │(Rich/TUI/  │                         │(.log)  │
             │  JSON/HTML)│                         └────────┘
             └────────────┘
```

---

## System Architecture Overview

```
src/
├── cli.py           Command dispatcher + all command implementations
├── tui.py           Textual TUI — 4-screen dashboard application
├── registry.py      TOML loader with safe custom tool merging
├── checker.py       Subprocess-based tool discovery + version extraction
├── installer.py     Multi-manager install engine with search validation
├── platform_mgr.py  OS detection + package manager command generation
├── health.py        Weighted scoring: Required×0.7 + Optional×0.3
├── repair.py        Batch repair orchestration
├── pip_checker.py   Python package audit via importlib.metadata
├── version_utils.py Regex + tuple-based semantic version comparison
├── snapshot.py      JSON state capture + differential analysis
├── report.py        HTML report generator
├── logger.py        Persistent timestamped event log
├── config.py        TOML-based user config with auto-defaults
├── constants.py     Centralized URLs — no circular imports
└── tools.toml       Core tool registry (extensible)
```

Full architecture documentation: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Tracked Tools

| Tool          | Role                            | Required |
| ------------- | ------------------------------- | :------: |
| **Ngspice**   | Circuit simulation engine       |    ✓     |
| **Python 3**  | Runtime                         |    ✓     |
| **pip**       | Package manager                 |    ✓     |
| **Git**       | Version control                 |    ✓     |
| **KiCad**     | PCB + schematic design          |    —     |
| **Verilator** | Verilog/SystemVerilog simulator |    —     |
| **GHDL**      | VHDL simulator                  |    —     |

Python packages tracked: `numpy`, `scipy`, `matplotlib`, `PyQt5`, `pyserial`, `requests`, `Pillow`

---

## Adding Custom Tools

Drop a `custom_tools.toml` file at `~/.esim_tool_manager/custom_tools.toml`:

```toml
[my_tool]
name        = "My Custom Tool"
check_cmd   = "mytool --version"
required    = false
min_version = "1.0"
apt_pkg     = "my-tool"
```

The registry merges custom tools safely — ID collisions and invalid entries are logged and skipped without interrupting normal operation.

---

## CI/CD Integration

```bash
# Fail the pipeline if required tools are missing
esim-tm check --json > health.json
python -c "
import json, sys
data = json.load(open('health.json'))
missing = [t for t in data if t['required'] and not t['installed']]
if missing:
    print('Missing required tools:', [t['name'] for t in missing])
    sys.exit(1)
"
```

---

## Health Scoring

| Score | Status        | Meaning                                  |
| ----- | ------------- | ---------------------------------------- |
| 100   | **Excellent** | All tools present, all versions current  |
| 70–99 | **Good**      | Required tools OK, some optional missing |
| 40–69 | **Partial**   | One or more required tools missing       |
| 0–39  | **Critical**  | Core toolchain non-functional            |

Formula: `score = (required_installed / required_total × 70) + (optional_installed / optional_total × 30)`

PATH issues and version conflicts are counted as failures in this formula.

---

## Documentation

| Document                                     | Contents                                                     |
| -------------------------------------------- | ------------------------------------------------------------ |
| [design_document.md](design_document.md)     | Architecture decisions, module breakdown, failure taxonomy   |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Component diagrams, execution flow, version engine internals |
| [docs/FEATURES.md](docs/FEATURES.md)         | Full feature reference with implementation details           |
| [docs/USAGE.md](docs/USAGE.md)               | Real-world workflows with annotated command sequences        |

---

## Development

```bash
git clone https://github.com/mimo-to/eSim-Tool-manager.git
cd eSim-Tool-manager

# Run tests
python -m unittest discover tests

# Run a specific command without installing
python run.py doctor
python run.py check --json
```

Tests cover: version utils, health scoring, platform detection, registry loading, and the checker engine.

---

<div align="center">

Built with [Rich](https://github.com/Textualize/rich) · [Textual](https://github.com/Textualize/textual) · Python 3.9+

</div>
