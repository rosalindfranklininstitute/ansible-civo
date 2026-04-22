#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_kubernetes_pool
short_description: Manage node pools in a Civo Kubernetes cluster
description:
  - Create, scale, or delete additional node pools in an existing Civo
    Kubernetes cluster.
  - C(state=present) creates the pool if it does not exist, or scales it to
    C(node_count) if it already exists.
  - C(state=absent) deletes the pool.
  - The default pool created with the cluster is B(not) managed by this module;
    use M(civo.cloud.civo_kubernetes) with C(node_count) for that.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  cluster:
    description: Name of the Kubernetes cluster to manage pools for.
    required: true
    type: str
  name:
    description: >-
      Name for the node pool.
      Used only during creation (C(--name) flag).
      When omitted the Civo API generates a name automatically.
    type: str
    default: ""
  pool_id:
    description: >-
      ID of an existing pool to update or delete.
      When supplied the module locates the pool by ID rather than by name.
      Required for C(state=absent) when more than one pool exists and the
      pool cannot be identified by name alone.
    type: str
    default: ""
  node_size:
    description: Instance size slug for nodes in this pool.
    type: str
    default: g4s.kube.medium
  node_count:
    description: Desired number of nodes in the pool.
    type: int
    default: 1
  wait:
    description: Wait for the pool to reach the desired node count after creation or scaling.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the pool to reach the desired node count.
    type: int
    default: 600
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
    description: Whether the node pool should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_kubernetes
  - module: civo.cloud.civo_kubernetes_pool_info
  - module: civo.cloud.civo_kubernetes_node
"""

EXAMPLES = r"""
- name: Add a GPU node pool to an existing cluster
  civo.cloud.civo_kubernetes_pool:
    region: LON1
    cluster: my-cluster
    name: gpu-pool
    node_size: g4g.kube.large
    node_count: 2
    wait: true
  register: pool

- name: Scale the pool to 4 nodes
  civo.cloud.civo_kubernetes_pool:
    region: LON1
    cluster: my-cluster
    pool_id: "{{ pool.pool.id }}"
    node_count: 4

- name: Delete the pool
  civo.cloud.civo_kubernetes_pool:
    region: LON1
    cluster: my-cluster
    pool_id: "{{ pool.pool.id }}"
    state: absent
"""

RETURN = r"""
pool:
  description: Details of the node pool.
  returned: when state is C(present)
  type: dict
  contains:
    id:
      description: Pool UUID.
      type: str
      sample: "aaaa-bbbb-cccc-dddd"
    count:
      description: Current node count in the pool.
      type: int
      sample: 2
    size:
      description: Instance size slug for nodes in the pool.
      type: str
      sample: "g4s.kube.medium"
