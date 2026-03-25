# OpenShift Gap Analysis Framework

A comprehensive framework for analyzing gaps between different versions and platforms of managed OpenShift offerings (OSD, ROSA Classic, ROSA HCP).

## Overview

This repository provides both automated scripts (for CI/Prow) and Claude AI skills for identifying and analyzing gaps across OpenShift versions:

- **AWS STS Policies**: IAM permission changes for AWS-based clusters (OSD AWS, ROSA Classic, ROSA HCP)
- **GCP WIF Policies**: Workload Identity Federation permission changes for GCP-based clusters (OSD GCP)
- **Feature Gates**: Feature gate additions, removals, and default enablement changes

**Exit Codes**: Scripts exit with code 0 on successful execution (regardless of differences), code 1 only on execution failures (missing tools, network errors).

**Report Generation**: All scripts automatically generate comprehensive reports in Markdown, HTML, and JSON formats for easy analysis and CI/CD integration.

## Quick Start

### Prerequisites

- `oc` CLI (OpenShift client) - **required** for extracting credential requests from releases
- `python3` - **required** for running gap analysis scripts
- `PyYAML` - **required** for YAML parsing (`pip install pyyaml`)
- `curl` - **required** for fetching release information (Sippy API)
- Claude Code (optional) - for using AI skills

### Local Usage

#### Auto-detect versions (recommended)

```bash
# Run analysis with auto-detected versions
# Baseline: latest stable version (e.g., 4.21.6)
# Target: latest candidate version (e.g., 4.22.0-ec.3)
# Analyzes: AWS STS, GCP WIF, and Feature Gates
# Generates reports in: ./reports/ directory
./scripts/gap-all.sh
# Exit code 0: Successful execution (regardless of differences)
# Exit code 1: Execution failure

# Auto-detect with nightly target
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh

# Individual platform analysis with auto-detection
python3 ./scripts/gap-aws-sts.py
python3 ./scripts/gap-gcp-wif.py
python3 ./scripts/gap-feature-gates.py

# Custom report directory
REPORT_DIR=/path/to/reports ./scripts/gap-all.sh
```

#### Specify versions explicitly

```bash
# Analyze AWS STS policy gaps between specific versions
python3 ./scripts/gap-aws-sts.py --baseline 4.21.6 --target 4.22.0-ec.3

# Analyze GCP WIF policy gaps
python3 ./scripts/gap-gcp-wif.py --baseline 4.21 --target 4.22

# Analyze feature gate changes
python3 ./scripts/gap-feature-gates.py --baseline 4.21 --target 4.22

# Run analysis for all platforms (AWS STS, GCP WIF, Feature Gates)
./scripts/gap-all.sh --baseline 4.21 --target 4.22

# Specify custom report directory
./scripts/gap-all.sh --baseline 4.21 --target 4.22 --report-dir /custom/reports
```

#### Use environment variables

```bash
# Override versions using environment variables
BASE_VERSION=4.21.5 TARGET_VERSION=4.22.0-ec.2 ./scripts/gap-all.sh

# Use nightly build as target
TARGET_VERSION=NIGHTLY python3 ./scripts/gap-aws-sts.py

# Explicit candidate (same as default)
TARGET_VERSION=CANDIDATE python3 ./scripts/gap-gcp-wif.py

# Custom report directory
REPORT_DIR=/custom/path ./scripts/gap-all.sh
```

#### Use in CI/CD pipelines

```bash
# Run analysis and check for differences (scripts exit 0 on success)
./scripts/gap-all.sh || {
  echo "Gap analysis execution failed"
  exit 1
}

# Check for differences by parsing output
if ./scripts/gap-all.sh 2>&1 | grep -q "differences detected"; then
  echo "Policy or feature gate changes detected - review recommended"
  # Reports are in ./reports/ directory
fi

# Test against nightly builds
if TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh 2>&1 | grep -q "differences detected"; then
  echo "Changes detected in nightly - review reports/"
fi

# Individual platform checks with auto-detection
python3 ./scripts/gap-aws-sts.py || exit 1
python3 ./scripts/gap-gcp-wif.py || exit 1
python3 ./scripts/gap-feature-gates.py || exit 1

# Generate reports in custom location for CI artifacts
REPORT_DIR=./ci-artifacts/gap-reports ./scripts/gap-all.sh
```

