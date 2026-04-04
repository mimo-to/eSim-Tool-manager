from pathlib import Path
from src import registry, checker, health, pip_checker
from datetime import datetime

def generate(output_path: str = None) -> str:
    tool_results = checker.check_all(registry.load())
    health_data = health.compute(tool_results)
    pkg_results = pip_checker.check_all()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if output_path is None:
        log_dir = Path.home() / ".esim_tool_manager"
        log_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(log_dir / "health_report.html")
        
    score_color = "#238636"
    if health_data["status"] == "Excellent":
        score_color = "#238636"
    elif health_data["status"] == "Good":
        score_color = "#d29922"
    elif health_data["status"] == "Partial":
        score_color = "#d29922"
    elif health_data["status"] == "Critical":
        score_color = "#da3633"

    req_total = health_data["required_total"]
    req_inst = health_data["required_installed"]
    opt_total = health_data["optional_total"]
    opt_inst = health_data["optional_installed"]
    py_total = len(pkg_results)
    py_ok = sum(1 for r in pkg_results if r["ok"])

    rows = []
    for res in tool_results:
        if res.get("conflict"):
            status_text = "&#9888; Outdated"
            status_color = "#d29922"
        elif res["installed"]:
            status_text = "&#10003; OK"
            status_color = "#238636"
        else:
            status_text = "&#10007; Missing"
            status_color = "#da3633"
            
        version_text = res["version"] if res["version"] else "&mdash;"
        req_text = "Required" if res["required"] else "Optional"
        
        rows.append(f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{res['name']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d; color: {status_color};">{status_text}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{version_text}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{req_text}</td>
        </tr>
        """)

    pkg_rows = []
    for res in pkg_results:
        if res["ok"]:
            status_text = "&#10003; OK"
            status_color = "#238636"
        else:
            status_text = "&#10007; Missing"
            status_color = "#da3633"
            
        version_text = res["version"] if res["version"] else "&mdash;"
        
        pkg_rows.append(f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{res['name']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d; color: {status_color};">{status_text}</td>
            <td style="padding: 12px; border-bottom: 1px solid #30363d;">{version_text}</td>
        </tr>
        """)
        
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>eSim Tool Manager — Health Report</title>
</head>
<body style="background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; margin: 0; padding: 40px; line-height: 1.5;">
    <div style="max-width: 800px; margin: 0 auto;">
        <h1 style="border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 10px;">eSim Tool Manager — Health Report</h1>
        <p style="margin-bottom: 30px; color: #8b949e; opacity: 0.7; font-size: 0.9em;"><strong>Generated at:</strong> {timestamp}</p>
        
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 30px; text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: {score_color};">{health_data['score']}/100</div>
            <div style="font-size: 18px; margin-top: 10px; margin-bottom: 15px;">Status: <span style="color: {score_color}; font-weight: bold;">{health_data['status']}</span></div>
            <div style="display: flex; justify-content: center; gap: 20px; font-size: 14px; color: #8b949e; border-top: 1px solid #30363d; padding-top: 15px;">
                <span>Required: <strong>{req_inst}/{req_total}</strong></span>
                <span>Optional: <strong>{opt_inst}/{opt_total}</strong></span>
                <span>Python: <strong>{py_ok}/{py_total} OK</strong></span>
            </div>
        </div>
        
        <h2>System Tools</h2>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Tool</th>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Status</th>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Version</th>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Required</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>

        <h3 style="margin-top: 40px; color: #8b949e; border-bottom: 1px solid #30363d; padding-bottom: 5px;">Python Packages</h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Package</th>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Status</th>
                    <th style="padding: 12px; border-bottom: 2px solid #30363d;">Version</th>
                </tr>
            </thead>
            <tbody>
                {''.join(pkg_rows)}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return output_path
