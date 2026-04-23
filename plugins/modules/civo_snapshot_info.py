#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_snapshot_info
short_description: Gather information about Civo instance snapshots
description:
  - Returns details of one or all Civo instance snapshots in a region.
  - When I(name) is given, returns a single-item list (or empty if not found).
  - Snapshots are available on CivoStack Enterprise Private Regions.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.4"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
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
  - module: civo.cloud.civo_snapshot
"""

EXAMPLES = r"""
- name: List all snapshots
  civo.cloud.civo_snapshot_info:
    region: LON1
  register: snaps

- name: Get a specific snapshot
  civo.cloud.civo_snapshot_info:
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
        name={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get("name")
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    rc, data, stderr = run_civo_command(
        module,
        ["resource-snapshot", "list"],
        api_key,
        region,
        binary,
        check_rc=False,
    )
    if rc != 0:
        if "not found" in stderr.lower() or "no " in stderr.lower():
            module.exit_json(changed=False, snapshots=[])
        module.fail_json(msg=f"Failed to list snapshots: {stderr}")

    items = data if isinstance(data, list) else data.get("items", []) if isinstance(data, dict) else []

    if name:
        items = [s for s in items if s.get("name") == name]

    module.exit_json(changed=False, snapshots=items)


if __name__ == "__main__":
    main()