### Using Claude Skills

With Claude Code installed, simply ask:

```
"Compare AWS STS policies between OpenShift 4.21 and 4.22"

"Analyze GCP WIF policy changes between 4.21 and 4.22"

"Run a full gap analysis between 4.21 and 4.22"
```

The skills will leverage the scripts while providing intelligent analysis and recommendations. The full gap analysis skill automatically checks both AWS and GCP platforms.

## Repository Structure

```
gap-analysis/
├── scripts/                       # Gap analysis scripts
│   ├── lib/                      # Shared libraries
│   │   ├── common.py            # Python utilities (logging, etc.)
│   │   ├── openshift_releases.py # Version resolution (Python)
│   │   ├── reporters.py         # Report generation (MD, HTML, JSON)
│   │   ├── common.sh            # Bash utilities
│   │   └── openshift-releases.sh # Version queries (Bash)
│   ├── gap-aws-sts.py           # AWS STS policy gap analysis
│   ├── gap-gcp-wif.py           # GCP WIF policy gap analysis
│   ├── gap-feature-gates.py     # Feature gate gap analysis
│   ├── gap-all.sh               # Orchestrator (runs all analyses)
│   └── generate-combined-report.py # Combined report generator
│
├── skills/                       # Claude AI skills
│   ├── aws-sts-gap/             # AWS STS gap analysis skill
│   ├── gcp-wif-gap/             # GCP WIF gap analysis skill
│   ├── feature-gates-gap/       # Feature gates gap analysis skill
│   └── full-gap-analysis/       # Full gap analysis orchestration
│
├── reports/                      # Generated reports (default location)
├── .prow/                        # Prow CI configuration
├── docs/                         # Documentation
├── REPORTS.md                    # Report generation documentation
└── examples/                     # Example outputs
```

## Gap Analysis Types

### 1. AWS STS Policies (`gap-aws-sts.py`)

Compares AWS Security Token Service (STS) policies between versions to identify:
- New IAM permissions required
- Removed permissions
- Changed permission scopes

**Uses the same approach as `osdctl iampermissions diff`** - extracts CredentialsRequests from release payloads using `oc adm release extract`.

**Example:**
```bash
python3 ./scripts/gap-aws-sts.py --baseline 4.21 --target 4.22
# Exit code 0: Successful execution (regardless of differences)
# Exit code 1: Execution failure
# Reports: ./reports/gap-analysis-aws-sts_*.{md,html,json}
```

### 2. GCP WIF Policies (`gap-gcp-wif.py`)

Compares Google Cloud Workload Identity Federation policies to identify:
- New GCP IAM roles/permissions
- Removed permissions
- Service account changes

**Uses the same approach as AWS STS** - extracts CredentialsRequests from release payloads using `oc adm release extract --cloud=gcp`.

**Example:**
```bash
python3 ./scripts/gap-gcp-wif.py --baseline 4.21 --target 4.22
# Exit code 0: Successful execution (regardless of differences)
# Exit code 1: Execution failure
# Reports: ./reports/gap-analysis-gcp-wif_*.{md,html,json}
```

### 3. Feature Gates (`gap-feature-gates.py`)

Compares feature gates between OpenShift versions using the Sippy API to identify:
- New feature gates added
- Feature gates removed
- Gates newly enabled by default
- Gates removed from default

**Uses Sippy Feature Gates API** - queries feature gate data for specified versions.

**Example:**
```bash
python3 ./scripts/gap-feature-gates.py --baseline 4.21 --target 4.22
# Exit code 0: Successful execution (regardless of differences)
# Exit code 1: Execution failure
# Reports: ./reports/gap-analysis-feature-gates_*.{md,html,json}
```

