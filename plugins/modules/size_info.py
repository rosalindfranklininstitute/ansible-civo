#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: size_info
short_description: List available Civo instance / Kubernetes / database sizes
description:
  - Returns all sizes (plan types) available in a Civo region.
  - Optionally filters by resource type using the I(filter) parameter.
  - The C(name) field of each size is the value to pass to C(civo_instance),
    C(civo_kubernetes), or C(civo_database) as the C(size) parameter.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  resource_type:
    description:
      - Filter sizes by resource type.
      - When omitted, all sizes are returned.
    type: str
    choices: [instance, kubernetes, database]
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
  - module: civo.cloud.instance
  - module: civo.cloud.kubernetes
  - module: civo.cloud.database
"""

EXAMPLES = r"""
- name: List all sizes
  civo.cloud.size_info:
    region: LON1
  register: all_sizes

- name: List only instance sizes
  civo.cloud.size_info:
    region: LON1
    resource_type: instance
  register: instance_sizes

- name: Show instance size names
  ansible.builtin.debug:
    msg: "{{ instance_sizes.sizes | map(attribute='name') | list }}"

- name: List only Kubernetes node sizes
  civo.cloud.size_info:
    region: LON1
    resource_type: kubernetes
  register: k8s_sizes

- name: List database sizes
  civo.cloud.size_info:
    region: LON1
    resource_type: database
  register: db_sizes
"""

RETURN = r"""
sizes:
  description: List of size dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Size slug — pass this to C(size) parameters in resource modules.
      type: str
      sample: "g3.xsmall"
    description:
      description: Human-readable size description.
      type: str
      sample: "Extra Small"
    type:
      description: Resource type the size applies to (C(Instance), C(Kubernetes), C(Database)).
      type: str
      sample: "Instance"
    cpu_cores:
      description: Number of vCPU cores (string as returned by the CLI).
      type: str
      sample: "1"
    ram_mb:
      description: RAM in megabytes (string as returned by the CLI).
      type: str
      sample: "1024"
    disk_gb:
      description: Disk size in gigabytes (string as returned by the CLI).
      type: str
      sample: "25"
    selectable:
      description: Whether this size can be selected when creating resources.
      type: str
      sample: "true"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]
    spec.update(
        resource_type={
            "type": "str",
            "choices": ["instance", "kubernetes", "database"],
        }
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    size_filter = module.params.get("resource_type")
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    cmd = ["size", "ls"]
    if size_filter:
        cmd += ["--filter", size_filter]

    _rc, data, _stderr = run_civo_command(module, cmd, api_key, region, binary, check_rc=False)
    sizes = data if isinstance(data, list) else []

    module.exit_json(changed=False, sizes=sizes)


if __name__ == "__main__":
    main()
