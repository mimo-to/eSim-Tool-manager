# eSim Tool Manager Features

This document details the core diagnostic, recovery, and development tools within `esim-tm`.

---

# eSim Tool Manager Features

This document details the core diagnostic, recovery, and development tools within `esim-tm`.

---

## 1. Core Features

### **Dynamic Doctor Mode**
- **What it does**: Performs a system-wide diagnostic check on all 10+ required and optional tools.
- **Value**: It’s a high-confidence reporter. It scans PATH, extracts version metadata, and audits executable health in one pass.

### **Interactive Assist System**
- **What it does**: An recursive recovery system that guides users through repairs via a dynamic menu.
- **Value**: Prevents manual setup errors by providing automated install attempts and direct links to official installation guides.

---

## 2. Advanced Features

### **Environment Snapshotting**
- **What it does**: Captures the exact state of your EDA environment (tool versions, package lists, PATH state).
- **Value**: Detects silent regressions caused by OS updates or conflicting software installations.

### **Cross-Platform Repair Logic**
- **What it does**: Automatically generates fix commands for `winget`, `choco`, `apt`, `dnf`, and `brew`.
- **Value**: Provides a consistent experience regardless of whether the user is on Windows, Ubuntu, Fedora, or macOS.

---

## 3. Engineering Highlights

### **Tuple-Based Version Engine**
- **Precision**: Uses regex-driven extraction to turn strings like `v1.2.3-release` into integer tuples `(1, 2, 3)`.
- **Reliability**: Enables mathematically sound comparisons (`installed >= minimum`) that handle non-standard versioning used by open-source EDA tools.

### **Deterministic Package Matching**
- **Safety**: Implements strict word-boundary checks during repository searches (e.g., matching the exact word `spice` rather than `libspice-dev`).
- **Control**: Prevents "False Installs" that could clutter the system with incorrect or incompatible dependencies.

### **Machine-Readable Diagnostics**
- **Integration**: Supports full `--json` output for every command.
- **Value**: Enables the tool to be used as a backend for larger IDEs or as a gatekeeper in CI/CD pipelines.
