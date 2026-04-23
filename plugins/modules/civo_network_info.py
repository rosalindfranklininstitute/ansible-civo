#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_network_info
short_description: Gather information about Civo private networks
description:
  - Returns details of one or all Civo private networks in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description:
      - Name of the network to look up.
      - When omitted, all networks in the region are returned.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
    type: str
  region:
    description: Civo region identifier (e.g. C(LON1), C(NYC1)).
    type: str
    default: LON1
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_network
"""

EXAMPLES = r"""
- name: Get all networks
  civo.cloud.civo_network_info:
    region: LON1
  register: nets

- name: Print network names
  ansible.builtin.debug:
    msg: "{{ nets.networks | map(attribute='label') | list }}"

- name: Get a specific network
  civo.cloud.civo_network_info:
    region: LON1
    name: my-network
  register: net

- name: Print network ID
  ansible.builtin.debug:
    msg: "{{ net.networks[0].id }}"
"""

RETURN = r"""
networks:
  description: List of network dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Network UUID.
      type: str
    label:
      description: Network name/label.
      type: str
    status:
      description: Network status.
      type: str
    default:
      description: Whether this is the account-default network.
      type: str
    region:
      description: Region the network belongs to.
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
    # _info modules have no state parameter
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
        result = find_resource_by_name(module, "network", name, api_key, region, binary)
        networks = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["network", "ls"], api_key, region, binary, check_rc=False)
        networks = data if isinstance(data, list) else []

    module.exit_json(changed=False, networks=networks)


if __name__ == "__main__":
    main()
