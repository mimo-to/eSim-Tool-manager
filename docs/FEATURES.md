# eSim Tool Manager Features

This document details the core diagnostic, recovery, and development tools within `esim-tm`.

---

### **Core Diagnostics**

#### **1. Feature: doctor**
-   **What it does**: Performs a system-wide diagnostic check on all 10+ required and optional tools.
-   **Value**: It’s the high-confidence reporter. It doesn’t just say if a tool is missing; it checks if it’s in your PATH, if the version meets requirements, and if it’s executable.

#### **2. Feature: assist**
-   **What it does**: An interactive recovery system that guides you through every step of a tool's installation or fix.
-   **Value**: This is your primary recovery path. It provides automated install attempts, links to official guides, and a dynamic "re-check loop" to ensure you don't exit until the tool is healthy.

---

### **Advanced Monitoring**

#### **3. Feature: snapshot**
-   **What it does**: Captures the exact state of your EDA environment (tool versions, package lists).
-   **Value**: Protects your environment against silent changes from system updates or accidental uninstalls.

#### **4. Feature: snapshot-diff**
-   **What it does**: Compares your current system state against your last captured baseline.
-   **Value**: Rapidly identifies "New Issues" (tools that just stopped working) or "Fixed Issues" (tools you’ve successfully recovered).

---

### **Developer Tools**

#### **5. Feature: check**
-   **What it does**: Performs a quick health check for a specific tool or package.
-   **Value**: Lightweight verification for use in custom scripts or post-install verification.

#### **6. Feature: pkgs**
-   **What it does**: Lists all eSim-specific Python libraries and checks for missing or outdated versions.
-   **Value**: Ensures library consistency across development and production environments.

---

**Terminology Guide**:
-   **Core Diagnostics**: Essential tools for system recovery.
-   **Advanced Monitoring**: State-tracking for long-term environment stability.
-   **Developer Tools**: Granular commands for specialized usage.
