#!/usr/bin/env python3
"""OpenShift release version utilities using Sippy API."""

import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError

from common import log_info, log_error


SIPPY_API = "https://sippy.dptools.openshift.org/api/releases"


def fetch_sippy_releases():
    """Fetch all releases from Sippy API."""
    try:
        req = Request(SIPPY_API, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=10) as response:
            data = response.read()
            return json.loads(data)
    except (URLError, json.JSONDecodeError) as e:
        log_error(f"Failed to fetch releases from Sippy API: {e}")
        sys.exit(1)


def get_latest_stable_version():
    """Get the latest stable OpenShift version."""
    releases = fetch_sippy_releases()

    # Filter for GA releases (no -rc, -ec, -nightly)
    stable_releases = [
        r for r in releases
        if r.get('phase') == 'GA'
        and '-rc' not in r['release']
        and '-ec' not in r['release']
        and 'nightly' not in r['release'].lower()
    ]

    if not stable_releases:
        log_error("No stable releases found in Sippy API")
        sys.exit(1)

    # Get the most recent stable (assumes sorted by release date)
    latest = stable_releases[0]
    return extract_minor_version(latest['release'])


def get_latest_candidate_version():
    """Get the latest candidate OpenShift version."""
    releases = fetch_sippy_releases()

    # Filter for candidate releases (-ec or -rc)
    candidate_releases = [
        r for r in releases
        if '-ec' in r['release'] or '-rc' in r['release']
    ]

    if not candidate_releases:
        log_error("No candidate releases found in Sippy API")
        sys.exit(1)

    # Get the most recent candidate
    latest = candidate_releases[0]
    return extract_minor_version(latest['release'])


def get_latest_dev_nightly_version():
    """Get the latest dev nightly OpenShift version."""
    releases = fetch_sippy_releases()

    # Filter for nightly releases
    nightly_releases = [
        r for r in releases
        if 'nightly' in r['release'].lower()
    ]

    if not nightly_releases:
        log_error("No nightly releases found in Sippy API")
        sys.exit(1)

    # Get the most recent nightly
    latest = nightly_releases[0]
    return extract_minor_version(latest['release'])


def extract_minor_version(version_string):
    """Extract minor version (e.g., '4.21' from '4.21.5')."""
    parts = version_string.split('.')
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return version_string


def resolve_baseline_version(cli_arg=None, env_var=None):
    """
    Resolve baseline version with precedence: CLI > ENV > Auto-detect.

    Args:
        cli_arg: Version from CLI argument (--baseline)
        env_var: Version from environment variable (BASE_VERSION)

    Returns:
        str: Resolved version string
    """
    if cli_arg:
        log_info(f"Using baseline version from CLI: {cli_arg}")
        return cli_arg
    elif env_var:
        log_info(f"Using baseline version from BASE_VERSION env: {env_var}")
        return env_var
    else:
        log_info("Auto-detecting baseline version from latest stable...")
        version = get_latest_stable_version()
        log_info(f"Auto-detected baseline version: {version}")
        return version


def resolve_target_version(cli_arg=None, env_var=None):
    """
    Resolve target version with precedence: CLI > ENV > Auto-detect.

    Args:
        cli_arg: Version from CLI argument (--target)
        env_var: Version from environment variable (TARGET_VERSION)

    Returns:
        str: Resolved version string
    """
    if cli_arg:
        log_info(f"Using target version from CLI: {cli_arg}")
        return cli_arg
    elif env_var:
        # Check if TARGET_VERSION is a special keyword
        if env_var.upper() == 'NIGHTLY':
            log_info("TARGET_VERSION=NIGHTLY detected, using latest dev nightly...")
            version = get_latest_dev_nightly_version()
            log_info(f"Auto-detected nightly target version: {version}")
            return version
        elif env_var.upper() == 'CANDIDATE':
            log_info("TARGET_VERSION=CANDIDATE detected, using latest candidate...")
            version = get_latest_candidate_version()
            log_info(f"Auto-detected candidate target version: {version}")
            return version
        else:
            log_info(f"Using target version from TARGET_VERSION env: {env_var}")
            return env_var
    else:
        log_info("Auto-detecting target version from latest candidate...")
        version = get_latest_candidate_version()
        log_info(f"Auto-detected target version: {version}")
        return version
