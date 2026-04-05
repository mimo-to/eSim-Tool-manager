# eSim Tool Manager (esim-tm)

**Detect → Fix → Guide → Monitor eSim tool environments from one CLI.**

The eSim Tool Manager is a production-grade diagnostic and recovery suite designed specifically for the eSim EDA ecosystem. It transforms complex, manual environment setups into a guided, deterministic experience.

---

### 1. Problem → Solution

**The Problem:**
Manual EDA setup is fragile. Missing dependencies like Ngspice, Verilator, or GHDL, combined with broken `PATH` variables and version mismatches, often lead to silent failures and user frustration.

**The Solution:**
`esim-tm` provides a "Single Source of Truth" for your EDA environment. It doesn't just detect issues; it guides you through fixes, provides direct installation paths, and monitors system changes via snapshots.

---

### 2. Quick Start (Get Running in 30s)

#### **Install via pipx (Recommended)**
```bash
pipx install git+https://github.com/mimo-to/eSim-Tool-manager.git
```

#### **Run Diagnostics**
```bash
esim-tm doctor
```

#### **Interactive Assistant (Primary Recovery)**
```bash
esim-tm assist
```

#### **State Tracking**
```bash
esim-tm snapshot
esim-tm snapshot-diff
```

---

### 3. Real Output (What to Expect)

#### **Doctor Report**
```text
Tools
✗ Ngspice — Not found (Required)
    → Fix: winget install --id ngspice -e --silent
✓ Python 3 — OK (Required)
✓ Git — OK (Required)

Python Packages
✗ numpy — Not found
```

#### **Interactive Assistant**
```text
╭─ Tool Assistance (1/3) — Ngspice ─╮
│ Status: Not found                │
╰──────────────────────────────────╯
  1. Attempt automated installation
  2. Open official installation guide
  3. Show manual installation steps
  4. Re-check status now
  5. Skip this tool
```

---

### 4. Why This Stands Out

- **No Dead-End UX**: Every detected issue comes with a direct fix command or a verified installation guide.
- **Interactive Recovery**: The `assist` command provides a decision-loop for non-trivial installations.
- **Deterministic State**: Use `snapshot` to capture a working environment and `snapshot-diff` to detect what changed after a system update.
- **Platform Aware**: Intelligent switching between WinGet, APT, Brew, and Chocolatey instructions.

---

### 5. Important Notes

- **Primary Command**: Always use `esim-tm`. This is the official way to interact with the suite.
- **Isolation**: Use `pipx install --force` to ensure you have the latest version in an isolated environment.
- **Documentation**: Explore the `docs/` folder for advanced workflows and architecture details.

---

### 6. Common Mistake

If `esim-tm` is not found after installation:
**Run:** `pipx install --force git+https://github.com/mimo-to/eSim-Tool-manager.git`

---

**Goal**: "Project is fully consistent and submission-ready."
