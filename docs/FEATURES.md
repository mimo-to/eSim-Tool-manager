# Project Features

This document provides a comprehensive breakdown of the eSim Tool Manager's capabilities, categorized by their primary use case.

## Most Important Features
*Fast diagnostics and recovery for students and developers.*

- **`doctor`** → One-command environment diagnostics.
- **`repair`** → Auto-fix system configuration issues.
- **`snapshot`** → Track and monitor state changes via baseline files.

---

## Core Features

*Essential tools for environment health and recovery.*

### `doctor`
- **What**: Full system diagnostics for eSim dependencies.
- **Why**: Reduces manual debugging time by identifying missing or outdated tools in one command.

### `repair`
- **What**: Automated fixing of identified environment issues.
- **Why**: Provides a safe, one-click solution for common setup errors (PATH, missing packages).

### `list`
- **What**: Quick status overview of all registered tools.
- **Why**: Allows users to verify their inventory without running deep diagnostics.

---

## Developer Features
*Tools for automation, CI/CD, and detailed troubleshooting.*

### `--verbose`
- **What**: Additive diagnostic tracing for all commands.
- **Why**: Helps contributors identify the exact step where a detection or install fails.

### `--json`
- **What**: Machine-readable output for all diagnostic data.
- **Why**: Enables integration with internal scripts, CI pipelines, and IDE extensions.

---

## Advanced Features
*Specialized tools for environment monitoring and extensibility.*

### `snapshot`
- **What**: Baselines the current environment state to a JSON file.
- **Why**: Creates a "known good" reference point for future comparisons.

### `snapshot-diff`
- **What**: Compares current environment against a saved snapshot.
- **Why**: Instantly identifies regressions (e.g., deleted tools) or improvements after a repair.

### Custom Tool Registration
- **What**: Extensible TOML-based tool definitions.
- **Why**: Allows teams to add project-specific tools to the eSim health-check suite.
