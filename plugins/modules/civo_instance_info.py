#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_instance_info
short_description: Gather information about Civo compute instances
description:
  - Returns details of one or all Civo compute instances in a region.
  - When I(hostname) is given, returns a single-item list (or empty list if not
    found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  hostname:
    description:
      - Hostname of the instance to look up.
      - When omitted, all instances in the region are returned.
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
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: Get all instances
  civo.cloud.civo_instance_info:
    region: LON1
  register: vms

- name: Get a specific instance
  civo.cloud.civo_instance_info:
    region: LON1
    hostname: web-01.example.com
  register: vm

- name: Print public IP
  ansible.builtin.debug:
    msg: "{{ vm.instances[0].public_ip }}"
"""

RETURN = r"""
instances:
  description: List of instance dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Instance UUID.
      type: str
    hostname:
      description: Instance hostname.
      type: str
    status:
      description: Current status (C(ACTIVE), C(BUILDING), etc.).
      type: str
    public_ip:
      description: Public IP address.
      type: str
    size:
      description: Instance size slug.
      type: str
    region:
      description: Region the instance is deployed in.
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
        hostname={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    hostname = module.params["hostname"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if hostname:
        result = find_resource_by_name(module, "instance", hostname, api_key, region, binary)
        instances = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["instance", "ls"], api_key, region, binary, check_rc=False)
        instances = data if isinstance(data, list) else []

    module.exit_json(changed=False, instances=instances)


if __name__ == "__main__":
    main()
