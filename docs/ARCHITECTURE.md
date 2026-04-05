# Architecture Overview

This document explains the high-level architecture of the eSim Tool Manager, its core modules, and its design philosophy.

## Entry Point
*Execution flow of the CLI application.*

**`run.py`** → **`cli.py`** → **Module logic** (`checker`, `installer`, etc.)

---

## Module Mapping
*A guide to the tool's modular structure.*

- **`registry`**: Central source of truth for tool definitions, commands, and requirements (`tools.toml`).
- **`checker`**: Core logic for tool detection, version parsing, and health status (installed/missing/outdated).
- **`installer`**: Executes automated fixes (e.g., `pip install`, `winget install`) based on registry instructions.
- **`snapshot`**: Manages state persistence, JSON storage, and environment comparison logic.
- **`cli`**: The user interface layer, managing subcommands, Rich-formatted output, and global flags.

---

## Why Modular?
*Philosophy behind the design.*

- **Easier Testing**: Each module is self-contained, allowing for isolated unit tests (e.g., test `checker` without a real CLI).
- **Separation of Concerns**: UI logic (`cli.py`) is decoupled from detection logic (`checker.py`), ensuring a clean data flow.
- **Extensibility**: Adding new tool types or repair methods only requires updates to the `registry` and `installer`.
- **System Stability**: Failure in one module (e.g., snaphot JSON corruption) is gracefully handled without crashing the core diagnostic engine.

---

## Data Flow
*How a simple `doctor` command works:*

1. **User** invokes `cmd_doctor`.
2. **CLI** requests all registered tools from the **Registry**.
3. **Checker** iterates through tools, running check commands and parsing results.
4. **Health Logic** scores the environment based on detections.
5. **CLI** formats the data with Rich and displays it to the **User**.
