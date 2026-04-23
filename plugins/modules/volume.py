#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: volume
short_description: Manage Civo block storage volumes
description:
  - Create, resize, attach, detach, or delete Civo persistent volumes.
  - Idempotent attach/detach — checks current attachment state before acting.
  - Supports in-place resize when I(size_gb) is increased on an existing volume.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description: Name of the volume.
    required: true
    type: str
  size_gb:
    description:
      - Size of the volume in gigabytes.
      - Can be increased on an existing volume (resize). Decreasing is not
        supported by the Civo API.
    type: int
    default: 10
  bootable:
    description: Whether this volume should be bootable.
    type: bool
    default: false
  network:
    description: Name or ID of the network to create the volume in.
    type: str
    default: default
  instance:
    description:
      - Hostname or ID of the instance to attach the volume to.
      - Required when I(state=attached).
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
      - C(present) ensures the volume exists (detached).
      - C(absent) deletes the volume.
      - C(attached) attaches the volume to I(instance).
      - C(detached) detaches the volume from any instance.
    type: str
    choices: [present, absent, attached, detached]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.instance
"""

EXAMPLES = r"""
- name: Create a 50 GB volume
  civo.cloud.volume:
    region: LON1
    name: data-vol
    size_gb: 50

- name: Attach volume to an instance
  civo.cloud.volume:
    region: LON1
    name: data-vol
    instance: web-01.example.com
    state: attached

- name: Resize volume to 100 GB
  civo.cloud.volume:
    region: LON1
    name: data-vol
    size_gb: 100

- name: Detach volume
  civo.cloud.volume:
    region: LON1
    name: data-vol
    state: detached

- name: Delete a volume
  civo.cloud.volume:
    region: LON1
    name: data-vol
    state: absent
