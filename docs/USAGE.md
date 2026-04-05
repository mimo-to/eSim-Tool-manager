# eSim-tm Usage Workflows

This document outlines real-world scenarios for using the `esim-tm` tool.

---

### **1. First-Time Environment Setup**

**Goal**: Verify your system and fix all core dependencies.

1.  **Check Diagnostics**: Run `esim-tm doctor` to see what is missing.
2.  **Interactive Guide**: Use `esim-tm assist` to fix issues.
3.  **Capture Baseline**: Once everything is "OK", run `esim-tm snapshot` to save your working state.

---

### **2. Broken Environment Recovery**

**Goal**: Restore a system that was previously working but is now failing.

1.  **Identify Changes**: Run `esim-tm snapshot-diff`. This will show you exactly what changed (e.g., a tool was uninstalled or a version changed).
2.  **Repair Issues**: Use `esim-tm assist` for guided recovery.
3.  **Bulk Fix (Advanced)**: Use `esim-tm repair` for automated attempt at fixing all required tools.

---

### **3. Monitoring System Changes**

**Goal**: Detect when a system update or another user has modified the EDA environment.

-   **Compare Baseline**: Run `esim-tm snapshot-diff`.
-   **Review Package Mismatches**: Use `esim-tm pkgs` to check for Python library consistency.

---

### **4. Pro Tips**

-   **Diagnostics First**: Always start with `esim-tm doctor`. It’s the highest-confidence report.
-   **No Guesswork**: If `doctor` shows an issue, don't guess the command. Use `assist` and follow the menus.
-   **Isolated Development**: Use `esim-tm --json` to extract data for your own scripts or CI/CD pipelines.

---

**Terminology Reference**:
-   **Tool**: External binaries like Ngspice, Verilator, or GHDL.
-   **Package**: Python libraries such as `numpy` or `scipy`.
-   **Issue**: Any mismatch in PATH, version, or installation state.
