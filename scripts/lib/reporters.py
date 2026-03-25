#!/usr/bin/env python3
"""Report generation utilities for gap analysis."""

import json
from datetime import datetime
from typing import Dict, List, Any


def generate_json_report(data: Dict[str, Any], output_file: str = None) -> str:
    """Generate JSON report from gap analysis data."""
    report = json.dumps(data, indent=2, sort_keys=True)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)

    return report


def generate_markdown_report(data: Dict[str, Any], output_file: str = None) -> str:
    """Generate Markdown report from gap analysis data."""
    report_type = data.get('type', 'Gap Analysis')
    baseline = data.get('baseline', 'N/A')
    target = data.get('target', 'N/A')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    md = f"""# {report_type} Report

**Generated:** {timestamp}
**Baseline Version:** {baseline}
**Target Version:** {target}

---

## Summary

"""

    # Add summary based on report type
    if data.get('type') == 'AWS STS Policy Gap Analysis':
        md += _generate_policy_summary_md(data)
    elif data.get('type') == 'GCP WIF Policy Gap Analysis':
        md += _generate_policy_summary_md(data)
    elif data.get('type') == 'Feature Gate Gap Analysis':
        md += _generate_feature_gate_summary_md(data)
    elif data.get('type') == 'Full Gap Analysis':
        md += _generate_full_gap_summary_md(data)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(md)

    return md


