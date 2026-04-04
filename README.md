# eSim Tool Manager
Automated CLI & TUI tool for managing eSim dependencies across platforms.

---

### **Overview**
Setting up an eSim development environment is a complex, error-prone process involving dozens of platform-specific tools and Python dependencies. The **eSim Tool Manager** transforms this into a 30-second automated check, providing a production-grade interface for detection, repair, and reporting.

---

### **Key Features**
- **Cross-Platform Support**: Seamless operation on Windows, Linux, and macOS.
- **Intelligent Dependency Checking**: Real-time validation of system binaries and PATH variables.
- **Automated Repair System**: One-command restoration of missing environment tools.
- **Python Package Validation**: Deep-dive checks for internal Python dependency alignment.
- **Interactive TUI Dashboard**: High-fidelity terminal interface built with Textual.
- **Health Scoring System**: Weighted metrics (0-100) to prioritize critical vs. optional tools.
- **Shareable Reports**: Generates professional, dark-themed HTML diagnostic reports.
- **CI/CD Integration**: Automated testing pipeline via GitHub Actions.

---

### **Installation**
```bash
# Clone the repository
git clone https://github.com/mimo-to/eSim-Tool-manager.git

# Navigate to project directory
cd eSim-Tool-manager

# Install dependencies
pip install -r requirements.txt
```

---

### **Usage**

#### **CLI Commands**
| Command | Action |
| :--- | :--- |
| `python run.py check` | Full scan of system tools and status. |
| `python run.py dashboard` | View system health score and tool categorization. |
| `python run.py repair` | Automatically install or update missing tools. |
| `python run.py report` | Generate a detailed HTML diagnostic report. |
| `python run.py pkgs` | Validate the Python environment and internal packages. |

#### **Terminal User Interface (TUI)**
Launch the immersive dashboard with:
```bash
python run.py tui
```
**Navigation Keys:**
- `1`: Dashboard (System Health Overview)
- `2`: Tools (Categorized Required/Optional List)
- `3`: Logs (Action Audit History)
- `4`: Packages (Python Environment Status)
- `q`: Quit

---

### **Example Output**
**CLI Check:**
```text
✓ OK       Python         3.11.2
✓ OK       npm            9.5.0
✗ Missing  esim-cli       None (Required)
```
**TUI Score:**
```text
92/100
Status: Healthy (Optional tools missing)
```

---

### **Project Structure**
- `src/`: Core implementation (logic, TUI, CLI engine).
- `tests/`: Unit test suite covering registry, health, and platform logic.
- `.github/`: CI/CD workflow configuration for automated testing.
- `tools.toml`: Centralized registry for tool metadata.

---

### **Testing & CI**
Quality is maintained through a dedicated test suite using Python's `unittest` framework.
- **Run Tests Locally**: `python -m unittest discover tests`
- **Automated CI**: Every push or PR triggers the `ci.yml` workflow on GitHub Actions to ensure cross-environment stability.

---

### **Why It Stands Out**
- **Production-Grade Architecture**: Modular design for easy extension.
- **Exceptional UX**: High-end TUI and clean CLI feedback.
- **Real-World Reliability**: Integrated repair system and automated validation.
- **Safety First**: Supports `--dry-run` to preview changes before execution.

---

### **Future Roadmap**
- **Plugin System**: Support for user-defined external tool checks.
- **Remote Registry**: Fetch tool definitions from a cloud-based source.
- **GUI Desktop Client**: A Native Qt or Electron based visual manager.
