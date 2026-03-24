#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_loadbalancer
short_description: Manage Civo load balancers
description:
  - Query or delete Civo load balancers.
  - >-
    B(Important:) The Civo CLI does not provide C(create) or C(update) commands
    for load balancers. Load balancers are created automatically by the
    Kubernetes cloud-controller-manager when a Kubernetes C(Service) of type
    C(LoadBalancer) is deployed. The only supported state transitions via the
    CLI are C(absent) (delete) and reading the current state.
  - To read load balancer details without mutating state, prefer
    M(civo.cloud.civo_loadbalancer_info).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name or ID of the load balancer.
    required: true
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
  state:
    description:
      - C(present) is a no-op that returns the current load balancer details
        (the Civo CLI has no create command for load balancers).
      - C(absent) deletes the load balancer.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
notes:
  - Load balancers are provisioned automatically by the Kubernetes
    cloud-controller-manager and cannot be created via the Civo CLI. This
    module can only query (C(state=present)) or delete (C(state=absent)) them.
  - Use M(civo.cloud.civo_loadbalancer_info) for read-only queries.
seealso:
  - module: civo.cloud.civo_loadbalancer_info
  - module: civo.cloud.civo_kubernetes
"""

EXAMPLES = r"""
- name: Look up a load balancer created by Kubernetes
  civo.cloud.civo_loadbalancer:
    region: LON1
    name: my-lb
    state: present
  register: lb

- name: Print load balancer public IP
  ansible.builtin.debug:
    msg: "LB public IP: {{ lb.loadbalancer.public_ip }}"

- name: Delete a load balancer
  civo.cloud.civo_loadbalancer:
    region: LON1
    name: my-lb
    state: absent
"""

RETURN = r"""
loadbalancer:
  description: Details of the load balancer.
  returned: when state is C(present) and the load balancer exists
  type: dict
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
    argument_spec.update(
        name={"type": "str", "required": True},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    existing = find_resource_by_name(module, "loadbalancer", name, api_key, region, binary)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Load balancer '{name}' not found")
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete load balancer '{name}'")
        run_civo_command(module, ["loadbalancer", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Load balancer '{name}' deleted")

    # state == present -- load balancers cannot be created via CLI; just return current state
    if existing is None:
        module.exit_json(
            changed=False,
            msg=(
                f"Load balancer '{name}' not found. "
                "Note: load balancers are created automatically by the Kubernetes "
                "cloud-controller-manager; they cannot be created via the Civo CLI."
            ),
        )
    module.exit_json(changed=False, loadbalancer=existing)


if __name__ == "__main__":
    main()
