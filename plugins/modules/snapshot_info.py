#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: snapshot_info
short_description: Gather information about Civo instance snapshots
description:
  - Returns details of one or all snapshots belonging to a Civo compute instance.
  - When I(name) is given, returns a single-item list (or empty if not found).
  - Uses the C(civo instance snapshot) CLI commands on the control node.
version_added: "0.0.4"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  instance:
    description: Hostname or ID of the instance whose snapshots to query.
    required: true
    type: str
  name:
    description: Filter results to the snapshot with this name.
    type: str
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
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.snapshot
"""

EXAMPLES = r"""
- name: List all snapshots for an instance
  civo.cloud.snapshot_info:
    instance: web-01
    region: LON1
  register: snaps

- name: Get a specific snapshot
  civo.cloud.snapshot_info:
    instance: web-01
    name: web-01-snap
    region: LON1
  register: snap
"""

RETURN = r"""
snapshots:
  description: List of matching snapshots.
  returned: always
  type: list
  elements: dict
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

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    # Info modules don't use state
    del argument_spec["state"]
    argument_spec.update(
        instance={"type": "str", "required": True},
        name={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    instance = module.params["instance"]
    name = module.params.get("name")
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if name:
        rc, data, stderr = run_civo_command(
            module,
            ["instance", "snapshot", "show", instance, name],
            api_key,
            region,
            binary,
            check_rc=False,
        )
        if rc != 0:
            module.exit_json(changed=False, snapshots=[])
        items = [data] if isinstance(data, dict) and data else []
    else:
        rc, data, stderr = run_civo_command(
            module,
            ["instance", "snapshot", "list", instance],
            api_key,
            region,
            binary,
            check_rc=False,
        )
        if rc != 0:
            module.fail_json(msg=f"Failed to list snapshots for instance '{instance}': {stderr.strip()}")
        items = data if isinstance(data, list) else []

    module.exit_json(changed=False, snapshots=items)


if __name__ == "__main__":
    main()
