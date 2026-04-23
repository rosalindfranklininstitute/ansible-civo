#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_database_info
short_description: Gather information about Civo managed databases
description:
  - Returns details of one or all Civo managed databases in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description:
      - Name of the database to look up.
      - When omitted, all databases in the region are returned.
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
  - module: civo.cloud.civo_database
"""

EXAMPLES = r"""
- name: Get all databases
  civo.cloud.civo_database_info:
    region: LON1
  register: dbs

- name: Get a specific database
  civo.cloud.civo_database_info:
    region: LON1
    name: myapp-db
  register: db

- name: Print database status
  ansible.builtin.debug:
    msg: "{{ db.databases[0].status }}"
"""

RETURN = r"""
databases:
  description: List of database dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Database UUID.
      type: str
    name:
      description: Database name.
      type: str
    status:
      description: Database status.
      type: str
    software:
      description: Database engine (e.g. C(PostgreSQL)).
      type: str
    software_version:
      description: Engine version string.
      type: str
    size:
      description: Database node size slug.
      type: str
    nodes:
      description: Number of database nodes.
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
        result = find_resource_by_name(module, "database", name, api_key, region, binary)
        databases = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["database", "ls"], api_key, region, binary, check_rc=False)
        databases = data if isinstance(data, list) else []

    module.exit_json(changed=False, databases=databases)


if __name__ == "__main__":
    main()
