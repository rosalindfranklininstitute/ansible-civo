#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: reserved_ip
short_description: Manage Civo reserved (static) public IP addresses
description:
  - Reserve, assign, reassign, or release Civo public IP addresses.
  - Idempotent — checks current assignment state before acting.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description: Label name for the reserved IP (used as the unique identifier).
    required: true
    type: str
  instance:
    description:
      - Hostname or ID of the instance to assign the IP to.
      - Required when I(state=assigned).
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
  state:
    description:
      - C(present) reserves the IP without assigning it.
      - C(absent) releases the reserved IP.
      - C(assigned) assigns the IP to I(instance).
      - C(unassigned) removes the assignment but keeps the reservation.
    type: str
    choices: [present, absent, assigned, unassigned]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.instance
"""

EXAMPLES = r"""
- name: Reserve a public IP
  civo.cloud.reserved_ip:
    region: LON1
    name: web-ip
    state: present
  register: rip

- name: Assign the reserved IP to an instance
  civo.cloud.reserved_ip:
    region: LON1
    name: web-ip
    instance: web-01.example.com
    state: assigned

- name: Unassign the reserved IP
  civo.cloud.reserved_ip:
    region: LON1
    name: web-ip
    state: unassigned

- name: Release a reserved IP
  civo.cloud.reserved_ip:
    region: LON1
    name: web-ip
    state: absent
"""

RETURN = r"""
reserved_ip:
  description: Details of the reserved IP.
  returned: when state is C(present), C(assigned), or C(unassigned)
  type: dict
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
      description: >
        Resource the IP is assigned to.  When assigned the value is
        C("hostname (instance-uuid)"); when unassigned it is C("No resource").
      type: str
      sample: "web-01.example.com (a1b2c3d4-0000-0000-0000-000000000000)"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec["state"] = {
        "type": "str",
        "default": "present",
        "choices": ["present", "absent", "assigned", "unassigned"],
    }
    argument_spec.update(
        name={"type": "str", "required": True},
        instance={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "ip", name, api_key, region, binary)
    before = existing or {}

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Reserved IP '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(
                changed=True, msg=f"Would release reserved IP '{name}'", diff={"before": before, "after": {}}
            )
        run_civo_command(module, ["ip", "delete", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Reserved IP '{name}' released", diff={"before": before, "after": {}})

    # Ensure reservation exists
    created = False
    if existing is None:
        if module.check_mode:
            module.exit_json(
                changed=True, msg=f"Would reserve IP '{name}'", diff={"before": {}, "after": {"name": name}}
            )
        run_civo_command(module, ["ip", "reserve", "--name", name], api_key, region, binary)
        existing = find_resource_by_name(module, "ip", name, api_key, region, binary) or {}
        created = True

    # ---------------------------------------------------------------- assigned
    if state == "assigned":
        instance = module.params.get("instance")
        if not instance:
            module.fail_json(msg="'instance' is required when state=assigned")

        # The CLI JSON uses "assigned_to" field; "No resource" means unassigned.
        # The value looks like "my-instance (instance)" when assigned.
        assigned_to = existing.get("assigned_to", "No resource") or "No resource"
        is_assigned = assigned_to != "No resource" and assigned_to != ""

        # Check if already assigned to the *requested* instance (hostname match).
        # assigned_to format is "hostname (instance)" — extract hostname prefix.
        already_correct = False
        if is_assigned:
            assigned_hostname = assigned_to.split(" (")[0] if " (" in assigned_to else assigned_to
            if assigned_hostname == instance:
                already_correct = True

        if already_correct:
            module.exit_json(changed=created, reserved_ip=existing, diff={"before": before, "after": existing})

        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would assign IP '{name}' to '{instance}'",
                diff={"before": before, "after": {**existing, "assigned_to": instance}},
            )
        run_civo_command(
            module,
            ["ip", "assign", name, "--instance", instance],
            api_key,
            region,
            binary,
        )
        ip = find_resource_by_name(module, "ip", name, api_key, region, binary) or {}
        module.exit_json(changed=True, reserved_ip=ip, diff={"before": before, "after": ip})

    # --------------------------------------------------------------- unassigned
    if state == "unassigned":
        assigned_to = existing.get("assigned_to", "No resource") or "No resource"
        is_assigned = assigned_to != "No resource" and assigned_to != ""
        if not is_assigned:
            # Already unassigned
            module.exit_json(changed=created, reserved_ip=existing, diff={"before": before, "after": existing})
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would unassign IP '{name}'",
                diff={"before": before, "after": {**existing, "assigned_to": "No resource"}},
            )
        run_civo_command(module, ["ip", "unassign", name], api_key, region, binary)
        ip = find_resource_by_name(module, "ip", name, api_key, region, binary) or {}
        module.exit_json(changed=True, reserved_ip=ip, diff={"before": before, "after": ip})

    # ----------------------------------------------------------------- present
    module.exit_json(changed=created, reserved_ip=existing, diff={"before": before, "after": existing})


if __name__ == "__main__":
    main()
