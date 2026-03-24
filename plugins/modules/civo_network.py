#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_network
short_description: Manage Civo private networks
description:
  - Create or delete Civo private networks.
  - Idempotent — if a network with the given name already exists, no change is
    made (CIDR is immutable after creation on Civo).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name of the network.
    required: true
    type: str
  cidr:
    description:
      - CIDR range for the network (e.g. C(192.168.1.0/24)).
      - Only used at creation time; the Civo API does not support changing
        the CIDR of an existing network.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable when not set.
    type: str
  region:
    description: Civo region identifier (e.g. C(LON1), C(NYC1), C(FRA1), C(PHX1)).
    type: str
    default: LON1
  state:
    description: Whether the network should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_firewall
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: Create a private network
  civo.cloud.civo_network:
    region: LON1
    name: my-network
    cidr: 192.168.10.0/24
    state: present
  register: net

- name: Print network ID
  ansible.builtin.debug:
    msg: "Network ID: {{ net.network.id }}"

- name: Delete a network
  civo.cloud.civo_network:
    region: LON1
    name: my-network
    state: absent
"""

RETURN = r"""
network:
  description: Details of the managed network.
  returned: when state is C(present) and the network exists
  type: dict
  contains:
    id:
      description: Network UUID.
      type: str
      sample: a1b2c3d4-0000-0000-0000-000000000000
    label:
      description: Network name/label (the Civo CLI returns C(label), not C(name)).
      type: str
      sample: my-network
    status:
      description: Network status (e.g. C(Active)).
      type: str
      sample: Active
    default:
      description: Whether this is the account-default network (returned as a string by the CLI).
      type: str
      sample: "false"
    region:
      description: Region the network belongs to.
      type: str
      sample: LON1
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        cidr={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    cidr = module.params["cidr"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    existing = find_resource_by_name(module, "network", name, api_key, region, binary)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Network '{name}' not found")
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete network '{name}'")
        run_civo_command(module, ["network", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Network '{name}' deleted")

    # state == present — CIDR is immutable, so no update path needed
    if existing:
        module.exit_json(changed=False, network=existing)

    if module.check_mode:
        module.exit_json(changed=True, msg=f"Would create network '{name}'")

    create_args = ["network", "create", name]
    if cidr:
        create_args += ["--cidr", cidr]

    run_civo_command(module, create_args, api_key, region, binary)

    network = find_resource_by_name(module, "network", name, api_key, region, binary)
    module.exit_json(changed=True, network=network or {})


if __name__ == "__main__":
    main()
