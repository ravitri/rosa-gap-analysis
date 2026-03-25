---
name: full-gap-analysis
description: >
  Comprehensive gap analysis between OpenShift versions covering AWS STS policies,
  GCP WIF policies, and feature gates. Use when performing complete version upgrade
  assessment for managed OpenShift (OSD, ROSA).
  Logs detected differences but always exits 0 on successful execution.
compatibility:
  required_tools:
    - oc
    - jq
    - yq or python3
---

# Full Gap Analysis

Orchestrate comprehensive gap analysis across OpenShift versions.
Automatically analyzes AWS STS policies, GCP WIF policies, and feature gates.

## When to Use

- Planning major version upgrades (e.g., 4.21 → 4.22)
- Comparing platform variants (ROSA Classic vs HCP)
- Cross-cloud comparison (OSD AWS vs GCP)
- Complete upgrade impact assessment for IAM/WIF policies
- Quarterly upgrade planning
- CI/CD pipelines that need to detect policy changes

## What This Analyzes

Automatically analyzes all of:

1. **AWS STS IAM Policies**
   - IAM permission changes
   - Service account requirements
   - Security posture changes

2. **GCP WIF Configurations**
   - Workload Identity Federation changes
   - GCP IAM role/permission changes
   - Service account bindings

3. **Feature Gates**
   - New feature gates added
   - Feature gates removed
   - Gates newly enabled by default
   - Gates removed from default

The script runs all analyses and reports if differences exist in any area.

## Workflow

### Step 1: Parse Request

Understand the comparison being requested:
- Baseline version (default: auto-detect latest stable)
- Target version (default: auto-detect latest candidate)
- Specific focus areas (if any)

The analysis automatically covers both AWS STS and GCP WIF platforms.

### Step 2: Use the Orchestrator Script

The `scripts/gap-all.sh` script runs credential policy analysis for both AWS and GCP:

**Auto-detect versions (recommended):**
```bash
# Compares latest stable → latest candidate
./scripts/gap-all.sh

# Use nightly as target
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh
```

**Explicit versions:**
```bash
./scripts/gap-all.sh --baseline 4.21 --target 4.22

# With full version strings
./scripts/gap-all.sh --baseline 4.21.6 --target 4.22.0-ec.3
```

**Environment variables:**
```bash
# Override versions
BASE_VERSION=4.21.5 TARGET_VERSION=4.22.0-ec.2 ./scripts/gap-all.sh

# Use nightly
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh
```

The script:
- Auto-detects versions if not specified (stable → candidate)
- Runs AWS STS policy analysis (Python)
- Runs GCP WIF policy analysis (Python)
- Runs feature gate analysis (Python)
- Generates individual reports for each analysis (MD, HTML, JSON)
- Generates combined report aggregating all analyses
- Logs detected differences to stdout/stderr
- Always exits 0 on successful execution (regardless of differences)
- Only exits 1 on execution failures (missing tools, network errors, etc.)

**Report Files Generated:**
- `reports/gap-analysis-aws-sts_*.{md,html,json}`
- `reports/gap-analysis-gcp-wif_*.{md,html,json}`
- `reports/gap-analysis-feature-gates_*.{md,html,json}`
- `reports/gap-analysis-full_*.{md,html,json}` (combined report)

**Use in CI/CD:**
```bash
# Auto-detect versions (script always exits 0 on success)
./scripts/gap-all.sh

# Test against nightly
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh

# Check for differences by parsing output
if ./scripts/gap-all.sh 2>&1 | grep -q "Policy differences detected"; then
  echo "Policy changes detected - review recommended"
else
  echo "No policy changes - safe to proceed"
fi
```

### Step 3: Interpret Results

The script provides pass/fail indication via exit codes. For detailed analysis:

**Extract comparison data manually:**
```bash
# Source the functions
source scripts/lib/common.sh
source scripts/gap-aws-sts.sh  # or gap-gcp-wif.sh

# Extract policies
baseline_policy=$(mktemp)
target_policy=$(mktemp)
get_sts_policy "4.21" > "$baseline_policy"
get_sts_policy "4.22" > "$target_policy"

# Compare and analyze
compare_sts_policies "$baseline_policy" "$target_policy" | jq '.'
```

### Step 4: Perform Deep Analysis

Go beyond the scripts by:
- **Security assessment**: Evaluate new permissions for security implications
- **Impact assessment**: Prioritize IAM/WIF changes by criticality
- **Timeline analysis**: Identify upgrade blockers related to credentials
- **Customer communication**: Draft IAM policy update notices

## Output

The script outputs log messages for both platforms and always exits 0 on successful execution:

**No differences:**
```
[INFO] OpenShift Gap Analysis Suite
[INFO] Baseline: 4.21
[INFO] Target: 4.22
[INFO] Platforms: AWS STS, GCP WIF, Feature Gates

[INFO] Running AWS STS Policy Gap Analysis...
[SUCCESS] No AWS STS policy differences found

[INFO] Running GCP WIF Policy Gap Analysis...
[SUCCESS] No GCP WIF policy differences found

[INFO] Running Feature Gates Gap Analysis...
[SUCCESS] No feature gate differences found between 4.21 and 4.22

[INFO] Gap Analysis Complete!
[SUCCESS] No policy or feature gate differences found
```
Exit code: `0` (successful execution, no differences)

**Differences found:**
```
[INFO] OpenShift Gap Analysis Suite
[INFO] Baseline: 4.21
[INFO] Target: 4.22
[INFO] Platforms: AWS STS, GCP WIF, Feature Gates

[INFO] Running AWS STS Policy Gap Analysis...
[INFO] Policy differences detected: 3 added, 1 removed

[INFO] Running GCP WIF Policy Gap Analysis...
[SUCCESS] No GCP WIF policy differences found

[INFO] Running Feature Gates Gap Analysis...
[INFO] Feature gate differences detected:
[INFO]   - New feature gates: 5
[INFO]   - Newly enabled by default: 2

[INFO] Gap Analysis Complete!
[INFO] AWS STS: Policy differences detected
[INFO] Feature Gates: Differences detected
[INFO] Differences detected - review recommended
```
Exit code: `0` (successful execution, differences found)

## Comparison Scenarios

### Version Upgrade (All Platforms)
```
Baseline: 4.21
Target: 4.22
```
Analyzes all of:
- AWS STS IAM policy changes
- GCP WIF policy changes
- Feature gate changes

Logs differences but always exits 0 on successful execution.

## Enhanced Analysis

Provide additional insights:

### Prioritization Matrix
| Change | Impact | Effort | Priority |
|--------|--------|--------|----------|
| New STS permission | High | Low | P0 |
| Removed WIF role | High | Medium | P0 |
| Changed permission scope | Medium | Low | P1 |

### Timeline Recommendations
- **Before upgrade**: Update IAM roles/policies in AWS/GCP
- **During upgrade**: Monitor for permission denied errors
- **After upgrade**: Validate all credential-dependent workloads

### Risk Assessment
- **High risk**: New required permissions, removed roles
- **Medium risk**: Changed permission scopes
- **Low risk**: Added optional permissions

## Going Beyond Scripts

While scripts provide credential policy data, add strategic value:
- Executive summaries for leadership
- Technical deep-dives for platform engineers
- Customer-facing IAM policy update guides
- Security risk mitigation strategies
- Rollback procedures for IAM changes

## Example Interaction

**User**: "Check if policies changed between latest stable and latest candidate"

**Response**:
```bash
# Auto-detect versions
./scripts/gap-all.sh
```

**User**: "Check if policies changed between 4.21 and 4.22"

**Response**:
```bash
./scripts/gap-all.sh --baseline 4.21 --target 4.22
```

**User**: "Check against latest nightly"

**Response**:
```bash
TARGET_VERSION=NIGHTLY ./scripts/gap-all.sh
```

**If no changes:**
```
[INFO] OpenShift Gap Analysis Suite
[INFO] Running AWS STS Policy Gap Analysis...
[SUCCESS] No AWS STS policy differences found
[INFO] Running GCP WIF Policy Gap Analysis...
[SUCCESS] No GCP WIF policy differences found
[INFO] Running Feature Gates Gap Analysis...
[SUCCESS] No feature gate differences found between 4.21 and 4.22
[SUCCESS] No policy or feature gate differences found
```
Exit code: `0` - Successful execution, no differences

**If changes detected:**
```
[INFO] OpenShift Gap Analysis Suite
[INFO] Running AWS STS Policy Gap Analysis...
[INFO] Policy differences detected: 3 added, 1 removed
[INFO] Running GCP WIF Policy Gap Analysis...
[SUCCESS] No GCP WIF policy differences found
[INFO] Running Feature Gates Gap Analysis...
[INFO] Feature gate differences detected:
[INFO]   - New feature gates: 5
[INFO] AWS STS: Policy differences detected
[INFO] Feature Gates: Differences detected
[INFO] Differences detected - review recommended
```
Exit code: `0` - Successful execution, differences found

**Next steps when changes detected:**
1. Run individual platform scripts to get detailed information
2. Extract detailed comparison data using the comparison functions
3. Analyze policy changes in depth
4. Assess security implications of new permissions
5. Evaluate upgrade complexity based on IAM/WIF changes
6. Generate prioritized update action plan
7. Provide go/no-go recommendation with security justification
