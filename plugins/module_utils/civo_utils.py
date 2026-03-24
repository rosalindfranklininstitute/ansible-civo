# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0
"""
Shared utilities for the civo.cloud Ansible collection.

All modules wrap the ``civo`` CLI binary, authenticating via the
``CIVO_TOKEN`` environment variable or the ``api_key`` module argument.
JSON output (``-o json``) is used throughout so results are machine-readable.
"""

import json
import os
import re
import time

from ansible.module_utils.basic import env_fallback  # noqa: F401 – re-exported

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CIVO_BINARY_DEFAULT = "civo"


# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------


def run_civo_command(module, args, api_key, region, binary=None, check_rc=True):
    """Run a civo CLI command and return (rc, stdout_parsed, stderr).

    Args:
        module:    AnsibleModule instance.
        args:      List of CLI arguments (not including ``civo`` itself).
        api_key:   Civo API token.
        region:    Civo region string (e.g. LON1).
        binary:    Path to the civo binary (default: 'civo').
        check_rc:  Fail the module on non-zero return code when True.

    Returns:
        tuple(rc, parsed_dict_or_list, stderr_str)
    """
    if binary is None:
        binary = CIVO_BINARY_DEFAULT

    cmd = [binary] + list(args) + ["--region", region, "-o", "json", "-y"]

    env = os.environ.copy()
    env["CIVO_TOKEN"] = api_key

    rc, stdout, stderr = module.run_command(cmd, environ_update=env)

    if rc != 0 and check_rc:
        module.fail_json(
            msg="civo command failed: {}".format(" ".join(str(a) for a in cmd)),
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )

    parsed = {}
    if stdout and stdout.strip():
        try:
            parsed = json.loads(stdout)
        except ValueError:
            if check_rc:
                module.fail_json(
                    msg="Failed to parse civo JSON output",
                    stdout=stdout,
                    stderr=stderr,
                    rc=rc,
                )

    return rc, parsed, stderr


# ---------------------------------------------------------------------------
# Generic lookup helpers
# ---------------------------------------------------------------------------


def find_resource_by_name(module, resource_type, name, api_key, region, binary=None):
    """Return the first resource dict whose name matches *name*, or None.

    Unlike a naive ``None``-on-error approach, this function distinguishes
    between a genuine "not found" (empty list) and a CLI error so that real
    failures are surfaced rather than silently treated as absent resources.
    """
    rc, data, stderr = run_civo_command(
        module,
        [resource_type, "ls"],
        api_key,
        region,
        binary=binary,
        check_rc=False,
    )

    if rc != 0:
        # Propagate only if this looks like a real error (not an empty-list
        # response that some CLI versions return with rc=1).
        if stderr and "no " not in stderr.lower() and "not found" not in stderr.lower():
            module.fail_json(
                msg=f"civo {resource_type} ls failed",
                rc=rc,
                stderr=stderr,
            )
        return None

    items = data if isinstance(data, list) else data.get("items", [])
    for item in items:
        # Different resource types use different fields for their display name:
        #   network     → "label"
        #   instance    → "hostname"
        #   all others  → "name"
        if resource_type == "network":
            if item.get("label") == name:
                return item
        elif resource_type == "instance":
            if item.get("hostname") == name:
                return item
        else:
            if item.get("name") == name:
                return item
    return None


# ---------------------------------------------------------------------------
# Wait helper
# ---------------------------------------------------------------------------


def wait_for_active(
    module,
    resource_type,
    name,
    api_key,
    region,
    binary=None,
    timeout=600,
    interval=15,
):
    """Poll until the named resource reaches an active/ready state.

    Handles both string ``status`` fields and boolean ``ready`` fields that
    the Civo CLI emits depending on resource type. Returns the final resource
    dict or calls ``module.fail_json`` on timeout or error.
    """
    deadline = time.time() + timeout
    # Regex to strip ANSI escape codes from status strings
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    while time.time() < deadline:
        resource = find_resource_by_name(module, resource_type, name, api_key, region, binary=binary)
        if resource is None:
            time.sleep(interval)
            continue

        raw_status = resource.get("status") or ""
        status_str = ansi_escape.sub("", raw_status).strip().upper()
        ready_val = resource.get("ready")

        # Boolean ready field (e.g. Kubernetes clusters)
        if ready_val is True or (isinstance(ready_val, str) and ready_val.lower() == "true"):
            return resource

        # String status field
        if status_str in ("ACTIVE", "READY", "RUNNING"):
            return resource
        if status_str in ("FAILED", "ERROR"):
            module.fail_json(
                msg=f"Resource '{name}' entered {status_str} state",
                resource=resource,
            )

        time.sleep(interval)

    module.fail_json(msg=f"Timed out after {timeout}s waiting for '{name}' to become active")


# ---------------------------------------------------------------------------
# Common argument spec shared by every module
# ---------------------------------------------------------------------------


def common_argument_spec():
    """Return the argument_spec entries shared by all civo.cloud modules.

    Note: ``api_key`` uses Ansible's ``env_fallback`` mechanism so that
    ``CIVO_TOKEN`` in the environment is transparently used when the
    parameter is not passed explicitly.  ``required`` is intentionally
    omitted — the env fallback fires only when ``required`` is not True.
    """
    return {
        "api_key": {
            "type": "str",
            "no_log": True,
            "fallback": (env_fallback, ["CIVO_TOKEN"]),
        },
        "region": {"type": "str", "default": "LON1"},
        "state": {"type": "str", "default": "present", "choices": ["present", "absent"]},
        "civo_binary": {"type": "str", "default": CIVO_BINARY_DEFAULT},
    }
