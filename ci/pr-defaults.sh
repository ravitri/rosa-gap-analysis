#!/bin/bash
# =============================================================================
# Standard PR Configuration for fix-prow-failure.sh
# This file is committed to the repository and contains standard defaults.
# =============================================================================

# Target repository (production upstream) - standardized
TARGET_REPO="openshift/managed-cluster-config"

# Git commit identity for automated PRs - standardized
GIT_USER_NAME="ROSA Gap Analysis Bot"
GIT_USER_EMAIL="rosa-gap-analysis-bot@redhat.com"

# GitHub username for bot authentication - standardized
GITHUB_USERNAME="rosa-gap-analysis-bot"

# Fork repository (bot's fork) - standardized
FORK_REPO="rosa-gap-analysis-bot/managed-cluster-config"

# =============================================================================
# Optional configuration (override via env vars or flags)
# =============================================================================
# All values above can be overridden if needed:
#   - Via environment variables (e.g., export FORK_REPO="...")
#   - Via command-line flags (e.g., --fork-repo)
#
# TEST_REPO (only needed for --test-mode):
#   - Via environment variable: export TEST_REPO="your-user/test-repo"
#   - Via command-line flag: --test-repo "your-user/test-repo"