### 3. OpenShift Release Information Library (`lib/openshift-releases.sh`)

A comprehensive library for querying OpenShift release data from Sippy API and OCP release streams.

**Key Features:**
- Auto-detect latest GA, dev, stable, and candidate versions
- Version validation (dev = GA + 1, candidate belongs to dev, stable belongs to GA)
- Fetch release image pullspecs
- Query nightly builds
- Both CLI and library (sourceable) interface

**CLI Usage:**
```bash
# Query versions
./scripts/lib/openshift-releases.sh --latest-ga              # 4.21
./scripts/lib/openshift-releases.sh --latest-dev             # 4.22 (GA+1)
./scripts/lib/openshift-releases.sh --latest-stable          # 4.21.6
./scripts/lib/openshift-releases.sh --latest-candidate       # 4.22.0-ec.3
./scripts/lib/openshift-releases.sh --latest-nightly         # 4.22.0-0.nightly-...

# Get pullspecs
./scripts/lib/openshift-releases.sh --latest-stable-pullspec
# quay.io/openshift-release-dev/ocp-release:4.21.6-x86_64

./scripts/lib/openshift-releases.sh --latest-candidate-pullspec
# quay.io/openshift-release-dev/ocp-release:4.22.0-ec.3-x86_64

./scripts/lib/openshift-releases.sh --latest-nightly-pullspec
# registry.ci.openshift.org/ocp/release:4.22.0-0.nightly-...

# Nightly for specific version
./scripts/lib/openshift-releases.sh --nightly 4.22
```

**Library Usage (in scripts):**
```bash
source scripts/lib/openshift-releases.sh

# Get versions
ga_version=$(get_latest_ga_version)              # 4.21
dev_version=$(get_latest_dev_version)            # 4.22
stable=$(get_latest_stable_version)              # 4.21.6
candidate=$(get_latest_candidate_version)        # 4.22.0-ec.3
nightly=$(get_latest_dev_nightly_version)        # 4.22.0-0.nightly-...

# Get pullspecs
stable_pullspec=$(get_latest_stable_pullspec)
candidate_pullspec=$(get_latest_candidate_pullspec)
nightly_pullspec=$(get_latest_dev_nightly_pullspec)

# Validation functions
validate_version_gap "4.21" "4.22"               # Returns 0 if valid
validate_candidate_belongs_to_version "4.22.0-ec.3" "4.22"
validate_stable_belongs_to_version "4.21.6" "4.21"
```

**Validation Rules:**
- Dev version must be exactly GA + 1 (e.g., GA=4.21, dev=4.22)
- Candidate versions must belong to dev version (e.g., 4.22.0-ec.3 → 4.22)
- Stable versions must belong to GA version (e.g., 4.21.6 → 4.21)
- All validation is automatic when using the library functions

## Script Arguments

### Command-line Flags

All scripts support these optional flags:

```bash
--baseline <version>    # Baseline version (default: auto-detect from latest stable)
                        # Examples: 4.21, 4.21.6, full pullspec
--target <version>      # Target version (default: auto-detect from latest candidate)
                        # Examples: 4.22, 4.22.0-ec.3, full pullspec
--report-dir <path>     # Directory to store reports (default: reports/)
                        # Reports are saved in MD, HTML, and JSON formats
--verbose               # Enable verbose logging
-h, --help              # Show help message
```

### Environment Variables

Override settings using environment variables (lower precedence than CLI flags):

```bash
BASE_VERSION           # Override baseline version
                       # Examples: 4.21.5, 4.21, full pullspec

TARGET_VERSION         # Override target version
                       # Examples: 4.22.0-ec.2, NIGHTLY, CANDIDATE
                       # Special values:
                       #   NIGHTLY - latest dev nightly build
                       #   CANDIDATE - latest dev candidate (default)

REPORT_DIR             # Directory to store reports (default: reports/)
                       # All scripts generate reports in this location
```

### Version Resolution Precedence

