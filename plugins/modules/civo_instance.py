#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_instance
short_description: Manage Civo compute instances
description:
  - Create, update, start, stop, or delete Civo compute instances.
  - Supports in-place updates for I(firewall), I(tags), and I(size) (resize)
    when an instance already exists.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  hostname:
    description: Hostname of the instance (used as the unique identifier).
    required: true
    type: str
  size:
    description:
      - Instance size slug (e.g. C(g4s.small), C(g4s.medium)).
      - When changed on an existing instance the instance is resized in place.
    type: str
    default: g4s.small
  diskimage:
    description: Disk image name or ID (e.g. C(ubuntu-noble)).
    type: str
    default: ubuntu-noble
  network:
    description: Name or ID of the network.
    type: str
    default: default
  firewall:
    description:
      - Name or ID of the firewall.
      - When changed on an existing instance the firewall assignment is updated.
    type: str
  ssh_key:
    description: Name or ID of the SSH key to inject.
    type: str
  initial_user:
    description: Username to create on the instance.
    type: str
  public_ip:
    description: Whether to assign a public IP (C(create)) or not (C(none)).
    type: str
    choices: [create, none]
    default: create
  tags:
    description:
      - Space-separated list of tags.
      - When changed on an existing instance the tags are updated in place.
    type: str
  script:
    description: User-data / cloud-init script to run on first boot.
    type: str
  wait:
    description: Wait for the instance to become C(ACTIVE) before returning.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the instance to become active.
    type: int
    default: 600
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable when not set.
    type: str
  region:
    description: Civo region identifier.
    type: str
    default: LON1
  state:
    description:
      - C(present) ensures the instance exists and is running.
      - C(absent) deletes the instance.
      - C(started) ensures the instance is running (creates if needed).
      - C(stopped) ensures the instance is stopped.
    type: str
    choices: [present, absent, started, stopped]
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
- name: Create an instance
  civo.cloud.civo_instance:
    region: LON1
    hostname: web-01.example.com
    size: g4s.small
    diskimage: ubuntu-noble
    network: my-network
    firewall: web-fw
    ssh_key: my-key
    initial_user: ubuntu
    wait: true
  register: vm

- name: Print public IP
  ansible.builtin.debug:
    msg: "Public IP: {{ vm.instance.public_ip }}"

- name: Resize an instance
  civo.cloud.civo_instance:
    region: LON1
    hostname: web-01.example.com
    size: g4s.medium

- name: Stop an instance
  civo.cloud.civo_instance:
    region: LON1
    hostname: web-01.example.com
    state: stopped

- name: Delete an instance
  civo.cloud.civo_instance:
    region: LON1
    hostname: web-01.example.com
    state: absent
"""

RETURN = r"""
instance:
  description: Details of the managed instance.
  returned: when state is C(present) or C(started) or C(stopped)
  type: dict
  contains:
    id:
      description: Instance UUID.
      type: str
      sample: a1b2c3d4-0000-0000-0000-000000000000
    hostname:
      description: Instance hostname.
      type: str
      sample: web-01.example.com
    status:
      description: Current status (C(ACTIVE), C(BUILDING), C(SHUTOFF), etc.).
      type: str
      sample: ACTIVE
    public_ip:
      description: Public IP address (empty string if no public IP was assigned).
      type: str
      sample: 74.220.1.2
    private_ip:
      description: Private IP address within the network.
      type: str
      sample: 192.168.1.4
    size:
      description: Instance size slug.
      type: str
      sample: g3.xsmall
    region:
      description: Region the instance is deployed in.
      type: str
      sample: LON1
    network_id:
      description: UUID of the network the instance belongs to.
      type: str
    firewall_id:
      description: UUID of the attached firewall.
      type: str
    diskimage_id:
      description: Disk image identifier used to create the instance.
      type: str
      sample: debian-11
    initial_user:
      description: Initial admin username on the instance.
      type: str
      sample: civo
    cpu_cores:
      description: Number of vCPU cores (returned as string by CLI).
      type: str
      sample: "1"
    ram_mb:
      description: RAM in megabytes (returned as string by CLI).
      type: str
      sample: "1024"
    disk_gb:
      description: Root disk size in gigabytes (returned as string by CLI).
      type: str
      sample: "25"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
    wait_for_active,
)


