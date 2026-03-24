#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_sshkey_info
short_description: List SSH keys stored in a Civo account
description:
  - Returns all SSH keys registered with a Civo account, or filters to a
    single key by name.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: >-
      Name of a specific SSH key to return (exact match).
      When omitted, all keys are returned.
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
  - module: civo.cloud.civo_sshkey
"""

EXAMPLES = r"""
- name: List all SSH keys
  civo.cloud.civo_sshkey_info:
  register: keys

- name: Show key names
  ansible.builtin.debug:
    msg: "{{ keys.sshkeys | map(attribute='name') | list }}"

- name: Look up a specific key by name
  civo.cloud.civo_sshkey_info:
    name: my-laptop-key
  register: my_key

- name: Assert the key exists
  ansible.builtin.assert:
    that:
      - my_key.sshkeys | length == 1
"""

RETURN = r"""
sshkeys:
  description: List of SSH key dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: SSH key UUID.
      type: str
      sample: "a1b2c3d4-0000-0000-0000-000000000000"
    name:
      description: SSH key label.
      type: str
      sample: "my-laptop-key"
    fingerprint:
      description: MD5 fingerprint of the public key.
      type: str
      sample: "12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]
    spec.update(name={"type": "str"})

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    name = module.params.get("name") or ""
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    _rc, data, _stderr = run_civo_command(module, ["sshkey", "ls"], api_key, region, binary, check_rc=False)
    keys = data if isinstance(data, list) else []

    if name:
        keys = [k for k in keys if k.get("name") == name]

    module.exit_json(changed=False, sshkeys=keys)


if __name__ == "__main__":
    main()
