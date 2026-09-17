import json
from datetime import datetime

class ReportGenerator:
    """Generates professional KYC audit dossiers and certificates in HTML and Markdown."""

    @staticmethod
    def generate_html_report(decision: dict) -> str:
        pillars_rows = ""
        for p in decision["pillars"]:
            status_color = "#059669" if p["status"] == "PASS" else ("#d97706" if p["status"] in ["WARN", "REVIEW"] else "#dc2626")
            status_bg = "#ecfdf5" if p["status"] == "PASS" else ("#fffbeb" if p["status"] in ["WARN", "REVIEW"] else "#fef2f2")
            status_border = "#a7f3d0" if p["status"] == "PASS" else ("#fde68a" if p["status"] in ["WARN", "REVIEW"] else "#fecaca")
            pillars_rows += f"""
            <tr>
                <td style="padding: 12px; font-weight: 600; color: #0f172a; border-bottom: 1px solid #e2e8f0;">{p['pillar']}</td>
                <td style="padding: 12px; text-align: center; color: #64748b; border-bottom: 1px solid #e2e8f0;">{p['weight']}</td>
                <td style="padding: 12px; text-align: center; font-weight: 600; color: #0f172a; border-bottom: 1px solid #e2e8f0;">{p['score']} / {p['max_score']}</td>
                <td style="padding: 12px; text-align: center; border-bottom: 1px solid #e2e8f0;">
                    <span style="background: {status_bg}; color: {status_color}; border: 1px solid {status_border}; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase;">
                        {p['status']}
                    </span>
                </td>
                <td style="padding: 12px; font-size: 13px; color: #334155; border-bottom: 1px solid #e2e8f0;">{p['details']}</td>
            </tr>
            """

        flags_html = ""
        if decision["risk_flags"]:
            flags_html = "<div style='margin-top: 20px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 16px;'>"
            flags_html += "<div style='margin: 0 0 8px 0; color: #991b1b; font-weight: 600; font-size: 13px;'>Flagged Verification Items:</div><ul style='margin: 0; padding-left: 20px; color: #b91c1c; font-size: 13px;'>"
            for f in decision["risk_flags"]:
                flags_html += f"<li style='margin-bottom: 4px;'>{f}</li>"
            flags_html += "</ul></div>"
        else:
            flags_html = "<div style='margin-top: 20px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; padding: 14px; color: #065f46; font-size: 13px;'>All validation checks passed successfully with zero risk flags.</div>"

        c = decision["customer_summary"]
        status_color = decision["badge_color"]

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>KYC Verification Dossier - {decision['reference_id']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8fafc; color: #0f172a; margin: 0; padding: 24px; }}
        .container {{ max-width: 820px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }}
        .header {{ background: #ffffff; padding: 24px 30px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }}
        .badge {{ background: transparent; color: {status_color}; border: 1px solid {status_color}; padding: 6px 14px; border-radius: 4px; font-weight: 700; font-size: 13px; letter-spacing: 0.5px; text-transform: uppercase; }}
        .content {{ padding: 28px 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; }}
        .card-label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 4px; letter-spacing: 0.5px; }}
        .card-value {{ font-size: 14px; font-weight: 600; color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; }}
        th {{ background: #f1f5f9; padding: 10px 12px; text-align: left; font-size: 11px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; }}
        .score-box {{ text-align: center; padding: 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 24px; }}
        .score-val {{ font-size: 36px; font-weight: 700; color: {status_color}; }}
        .footer {{ padding: 16px 30px; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; display: flex; justify-content: space-between; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin: 0; font-size: 18px; font-weight: 700; letter-spacing: -0.3px; color: #0f172a;">IDENTITY VERIFICATION REPORT</h1>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">Customer Due Diligence & Identity Assurance Record</p>
            </div>
            <div class="badge">
                {decision['final_status']}
            </div>
        </div>

        <div class="content">
            <div class="score-box">
                <div style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: #64748b; margin-bottom: 4px; letter-spacing: 0.5px;">Aggregate Verification Score</div>
                <div class="score-val">{decision['total_score']} <span style="font-size: 16px; color: #64748b; font-weight: 400;">/ 100</span></div>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #334155;">{decision['summary_statement']}</p>
            </div>

            <div style="font-size: 13px; font-weight: 600; color: #0f172a; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">Applicant Details</div>
            <div class="grid">
                <div class="card">
                    <div class="card-label">Applicant Name</div>
                    <div class="card-value">{c.get('name', 'N/A')}</div>
                </div>
                <div class="card">
                    <div class="card-label">Date of Birth</div>
                    <div class="card-value">{c.get('dob', 'N/A')}</div>
                </div>
                <div class="card">
                    <div class="card-label">Document Type</div>
                    <div class="card-value">{c.get('id_type', 'N/A')}</div>
                </div>
                <div class="card">
                    <div class="card-label">Document Identifier</div>
                    <div class="card-value">{c.get('id_number', 'N/A')}</div>
                </div>
                <div class="card">
                    <div class="card-label">Contact Information</div>
                    <div class="card-value">{c.get('email', 'N/A')} | {c.get('phone', 'N/A')}</div>
                </div>
                <div class="card">
                    <div class="card-label">Verification Timestamp</div>
                    <div class="card-value">{decision['timestamp']}</div>
                </div>
            </div>

            <div style="font-size: 13px; font-weight: 600; color: #0f172a; margin: 24px 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">Evaluation Breakdown</div>
            <table>
                <thead>
                    <tr>
                        <th>Pillar</th>
                        <th style="text-align: center;">Weight</th>
                        <th style="text-align: center;">Score</th>
                        <th style="text-align: center;">Status</th>
                        <th>Findings</th>
                    </tr>
                </thead>
                <tbody>
                    {pillars_rows}
                </tbody>
            </table>

            {flags_html}

            <div style="margin-top: 20px; padding: 14px 16px; background: #f8fafc; border-left: 3px solid {status_color}; border-radius: 4px;">
                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 2px;">Recommended Action</div>
                <div style="font-size: 13px; color: #0f172a;">{decision['recommended_action']}</div>
            </div>
        </div>

        <div class="footer">
            <div>Reference: <strong>{decision['reference_id']}</strong></div>
            <div>Generated by Identity Verification Engine • Internal Record</div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    @staticmethod
    def generate_markdown_summary(decision: dict) -> str:
        c = decision["customer_summary"]
        md = f"""# Identity Verification Report
**Reference**: `{decision['reference_id']}`  
**Timestamp**: `{decision['timestamp']}`  
**Status**: **{decision['final_status']}** (Score: {decision['total_score']} / 100)

---

### Applicant Information
- **Full Name**: {c.get('name')}
- **Date of Birth**: {c.get('dob')}
- **Document Type**: {c.get('id_type')}
- **ID Number**: {c.get('id_number')}
- **Email**: {c.get('email')}
- **Phone**: {c.get('phone')}

---

### Assessment Breakdown
| Pillar | Weight | Score | Status | Findings |
| :--- | :---: | :---: | :---: | :--- |
"""
        for p in decision["pillars"]:
            md += f"| {p['pillar']} | {p['weight']} | {p['score']}/{p['max_score']} | {p['status']} | {p['details']} |\n"

        md += f"\n### Summary\n{decision['summary_statement']}\n\n"
        md += f"**Action**: {decision['recommended_action']}\n\n"

        if decision["risk_flags"]:
            md += "### Review Items\n"
            for f in decision["risk_flags"]:
                md += f"- {f}\n"

        return md
