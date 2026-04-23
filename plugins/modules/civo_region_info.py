#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_region_info
short_description: List available Civo regions
description:
  - Returns all regions available in a Civo account.
  - The C(code) field of each region is the value accepted by the C(region)
    parameter of all other C(civo.cloud) modules.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
    type: str
  region:
    description: >-
      Civo region identifier used to authenticate the CLI call.
      The result always contains all regions regardless of this value.
    type: str
    default: LON1
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
"""

EXAMPLES = r"""
- name: List all Civo regions
  civo.cloud.civo_region_info:
  register: regions

- name: Show region codes
  ansible.builtin.debug:
    msg: "{{ regions.regions | map(attribute='code') | list }}"

- name: Find the current (default) region
  ansible.builtin.debug:
    msg: "{{ regions.regions | selectattr('current', 'equalto', 'Yes') | map(attribute='code') | list }}"
"""

RETURN = r"""
regions:
  description: List of all available Civo regions.
  returned: always
  type: list
  elements: dict
  contains:
    code:
      description: >-
        Region code — use this as the C(region) parameter in other modules
        (e.g. C(LON1), C(NYC1)).
      type: str
      sample: "lon1"
    name:
      description: Human-readable region name.
      type: str
      sample: "lon1"
    country:
      description: Country where the region is located.
      type: str
      sample: "United Kingdom"
    current:
      description: >-
        Whether this is the currently configured default region
        (C("Yes") or C("No")).
      type: str
      sample: "Yes"
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
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    _rc, data, _stderr = run_civo_command(module, ["region", "ls"], api_key, region, binary, check_rc=False)
    regions = data if isinstance(data, list) else []

    module.exit_json(changed=False, regions=regions)


if __name__ == "__main__":
    main()