"""

import json as _json
import time as _time

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def _list_pools(module, cluster, api_key, region, binary):
    """Return pool dicts for *cluster*.  Keys may be capitalized."""
    env_update = {"CIVO_TOKEN": api_key}
    cmd = [
        binary,
        "kubernetes",
        "node-pool",
        "ls",
        cluster,
        "--region",
        region,
        "-o",
        "json",
    ]
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


def _normalise_pool(pool):
    """Return a normalised pool dict with lowercase keys."""
    return {
        "id": pool.get("ID") or pool.get("id") or "",
        "name": pool.get("Name") or pool.get("name") or "",
        "count": int(pool.get("Count") or pool.get("count") or pool.get("nodes") or 0),
        "size": pool.get("Size") or pool.get("size") or "",
    }


def _find_pool(pools, pool_id, name):
    """Locate a pool by ID (preferred) or by name."""
    for pool in pools:
        n = _normalise_pool(pool)
        if pool_id and n["id"] == pool_id:
            return n
        if not pool_id and name and n["name"] == name:
            return n
    return None


def _wait_for_pool_count(module, cluster, pool_id, desired, api_key, region, binary, timeout):
    """Poll until the pool reaches *desired* node count."""
    deadline = _time.time() + timeout
    while _time.time() < deadline:
        pools = _list_pools(module, cluster, api_key, region, binary)
        for pool in pools:
            n = _normalise_pool(pool)
            if n["id"] == pool_id:
                if n["count"] == desired:
                    return n
                break
        _time.sleep(15)
    module.fail_json(msg=f"Timed out after {timeout}s waiting for pool '{pool_id}' to reach {desired} nodes")


def main():
    spec = common_argument_spec()
    spec.update(
        cluster={"type": "str", "required": True},
        name={"type": "str", "default": ""},
        pool_id={"type": "str", "default": ""},
        node_size={"type": "str", "default": "g4s.kube.medium"},
        node_count={"type": "int", "default": 1},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 600},
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    cluster = module.params["cluster"]
    pool_name = module.params.get("name") or ""
    pool_id = module.params.get("pool_id") or ""
    node_size = module.params["node_size"]
    node_count = module.params["node_count"]
    do_wait = module.params["wait"]
    timeout = module.params["timeout"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    pools = _list_pools(module, cluster, api_key, region, binary)
    existing = _find_pool(pools, pool_id, pool_name)
    before = existing or {}

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg="Pool not found; nothing to delete", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would delete pool '{existing['id']}' from cluster '{cluster}'",
                diff={"before": before, "after": {}},
            )
        run_civo_command(
            module,
            ["kubernetes", "node-pool", "delete", cluster, existing["id"]],
            api_key,
            region,
            binary,
        )
        module.exit_json(
            changed=True,
            msg=f"Pool '{existing['id']}' deleted from cluster '{cluster}'",
            diff={"before": before, "after": {}},
        )

    # state == "present"
    if existing is None:
        # Create a new pool
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would create pool in cluster '{cluster}' with {node_count} x {node_size} nodes",
                diff={"before": {}, "after": {"size": node_size, "count": node_count}},
            )
        create_args = [
            "kubernetes",
            "node-pool",
            "create",
            cluster,
            "--size",
            node_size,
            "--nodes",
            str(node_count),
        ]
        if pool_name:
            create_args += ["--name", pool_name]
        run_civo_command(module, create_args, api_key, region, binary)

        if do_wait:
            # Re-fetch pools and find the new one by name (if named) or by
            # process of elimination (pick the ID not in the original list)
            original_ids = {_normalise_pool(p)["id"] for p in pools}
            deadline = _time.time() + timeout
            new_pool = None
            while _time.time() < deadline:
                fresh_pools = _list_pools(module, cluster, api_key, region, binary)
                for p in fresh_pools:
                    n = _normalise_pool(p)
                    if n["id"] not in original_ids:
                        if n["count"] >= node_count:
                            new_pool = n
                            break
                        # Found the new pool but not yet at count; keep waiting
                        new_pool = n
                        break
                if new_pool and new_pool["count"] >= node_count:
                    break
                _time.sleep(15)
            else:
                module.fail_json(msg=f"Timed out after {timeout}s waiting for new pool to reach {node_count} nodes")
        else:
            original_ids = {_normalise_pool(p)["id"] for p in pools}
            fresh_pools = _list_pools(module, cluster, api_key, region, binary)
            new_pool = None
            for p in fresh_pools:
                n = _normalise_pool(p)
                if n["id"] not in original_ids:
                    new_pool = n
                    break
            new_pool = new_pool or {}

        module.exit_json(changed=True, pool=new_pool, diff={"before": {}, "after": new_pool or {}})

    # Pool already exists — check if scale is needed
    if existing["count"] != node_count:
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=(
                    f"Would scale pool '{existing['id']}' in cluster '{cluster}' "
                    f"from {existing['count']} to {node_count} nodes"
                ),
                diff={"before": before, "after": {**before, "count": node_count}},
            )
        run_civo_command(
            module,
            ["kubernetes", "node-pool", "scale", cluster, existing["id"], "--nodes", str(node_count)],
            api_key,
            region,
            binary,
        )
        if do_wait:
            existing = _wait_for_pool_count(
                module, cluster, existing["id"], node_count, api_key, region, binary, timeout
            )
        else:
            pools = _list_pools(module, cluster, api_key, region, binary)
            existing = _find_pool(pools, existing["id"], pool_name) or existing
        module.exit_json(changed=True, pool=existing, diff={"before": before, "after": existing})

    module.exit_json(changed=False, pool=existing, diff={"before": before, "after": before})


if __name__ == "__main__":
    main()
