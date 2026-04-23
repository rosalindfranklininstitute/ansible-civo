#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_snapshot
short_description: Manage Civo instance snapshots
description:
  - Create, delete, or restore point-in-time snapshots of Civo compute instances.
  - Uses the C(civo instance snapshot) CLI commands on the control node.
version_added: "0.0.4"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description: Name of the snapshot (used as the unique identifier).
    required: true
    type: str
  instance:
    description:
      - Hostname or ID of the instance the snapshot belongs to.
      - Required for all states — the snapshot CLI scopes operations per instance.
    required: true
    type: str
  description:
    description: Human-readable description for the snapshot or restore operation.
    type: str
  hostname:
    description:
      - Hostname to assign to the newly restored instance.
      - When omitted alongside I(overwrite_existing=false) the CLI assigns a default name.
      - Used only when I(state=restored).
    type: str
  overwrite_existing:
    description:
      - When C(true) the restore replaces the original instance in-place.
      - When C(false) (default) a new instance is created from the snapshot.
      - Used only when I(state=restored).
    type: bool
    default: false
  wait:
    description: Wait for the snapshot to reach C(AVAILABLE) status after creation.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the snapshot to become available.
    type: int
    default: 600
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active
        key in C(~/.civo.json), when not set.
    type: str
  region:
    description: Civo region identifier.
    type: str
    default: LON1
  state:
    description:
      - C(present) creates the snapshot if it does not already exist.
        Idempotent — if a snapshot with I(name) already exists on I(instance)
        no action is taken.
      - C(absent) deletes the snapshot if it exists.
      - C(restored) restores the snapshot.  This state is not idempotent and
        always triggers a restore operation.
    type: str
    choices: [present, absent, restored]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_snapshot_info
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: Create a snapshot of an instance
  civo.cloud.civo_snapshot:
    name: web-01-snap
    instance: web-01
    description: "Pre-upgrade snapshot"
    region: LON1
    state: present
  register: snap

- name: Restore snapshot to a new instance
  civo.cloud.civo_snapshot:
    name: web-01-snap
    instance: web-01
    hostname: web-01-restored
    region: LON1
    state: restored

- name: Restore snapshot overwriting the original instance
  civo.cloud.civo_snapshot:
    name: web-01-snap
    instance: web-01
    overwrite_existing: true
    region: LON1
    state: restored

- name: Delete a snapshot
  civo.cloud.civo_snapshot:
    name: web-01-snap
    instance: web-01
    region: LON1
    state: absent
"""

RETURN = r"""
snapshot:
  description: Details of the snapshot.
  returned: when state is C(present)
  type: dict
  contains:
    id:
      description: Snapshot UUID.
      type: str
    name:
      description: Snapshot name.
      type: str
    description:
      description: Snapshot description.
      type: str
    status:
      description: Current snapshot status (e.g. C(AVAILABLE), C(CREATING)).
      type: str
    created_at:
      description: ISO 8601 creation timestamp.
      type: str
"""

import time

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def _find_snapshot(module, instance, name, api_key, region, binary):
    """Return the snapshot dict for *name* on *instance*, or None if not found."""
    rc, data, stderr = run_civo_command(
        module,
        ["instance", "snapshot", "show", instance, name],
        api_key,
        region,
        binary,
        check_rc=False,
    )
    if rc != 0:
        return None
    if isinstance(data, dict) and data:
        return data
    return None


def _wait_for_snapshot(module, instance, name, api_key, region, binary, timeout):
    """Poll until the snapshot reaches AVAILABLE status or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        snap = _find_snapshot(module, instance, name, api_key, region, binary)
        if snap:
            status = (snap.get("status") or "").upper()
            if status in ("AVAILABLE", "COMPLETE"):
                return snap
            if status == "FAILED":
                module.fail_json(msg=f"Snapshot '{name}' entered FAILED state", snapshot=snap)
        time.sleep(15)
    module.fail_json(msg=f"Timed out after {timeout}s waiting for snapshot '{name}' to become available")


def main():
    argument_spec = common_argument_spec()
    argument_spec["state"] = {
        "type": "str",
        "default": "present",
        "choices": ["present", "absent", "restored"],
    }
    argument_spec.update(
        name={"type": "str", "required": True},
        instance={"type": "str", "required": True},
        description={"type": "str"},
        hostname={"type": "str"},
        overwrite_existing={"type": "bool", "default": False},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 600},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    instance = module.params["instance"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]
    description = module.params.get("description") or ""

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = _find_snapshot(module, instance, name, api_key, region, binary)
    before = existing or {}

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Snapshot '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would delete snapshot '{name}'",
                diff={"before": before, "after": {}},
            )
        run_civo_command(module, ["instance", "snapshot", "delete", instance, name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Snapshot '{name}' deleted", diff={"before": before, "after": {}})

    # ---------------------------------------------------------------- restored
    if state == "restored":
        if existing is None:
            module.fail_json(msg=f"Snapshot '{name}' not found on instance '{instance}' — cannot restore")
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would restore snapshot '{name}'",
                diff={"before": before, "after": {"restored": True}},
            )
        restore_args = ["instance", "snapshot", "restore", instance, name]
        if module.params.get("hostname"):
            restore_args += ["--hostname", module.params["hostname"]]
        if module.params["overwrite_existing"]:
            restore_args += ["--overwrite-existing"]
        if description:
            restore_args += ["--description", description]
        run_civo_command(module, restore_args, api_key, region, binary)
        module.exit_json(
            changed=True,
            msg=f"Snapshot '{name}' restore initiated",
            diff={"before": before, "after": {"restored": True}},
        )

    # ----------------------------------------------------------------- present
    if existing is not None:
        module.exit_json(changed=False, snapshot=existing, diff={"before": existing, "after": existing})

    if module.check_mode:
        module.exit_json(
            changed=True,
            msg=f"Would create snapshot '{name}' of instance '{instance}'",
            diff={"before": {}, "after": {"name": name, "instance": instance}},
        )

    create_args = ["instance", "snapshot", "create", instance, "--name", name]
    if description:
        create_args += ["--description", description]
    run_civo_command(module, create_args, api_key, region, binary)

    if module.params["wait"]:
        snap = _wait_for_snapshot(module, instance, name, api_key, region, binary, module.params["timeout"])
    else:
        snap = _find_snapshot(module, instance, name, api_key, region, binary) or {}

    module.exit_json(changed=True, snapshot=snap, diff={"before": {}, "after": snap})


if __name__ == "__main__":
    main()
