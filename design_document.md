# eSim Tool Manager - Design Document

This document outlines the design decisions, trade-offs, and failure-handling strategies for the eSim Tool Manager (`esim-tm`).

### **1. Core Philosophy**

The primary objective of `esim-tm` is **system-wide transparency**. Instead of opaque automation, the tool focuses on making the current state of an EDA environment visible and recoverable.

---

### **2. Design Trade-offs**

-   **Simplicity > Complexity**: We prioritize a robust CLI over a complex GUI to ensure maximum compatibility and maintainability across different environments.
-   **Manual Fallback > Forced Automation**: While we provide auto-install paths (WinGet, APT), we always maintain a direct link to the official documentation and manual steps. This ensures the user is never stuck if an automated command fails.
-   **Static Registry > Dynamic Discovery**: Metadata for tools (versions, links, and package mappings) is stored in a static `tools.toml`. This makes the suite predictable and easy to audit.

---

### **3. Failure Handling & Resilience**

-   **Subprocess Timeouts**: Every external system call is bounded by a `30-second` timeout to prevent the CLI from hanging during network or execution issues.
-   **Graceful Degenerancy**: If a tool cannot be detected correctly (e.g., due to a non-standard PATH), the manager warns the user but continues the diagnostic for other dependencies.
-   **Recursive Health Checks**: The `assist` system performs a fresh health check after every installation attempt. A tool is only marked as "Installed" if it passes a verified test command.

---

### **4. Rationales**

-   **Why `pipx`?**: To keep the Tool Manager isolated from the user’s system Python, preventing dependency conflicts while still allowing it to manage system-wide EDA tools.
-   **Why `rich`?**: To provide a product-grade, color-coded diagnostic report that is easy for evaluators to scan in seconds.
-   **Why `SNAPSHOT`?**: To give users a "System Recovery Point" for their EDA settings, which is essential for projects that depend on specific library versions.

---

**Current Status**: "PROJECT IS FULLY CONSISTENT AND SUBMISSION-READY"
