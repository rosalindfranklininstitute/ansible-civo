#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_kubernetes_pool_info
short_description: Query node pools in a Civo Kubernetes cluster
description:
  - Returns information about node pools in an existing Civo Kubernetes
    cluster, including the list of node instances in each pool.
  - When C(pool_id) is supplied only that pool is returned.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  cluster:
    description: Name of the Kubernetes cluster to query.
    required: true
    type: str
  pool_id:
    description: ID of a specific pool to return.  When omitted all pools are returned.
    type: str
  instances:
    description: >-
      When C(true) each pool dict will include an C(instances) list with
      the node hostnames and IDs in that pool.
    type: bool
    default: false
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
seealso:
  - module: civo.cloud.civo_kubernetes_pool
  - module: civo.cloud.civo_kubernetes_node
  - module: civo.cloud.civo_kubernetes_info
"""

EXAMPLES = r"""
- name: List all pools in a cluster
  civo.cloud.civo_kubernetes_pool_info:
    region: LON1
    cluster: my-cluster
  register: pools

- name: List pools and include node instance details
  civo.cloud.civo_kubernetes_pool_info:
    region: LON1
    cluster: my-cluster
    instances: true
  register: pools_detail

- name: Show the first pool's node hostnames
  ansible.builtin.debug:
    msg: "{{ pools_detail.pools[0].instances | map(attribute='hostname') | list }}"
"""

RETURN = r"""
pools:
  description: List of node pool dicts.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Pool UUID.
      type: str
      sample: "aaaa-bbbb-cccc-dddd"
    name:
      description: Pool name.
      type: str
      sample: "gpu-pool"
    count:
      description: Current node count.
      type: int
      sample: 2
    size:
      description: Node instance size slug.
      type: str
      sample: "g4s.kube.medium"
    instances:
      description: List of node instance dicts (only when C(instances=true)).
      type: list
      elements: dict
      returned: when instances is C(true)
      contains:
        id:
          description: Instance UUID.
          type: str
        hostname:
          description: Node hostname.
          type: str
"""

import json as _json

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
)


def _list_pools(module, cluster, api_key, region, binary):
    env_update = {"CIVO_TOKEN": api_key}
    cmd = [binary, "kubernetes", "node-pool", "ls", cluster, "--region", region, "-o", "json"]
    rc, stdout, stderr = module.run_command(cmd, environ_update=env_update)
    if rc != 0:
        module.fail_json(msg=f"Failed to list node pools for '{cluster}': {stderr}")
    json_line = None
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            json_line = stripped
            break
    if json_line is None:
        return []
    try:
        pools = _json.loads(json_line)
    except _json.JSONDecodeError:
        return []
    return pools if isinstance(pools, list) else []


def _list_instances(module, cluster, pool_id, api_key, region, binary):
    env_update = {"CIVO_TOKEN": api_key}
    cmd = [
        binary,
        "kubernetes",
        "node-pool",
        "instance-ls",
        cluster,
        "--node-pool-id",
        pool_id,
        "--region",
        region,
        "-o",
        "json",
    ]
    rc, stdout, stderr = module.run_command(cmd, environ_update=env_update)
    if rc != 0:
        return []
    json_line = None
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            json_line = stripped
            break
    if json_line is None:
        return []
    try:
        instances = _json.loads(json_line)
    except _json.JSONDecodeError:
        return []
    return instances if isinstance(instances, list) else []


def _normalise_pool(pool):
    return {
        "id": pool.get("ID") or pool.get("id") or "",
        "name": pool.get("Name") or pool.get("name") or "",
        "count": int(pool.get("Count") or pool.get("count") or pool.get("nodes") or 0),
        "size": pool.get("Size") or pool.get("size") or "",
    }


def _normalise_instance(inst):
    return {
        "id": inst.get("ID") or inst.get("id") or "",
        "hostname": inst.get("Hostname") or inst.get("hostname") or inst.get("name") or "",
    }


def main():
    spec = common_argument_spec()
    # info module — no state
    del spec["state"]
    spec.update(
        cluster={"type": "str", "required": True},
        pool_id={"type": "str"},
        instances={"type": "bool", "default": False},
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    cluster = module.params["cluster"]
    filter_pool_id = module.params.get("pool_id") or ""
    include_instances = module.params["instances"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    raw_pools = _list_pools(module, cluster, api_key, region, binary)
    result_pools = []
    for raw in raw_pools:
        n = _normalise_pool(raw)
        if filter_pool_id and n["id"] != filter_pool_id:
            continue
        if include_instances:
            raw_insts = _list_instances(module, cluster, n["id"], api_key, region, binary)
            n["instances"] = [_normalise_instance(i) for i in raw_insts]
        result_pools.append(n)

    module.exit_json(changed=False, pools=result_pools)


if __name__ == "__main__":
    main()