def generate_html_report(data: Dict[str, Any], output_file: str = None) -> str:
    """Generate HTML report from gap analysis data."""
    report_type = data.get('type', 'Gap Analysis')
    baseline = data.get('baseline', 'N/A')
    target = data.get('target', 'N/A')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_type} Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #444;
            margin-top: 30px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        .metadata {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        .summary-card {{
            display: inline-block;
            margin: 10px;
            padding: 20px;
            background-color: #e3f2fd;
            border-radius: 5px;
            border-left: 4px solid #0066cc;
        }}
        .summary-card.success {{
            background-color: #e8f5e9;
            border-left-color: #4caf50;
        }}
        .summary-card.warning {{
            background-color: #fff3e0;
            border-left-color: #ff9800;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #0066cc;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .added {{
            color: #4caf50;
            font-weight: 500;
        }}
        .removed {{
            color: #f44336;
            font-weight: 500;
        }}
        .changed {{
            color: #ff9800;
            font-weight: 500;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        ul li {{
            padding: 5px 0;
        }}
        ul li:before {{
            content: "▸ ";
            color: #0066cc;
            font-weight: bold;
            margin-right: 5px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_type} Report</h1>

        <div class="metadata">
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Baseline Version:</strong> <code>{baseline}</code></p>
            <p><strong>Target Version:</strong> <code>{target}</code></p>
        </div>

        <h2>Summary</h2>
"""

    # Add summary based on report type
    if data.get('type') == 'AWS STS Policy Gap Analysis':
        html += _generate_policy_summary_html(data, 'AWS STS Policy')
    elif data.get('type') == 'GCP WIF Policy Gap Analysis':
        html += _generate_policy_summary_html(data, 'GCP WIF Policy')
    elif data.get('type') == 'Feature Gate Gap Analysis':
        html += _generate_feature_gate_summary_html(data)
    elif data.get('type') == 'Full Gap Analysis':
        html += _generate_full_gap_summary_html(data)

    html += """
        <div class="footer">
            Generated by OpenShift Gap Analysis Tools
        </div>
    </div>
</body>
</html>
"""

    if output_file:
        with open(output_file, 'w') as f:
            f.write(html)

    return html


# Helper functions for Markdown generation

def _generate_policy_summary_md(data: Dict[str, Any]) -> str:
    """Generate policy comparison summary in markdown."""
    comparison = data.get('comparison', {})
    actions = comparison.get('actions', {})
    added = actions.get('target_only', [])
    removed = actions.get('baseline_only', [])

    md = f"""
### Changes Detected

- **Added Actions:** {len(added)}
- **Removed Actions:** {len(removed)}
- **Total Changes:** {len(added) + len(removed)}

"""

    if added:
        md += "### Added Actions\n\n"
        for action in added:
            md += f"- ✅ `{action}`\n"
        md += "\n"

    if removed:
        md += "### Removed Actions\n\n"
        for action in removed:
            md += f"- ❌ `{action}`\n"
        md += "\n"

    if not added and not removed:
        md += "**✅ No policy differences detected**\n\n"

    return md


def _generate_feature_gate_summary_md(data: Dict[str, Any]) -> str:
    """Generate feature gate comparison summary in markdown."""
    comparison = data.get('comparison', {})
    added = comparison.get('added', [])
    removed = comparison.get('removed', [])
    newly_default = comparison.get('newly_enabled_by_default', [])
    removed_default = comparison.get('removed_from_default', [])

    md = f"""
### Changes Detected

- **New Feature Gates:** {len(added)}
- **Removed Feature Gates:** {len(removed)}
- **Newly Enabled by Default:** {len(newly_default)}
- **Removed from Default:** {len(removed_default)}

"""

    if added:
        md += "### New Feature Gates\n\n"
        for gate in added:
            md += f"- ➕ `{gate}`\n"
        md += "\n"

    if removed:
        md += "### Removed Feature Gates\n\n"
        for gate in removed:
            md += f"- ➖ `{gate}`\n"
        md += "\n"

    if newly_default:
        md += "### Newly Enabled by Default\n\n"
        for gate in newly_default:
            md += f"- ⭐ `{gate}`\n"
        md += "\n"

    if removed_default:
        md += "### Removed from Default\n\n"
        for gate in removed_default:
            md += f"- ⚠️ `{gate}`\n"
        md += "\n"

    if not any([added, removed, newly_default, removed_default]):
        md += "**✅ No feature gate differences detected**\n\n"

    return md


def _generate_full_gap_summary_md(data: Dict[str, Any]) -> str:
    """Generate full gap analysis summary in markdown."""
    aws = data.get('aws_sts', {})
    gcp = data.get('gcp_wif', {})
    fg = data.get('feature_gates', {})

    md = "### Platform Analysis Results\n\n"

    # AWS STS
    if aws:
        aws_added = len(aws.get('comparison', {}).get('actions', {}).get('target_only', []))
        aws_removed = len(aws.get('comparison', {}).get('actions', {}).get('baseline_only', []))
        md += f"#### AWS STS\n- Added: {aws_added}\n- Removed: {aws_removed}\n\n"

    # GCP WIF
    if gcp:
        gcp_added = len(gcp.get('comparison', {}).get('actions', {}).get('target_only', []))
        gcp_removed = len(gcp.get('comparison', {}).get('actions', {}).get('baseline_only', []))
        md += f"#### GCP WIF\n- Added: {gcp_added}\n- Removed: {gcp_removed}\n\n"

    # Feature Gates
    if fg:
        fg_comparison = fg.get('comparison', {})
        fg_added = len(fg_comparison.get('added', []))
        fg_removed = len(fg_comparison.get('removed', []))
        fg_newly_default = len(fg_comparison.get('newly_enabled_by_default', []))
        md += f"#### Feature Gates\n- New: {fg_added}\n- Removed: {fg_removed}\n- Newly Default: {fg_newly_default}\n\n"

    return md


# Helper functions for HTML generation

def _generate_policy_summary_html(data: Dict[str, Any], policy_type: str) -> str:
    """Generate policy comparison summary in HTML."""
    comparison = data.get('comparison', {})
    actions = comparison.get('actions', {})
    added = actions.get('target_only', [])
    removed = actions.get('baseline_only', [])

    total_changes = len(added) + len(removed)

    if total_changes == 0:
        card_class = "success"
        status = "✅ No Differences"
    else:
        card_class = "warning"
        status = f"⚠️ {total_changes} Changes Detected"

    html = f"""
        <div class="summary-card {card_class}">
            <h3>{status}</h3>
            <p><strong>Added:</strong> {len(added)} | <strong>Removed:</strong> {len(removed)}</p>
        </div>
"""

    if added or removed:
        html += "<h2>Details</h2>"

    if added:
        html += """
        <h3>Added Actions</h3>
        <table>
            <thead>
                <tr>
                    <th>Action</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        for action in added:
            html += f"<tr><td><code>{action}</code></td><td class='added'>✅ Added</td></tr>\n"
        html += "</tbody></table>\n"

    if removed:
        html += """
        <h3>Removed Actions</h3>
        <table>
            <thead>
                <tr>
                    <th>Action</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        for action in removed:
            html += f"<tr><td><code>{action}</code></td><td class='removed'>❌ Removed</td></tr>\n"
        html += "</tbody></table>\n"

    return html


def _generate_feature_gate_summary_html(data: Dict[str, Any]) -> str:
    """Generate feature gate comparison summary in HTML."""
    comparison = data.get('comparison', {})
    added = comparison.get('added', [])
    removed = comparison.get('removed', [])
    newly_default = comparison.get('newly_enabled_by_default', [])
    removed_default = comparison.get('removed_from_default', [])

    total_changes = len(added) + len(removed) + len(newly_default) + len(removed_default)

    if total_changes == 0:
        card_class = "success"
        status = "✅ No Differences"
    else:
        card_class = "warning"
        status = f"⚠️ {total_changes} Changes Detected"

    html = f"""
        <div class="summary-card {card_class}">
            <h3>{status}</h3>
            <p>
                <strong>New:</strong> {len(added)} |
                <strong>Removed:</strong> {len(removed)} |
                <strong>Newly Default:</strong> {len(newly_default)}
            </p>
        </div>
"""

    if added or removed or newly_default or removed_default:
        html += "<h2>Details</h2>"

    if added:
        html += """
        <h3>New Feature Gates</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature Gate</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        for gate in added:
            html += f"<tr><td><code>{gate}</code></td><td class='added'>➕ New</td></tr>\n"
        html += "</tbody></table>\n"

    if newly_default:
        html += """
        <h3>Newly Enabled by Default</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature Gate</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        for gate in newly_default:
            html += f"<tr><td><code>{gate}</code></td><td class='changed'>⭐ Promoted to Default</td></tr>\n"
        html += "</tbody></table>\n"

    if removed:
        html += """
        <h3>Removed Feature Gates</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature Gate</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
        for gate in removed:
            html += f"<tr><td><code>{gate}</code></td><td class='removed'>➖ Removed</td></tr>\n"
        html += "</tbody></table>\n"

    return html


def _generate_full_gap_summary_html(data: Dict[str, Any]) -> str:
    """Generate full gap analysis summary in HTML."""
    aws = data.get('aws_sts', {})
    gcp = data.get('gcp_wif', {})
    fg = data.get('feature_gates', {})

    html = "<div style='display: flex; flex-wrap: wrap;'>\n"

    # AWS STS Summary
    if aws:
        aws_added = len(aws.get('comparison', {}).get('actions', {}).get('target_only', []))
        aws_removed = len(aws.get('comparison', {}).get('actions', {}).get('baseline_only', []))
        aws_total = aws_added + aws_removed
        card_class = "success" if aws_total == 0 else "warning"
        html += f"""
        <div class="summary-card {card_class}">
            <h3>AWS STS</h3>
            <p><strong>Added:</strong> {aws_added}</p>
            <p><strong>Removed:</strong> {aws_removed}</p>
        </div>
"""

    # GCP WIF Summary
    if gcp:
        gcp_added = len(gcp.get('comparison', {}).get('actions', {}).get('target_only', []))
        gcp_removed = len(gcp.get('comparison', {}).get('actions', {}).get('baseline_only', []))
        gcp_total = gcp_added + gcp_removed
        card_class = "success" if gcp_total == 0 else "warning"
        html += f"""
        <div class="summary-card {card_class}">
            <h3>GCP WIF</h3>
            <p><strong>Added:</strong> {gcp_added}</p>
            <p><strong>Removed:</strong> {gcp_removed}</p>
        </div>
"""

    # Feature Gates Summary
    if fg:
        fg_comparison = fg.get('comparison', {})
        fg_added = len(fg_comparison.get('added', []))
        fg_removed = len(fg_comparison.get('removed', []))
        fg_newly_default = len(fg_comparison.get('newly_enabled_by_default', []))
        fg_total = fg_added + fg_removed + fg_newly_default
        card_class = "success" if fg_total == 0 else "warning"
        html += f"""
        <div class="summary-card {card_class}">
            <h3>Feature Gates</h3>
            <p><strong>New:</strong> {fg_added}</p>
            <p><strong>Removed:</strong> {fg_removed}</p>
            <p><strong>Newly Default:</strong> {fg_newly_default}</p>
        </div>
"""

    html += "</div>\n"

    return html