"""

RETURN = r"""
volume:
  description: Details of the managed volume.
  returned: when state is C(present), C(attached), or C(detached)
  type: dict
  contains:
    id:
      description: Volume UUID.
      type: str
      sample: a1b2c3d4-0000-0000-0000-000000000000
    name:
      description: Volume name.
      type: str
      sample: data-vol
    size_gigabytes:
      description: >-
        Volume size as returned by the Civo CLI, including a unit suffix
        (e.g. C("10 GB")). Strip the suffix before numeric comparison.
      type: str
      sample: "10 GB"
    status:
      description: Volume status (C(available), C(creating), C(resizing), etc.).
      type: str
      sample: available
    network_id:
      description: >-
        Name or UUID of the network the volume belongs to. Returns the network
        name when the default network is used, or the UUID for custom networks.
      type: str
      sample: default
    instance_id:
      description: >-
        Hostname (not UUID) of the instance the volume is attached to.
        Empty string when the volume is not attached.
        Note: the Civo CLI stores the instance hostname here, not its UUID.
      type: str
      sample: web-01.example.com
    bootable:
      description: Whether the volume is marked as bootable.
      type: bool
      sample: false
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    is_uuid,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec["state"] = {
        "type": "str",
        "default": "present",
        "choices": ["present", "absent", "attached", "detached"],
    }
    argument_spec.update(
        name={"type": "str", "required": True},
        size_gb={"type": "int", "default": 10},
        bootable={"type": "bool", "default": False},
        network={"type": "str", "default": "default"},
        instance={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]
    desired_size = module.params["size_gb"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "volume", name, api_key, region, binary)
    before = existing or {}

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Volume '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete volume '{name}'", diff={"before": before, "after": {}})
        run_civo_command(module, ["volume", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Volume '{name}' deleted", diff={"before": before, "after": {}})

    # Ensure the volume exists
    created = False
    if existing is None:
        after_preview = {"name": name, "size_gigabytes": f"{desired_size} GB", "network_id": module.params["network"]}
        if module.check_mode:
            module.exit_json(
                changed=True, msg=f"Would create volume '{name}'", diff={"before": {}, "after": after_preview}
            )
        create_args = [
            "volume",
            "create",
            name,
            "--size-gb",
            str(desired_size),
            "--network",
            module.params["network"],
        ]
        if module.params["bootable"]:
            create_args.append("--bootable")
        run_civo_command(module, create_args, api_key, region, binary)
        existing = find_resource_by_name(module, "volume", name, api_key, region, binary) or {}
        created = True

    changed = created

    # ---- resize if size increased (only when state=present) ----
    if state == "present" and not created and existing:
        # size_gigabytes field from CLI is like "5 GB" — strip the unit
        raw_size = existing.get("size_gigabytes", existing.get("size_gb", existing.get("size", "0"))) or "0"
        current_size = int(str(raw_size).split()[0])
        if desired_size > current_size:
            if not module.check_mode:
                run_civo_command(
                    module,
                    ["volume", "resize", name, "--size-gb", str(desired_size)],
                    api_key,
                    region,
                    binary,
                )
            changed = True

    # ---------------------------------------------------------------- attached
    if state == "attached":
        instance = module.params.get("instance")
        if not instance:
            module.fail_json(msg="'instance' is required when state=attached")

        current_instance_id = existing.get("instance_id", "")
        if current_instance_id:
            # The Civo CLI stores the hostname (not UUID) in instance_id after
            # attach.  Handle both hostname and UUID comparisons so idempotency
            # works regardless of how the caller identifies the instance.
            if is_uuid(instance):
                # Caller passed a UUID — resolve current hostname to UUID for
                # comparison, or check if the stored value is already a UUID.
                if current_instance_id == instance:
                    module.exit_json(changed=changed, volume=existing, diff={"before": before, "after": existing})
                inst_obj = find_resource_by_name(module, "instance", current_instance_id, api_key, region, binary)
                current_uuid = inst_obj.get("id", "") if inst_obj else ""
                if current_uuid == instance:
                    module.exit_json(changed=changed, volume=existing, diff={"before": before, "after": existing})
            else:
                # Caller passed a name — compare directly against stored hostname,
                # then fall back to UUID comparison.
                if current_instance_id == instance:
                    module.exit_json(changed=changed, volume=existing, diff={"before": before, "after": existing})
                inst_obj = find_resource_by_name(module, "instance", instance, api_key, region, binary)
                if inst_obj is None:
                    module.fail_json(msg=f"Instance '{instance}' not found in region '{region}'")
                desired_uuid = inst_obj.get("id", "")
                if desired_uuid == current_instance_id:
                    module.exit_json(changed=changed, volume=existing, diff={"before": before, "after": existing})

        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would attach volume '{name}' to '{instance}'",
                diff={"before": before, "after": {**before, "instance_id": instance}},
            )
        run_civo_command(
            module,
            ["volume", "attach", name, instance],
            api_key,
            region,
            binary,
        )
        volume = find_resource_by_name(module, "volume", name, api_key, region, binary) or {}
        module.exit_json(changed=True, volume=volume, diff={"before": before, "after": volume})

    # ---------------------------------------------------------------- detached
    if state == "detached":
        current_instance_id = existing.get("instance_id", "")
        if not current_instance_id:
            module.exit_json(changed=changed, volume=existing, diff={"before": before, "after": before})
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would detach volume '{name}'",
                diff={"before": before, "after": {**before, "instance_id": ""}},
            )
        run_civo_command(module, ["volume", "detach", name], api_key, region, binary)
        volume = find_resource_by_name(module, "volume", name, api_key, region, binary) or {}
        module.exit_json(changed=True, volume=volume, diff={"before": before, "after": volume})

    # ----------------------------------------------------------------- present
    volume = (
        find_resource_by_name(module, "volume", name, api_key, region, binary)
        if changed and not module.check_mode
        else existing
    )
    module.exit_json(changed=changed, volume=volume or existing, diff={"before": before, "after": volume or existing})


if __name__ == "__main__":
    main()