Versions are resolved in this order (highest to lowest):
1. **Command-line flags** (`--baseline`, `--target`)
2. **Environment variables** (`BASE_VERSION`, `TARGET_VERSION`)
3. **Auto-detected** (latest stable for baseline, latest candidate for target)

### Auto-Detection Details

When versions are auto-detected:
- **Baseline**: Latest stable release for GA version (e.g., `4.21.6` for GA `4.21`)
- **Target**: Latest candidate release for dev version (e.g., `4.22.0-ec.3` for dev `4.22`)
- **Dev version**: Always exactly GA + 1 (e.g., GA=`4.21`, dev=`4.22`)
- **Pullspecs**: Automatically fetched and used when auto-detecting

**Note:** The `gap-all.sh` script runs analysis for all platforms automatically (AWS STS, GCP WIF, and Feature Gates) and generates a combined report.

**Exit Codes:**
- `0`: Successful execution (regardless of whether differences were found)
- `1`: Execution failure (missing tools, network errors, invalid versions)

**Report Generation:**
Each analysis generates three report formats:
- **Markdown** (`.md`) - Human-readable formatted reports
- **HTML** (`.html`) - Styled web-viewable reports
- **JSON** (`.json`) - Machine-readable structured data

Additionally, `gap-all.sh` generates a combined report aggregating all analyses.

## Comparison Scenarios

### Auto-Detected Analysis (Recommended)
```bash
# Run analysis with auto-detected versions
# Compares latest stable → latest candidate
./scripts/gap-all.sh
echo $?  # 0 = no changes, 1 = changes detected

# Use latest nightly as target
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh

# Individual platform with auto-detection
./scripts/gap-aws-sts.sh
./scripts/gap-gcp-wif.sh
```

### Explicit Version Analysis
```bash
# Run analysis for both AWS STS and GCP WIF: 4.21 → 4.22
./scripts/gap-all.sh --baseline 4.21 --target 4.22
echo $?  # 0 = no changes in any platform, 1 = changes detected

# AWS STS analysis
./scripts/gap-aws-sts.sh --baseline 4.21.6 --target 4.22.0-ec.3

# GCP WIF analysis
./scripts/gap-gcp-wif.sh --baseline 4.21 --target 4.22

# With verbose logging
./scripts/gap-aws-sts.sh --baseline 4.21 --target 4.22 --verbose
```

### Environment Variable Usage
```bash
# Override baseline, auto-detect target
BASE_VERSION=4.21.5 ./scripts/gap-all.sh

# Use specific versions
BASE_VERSION=4.21.5 TARGET_VERSION=4.22.0-ec.2 ./scripts/gap-all.sh

# Compare stable against nightly
TARGET_VERSION=NIGHTLY ./scripts/gap-aws-sts.sh
```

## Output Format

Scripts output log messages to stderr and automatically generate reports in the configured report directory (default: `./reports/`).

**Auto-detected versions (no differences found):**
```
[INFO] Starting AWS STS Policy Gap Analysis
[INFO] Baseline version: 4.21.6
[INFO] Target version: 4.22.0-ec.3
[INFO] Fetching baseline STS policy...
[SUCCESS] Successfully extracted STS policy
[INFO] Fetching target STS policy...
[SUCCESS] Successfully extracted STS policy
[INFO] Comparing STS policies...
[SUCCESS] No policy differences found between 4.21.6 and 4.22.0-ec.3
[SUCCESS] Markdown report generated: reports/gap-analysis-aws-sts_4.21.6_to_4.22.0-ec.3_20260325_120000.md
[SUCCESS] HTML report generated: reports/gap-analysis-aws-sts_4.21.6_to_4.22.0-ec.3_20260325_120000.html
[SUCCESS] JSON report generated: reports/gap-analysis-aws-sts_4.21.6_to_4.22.0-ec.3_20260325_120000.json
```
Exit code: `0` (successful execution, no differences)

