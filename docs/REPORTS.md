# Gap Analysis Reports

All gap analysis scripts automatically generate reports in multiple formats when executed.

## Report Formats

Each script execution generates three report files:

1. **Markdown (.md)** - Human-readable text format
2. **HTML (.html)** - Rich formatted report for viewing in browsers
3. **JSON (.json)** - Machine-readable data for automation

## Report Naming Convention

Reports are automatically named with timestamps:

```
gap-analysis-{type}_{baseline}_to_{target}_{timestamp}.{format}
```

**Examples:**
```
gap-analysis-aws-sts_4.20_to_4.21_20260325_153237.md
gap-analysis-aws-sts_4.20_to_4.21_20260325_153237.html
gap-analysis-aws-sts_4.20_to_4.21_20260325_153237.json

gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.md
gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.html
gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.json

gap-analysis-full_4.20_to_4.21_20260325_153500.md
gap-analysis-full_4.20_to_4.21_20260325_153500.html
gap-analysis-full_4.20_to_4.21_20260325_153500.json
```

## Individual Script Reports

### AWS STS Gap Analysis

```bash
python3 scripts/gap-aws-sts.py --baseline 4.20 --target 4.21
```

Generates:
- `gap-analysis-aws-sts_4.20_to_4.21_YYYYMMDD_HHMMSS.md`
- `gap-analysis-aws-sts_4.20_to_4.21_YYYYMMDD_HHMMSS.html`
- `gap-analysis-aws-sts_4.20_to_4.21_YYYYMMDD_HHMMSS.json`

**Report Contents:**
- Added IAM actions/permissions
- Removed IAM actions/permissions
- Total changes summary
- Timestamp and version information

### GCP WIF Gap Analysis

```bash
python3 scripts/gap-gcp-wif.py --baseline 4.20 --target 4.21
```

Generates:
- `gap-analysis-gcp-wif_4.20_to_4.21_YYYYMMDD_HHMMSS.md`
- `gap-analysis-gcp-wif_4.20_to_4.21_YYYYMMDD_HHMMSS.html`
- `gap-analysis-gcp-wif_4.20_to_4.21_YYYYMMDD_HHMMSS.json`

**Report Contents:**
- Added GCP IAM permissions
- Removed GCP IAM permissions
- Total changes summary
- Timestamp and version information

### Feature Gate Gap Analysis

```bash
python3 scripts/gap-feature-gates.py --baseline 4.20 --target 4.21
```

Generates:
- `gap-analysis-feature-gates_4.20_to_4.21_YYYYMMDD_HHMMSS.md`
- `gap-analysis-feature-gates_4.20_to_4.21_YYYYMMDD_HHMMSS.html`
- `gap-analysis-feature-gates_4.20_to_4.21_YYYYMMDD_HHMMSS.json`

**Report Contents:**
- New feature gates
- Removed feature gates
- Newly enabled by default
- Removed from default
- Total changes summary
- Timestamp and version information

## Combined Report (gap-all.sh)

When running the full gap analysis orchestrator:

```bash
bash scripts/gap-all.sh --baseline 4.20 --target 4.21
```

**Generates individual reports for each analysis PLUS a combined report:**

- `gap-analysis-full_4.20_to_4.21_YYYYMMDD_HHMMSS.md`
- `gap-analysis-full_4.20_to_4.21_YYYYMMDD_HHMMSS.html`
- `gap-analysis-full_4.20_to_4.21_YYYYMMDD_HHMMSS.json`

**Combined Report Contents:**
- AWS STS analysis summary
- GCP WIF analysis summary
- Feature Gates analysis summary
- Aggregate statistics
- Timestamp and version information

## Viewing Reports

### Markdown Reports (.md)

View in any text editor or markdown viewer:
```bash
cat gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.md
```

Or use a markdown preview tool:
```bash
mdless gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.md
```

### HTML Reports (.html)

Open in any web browser:
```bash
firefox gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.html
```

Or:
```bash
open gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.html  # macOS
xdg-open gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.html  # Linux
```

**Features:**
- Professional styling with tables
- Color-coded changes (green for added, red for removed, orange for changed)
- Responsive design
- Print-friendly layout

### JSON Reports (.json)

Process programmatically:
```bash
jq '.' gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.json
```

Parse in scripts:
```python
import json
with open('gap-analysis-feature-gates_4.20_to_4.21_20260325_153237.json') as f:
    data = json.load(f)
    print(f"Total changes: {data['summary']['total_changes']}")
```

## Report Location

Reports are generated in the **current working directory** where the script is executed.

To specify a different location:
```bash
cd /path/to/reports
python3 /path/to/scripts/gap-aws-sts.py --baseline 4.20 --target 4.21
```

## CI/CD Integration

### Archiving Reports

```yaml
# In ci-operator config
- as: gap-analysis-all
  commands: |
    gap-all.sh --baseline 4.20 --target 4.21
  container:
    from: src
  artifacts:
    - name: gap-analysis-reports
      path: gap-analysis-*.html
    - name: gap-analysis-reports
      path: gap-analysis-*.md
    - name: gap-analysis-reports
      path: gap-analysis-*.json
```

### Parsing JSON for Automation

```bash
#!/bin/bash
# Check if any differences were found
REPORT=$(ls -t gap-analysis-full_*.json | head -1)

AWS_CHANGES=$(jq '.aws_sts.summary.total_changes' "$REPORT")
GCP_CHANGES=$(jq '.gcp_wif.summary.total_changes' "$REPORT")
FG_CHANGES=$(jq '.feature_gates.summary.total_changes' "$REPORT")

if [ $AWS_CHANGES -gt 0 ] || [ $GCP_CHANGES -gt 0 ] || [ $FG_CHANGES -gt 0 ]; then
    echo "Changes detected - review required"
    # Send notification, create Jira ticket, etc.
fi
```

## Report Customization

The report generation is handled by `scripts/lib/reporters.py`. To customize:

1. Edit report templates in `reporters.py`
2. Modify CSS styles in HTML report generator
3. Add new report formats (PDF, Excel, etc.)

See `scripts/lib/reporters.py` for implementation details.

## Troubleshooting

### Reports Not Generated

Check that the script completed successfully:
```bash
echo $?  # Should be 0
```

### Missing Reports

Verify you have write permissions in the current directory:
```bash
pwd
ls -la
```

### Large Reports

For versions with many changes, reports can be large. Use JSON for programmatic processing:
```bash
jq '.summary' gap-analysis-*.json  # Get summary only
```

## Future Enhancements

Planned features:
- PDF report generation
- Excel spreadsheet export
- Email notifications with attached reports
- Slack/Teams integration for posting reports
- Chart/graph generation for trends over time
