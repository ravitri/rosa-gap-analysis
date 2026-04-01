#!/usr/bin/env python3
"""OCP Admin Gate Acknowledgment Analysis - Verify admin gates are acknowledged for upgrades."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from common import log_info, log_success, log_error, log_warning
from openshift_releases import resolve_baseline_version, resolve_target_version, extract_minor_version
from reporters import generate_markdown_report, generate_html_report, generate_json_report

try:
    import yaml
except ImportError:
    log_error("PyYAML not installed. Please install: pip3 install PyYAML")
    sys.exit(1)


# GitHub raw URLs
CVO_ADMIN_GATE_URL = "https://raw.githubusercontent.com/openshift/cluster-version-operator/release-{version}/install/0000_00_cluster-version-operator_01_admingate_configmap.yaml"
MCC_ADMIN_ACK_URL = "https://raw.githubusercontent.com/openshift/managed-cluster-config/master/deploy/osd-cluster-acks/ocp/{version}/admin-ack.yaml"


def fetch_yaml_from_github(url):
    """Fetch and parse YAML from GitHub."""
    try:
        req = Request(url, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=30) as response:
            data = response.read()
            return yaml.safe_load(data)
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    except (URLError, yaml.YAMLError) as e:
        log_error(f"Failed to fetch or parse YAML from {url}: {e}")
        raise


def fetch_admin_gates(version):
    """Fetch admin gates ConfigMap from cluster-version-operator repo."""
    url = CVO_ADMIN_GATE_URL.format(version=version)
    log_info(f"Fetching admin gates from {url}")

    configmap = fetch_yaml_from_github(url)
    if not configmap:
        log_error(f"Admin gate ConfigMap not found for version {version}")
        return None

    # Extract gates from data field
    gates = configmap.get('data', {})
    if gates:
        log_success(f"Found {len(gates)} admin gate(s) for version {version}")
    else:
        log_info(f"No admin gates found for version {version}")

    return gates


def fetch_admin_acks(version):
    """Fetch admin acknowledgments from managed-cluster-config repo."""
    url = MCC_ADMIN_ACK_URL.format(version=version)
    log_info(f"Fetching admin acknowledgments from {url}")

    ack_configmap = fetch_yaml_from_github(url)
    if not ack_configmap:
        log_warning(f"Admin acknowledgment ConfigMap not found for version {version}")
        return None

    # Extract acks from data field
    acks = ack_configmap.get('data', {})
    if acks:
        log_success(f"Found {len(acks)} acknowledgment(s) for version {version}")
    else:
        log_warning(f"No acknowledgments found in ConfigMap for version {version}")

    return acks


def analyze_gate_acknowledgments(baseline_version, target_version, baseline_gates, target_acks):
    """Analyze if gates from baseline are properly acknowledged in target."""
    result = {
        'gates_requiring_ack': [],
        'acknowledged_gates': [],
        'unacknowledged_gates': [],
        'extra_acks': [],
        'ack_file_missing': target_acks is None
    }

    if not baseline_gates:
        log_info(f"No admin gates in baseline version {baseline_version}, no acknowledgments required")
        return result

    gate_keys = set(baseline_gates.keys())
    result['gates_requiring_ack'] = sorted(gate_keys)

    if target_acks is None:
        # Acknowledgment file is missing but gates exist
        result['unacknowledged_gates'] = sorted(gate_keys)
        log_error(f"Admin gates exist in {baseline_version} but no acknowledgment file found for {target_version}")
        return result

    ack_keys = set(target_acks.keys())

    # Check which gates are acknowledged
    for gate_key in gate_keys:
        if gate_key in ack_keys:
            result['acknowledged_gates'].append(gate_key)
        else:
            result['unacknowledged_gates'].append(gate_key)

    # Check for extra acknowledgments (not strictly an error, but informational)
    result['extra_acks'] = sorted(ack_keys - gate_keys)

    # Sort for consistent output
    result['acknowledged_gates'] = sorted(result['acknowledged_gates'])
    result['unacknowledged_gates'] = sorted(result['unacknowledged_gates'])

    return result


def print_analysis(analysis, baseline, target):
    """Print analysis results."""
    if not analysis['gates_requiring_ack']:
        log_success(f"No admin gates in {baseline}, upgrade to {target} requires no acknowledgments")
        return

    log_info(f"Admin gates in {baseline} requiring acknowledgment: {len(analysis['gates_requiring_ack'])}")

    if analysis['ack_file_missing']:
        log_error(f"❌ UPGRADE BLOCKED: Acknowledgment file missing for {target}")
        log_error(f"   Required file: deploy/osd-cluster-acks/ocp/{target}/admin-ack.yaml")
        return

    if analysis['unacknowledged_gates']:
        log_error(f"❌ UPGRADE BLOCKED: {len(analysis['unacknowledged_gates'])} gate(s) not acknowledged")
        for gate in analysis['unacknowledged_gates']:
            log_error(f"   - {gate}")

    if analysis['acknowledged_gates']:
        log_success(f"✅ {len(analysis['acknowledged_gates'])} gate(s) properly acknowledged")
        for gate in analysis['acknowledged_gates']:
            log_success(f"   - {gate}")

    if analysis['extra_acks']:
        log_info(f"ℹ️  {len(analysis['extra_acks'])} extra acknowledgment(s) present (not required by baseline)")
        for ack in analysis['extra_acks']:
            log_info(f"   - {ack}")

    # Final verdict
    if analysis['unacknowledged_gates']:
        log_error(f"\n❌ UPGRADE NOT READY: {baseline} → {target}")
    else:
        log_success(f"\n✅ UPGRADE READY: All gates acknowledged for {baseline} → {target}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze OCP admin gate acknowledgments for upgrade readiness.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check if gates from 4.21 are acknowledged in 4.22
  %(prog)s --baseline 4.21 --target 4.22

  # With verbose output
  %(prog)s --baseline 4.21 --target 4.22 --verbose

  # Auto-detect versions
  %(prog)s

Exit Codes:
  0 - Successful execution (regardless of whether gates are acknowledged)
  1 - Execution failure (e.g., network errors, missing files)
        """
    )

    parser.add_argument('--baseline', help='Baseline version (default: auto-detect from latest stable)')
    parser.add_argument('--target', help='Target version (default: auto-detect from latest candidate)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--report-dir',
                       default=os.environ.get('REPORT_DIR', 'reports'),
                       help='Directory to store reports (default: reports/, env: REPORT_DIR)')

    args = parser.parse_args()

    # Resolve versions using shared logic
    baseline_full = resolve_baseline_version(
        cli_arg=args.baseline,
        env_var=os.environ.get('BASE_VERSION')
    )
    target_full = resolve_target_version(
        cli_arg=args.target,
        env_var=os.environ.get('TARGET_VERSION')
    )

    # Extract minor versions (admin gates use minor versions like 4.21, 4.22)
    baseline = extract_minor_version(baseline_full)
    target = extract_minor_version(target_full)

    # Main execution
    log_info("Starting OCP Admin Gate Acknowledgment Analysis")
    log_info("=" * 60)
    log_info(f"Baseline version: {baseline_full} (minor: {baseline})")
    log_info(f"Target version: {target_full} (minor: {target})")
    log_info("=" * 60)

    try:
        # Fetch admin gates from baseline version
        baseline_gates = fetch_admin_gates(baseline)

        # Fetch admin acknowledgments from target version
        target_acks = fetch_admin_acks(target)

        # Analyze acknowledgments
        log_info("\nAnalyzing gate acknowledgments...")
        analysis = analyze_gate_acknowledgments(baseline, target, baseline_gates, target_acks)

        # Print results
        print_analysis(analysis, baseline, target)

        # Generate reports
        report_dir = args.report_dir
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Calculate summary
        gates_count = len(analysis['gates_requiring_ack'])
        acked_count = len(analysis['acknowledged_gates'])
        unacked_count = len(analysis['unacknowledged_gates'])
        upgrade_ready = (gates_count == 0) or (unacked_count == 0 and not analysis['ack_file_missing'])

        report_data = {
            'type': 'OCP Admin Gate Acknowledgment Analysis',
            'baseline': baseline,
            'target': target,
            'baseline_full': baseline_full,
            'target_full': target_full,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'summary': {
                'gates_requiring_ack': gates_count,
                'acknowledged': acked_count,
                'unacknowledged': unacked_count,
                'extra_acks': len(analysis['extra_acks']),
                'ack_file_missing': analysis['ack_file_missing'],
                'upgrade_ready': upgrade_ready
            },
            'baseline_gates': baseline_gates or {},
            'target_acks': target_acks or {}
        }

        # Always generate JSON report (needed for combined report)
        json_file = os.path.join(report_dir, f"gap-analysis-ocp-gate-ack_{baseline}_to_{target}_{timestamp}.json")
        generate_json_report(report_data, json_file)
        log_info(f"JSON report generated: {json_file}")

        # Skip Markdown and HTML reports if GAP_FULL_REPORT is set (full report will include these)
        if os.environ.get('GAP_FULL_REPORT'):
            log_info("Skipping Markdown/HTML reports (full report will be generated)")
        else:
            # Generate Markdown report
            md_file = os.path.join(report_dir, f"gap-analysis-ocp-gate-ack_{baseline}_to_{target}_{timestamp}.md")
            generate_markdown_report(report_data, md_file)
            log_info(f"Markdown report generated: {md_file}")

            # Generate HTML report
            html_file = os.path.join(report_dir, f"gap-analysis-ocp-gate-ack_{baseline}_to_{target}_{timestamp}.html")
            generate_html_report(report_data, html_file)
            log_info(f"HTML report generated: {html_file}")

        # Always exit 0 on successful completion
        sys.exit(0)

    except Exception as e:
        log_error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
