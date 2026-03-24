#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_volume_info
short_description: Gather information about Civo block storage volumes
description:
  - Returns details of one or all Civo volumes in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description:
      - Name of the volume to look up.
      - When omitted, all volumes in the region are returned.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable when not set.
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
  - module: civo.cloud.civo_volume
"""

EXAMPLES = r"""
- name: Get all volumes
  civo.cloud.civo_volume_info:
    region: LON1
  register: vols

- name: Get a specific volume
  civo.cloud.civo_volume_info:
    region: LON1
    name: data-vol
  register: vol

- name: Print volume size
  ansible.builtin.debug:
    msg: "{{ vol.volumes[0].size_gigabytes }}"
"""

RETURN = r"""
volumes:
  description: List of volume dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Volume UUID.
      type: str
    name:
      description: Volume name.
      type: str
    size_gigabytes:
      description: Volume size (e.g. C("10 GB")).
      type: str
    status:
      description: Volume status (C(available), C(creating), etc.).
      type: str
    network_id:
      description: Network name or UUID the volume belongs to.
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
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    if name:
        result = find_resource_by_name(module, "volume", name, api_key, region, binary)
        volumes = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["volume", "ls"], api_key, region, binary, check_rc=False)
        volumes = data if isinstance(data, list) else []

    module.exit_json(changed=False, volumes=volumes)


if __name__ == "__main__":
    main()
