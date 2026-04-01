#!/usr/bin/env python3
"""OpenShift release version utilities using release streams API."""

import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError

from common import log_info, log_error


SIPPY_API = "https://sippy.dptools.openshift.org/api/releases"
RELEASE_STREAM_BASE = "https://amd64.ocp.releases.ci.openshift.org/api/v1/releasestream"
DEV_PREVIEW_STREAM = "4-dev-preview"
STABLE_STREAM = "4-stable"


def fetch_sippy_ga_dates():
    """Fetch GA dates from Sippy API."""
    try:
        req = Request(SIPPY_API, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=10) as response:
            data = response.read()
            return json.loads(data).get('ga_dates', {})
    except (URLError, json.JSONDecodeError) as e:
        log_error(f"Failed to fetch GA dates from Sippy API: {e}")
        sys.exit(1)


def get_latest_ga_version():
    """Get the latest GA version from Sippy API."""
    ga_dates = fetch_sippy_ga_dates()
    if not ga_dates:
        log_error("No GA versions found in Sippy API")
        sys.exit(1)

    # Sort versions and get the latest
    versions = sorted(ga_dates.keys(), key=lambda v: list(map(int, v.split('.'))))
    return versions[-1]


def get_latest_stable_version():
    """Get the latest stable OpenShift version from stable stream."""
    try:
        url = f"{RELEASE_STREAM_BASE}/{STABLE_STREAM}/tags"
        req = Request(url, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            tags = data.get('tags', [])
            if not tags:
                log_error(f"No tags found in {STABLE_STREAM} stream")
                sys.exit(1)
            # Tags are sorted by date, first is most recent
            return tags[0]['name']
    except (URLError, json.JSONDecodeError, KeyError) as e:
        log_error(f"Failed to fetch latest stable version: {e}")
        sys.exit(1)


def get_latest_candidate_version():
    """Get the latest candidate OpenShift version from dev-preview stream."""
    try:
        url = f"{RELEASE_STREAM_BASE}/{DEV_PREVIEW_STREAM}/tags"
        req = Request(url, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            tags = data.get('tags', [])
            if not tags:
                log_error(f"No tags found in {DEV_PREVIEW_STREAM} stream")
                sys.exit(1)
            # Tags are sorted by date, first is most recent
            return tags[0]['name']
    except (URLError, json.JSONDecodeError, KeyError) as e:
        log_error(f"Failed to fetch latest candidate version: {e}")
        sys.exit(1)


def get_latest_dev_nightly_version():
    """Get the latest dev nightly OpenShift version."""
    # Get the latest GA version
    ga_version = get_latest_ga_version()

    # Calculate dev version (GA + 1)
    parts = ga_version.split('.')
    dev_minor = int(parts[1]) + 1
    dev_version = f"{parts[0]}.{dev_minor}"

    try:
        url = f"{RELEASE_STREAM_BASE}/{dev_version}.0-0.nightly/latest?rel=1"
        req = Request(url, headers={'User-Agent': 'gap-analysis-script'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            nightly_name = data.get('name')
            if not nightly_name:
                log_error(f"No nightly version found for {dev_version}")
                sys.exit(1)
            return nightly_name
    except (URLError, json.JSONDecodeError, KeyError) as e:
        log_error(f"Failed to fetch latest nightly version: {e}")
        sys.exit(1)


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
