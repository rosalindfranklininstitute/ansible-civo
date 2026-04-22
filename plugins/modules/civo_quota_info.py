#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_quota_info
short_description: Return current Civo account quota and usage
description:
  - Returns the quota limits and current usage for a Civo account in a given
    region.
  - Useful for capacity-planning checks before provisioning resources.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
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
"""

EXAMPLES = r"""
- name: Get account quota and usage
  civo.cloud.civo_quota_info:
    region: LON1
  register: quota

- name: Show instance usage vs limit
  ansible.builtin.debug:
    msg: >-
      Instances: {{ quota.quota.instance_count_usage }}
      / {{ quota.quota.instance_count_limit }}

- name: Fail if near instance limit
  ansible.builtin.fail:
    msg: "Instance quota nearly exhausted!"
  when: >-
    quota.quota.instance_count_usage | int
    >= (quota.quota.instance_count_limit | int * 0.9) | int
"""

RETURN = r"""
quota:
  description: >-
    Dict of quota limits and current usage for the account.
    All values are returned as strings by the Civo CLI; cast to C(int) as
    needed.
  returned: always
  type: dict
  contains:
    instance_count_limit:
      description: Maximum number of instances allowed.
      type: str
      sample: "16"
    instance_count_usage:
      description: Current number of instances.
      type: str
      sample: "2"
    cpu_core_limit:
      description: Maximum total vCPU cores across all instances.
      type: str
      sample: "16"
    cpu_core_usage:
      description: Currently used vCPU cores.
      type: str
      sample: "2"
    ram_mb_limit:
      description: Maximum total RAM in megabytes.
      type: str
      sample: "64512"
    ram_mb_usage:
      description: Currently used RAM in megabytes.
      type: str
      sample: "2048"
    disk_gb_limit:
      description: Maximum total disk in gigabytes.
      type: str
      sample: "400"
    disk_gb_usage:
      description: Currently used disk in gigabytes.
      type: str
      sample: "25"
    disk_volume_count_limit:
      description: Maximum number of volumes.
      type: str
      sample: "16"
    disk_volume_count_usage:
      description: Current number of volumes.
      type: str
      sample: "0"
    network_count_limit:
      description: Maximum number of networks.
      type: str
      sample: "10"
    network_count_usage:
      description: Current number of networks.
      type: str
      sample: "2"
    public_ip_address_limit:
      description: Maximum number of reserved public IPs.
      type: str
      sample: "16"
    public_ip_address_usage:
      description: Current number of reserved public IPs.
      type: str
      sample: "0"
    security_group_limit:
      description: Maximum number of security groups (firewalls).
      type: str
      sample: "16"
    security_group_usage:
      description: Current number of security groups.
      type: str
      sample: "1"
    database_count_limit:
      description: Maximum number of managed databases.
      type: str
      sample: "4"
    database_count_usage:
      description: Current number of managed databases.
      type: str
      sample: "0"
    objectstore_gb_limit:
      description: Maximum object store capacity in gigabytes.
      type: str
      sample: "1000"
    objectstore_gb_usage:
      description: Currently used object store capacity in gigabytes.
      type: str
      sample: "0"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    _rc, data, _stderr = run_civo_command(module, ["quota"], api_key, region, binary, check_rc=False)

    # CLI returns a JSON array with a single object
    if isinstance(data, list) and data:
        quota = data[0]
    elif isinstance(data, dict):
        quota = data
    else:
        quota = {}

    module.exit_json(changed=False, quota=quota)


if __name__ == "__main__":
    main()
