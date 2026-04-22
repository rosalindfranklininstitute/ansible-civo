# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0
"""
Shared utilities for the civo.cloud Ansible collection.

All modules wrap the ``civo`` CLI binary.  Authentication is resolved in
order: explicit ``api_key`` parameter → ``CIVO_TOKEN`` environment variable →
active key in ``~/.civo.json`` (the civo CLI config file).
JSON output (``-o json``) is used throughout so results are machine-readable.
"""

import json
import os
import re
import time

from ansible.module_utils.basic import AnsibleFallbackNotFound

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CIVO_BINARY_DEFAULT = "civo"

# Matches a standard RFC 4122 UUID (case-insensitive).
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_uuid(value):
    """Return True if *value* looks like a Civo resource UUID."""
    return bool(_UUID_RE.match(value))


def _civo_api_key_fallback(*args, **_kwargs):
    """Ansible fallback that checks CIVO_TOKEN then ~/.civo.json.

    Priority:
    1. ``CIVO_TOKEN`` environment variable.
    2. The active API key stored in ``~/.civo.json`` (populated by
       ``civo apikey add`` / ``civo apikey ls``).

    Raises ``AnsibleFallbackNotFound`` if neither source yields a value,
    which causes Ansible to leave the parameter as ``None`` so that the
    module's own ``fail_json`` check runs with a user-friendly message.
    """
    # 1. Environment variable
    token = os.environ.get("CIVO_TOKEN")
    if token:
        return token

    # 2. ~/.civo.json — the civo CLI config file
    config_path = os.path.expanduser("~/.civo.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path) as fh:
                config = json.load(fh)
            key_name = config.get("meta", {}).get("current_apikey", "")
            if key_name:
                key = config.get("apikeys", {}).get(key_name)
                if key:
                    return key
        except (OSError, ValueError):
            # OSError: permission denied or file vanished between isfile() and open()
            # ValueError: json.load() failed on a corrupt config file
            pass

    raise AnsibleFallbackNotFound


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
    """Return the resource dict whose name matches *name*, or None.

    Unlike a naive ``None``-on-error approach, this function distinguishes
    between a genuine "not found" (empty list) and a CLI error so that real
    failures are surfaced rather than silently treated as absent resources.

    Fails hard if more than one resource with the same name is found.  Name
    collisions should not occur in a healthy Civo account, but if they do the
    caller cannot safely determine which resource to operate on, and silently
    picking one would risk mutating or deleting the wrong resource.
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

    # Different resource types use different fields for their display name:
    #   network     → "label"
    #   instance    → "hostname"
    #   all others  → "name"
    if resource_type == "network":
        matches = [item for item in items if item.get("label") == name]
    elif resource_type == "instance":
        matches = [item for item in items if item.get("hostname") == name]
    else:
        matches = [item for item in items if item.get("name") == name]

    if len(matches) > 1:
        module.fail_json(
            msg=(
                f"Found {len(matches)} {resource_type} resources named '{name}'. "
                "Resource names must be unique within a region. "
                "Resolve the collision manually before running this module."
            )
        )

    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# Kubernetes node-pool helper
# ---------------------------------------------------------------------------


def list_node_pools(module, cluster_name, api_key, region, binary=None):
    """Return the list of node pool dicts for *cluster_name*.

    The Civo CLI mixes human-readable table text and a JSON array in stdout.
    The JSON array is extracted by finding the first line that starts with '['.
    Keys are capitalised in the CLI output (e.g. ``"ID"``, ``"Count"``).

    Fails the module (via ``fail_json``) on CLI errors or unparseable output
    rather than silently returning an empty list, so callers see the real error.
    """
    if binary is None:
        binary = CIVO_BINARY_DEFAULT

    env_update = {"CIVO_TOKEN": api_key}
    cmd = [
        binary,
        "kubernetes",
        "node-pool",
        "ls",
        cluster_name,
        "--region",
        region,
        "-o",
        "json",
    ]
    rc, stdout, stderr = module.run_command(cmd, environ_update=env_update)
    if rc != 0:
        module.fail_json(msg=f"Failed to list node pools for '{cluster_name}': {stderr}")

    json_line = None
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            json_line = stripped
            break

    if json_line is None:
        module.fail_json(msg=f"Failed to find node-pool JSON in output: {stdout!r}")

    try:
        pools = json.loads(json_line)
    except ValueError as exc:
        module.fail_json(msg=f"Failed to parse node-pool JSON: {exc}: {json_line!r}")

    return pools if isinstance(pools, list) else []


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

    ``api_key`` is resolved in order:
    1. Explicit ``api_key`` module parameter.
    2. ``CIVO_TOKEN`` environment variable.
    3. Active key in ``~/.civo.json`` (the civo CLI config file).

    ``required`` is intentionally omitted so that the fallback chain runs;
    a missing key produces a clear ``fail_json`` message in each module.
    """
    return {
        "api_key": {
            "type": "str",
            "no_log": True,
            "fallback": (_civo_api_key_fallback, []),
        },
        "region": {"type": "str", "default": "LON1"},
        "state": {"type": "str", "default": "present", "choices": ["present", "absent"]},
        "civo_binary": {"type": "str", "default": CIVO_BINARY_DEFAULT},
    }
