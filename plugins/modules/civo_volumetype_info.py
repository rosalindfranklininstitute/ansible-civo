#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_volumetype_info
short_description: List available Civo volume types
description:
  - Returns all volume types available in a Civo account.
  - The C(name) field of each volume type is the value accepted by the
    C(volume_type) parameter of C(civo.cloud.civo_volume) (when that option is
    added); currently useful for discovery and documentation purposes.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
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
- name: List all volume types
  civo.cloud.civo_volumetype_info:
    region: LON1
  register: vtypes

- name: Show volume type names
  ansible.builtin.debug:
    msg: "{{ vtypes.volume_types | map(attribute='name') | list }}"

- name: Find the default volume type
  ansible.builtin.debug:
    msg: >-
      {{ vtypes.volume_types
         | selectattr('default', 'equalto', 'true')
         | map(attribute='name') | list }}
"""

RETURN = r"""
volume_types:
  description: List of available volume type dicts.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Volume type slug / identifier.
      type: str
      sample: "standard"
    default:
      description: Whether this is the default volume type (C("true") or C("false")).
      type: str
      sample: "false"
    description:
      description: Human-readable description of the volume type.
      type: str
      sample: "Encrypted - 2 replicas"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    _rc, data, _stderr = run_civo_command(module, ["volumetypes", "ls"], api_key, region, binary, check_rc=False)
    volume_types = data if isinstance(data, list) else []

    module.exit_json(changed=False, volume_types=volume_types)


if __name__ == "__main__":
    main()
