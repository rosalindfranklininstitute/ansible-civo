#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_sshkey
short_description: Manage Civo SSH keys
description:
  - Upload, rename, or remove SSH public keys stored in a Civo account.
  - Idempotent — if a key with the same name already exists, the module reports
    C(changed=False) for C(state=present) (re-upload is not supported by the
    Civo CLI; rename the key first if you need to replace it).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name / label for the SSH key.
    required: true
    type: str
  public_key_file:
    description:
      - Path to the SSH public key file on the control node.
      - Required when I(state=present) and the key does not yet exist.
    type: str
  new_name:
    description:
      - Rename an existing SSH key to this value.
      - When provided alongside I(state=present) the key is first created (if
        absent) and then renamed; if the key already exists under I(name) it is
        just renamed.
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
      - C(present) ensures the SSH key exists in the account.
      - C(absent) removes the SSH key.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_sshkey_info
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: Upload an SSH public key
  civo.cloud.civo_sshkey:
    name: my-laptop-key
    public_key_file: ~/.ssh/id_ed25519.pub

- name: Remove an SSH key
  civo.cloud.civo_sshkey:
    name: my-laptop-key
    state: absent

- name: Rename an existing SSH key
  civo.cloud.civo_sshkey:
    name: my-laptop-key
    new_name: laptop-ed25519
    state: present

- name: Upload key and use it when creating an instance
  civo.cloud.civo_sshkey:
    name: deploy-key
    public_key_file: /home/ci/.ssh/id_rsa.pub

- name: Create instance using the uploaded key
  civo.cloud.civo_instance:
    hostname: web-01
    size: g3.xsmall
    diskimage: debian-11
    sshkey: deploy-key
    state: present
"""

RETURN = r"""
sshkey:
  description: Details of the managed SSH key.
  returned: when state is C(present)
  type: dict
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

import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        public_key_file={"type": "str"},
        new_name={"type": "str"},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]
    public_key_file = module.params.get("public_key_file")
    new_name = module.params.get("new_name")

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "sshkey", name, api_key, region, binary)
    before = existing or {}

    # ------------------------------------------------------------------ absent
    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"SSH key '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would remove SSH key '{name}'", diff={"before": before, "after": {}})
        run_civo_command(module, ["sshkey", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"SSH key '{name}' removed", diff={"before": before, "after": {}})

    # ----------------------------------------------------------------- present
    created = False
    if existing is None:
        if not public_key_file:
            module.fail_json(msg="'public_key_file' is required when state=present and the key does not exist")
        key_path = os.path.expanduser(public_key_file)
        if not os.path.isfile(key_path):
            module.fail_json(msg=f"public_key_file not found: {key_path}")
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would upload SSH key '{name}' from {key_path}",
                diff={"before": {}, "after": {"name": name}},
            )
        run_civo_command(
            module,
            ["sshkey", "create", name, "--key", key_path],
            api_key,
            region,
            binary,
        )
        existing = find_resource_by_name(module, "sshkey", name, api_key, region, binary) or {}
        created = True

    changed = created

    # ------------------------------------------------------------------ rename
    if new_name and new_name != name:
        target = find_resource_by_name(module, "sshkey", new_name, api_key, region, binary)
        if target is None:
            if module.check_mode:
                module.exit_json(
                    changed=True,
                    msg=f"Would rename SSH key '{name}' to '{new_name}'",
                    diff={"before": before, "after": {**before, "name": new_name}},
                )
            run_civo_command(
                module,
                ["sshkey", "update", name, new_name],
                api_key,
                region,
                binary,
            )
            existing = find_resource_by_name(module, "sshkey", new_name, api_key, region, binary) or {}
            changed = True
        else:
            # Already renamed / target exists — report the target key
            existing = target

    module.exit_json(changed=changed, sshkey=existing, diff={"before": before, "after": existing})


if __name__ == "__main__":
    main()
