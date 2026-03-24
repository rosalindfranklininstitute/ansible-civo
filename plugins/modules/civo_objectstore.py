#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_objectstore
short_description: Manage Civo S3-compatible object stores
description:
  - Create or delete Civo object store buckets.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name of the object store.
    required: true
    type: str
  max_size_gb:
    description:
      - Maximum size of the object store in gigabytes.
      - C(0) means unlimited.
    type: int
  access_key_id:
    description:
      - Access key ID of existing object store credentials to associate.
      - When omitted, new credentials are generated automatically.
      - Maps to the C(--owner-access-key) CLI flag.
    type: str
  wait:
    description: Wait for the object store to become ready before returning.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the object store to become ready.
    type: int
    default: 300
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
    description: Whether the object store should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_network
"""

EXAMPLES = r"""
- name: Create an object store with a 500 GB limit
  civo.cloud.civo_objectstore:
    region: LON1
    name: my-bucket
    max_size_gb: 500
    wait: true
  register: bucket

- name: Print S3 endpoint
  ansible.builtin.debug:
    msg: "Endpoint: {{ bucket.objectstore.endpoint }}"

- name: Delete an object store
  civo.cloud.civo_objectstore:
    region: LON1
    name: my-bucket
    state: absent
"""

RETURN = r"""
objectstore:
  description: Details of the managed object store.
  returned: when state is C(present)
  type: dict
  sample:
    id: "a1b2c3d4-0000-0000-0000-000000000000"
    name: "my-bucket"
    max_size: "500"
    status: "ready"
    objectstore_endpoint: "objectstore.lon1.civo.com"
  contains:
    id:
      description: Object store UUID.
      type: str
      sample: "a1b2c3d4-0000-0000-0000-000000000000"
    name:
      description: Object store name.
      type: str
      sample: "my-bucket"
    max_size:
      description: Maximum size quota in GB (as a string from the CLI).
      type: str
      sample: "500"
    status:
      description: Object store status (e.g. C(ready)).
      type: str
      sample: "ready"
    objectstore_endpoint:
      description: S3-compatible endpoint hostname.
      type: str
      sample: "objectstore.lon1.civo.com"
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
        max_size_gb={"type": "int"},
        access_key_id={"type": "str"},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 300},
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
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    existing = find_resource_by_name(module, "objectstore", name, api_key, region, binary)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Object store '{name}' not found")
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete object store '{name}'")
        run_civo_command(module, ["objectstore", "delete", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Object store '{name}' deleted")

    if existing:
        module.exit_json(changed=False, objectstore=existing)

    if module.check_mode:
        module.exit_json(changed=True, msg=f"Would create object store '{name}'")

    create_args = ["objectstore", "create", name]
    # Explicit is-not-None guard so that 0 (unlimited) is correctly passed through
    if module.params.get("max_size_gb") is not None:
        create_args += ["--size", str(module.params["max_size_gb"])]
    if module.params.get("access_key_id"):
        create_args += ["--owner-access-key", module.params["access_key_id"]]

    run_civo_command(module, create_args, api_key, region, binary)

    if do_wait:
        store = wait_for_active(
            module,
            "objectstore",
            name,
            api_key,
            region,
            binary=binary,
            timeout=timeout,
        )
    else:
        store = find_resource_by_name(module, "objectstore", name, api_key, region, binary) or {}

    module.exit_json(changed=True, objectstore=store)


if __name__ == "__main__":
    main()
