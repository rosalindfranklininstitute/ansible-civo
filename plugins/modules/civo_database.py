#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_database
short_description: Manage Civo managed databases
description:
  - Create or delete Civo managed database clusters (MySQL or PostgreSQL).
  - Uses the C(civo) CLI binary on the control node.
  - >-
    Note: C(--software) is the CLI flag for the engine type and C(--version)
    for the version string — the module maps the user-facing I(engine)/I(version)
    parameters to those flags.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description: Name of the database cluster.
    required: true
    type: str
  size:
    description: Database node size slug (e.g. C(g3.db.small)).
    type: str
    default: g3.db.small
  engine:
    description:
      - Database engine type.
      - Currently only C(postgresql) is supported by Civo.
      - Run C(civo database versions) to see available engines and versions in your region.
    type: str
    choices: [postgresql]
    default: postgresql
  version:
    description:
      - Engine version string.
      - Run C(civo database versions) to list available versions for your region.
    type: str
    default: "17"
  nodes:
    description: Number of database nodes.
    type: int
    default: 1
  network:
    description: Name or ID of the network.
    type: str
    default: default
  firewall:
    description: Name or ID of the firewall.
    type: str
  wait:
    description: Wait for the database to become ready before returning.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the database to become ready.
    type: int
    default: 600
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
    type: str
  region:
    description: Civo region identifier.
    type: str
    default: LON1
  state:
    description: Whether the database should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_network
  - module: civo.cloud.civo_firewall
"""

EXAMPLES = r"""
- name: Create a PostgreSQL database
  civo.cloud.civo_database:
    region: LON1
    name: myapp-db
    engine: postgresql
    version: "17"
    size: g3.db.small
    nodes: 1
    network: my-network
    wait: true
  register: db

- name: Print database endpoint
  ansible.builtin.debug:
    msg: "DB endpoint: {{ db.database.endpoint }}"

- name: Delete a database
  civo.cloud.civo_database:
    region: LON1
    name: myapp-db
    state: absent
"""

RETURN = r"""
database:
  description: Details of the managed database cluster.
  returned: when state is C(present)
  type: dict
  sample:
    id: "a1b2c3d4-0000-0000-0000-000000000000"
    name: "myapp-db"
    status: "Ready"
    software: "PostgreSQL"
    software_version: "17"
    size: "g3.db.small"
    nodes: "1"
  contains:
    id:
      description: Database UUID.
      type: str
      sample: "a1b2c3d4-0000-0000-0000-000000000000"
    name:
      description: Database name.
      type: str
      sample: "myapp-db"
    status:
      description: Database status (e.g. C(Ready), C(Building)).
      type: str
      sample: "Ready"
    software:
      description: Database engine type (e.g. C(PostgreSQL), C(MySQL)).
      type: str
      sample: "PostgreSQL"
    software_version:
      description: Engine version string.
      type: str
      sample: "17"
    size:
      description: Database node size slug.
      type: str
      sample: "g3.db.small"
    nodes:
      description: Number of database nodes.
      type: str
      sample: "1"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
    wait_for_active,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        size={"type": "str", "default": "g3.db.small"},
        engine={"type": "str", "default": "postgresql", "choices": ["postgresql"]},
        version={"type": "str", "default": "17"},
        nodes={"type": "int", "default": 1},
        network={"type": "str", "default": "default"},
        firewall={"type": "str"},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 600},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]
    do_wait = module.params["wait"]
    timeout = module.params["timeout"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "database", name, api_key, region, binary)
    before = existing or {}

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Database '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete database '{name}'", diff={"before": before, "after": {}})
        run_civo_command(module, ["database", "delete", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Database '{name}' deleted", diff={"before": before, "after": {}})

    if existing:
        module.exit_json(changed=False, database=existing, diff={"before": before, "after": before})

    after_preview = {
        "name": name,
        "size": module.params["size"],
        "software": module.params["engine"],
        "software_version": module.params["version"],
        "nodes": str(module.params["nodes"]),
    }
    if module.check_mode:
        module.exit_json(
            changed=True, msg=f"Would create database '{name}'", diff={"before": {}, "after": after_preview}
        )

    # The Civo CLI uses --software / --version (not --engine / --software-version)
    create_args = [
        "database",
        "create",
        name,
        "--size",
        module.params["size"],
        "--software",
        module.params["engine"],
        "--version",
        module.params["version"],
        "--nodes",
        str(module.params["nodes"]),
        "--network",
        module.params["network"],
    ]
    if module.params.get("firewall"):
        create_args += ["--firewall", module.params["firewall"]]

    run_civo_command(module, create_args, api_key, region, binary)

    if do_wait:
        database = wait_for_active(
            module,
            "database",
            name,
            api_key,
            region,
            binary=binary,
            timeout=timeout,
        )
    else:
        database = find_resource_by_name(module, "database", name, api_key, region, binary) or {}

    module.exit_json(changed=True, database=database, diff={"before": {}, "after": database})


if __name__ == "__main__":
    main()
