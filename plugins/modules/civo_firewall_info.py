#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_firewall_info
short_description: Gather information about Civo firewalls
description:
  - Returns details of one or all Civo firewalls in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - When I(rules) is C(true), each firewall dict includes a C(rules) key with the
    full list of firewall rules.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description:
      - Name of the firewall to look up.
      - When omitted, all firewalls in the region are returned.
    type: str
  rules:
    description:
      - When C(true), also fetch the rule list for each firewall and attach it
        as a C(rules) key in the returned dict.
    type: bool
    default: false
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
  - module: civo.cloud.civo_firewall
"""

EXAMPLES = r"""
- name: Get all firewalls
  civo.cloud.civo_firewall_info:
    region: LON1
  register: fws

- name: Get a specific firewall with its rules
  civo.cloud.civo_firewall_info:
    region: LON1
    name: web-fw
    rules: true
  register: fw

- name: Print rule count
  ansible.builtin.debug:
    msg: "{{ fw.firewalls[0].rules | length }} rules"
"""

RETURN = r"""
firewalls:
  description: List of firewall dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Firewall UUID.
      type: str
    name:
      description: Firewall name.
      type: str
    network:
      description: Network name the firewall belongs to.
      type: str
    rules_count:
      description: Total number of rules on the firewall.
      type: str
    rules:
      description: Full rule list (only present when I(rules=true)).
      type: list
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def _fetch_rules(module, firewall_id, api_key, region, binary):
    _rc, data, _stderr = run_civo_command(
        module,
        ["firewall", "rule", "ls", firewall_id],
        api_key,
        region,
        binary,
        check_rc=False,
    )
    return data if isinstance(data, list) else []


def main():
    argument_spec = common_argument_spec()
    argument_spec.pop("state", None)
    argument_spec.update(
        name={"type": "str"},
        rules={"type": "bool", "default": False},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    fetch_rules = module.params["rules"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if name:
        result = find_resource_by_name(module, "firewall", name, api_key, region, binary)
        firewalls = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["firewall", "ls"], api_key, region, binary, check_rc=False)
        firewalls = data if isinstance(data, list) else []

    if fetch_rules:
        for fw in firewalls:
            fw["rules"] = _fetch_rules(module, fw["id"], api_key, region, binary)

    module.exit_json(changed=False, firewalls=firewalls)


if __name__ == "__main__":
    main()