def _update_instance(module, hostname, existing, api_key, region, binary):
    """Apply any in-place updates. Returns True if any change was made."""
    changed = False

    # ---- firewall reassignment ----
    desired_fw = module.params.get("firewall")
    if desired_fw:
        current_fw_id = existing.get("firewall_id", "")
        # desired_fw may be a name or UUID; compare against existing UUID/name
        # If it looks like a name (not a UUID), resolve it to its ID first.
        fw_match = desired_fw in (current_fw_id,)
        if not fw_match:
            # Try to resolve the desired firewall name to an ID
            fw_obj = find_resource_by_name(module, "firewall", desired_fw, api_key, region, binary)
            if fw_obj and fw_obj.get("id") == current_fw_id:
                fw_match = True
        if not fw_match:
            if not module.check_mode:
                run_civo_command(
                    module,
                    ["instance", "firewall", hostname, desired_fw],
                    api_key,
                    region,
                    binary,
                )
            changed = True

    # ---- tag update ----
    desired_tags = module.params.get("tags")
    if desired_tags is not None:
        current_tags = " ".join(existing.get("tags", []) or [])
        if desired_tags != current_tags:
            if not module.check_mode:
                run_civo_command(
                    module,
                    ["instance", "tags", hostname, desired_tags],
                    api_key,
                    region,
                    binary,
                )
            changed = True

    # ---- resize ----
    desired_size = module.params.get("size")
    if desired_size and desired_size != existing.get("size", ""):
        if not module.check_mode:
            run_civo_command(
                module,
                ["instance", "upgrade", hostname, desired_size],
                api_key,
                region,
                binary,
            )
        changed = True

    return changed


def main():
    argument_spec = common_argument_spec()
    argument_spec["state"] = {
        "type": "str",
        "default": "present",
        "choices": ["present", "absent", "started", "stopped"],
    }
    argument_spec.update(
        hostname={"type": "str", "required": True},
        size={"type": "str", "default": "g4s.small"},
        diskimage={"type": "str", "default": "ubuntu-noble"},
        network={"type": "str", "default": "default"},
        firewall={"type": "str"},
        ssh_key={"type": "str"},
        initial_user={"type": "str"},
        public_ip={"type": "str", "default": "create", "choices": ["create", "none"]},
        tags={"type": "str"},
        script={"type": "str"},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 600},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    hostname = module.params["hostname"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]
    do_wait = module.params["wait"]
    timeout = module.params["timeout"]

    if not api_key:
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    existing = find_resource_by_name(module, "instance", hostname, api_key, region, binary)

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Instance '{hostname}' not found")
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete instance '{hostname}'")
        run_civo_command(module, ["instance", "remove", hostname], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Instance '{hostname}' deleted")

    # ------------------------------------------------------------------ stopped
    if state == "stopped":
        if existing is None:
            module.fail_json(msg=f"Instance '{hostname}' not found; cannot stop")
        current_status = existing.get("status", "").upper()
        if current_status == "SHUTOFF":
            module.exit_json(changed=False, instance=existing)
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would stop instance '{hostname}'")
        # Use --wait so the CLI blocks until the instance is fully stopped,
        # then re-fetch to return the current state.
        stop_args = ["instance", "stop", hostname]
        if do_wait:
            stop_args.append("--wait")
        run_civo_command(module, stop_args, api_key, region, binary)
        instance = find_resource_by_name(module, "instance", hostname, api_key, region, binary) or existing
        module.exit_json(changed=True, instance=instance)

    # ----------------------------------------------------------- present/started
    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would create instance '{hostname}'")

        create_args = [
            "instance",
            "create",
            "--hostname",
            hostname,
            "--size",
            module.params["size"],
            "--diskimage",
            module.params["diskimage"],
            "--network",
            module.params["network"],
            "--publicip",
            module.params["public_ip"],
        ]
        if module.params.get("firewall"):
            create_args += ["--firewall", module.params["firewall"]]
        if module.params.get("ssh_key"):
            create_args += ["--sshkey", module.params["ssh_key"]]
        if module.params.get("initial_user"):
            create_args += ["--initialuser", module.params["initial_user"]]
        if module.params.get("tags"):
            create_args += ["--tags", module.params["tags"]]
        if module.params.get("script"):
            create_args += ["--script", module.params["script"]]

        run_civo_command(module, create_args, api_key, region, binary)

        if do_wait:
            instance = wait_for_active(
                module,
                "instance",
                hostname,
                api_key,
                region,
                binary=binary,
                timeout=timeout,
            )
        else:
            instance = find_resource_by_name(module, "instance", hostname, api_key, region, binary) or {}

        module.exit_json(changed=True, instance=instance)

    # Instance exists — apply updates
    current_status = existing.get("status", "").upper()

    # Ensure it is running if state=started
    if state == "started" and current_status == "SHUTOFF":
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would start instance '{hostname}'")
        run_civo_command(module, ["instance", "start", hostname], api_key, region, binary)
        if do_wait:
            existing = wait_for_active(
                module,
                "instance",
                hostname,
                api_key,
                region,
                binary=binary,
                timeout=timeout,
            )
        else:
            existing = find_resource_by_name(module, "instance", hostname, api_key, region, binary) or existing
        module.exit_json(changed=True, instance=existing)

    # Apply drift corrections (firewall, tags, size)
    changed = _update_instance(module, hostname, existing, api_key, region, binary)

    if changed and not module.check_mode:
        existing = find_resource_by_name(module, "instance", hostname, api_key, region, binary) or existing

    module.exit_json(changed=changed, instance=existing)


if __name__ == "__main__":
    main()
