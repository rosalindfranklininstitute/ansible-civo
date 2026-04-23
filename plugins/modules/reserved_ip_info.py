#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: reserved_ip_info
short_description: Gather information about Civo reserved IP addresses
description:
  - Returns details of one or all Civo reserved IPs in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description:
      - Name/label of the reserved IP to look up.
      - When omitted, all reserved IPs in the region are returned.
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
  - module: civo.cloud.reserved_ip
"""

EXAMPLES = r"""
- name: Get all reserved IPs
  civo.cloud.reserved_ip_info:
    region: LON1
  register: ips

- name: Get a specific reserved IP
  civo.cloud.reserved_ip_info:
    region: LON1
    name: web-ip
  register: ip

- name: Print IP address
  ansible.builtin.debug:
    msg: "{{ ip.reserved_ips[0].address }}"
"""

RETURN = r"""
reserved_ips:
  description: List of reserved IP dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Reserved IP UUID.
      type: str
    name:
      description: Label for the IP.
      type: str
    address:
      description: The reserved IP address.
      type: str
    assigned_to:
      description: Resource the IP is assigned to, or C(No resource).
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
        result = find_resource_by_name(module, "ip", name, api_key, region, binary)
        reserved_ips = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["ip", "ls"], api_key, region, binary, check_rc=False)
        reserved_ips = data if isinstance(data, list) else []

    module.exit_json(changed=False, reserved_ips=reserved_ips)


if __name__ == "__main__":
    main()
