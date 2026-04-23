#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_objectstore_info
short_description: Gather information about Civo object stores
description:
  - Returns details of one or all Civo object stores in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description:
      - Name of the object store to look up.
      - When omitted, all object stores in the region are returned.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
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
  - module: civo.cloud.civo_objectstore
"""

EXAMPLES = r"""
- name: Get all object stores
  civo.cloud.civo_objectstore_info:
    region: LON1
  register: stores

- name: Get a specific object store
  civo.cloud.civo_objectstore_info:
    region: LON1
    name: my-bucket
  register: store

- name: Print endpoint
  ansible.builtin.debug:
    msg: "{{ store.objectstores[0].objectstore_endpoint }}"
"""

RETURN = r"""
objectstores:
  description: List of object store dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Object store UUID (may be truncated in CLI output).
      type: str
    name:
      description: Object store name.
      type: str
    status:
      description: Object store status.
      type: str
    max_size:
      description: Maximum size quota in GB.
      type: str
    objectstore_endpoint:
      description: S3-compatible endpoint hostname.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec.pop("state", None)
    argument_spec.update(
        name={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if name:
        result = find_resource_by_name(module, "objectstore", name, api_key, region, binary)
        objectstores = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["objectstore", "ls"], api_key, region, binary, check_rc=False)
        objectstores = data if isinstance(data, list) else []

    module.exit_json(changed=False, objectstores=objectstores)


if __name__ == "__main__":
    main()
