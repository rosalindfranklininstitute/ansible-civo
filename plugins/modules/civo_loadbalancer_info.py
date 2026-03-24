#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_loadbalancer_info
short_description: Gather information about Civo load balancers
description:
  - Returns details of one or all Civo load balancers in a region.
  - Load balancers on Civo are created automatically by the Kubernetes
    cloud-controller-manager when a C(Service) of type C(LoadBalancer) is
    deployed; they cannot be created or deleted directly via the Civo CLI.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description:
      - Name of the load balancer to look up.
      - When omitted, all load balancers in the region are returned.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable when not set.
    type: str
  region:
    description: Civo region identifier (e.g. C(LON1), C(NYC1), C(FRA1), C(PHX1)).
    type: str
    default: LON1
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_kubernetes
notes:
  - Load balancers are provisioned automatically by the Kubernetes
    cloud-controller-manager and cannot be managed directly through the Civo
    CLI. Use this module only to query existing load balancers that were
    created by a Kubernetes C(LoadBalancer) service.
"""

EXAMPLES = r"""
- name: List all load balancers
  civo.cloud.civo_loadbalancer_info:
    region: LON1
  register: lbs

- name: Get a specific load balancer
  civo.cloud.civo_loadbalancer_info:
    region: LON1
    name: my-lb
  register: lb

- name: Print load balancer public IP
  ansible.builtin.debug:
    msg: "LB public IP: {{ lb.loadbalancers[0].public_ip }}"
  when: lb.loadbalancers | length > 0
"""

RETURN = r"""
loadbalancers:
  description: List of load balancer dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Load balancer UUID.
      type: str
      sample: a1b2c3d4-0000-0000-0000-000000000000
    name:
      description: Load balancer name.
      type: str
      sample: my-lb
    algorithm:
      description: Load-balancing algorithm (e.g. C(round_robin)).
      type: str
      sample: round_robin
    public_ip:
      description: Assigned public IP address.
      type: str
      sample: 74.220.1.2
    state:
      description: Provisioning state (e.g. C(active)).
      type: str
      sample: active
    firewall_id:
      description: UUID of the attached firewall.
      type: str
    cluster_id:
      description: UUID of the Kubernetes cluster that owns this load balancer.
      type: str
    dns_entry:
      description: DNS hostname for the load balancer (if set).
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
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    if name:
        result = find_resource_by_name(module, "loadbalancer", name, api_key, region, binary)
        loadbalancers = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["loadbalancer", "ls"], api_key, region, binary, check_rc=False)
        loadbalancers = data if isinstance(data, list) else []

    module.exit_json(changed=False, loadbalancers=loadbalancers)


if __name__ == "__main__":
    main()
