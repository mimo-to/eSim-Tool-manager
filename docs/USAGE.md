# Usage Guide

This guide covers common user scenarios, from initial setup to environment monitoring and repair workflows.

## 1-Minute Workflow
*The standard sequence for maintaining a healthy environment.*

**`doctor`** → **`repair`** → **`snapshot`** → **`snapshot-diff`**

---

## First-Time Setup

*Goal: Ensure your machine is ready for eSim development.*

1. **Verify your environment**:
   ```bash
   python run.py doctor
   ```
2. **Review identified issues**: Check both `Required` (essential) and `Optional` dependencies.
3. **Save a baseline state**:
   ```bash
   python run.py snapshot
   ```
   *This creates a known-good reference of your current setup.*

---

## Broken Environment
*Goal: Fix missing or outdated dependencies.*

1. **Perform deep diagnostics**:
   ```bash
   python run.py doctor
   ```
2. **Run an automated repair**:
   ```bash
   python run.py repair
   ```
3. **Verify the fix**:
   ```bash
   python run.py snapshot-diff
   ```
   *This shows you exactly what changed since your last snapshot.*

---

## Monitoring Changes
*Goal: Detect regressions in tool versions or PATH settings.*

1. **Run a comparison**:
   ```bash
   python run.py snapshot-diff
   ```
2. **Review differences**:
   - **New Issues**: Tools that were working but are now missing or outdated.
   - **Fixed Issues**: Tools resolved since the last snapshot.

---

## What NOT to do
*Avoid these common anti-patterns:*

- **Do not manually edit PATH blindly**: Use `repair` or check `doctor` output for guided fixes.
- **Do not install tools without checking**: Running `doctor` first ensures you're installing the correct version.
- **Do not skip snapshot baseline**: Without a baseline, you cannot detect regressions efficiently.
- **Do not ignore "Outdated" warnings**: Even if a tool is detected, missing patches can cause project failures.
