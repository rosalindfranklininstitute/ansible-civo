#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_snapshot_schedule
short_description: Manage Civo instance snapshot schedules
description:
  - Create, update, or delete Civo instance snapshot schedules.
  - Schedules are available on CivoStack Enterprise Private Regions.
  - Uses the C(civo) CLI binary on the control node.
  - >
    The following parameters are set at creation and cannot be changed on an
    existing schedule: I(cron), I(instance_ids), I(max_snapshots),
    I(include_volumes).  To change them, set I(state=absent) first, then
    re-create the schedule.
version_added: "0.0.4"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description: Name of the snapshot schedule (used as the unique identifier).
    required: true
    type: str
  instance_ids:
    description:
      - List of instance IDs to include in each scheduled snapshot.
      - Required when I(state=present) and the schedule does not already exist.
      - Ignored on update — see module description.
    type: list
    elements: str
  cron:
    description:
      - Cron expression defining the snapshot frequency (e.g. C(0 0 * * *) for daily at midnight).
      - Required when I(state=present) and the schedule does not already exist.
      - Ignored on update — see module description.
    type: str
  max_snapshots:
    description:
      - Maximum number of snapshots to retain per instance.
      - Ignored on update — see module description.
    type: int
  include_volumes:
    description:
      - When C(true), attached volumes are included in each snapshot.
      - Ignored on update — see module description.
    type: bool
    default: false
  description:
    description: Human-readable description for the schedule. Can be updated in place.
    type: str
  paused:
    description:
      - Set to C(true) to pause the schedule, C(false) to resume it.
      - Can be updated in place.
    type: bool
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active
        key in C(~/.civo.json), when not set.
    type: str
  region:
    description: Civo region identifier.
    type: str
    default: LON1
  state:
    description:
      - C(present) creates the schedule if absent, or updates I(description) and
        I(paused) if the schedule already exists.
      - C(absent) deletes the schedule.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_snapshot
  - module: civo.cloud.civo_snapshot_info
"""

EXAMPLES = r"""
- name: Create a daily snapshot schedule for an instance
  civo.cloud.civo_snapshot_schedule:
    name: daily-web-snap
    instance_ids:
      - "a1b2c3d4-0000-0000-0000-000000000000"
    cron: "0 2 * * *"
    max_snapshots: 7
    include_volumes: true
    description: "Daily 02:00 snapshot, 7-day retention"
    region: LON1
    state: present

- name: Pause a schedule
  civo.cloud.civo_snapshot_schedule:
    name: daily-web-snap
    paused: true
    region: LON1
    state: present

- name: Update description
  civo.cloud.civo_snapshot_schedule:
    name: daily-web-snap
    description: "Updated retention policy"
    region: LON1
    state: present

- name: Delete a schedule
  civo.cloud.civo_snapshot_schedule:
    name: daily-web-snap
    region: LON1
    state: absent
"""

RETURN = r"""
schedule:
  description: Details of the snapshot schedule.
  returned: when state is C(present)
  type: dict
  contains:
    id:
      description: Schedule UUID.
      type: str
    name:
      description: Schedule name.
      type: str
    description:
      description: Schedule description.
      type: str
    cron:
      description: Cron expression for the schedule.
      type: str
    instance_ids:
      description: List of instance IDs covered by the schedule.
      type: list
      elements: str
    max_snapshots:
      description: Maximum number of snapshots retained per instance.
      type: int
    include_volumes:
      description: Whether attached volumes are included in snapshots.
      type: bool
    paused:
      description: Whether the schedule is currently paused.
      type: bool
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def _find_schedule(module, name, api_key, region, binary):
    """Return the schedule dict for *name*, or None if not found."""
    rc, data, stderr = run_civo_command(
        module,
        ["snapshot", "schedule", "show", name],
        api_key,
        region,
        binary,
        check_rc=False,
    )
    if rc != 0:
        return None
    # show returns a single object, not a list
    if isinstance(data, dict) and data:
        return data
    return None


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        instance_ids={"type": "list", "elements": "str"},
        cron={"type": "str"},
        max_snapshots={"type": "int"},
        include_volumes={"type": "bool", "default": False},
        description={"type": "str"},
        paused={"type": "bool"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = _find_schedule(module, name, api_key, region, binary)
    before = existing or {}

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Schedule '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would delete schedule '{name}'",
                diff={"before": before, "after": {}},
            )
        run_civo_command(module, ["snapshot", "schedule", "delete", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Schedule '{name}' deleted", diff={"before": before, "after": {}})

    # ----------------------------------------------------------------- present
    if existing is None:
        # Validate required-for-create params
        instance_ids = module.params.get("instance_ids")
        cron = module.params.get("cron")
        if not instance_ids:
            module.fail_json(msg="'instance_ids' is required when creating a new schedule")
        if not cron:
            module.fail_json(msg="'cron' is required when creating a new schedule")

        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would create schedule '{name}'",
                diff={"before": {}, "after": {"name": name, "cron": cron, "instance_ids": instance_ids}},
            )

        create_args = ["snapshot", "schedule", "create", "--name", name, "--cron", cron]
        for iid in instance_ids:
            create_args += ["--instance-id", iid]
        if module.params.get("max_snapshots"):
            create_args += ["--max-snapshots", str(module.params["max_snapshots"])]
        if module.params["include_volumes"]:
            create_args += ["--include-volumes"]
        if module.params.get("description"):
            create_args += ["--description", module.params["description"]]

        run_civo_command(module, create_args, api_key, region, binary)
        schedule = _find_schedule(module, name, api_key, region, binary) or {}
        module.exit_json(changed=True, schedule=schedule, diff={"before": {}, "after": schedule})

    # Schedule exists — update mutable fields if needed
    update_args = ["snapshot", "schedule", "update", name]
    changed = False

    desired_desc = module.params.get("description")
    if desired_desc is not None and desired_desc != existing.get("description", ""):
        update_args += ["--description", desired_desc]
        changed = True

    desired_paused = module.params.get("paused")
    if desired_paused is not None:
        # The CLI stores paused as bool; compare carefully
        current_paused = bool(existing.get("paused", False))
        if desired_paused != current_paused:
            update_args += ["--paused", "true" if desired_paused else "false"]
            changed = True

    if not changed:
        module.exit_json(changed=False, schedule=existing, diff={"before": before, "after": existing})

    if module.check_mode:
        module.exit_json(
            changed=True,
            msg=f"Would update schedule '{name}'",
            diff={"before": before, "after": {**existing, "description": desired_desc or existing.get("description")}},
        )

    run_civo_command(module, update_args, api_key, region, binary)
    schedule = _find_schedule(module, name, api_key, region, binary) or existing
    module.exit_json(changed=True, schedule=schedule, diff={"before": before, "after": schedule})


if __name__ == "__main__":
    main()
