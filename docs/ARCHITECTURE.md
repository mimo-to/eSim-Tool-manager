# eSim-tm Architecture Overview

This document describes the internal structure and logic of the eSim Tool Manager (`esim-tm`).

---

### **1. System Flow Diagram (ASCII)**

```text
User Commands (esim-tm)
  ↓
CLI Layer (src/cli.py) ←──────┐
  ↓ (args)                    │
Registry (src/tools.toml)      │
  ↓ (tool_data)                │
Checker (src/checker.py) ──────┘
  ↓ (results)
Action Planner (src/repair.py)
  ↓ (fix_steps)
Installer (src/installer.py)
  ↓ (subprocess)
System Changes (Success/Fail)
```

---

### **2. Core Modules**

-   **CLI (src/cli.py)**: The entry point. Handles argument parsing, user interaction, and high-level command logic.
-   **Registry (src/tools.toml)**: The static configuration for all eSim-related tools (name, version, packages, links).
-   **Checker (src/checker.py)**: The diagnostic heart. Runs platform-specific commands to verify a tool's existence and health.
-   **Installer (src/installer.py)**: A safe wrapper for system-level package managers (WinGet, APT, Brew) with built-in timeouts.
-   **Snapshot (src/snapshot.py)**: State-tracking logic for environment captures and diffing.

---

### **3. The Assist System (State Machine)**

The `esim-tm assist` command is built around a robust state machine that guarantees a non-dead-end UX:

1.  **Discovery Phase**: Scans the system using `checker.check_all()`.
2.  **Partitioning**: Divides tools into `Installed`, `Skipped`, and `Remaining` sets.
3.  **Iteration Loop**:
    -   Picks a `Remaining` tool.
    -   Displays a dynamic menu based on tool metadata (Auto-install, manual guide, steps).
    -   Executes user choice and **re-checks automatically** using `checker.check_tool()`.
4.  **Final Summary**: Generates a product-grade categorization report once all tools are addressed.

---

### **4. Error Handling & Stability**

-   **Subprocess Protection**: All system calls use `subprocess.run` with explicit `timeout=30` and `try-except` blocks.
-   **Safe State Tracking**: Tools are only marked as "Installed" if a fresh diagnostic check passes, ensuring that temporary installation success doesn't hide a permanent tool failure.