**Differences found:**
```
[INFO] Starting AWS STS Policy Gap Analysis
[INFO] Baseline version: 4.21
[INFO] Target version: 4.22
[INFO] Fetching baseline STS policy...
[SUCCESS] Successfully extracted STS policy
[INFO] Fetching target STS policy...
[SUCCESS] Successfully extracted STS policy
[INFO] Comparing STS policies...
[INFO] Policy differences detected: 3 added, 1 removed
[SUCCESS] Markdown report generated: reports/gap-analysis-aws-sts_4.21_to_4.22_20260325_120000.md
[SUCCESS] HTML report generated: reports/gap-analysis-aws-sts_4.21_to_4.22_20260325_120000.html
[SUCCESS] JSON report generated: reports/gap-analysis-aws-sts_4.21_to_4.22_20260325_120000.json
```
Exit code: `0` (successful execution, differences found)

**For detailed analysis**, view the generated reports:
```bash
# View Markdown report
cat reports/gap-analysis-aws-sts_*.md

# Open HTML report in browser
firefox reports/gap-analysis-aws-sts_*.html

# Parse JSON report programmatically
jq '.comparison' reports/gap-analysis-aws-sts_*.json
```

See [REPORTS.md](REPORTS.md) for comprehensive report documentation.

## Examples

See the `examples/` directory for sample outputs:
- `examples/4.21-to-4.22-osd-aws/` - Version upgrade on AWS

## Development

### Testing Scripts Locally

```bash
# Enable verbose mode (see detailed logging)
python3 ./scripts/gap-aws-sts.py --baseline 4.21 --target 4.22 --verbose

# Test GCP WIF analysis
python3 ./scripts/gap-gcp-wif.py --baseline 4.21 --target 4.22 --verbose

# Test feature gates analysis
python3 ./scripts/gap-feature-gates.py --baseline 4.21 --target 4.22 --verbose

# Run all analyses
./scripts/gap-all.sh --baseline 4.21 --target 4.22

# Check execution status (scripts exit 0 on success)
if python3 ./scripts/gap-aws-sts.py --baseline 4.21 --target 4.22; then
  echo "Analysis completed successfully - check reports/ for results"
else
  echo "Analysis execution failed"
fi

# View generated reports
ls -lh reports/
cat reports/gap-analysis-aws-sts_*.md
```

### Comparing with osdctl

You can validate AWS STS results against osdctl:

```bash
# Using osdctl (simple diff)
osdctl iampermissions diff -c aws -b 4.21 -t 4.22

# Using gap-analysis (generates comprehensive reports)
python3 ./scripts/gap-aws-sts.py --baseline 4.21 --target 4.22
cat reports/gap-analysis-aws-sts_*.md
```

Both use the same `oc adm release extract --credentials-requests --cloud=aws` under the hood, but gap-analysis provides:
- Automatic report generation in MD, HTML, and JSON formats
- Structured comparison data for CI/CD integration
- Combined analysis across AWS, GCP, and feature gates

### Extracting Detailed Comparison Data

All scripts automatically generate JSON reports with structured comparison data:

```bash
# Run analysis to generate reports
python3 ./scripts/gap-aws-sts.py --baseline 4.21 --target 4.22

# Extract specific data from JSON report
jq '.comparison.actions.target_only' reports/gap-analysis-aws-sts_*.json  # Added actions
jq '.comparison.actions.baseline_only' reports/gap-analysis-aws-sts_*.json  # Removed actions

# Feature gates comparison
python3 ./scripts/gap-feature-gates.py --baseline 4.21 --target 4.22
jq '.comparison.added' reports/gap-analysis-feature-gates_*.json  # New gates
jq '.comparison.newly_enabled_by_default' reports/gap-analysis-feature-gates_*.json

# Combined report for all platforms
./scripts/gap-all.sh --baseline 4.21 --target 4.22
jq '.aws_sts.comparison' reports/gap-analysis-full_*.json
jq '.gcp_wif.comparison' reports/gap-analysis-full_*.json
jq '.feature_gates.comparison' reports/gap-analysis-full_*.json
```

## Support

For issues or questions:
- Get in touch with ROSA SRE team
