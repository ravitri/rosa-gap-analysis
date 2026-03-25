---
name: gcp-wif-gap
description: >
  Analyze GCP Workload Identity Federation (WIF) policy gaps between OpenShift versions.
  Use when comparing WIF configurations, IAM roles, and service account permissions
  across OpenShift versions.
  Logs detected policy differences but always exits 0 on successful execution.
compatibility:
  required_tools:
    - bash
    - oc (OpenShift CLI - for extracting credential requests)
    - jq (for JSON processing)
    - yq or python3 with PyYAML (for YAML parsing)
---

# GCP WIF Policy Gap Analysis

Analyze differences in GCP Workload Identity Federation policies between OpenShift versions.

## When to Use

- Comparing WIF policies between versions
- Planning GCP-based upgrades
- Investigating WIF permission issues
- Understanding service account changes
- CI/CD pipelines that need to detect policy changes

## Workflow

1. Parse baseline and target versions (default: auto-detect latest stable → latest candidate)
2. Extract credential requests from release payloads using `oc adm release extract --cloud=gcp`
3. Convert CredentialsRequest YAML manifests to GCP IAM policy format
4. Compare IAM roles, permissions, and service account bindings
5. Log detected differences and always exit 0 on successful execution

## Script Usage

**Auto-detect versions (recommended):**
```bash
# Compares latest stable → latest candidate
./scripts/gap-gcp-wif.sh

# Use nightly as target
TARGET_VERSION=NIGHTLY ./scripts/gap-gcp-wif.sh
```

**Explicit versions:**
```bash
./scripts/gap-gcp-wif.sh \
  --baseline <version> \
  --target <version> \
  [--verbose]
```

**Examples:**
```bash
# Auto-detect
./scripts/gap-gcp-wif.sh

# Explicit versions
./scripts/gap-gcp-wif.sh --baseline 4.21 --target 4.22 --verbose

# Full version strings
./scripts/gap-gcp-wif.sh --baseline 4.21.6 --target 4.22.0-ec.3

# Environment variables
BASE_VERSION=4.21.5 TARGET_VERSION=4.22.0-ec.2 ./scripts/gap-gcp-wif.sh

# Use nightly
TARGET_VERSION=NIGHTLY ./scripts/gap-gcp-wif.sh
```

**Exit Codes:**
- `0`: Successful execution (regardless of whether differences were found)
- `1`: Execution failure (e.g., missing tools, network errors, invalid versions)

**Version Resolution:**
- CLI flags > Environment variables > Auto-detect
- Auto-detect: latest stable (baseline) → latest candidate (target)
- Special keywords: `TARGET_VERSION=NIGHTLY` or `TARGET_VERSION=CANDIDATE`

Note: Platform is always 'gcp' for this script.

## Key Focus Areas

- **IAM Roles**: New or removed GCP IAM roles
- **Permissions**: Individual permission changes within roles
- **Service Accounts**: Changes to GCP service account configurations
- **Workload Identity Pools**: Pool and provider configuration changes
- **Bindings**: Service account to Kubernetes service account bindings

## Output

The script outputs log messages to stderr and always exits 0 on successful execution:

```
[INFO] Starting GCP WIF Policy Gap Analysis
[INFO] Baseline version: 4.21
[INFO] Target version: 4.22
[INFO] Fetching baseline WIF policy...
[SUCCESS] Successfully extracted WIF policy
[INFO] Fetching target WIF policy...
[SUCCESS] Successfully extracted WIF policy
[INFO] Comparing WIF policies...
[INFO] Policy differences detected: 5 added, 2 removed
```

Exit code: `0` (successful execution, differences found)

Or:

```
[SUCCESS] No policy differences found between 4.21 and 4.22
```

Exit code: `0` (successful execution, no differences)

**Use in CI/CD:**
```bash
# Script always exits 0 on success
./scripts/gap-gcp-wif.sh --baseline 4.21 --target 4.22

# Check for differences by parsing output
if ./scripts/gap-gcp-wif.sh --baseline 4.21 --target 4.22 2>&1 | grep -q "Policy differences detected"; then
  echo "Policy changes detected - review recommended"
else
  echo "No policy changes - safe to proceed"
fi
```

## Going Beyond the Script

The script provides a simple pass/fail check. For detailed analysis, you can:

**Extract Detailed Comparison Data:**
If you need to analyze what changed, you can run the comparison functions manually:
```bash
# Extract policies to temp files
baseline_policy=$(mktemp)
target_policy=$(mktemp)

# Get policies (using functions from the script)
source scripts/lib/common.sh
source scripts/gap-gcp-wif.sh
get_wif_policy "4.21" > "$baseline_policy"
get_wif_policy "4.22" > "$target_policy"

# Compare and examine results
compare_sts_policies "$baseline_policy" "$target_policy" | jq '.'
```

**Context and Explanation:**
- Explain why WIF permissions changed
- Connect changes to OpenShift features and enhancements
- Identify patterns across versions

**Security Analysis:**
- Assess security posture changes
- Highlight permissions with broad scopes
- Recommend least-privilege alternatives

**Customer Impact:**
- Identify if changes require customer action
- Provide migration guides for complex changes
- Suggest pre-upgrade validation steps

**CI/CD Integration:**
- Parse script output to detect policy changes (exit codes only indicate execution success/failure)
- Script always exits 0 on successful execution regardless of differences
- Automate notifications when policies differ by parsing log messages
