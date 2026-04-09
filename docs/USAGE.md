# eSim-tm Usage Workflows

This document outlines real-world scenarios for using the `esim-tm` tool.

---

# eSim Tool Manager: Professional Workflows

This guide outlines standard operational procedures for maintaining a robust eSim environment using `esim-tm`.

---

## 1. Initial Environment Bootstrap

**Goal**: Transform a fresh machine into a ready-for-development eSim node.

1.  **Diagnostic Audit**: Run `esim-tm doctor`. Identify missing system binaries (e.g., Ngspice) and Python libraries.
2.  **Guided Recovery**: Use `esim-tm assist`. Follow the interactive prompts to auto-install dependencies via system managers (`winget`, `apt`, etc.).
3.  **Verification**: Re-run `esim-tm doctor` to ensure a 100% "Excellent" health score.
4.  **Baseline Capture**: Run `esim-tm snapshot`. This saves your "Known Good" state to a JSON baseline.

---

## 2. Dealing with Environment Regressions

**Goal**: Recover a broken environment after a system update or accidental deletion.

1.  **Change Detection**: Run `esim-tm snapshot-diff`. The tool will compare your current state against the last snapshot and highlight exactly what broke.
2.  **Targeted Fix**: Use `esim-tm repair` to attempt an automated batch fix of all core toolchain components.
3.  **Manual Intervention**: If automated fix fails, use `esim-tm assist` to follow the guided manual steps and official download links.

---

## 3. Continuous Monitoring (TUI Dashboard)

**Goal**: Keep a persistent eye on system readiness during an intensive development session.

-   **Launch TUI**: Run `esim-tm tui`.
-   **Features**:
    -   Live refresh of tool executable status.
    -   One-click re-scanning from the dashboard interface.
    -   Visual health progress bar.

---

## 4. Automation & CI/CD Integration

**Goal**: Use `esim-tm` as a gatekeeper in automated pipelines.

-   **JSON Health Check**:
    ```bash
    esim-tm check --json > health.json
    ```
-   **Integration Logic**:
    Use the exit codes to fail a CI build if `health.json` indicates missing required tools.
-   **Logging**:
    Review `esim_tm.log` for a timestamped audit trail of all diagnostic and installation events.

---

## 5. Professional Health Reporting

For team leads or evaluators, generate a high-fidelity report:

```bash
esim-tm report
```
This produces a `health_report.html` (or similar) containing a detailed breakdown of tool versions, status, and system metadata.
