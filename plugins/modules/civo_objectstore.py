#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_objectstore
short_description: Manage Civo S3-compatible object stores
description:
  - Create or delete Civo object store buckets.
  - When a store is created without an explicit owner credential, Civo
    automatically generates a dedicated credential for it.  Those auto-created
    credentials are B(not) removed when the store is deleted.  Set
    I(purge_credentials=true) on the delete call to clean them up.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
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
  purge_credentials:
    description:
      - When C(true) and I(state=absent), also delete the object store's
        owner credential after the store is removed.
      - The module looks up the linked credential via C(civo objectstore show)
        (which returns the C(accesskey) field), then cross-references
        C(civo objectstore credential ls) to find its name and deletes it.
      - B(Only) set this when you know the credential is not shared with other
        stores.  If you created the store with an explicit I(access_key_id)
        pointing to a shared credential, leave this as C(false).
      - Has no effect when I(state=present).
    type: bool
    default: false
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
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
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

- name: Delete an object store and its auto-created credential
  civo.cloud.civo_objectstore:
    region: LON1
    name: my-bucket
    state: absent
    purge_credentials: true
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
        purge_credentials={"type": "bool", "default": False},
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
    purge_credentials = module.params["purge_credentials"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "objectstore", name, api_key, region, binary)
    before = existing or {}

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Object store '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(
                changed=True, msg=f"Would delete object store '{name}'", diff={"before": before, "after": {}}
            )

        # Resolve linked credential before the store is deleted (show returns accesskey).
        cred_name_to_delete = None
        if purge_credentials:
            _rc, show_data, _stderr = run_civo_command(
                module, ["objectstore", "show", name], api_key, region, binary, check_rc=False
            )
            show_list = show_data if isinstance(show_data, list) else ([show_data] if show_data else [])
            store_access_key = None
            for item in show_list:
                if isinstance(item, dict):
                    store_access_key = item.get("accesskey") or item.get("access_key")
                    if store_access_key:
                        break

            if store_access_key:
                _rc2, cred_data, _stderr2 = run_civo_command(
                    module, ["objectstore", "credential", "ls"], api_key, region, binary, check_rc=False
                )
                creds = cred_data if isinstance(cred_data, list) else []
                for cred in creds:
                    if cred.get("access_key") == store_access_key:
                        cred_name_to_delete = cred.get("name")
                        break

                # Safety check: refuse to purge a credential that is shared with other stores.
                if cred_name_to_delete:
                    _rc3, stores_data, _stderr3 = run_civo_command(
                        module, ["objectstore", "ls"], api_key, region, binary, check_rc=False
                    )
                    all_stores = stores_data if isinstance(stores_data, list) else []
                    sharing = []
                    for other in all_stores:
                        other_name = other.get("name", "")
                        if not other_name or other_name == name:
                            continue
                        # Fetch the other store's detail to check its access key
                        _rc4, other_show, _se4 = run_civo_command(
                            module, ["objectstore", "show", other_name], api_key, region, binary, check_rc=False
                        )
                        other_list = (
                            other_show if isinstance(other_show, list) else ([other_show] if other_show else [])
                        )
                        for oitem in other_list:
                            if isinstance(oitem, dict):
                                okey = oitem.get("accesskey") or oitem.get("access_key")
                                if okey and okey == store_access_key:
                                    sharing.append(other_name)
                    if sharing:
                        module.fail_json(
                            msg=(
                                f"Refusing to purge credential '{cred_name_to_delete}': "
                                f"it is also used by object store(s): {sharing}. "
                                "Delete those stores first, or set purge_credentials=false."
                            )
                        )

        run_civo_command(module, ["objectstore", "delete", name], api_key, region, binary)

        if purge_credentials and cred_name_to_delete:
            run_civo_command(
                module,
                ["objectstore", "credential", "delete", cred_name_to_delete],
                api_key,
                region,
                binary,
            )
            module.exit_json(
                changed=True,
                msg=f"Object store '{name}' deleted; credential '{cred_name_to_delete}' purged",
                diff={"before": before, "after": {}},
            )

        module.exit_json(changed=True, msg=f"Object store '{name}' deleted", diff={"before": before, "after": {}})

    if existing:
        module.exit_json(changed=False, objectstore=existing, diff={"before": before, "after": before})

    after_preview = {"name": name}
    if module.params.get("max_size_gb") is not None:
        after_preview["max_size"] = str(module.params["max_size_gb"])
    if module.check_mode:
        module.exit_json(
            changed=True, msg=f"Would create object store '{name}'", diff={"before": {}, "after": after_preview}
        )

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

    module.exit_json(changed=True, objectstore=store, diff={"before": {}, "after": store})


if __name__ == "__main__":
    main()
