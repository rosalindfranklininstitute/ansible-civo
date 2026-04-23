#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_kubernetes
short_description: Manage Civo Kubernetes clusters
description:
  - Create, scale, upgrade, or delete Civo Kubernetes (k3s) clusters.
  - Supports in-place node-count scaling when the cluster already exists.
  - When the cluster has a single pool (the default), C(node_count) targets
    that pool.  When multiple pools exist you B(must) supply C(pool_id) to
    identify which pool to scale; otherwise the module fails to avoid silently
    operating on the wrong pool.
  - Supports in-place Kubernetes version upgrade via C(upgrade_version).
  - Returns the kubeconfig for an active cluster.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name of the Kubernetes cluster.
    required: true
    type: str
  node_size:
    description: Node pool instance size slug.
    type: str
    default: g4s.kube.medium
  node_count:
    description:
      - Desired number of worker nodes in the target pool.
      - When the cluster has only one pool this targets that pool.
      - When the cluster has multiple pools C(pool_id) must also be supplied.
      - When changed on an existing cluster the target pool is scaled in place.
    type: int
    default: 3
  pool_id:
    description:
      - ID of the node pool to scale.
      - Required when the cluster has more than one pool and C(node_count) is
        being changed.
      - Ignored during cluster creation (the first pool is always created
        automatically).
    type: str
  network:
    description: Name or ID of the network.
    type: str
    default: default
  firewall:
    description: Name or ID of the firewall.
    type: str
  cni:
    description: Container Network Interface plugin.
    type: str
    choices: [flannel, cilium]
    default: flannel
  version:
    description: Kubernetes version string (e.g. C(1.28.7-k3s1)). Empty means latest.
    type: str
    default: ""
  applications:
    description: List of Civo Marketplace application names to pre-install.
    type: list
    elements: str
    default: []
  upgrade_version:
    description:
      - Target Kubernetes version string to upgrade an existing cluster to
        (e.g. C(1.29.2-k3s1)).
      - Ignored when creating a new cluster; use C(version) for that.
      - Calls C(civo kubernetes upgrade CLUSTER UPGRADE_VERSION) and waits for
        the cluster to return to C(ACTIVE) status.
    type: str
  wait:
    description: Wait for the cluster to become ready before returning.
    type: bool
    default: true
  timeout:
    description: Seconds to wait for the cluster to become ready.
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
    description: Whether the cluster should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_network
  - module: civo.cloud.civo_firewall
  - module: civo.cloud.civo_kubernetes_pool
  - module: civo.cloud.civo_kubernetes_node
"""

EXAMPLES = r"""
- name: Create a 3-node Kubernetes cluster
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    node_size: g4s.kube.medium
    node_count: 3
    network: my-network
    cni: flannel
    wait: true
  register: k8s

- name: Save kubeconfig locally
  ansible.builtin.copy:
    content: "{{ k8s.cluster.kubeconfig }}"
    dest: ~/.kube/my-cluster.yaml
    mode: "0600"

- name: Scale the default (only) pool to 5 nodes
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    node_count: 5

- name: Scale a specific pool when the cluster has multiple pools
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    node_count: 2
    pool_id: "aaaa-bbbb-cccc"

- name: Upgrade the cluster to a newer Kubernetes version
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    upgrade_version: "1.29.2-k3s1"
    wait: true

- name: Delete a cluster
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    state: absent
"""

RETURN = r"""
cluster:
  description: Details of the Kubernetes cluster.
  returned: when state is C(present)
  type: dict
  sample:
    id: "a1b2c3d4-0000-0000-0000-000000000000"
    name: "my-cluster"
    status: "ACTIVE"
    nodes: "3"
    kubernetes_version: "1.28.7-k3s1"
    api_url: "https://74.220.1.2:6443"
    kubeconfig: "apiVersion: v1..."
  contains:
    id:
      description: Cluster UUID.
      type: str
      sample: "a1b2c3d4-0000-0000-0000-000000000000"
    name:
      description: Cluster name.
      type: str
      sample: "my-cluster"
    status:
      description: Cluster status (e.g. C(ACTIVE), C(BUILDING)).
      type: str
      sample: "ACTIVE"
    nodes:
      description: >-
        Total number of worker nodes across all pools (returned as a string
        by the CLI).
      type: str
      sample: "3"
    kubernetes_version:
      description: Kubernetes version string.
      type: str
      sample: "1.28.7-k3s1"
    api_url:
      description: Kubernetes API server endpoint URL.
      type: str
      sample: "https://74.220.1.2:6443"
    kubeconfig:
      description: Raw kubeconfig YAML for the cluster (fetched separately via C(civo kubernetes config)).
      type: str
    cluster_type:
      description: Cluster engine type (always C(k3s) for Civo).
      type: str
      sample: "k3s"
    conditions:
      description: >-
        Multi-line human-readable string describing current cluster conditions
        (e.g. "Control Plane Accessible: True\\nAll Workers Up: True").
      type: str
      sample: "Control Plane Accessible: True\nAll Workers Up: True\nCluster On Desired Version: True\n"
    pools:
      description: Total number of node pools (returned as a string by the CLI).
      type: str
      sample: "1"
"""

import time as _time

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    list_node_pools,
    run_civo_command,
    wait_for_active,
)


def _get_kubeconfig(module, cluster_name, api_key, region, binary):
    """Retrieve the raw kubeconfig YAML for a cluster."""
    env_update = {"CIVO_TOKEN": api_key}
    cmd = [binary, "kubernetes", "config", cluster_name, "--region", region, "-y"]
    rc, stdout, _ = module.run_command(cmd, environ_update=env_update)
    if rc == 0:
        return stdout.strip()
    return ""


def _resolve_pool(module, cluster_name, api_key, region, binary, requested_pool_id):
    """Return (pool_id, current_node_count) for the target pool.

    If *requested_pool_id* is given it is validated against the real pool list.
    If it is empty and there is exactly one pool, that pool is used.
    If it is empty and there are multiple pools, the module fails with a clear
    message so the operator knows they must be explicit.
    """
    pools = list_node_pools(module, cluster_name, api_key, region, binary)
    if not pools:
        module.fail_json(msg=f"No node pools found for cluster '{cluster_name}'")

    if requested_pool_id:
        for pool in pools:
            pid = pool.get("ID") or pool.get("id") or ""
            if pid == requested_pool_id:
                count = pool.get("Count") or pool.get("count") or pool.get("nodes", 0)
                return pid, int(count)
        module.fail_json(
            msg=f"pool_id '{requested_pool_id}' not found in cluster '{cluster_name}'. "
            f"Available pools: {[p.get('ID') or p.get('id') for p in pools]}"
        )

    if len(pools) > 1:
        pool_ids = [p.get("ID") or p.get("id") for p in pools]
        module.fail_json(
            msg=(
                f"Cluster '{cluster_name}' has {len(pools)} node pools. "
                "Specify 'pool_id' to identify which pool to scale. "
                f"Available pool IDs: {pool_ids}"
            )
        )

    pool = pools[0]
    pid = pool.get("ID") or pool.get("id")
    if not pid:
        module.fail_json(msg=f"Could not find pool ID in: {pool}")
    count = pool.get("Count") or pool.get("count") or pool.get("nodes", 0)
    return pid, int(count)


def _pool_node_count(module, cluster_name, pool_id, api_key, region, binary):
    """Return the current node count for a specific pool (used while waiting)."""
    pools = list_node_pools(module, cluster_name, api_key, region, binary)
    for pool in pools:
        pid = pool.get("ID") or pool.get("id") or ""
        if pid == pool_id:
            count = pool.get("Count") or pool.get("count") or pool.get("nodes", 0)
            return int(count)
    return None  # pool disappeared


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        node_size={"type": "str", "default": "g4s.kube.medium"},
        node_count={"type": "int", "default": 3},
        pool_id={"type": "str", "default": ""},
        network={"type": "str", "default": "default"},
        firewall={"type": "str"},
        cni={"type": "str", "default": "flannel", "choices": ["flannel", "cilium"]},
        version={"type": "str", "default": ""},
        applications={"type": "list", "elements": "str", "default": []},
        upgrade_version={"type": "str"},
        wait={"type": "bool", "default": True},
        timeout={"type": "int", "default": 600},
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
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary)
    before = {k: v for k, v in (existing or {}).items() if k != "kubeconfig"}

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Cluster '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete cluster '{name}'", diff={"before": before, "after": {}})
        run_civo_command(module, ["kubernetes", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Cluster '{name}' deleted", diff={"before": before, "after": {}})

    if existing:
        # ---- upgrade version if requested ----
        upgrade_version = module.params.get("upgrade_version")
        if upgrade_version:
            current_version = existing.get("kubernetes_version", "")
            if current_version != upgrade_version:
                if module.check_mode:
                    module.exit_json(
                        changed=True,
                        msg=f"Would upgrade cluster '{name}' from {current_version} to {upgrade_version}",
                        diff={"before": before, "after": {**before, "kubernetes_version": upgrade_version}},
                    )
                run_civo_command(
                    module,
                    ["kubernetes", "upgrade", name, upgrade_version],
                    api_key,
                    region,
                    binary,
                )
                if do_wait:
                    existing = wait_for_active(
                        module,
                        "kubernetes",
                        name,
                        api_key,
                        region,
                        binary=binary,
                        timeout=timeout,
                    )
                else:
                    existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary) or existing
                existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
                after = {k: v for k, v in existing.items() if k != "kubeconfig"}
                module.exit_json(changed=True, cluster=existing, diff={"before": before, "after": after})
            # already at the desired version — fall through to no-change path
            existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
            module.exit_json(changed=False, cluster=existing, diff={"before": before, "after": before})

        # ---- scale in place if node_count changed ----
        desired_count = module.params["node_count"]
        requested_pool_id = module.params.get("pool_id") or ""

        # Resolve which pool to target and its current count.
        # This call fails if there are multiple pools and pool_id is not given.
        pool_id, current_count = _resolve_pool(module, name, api_key, region, binary, requested_pool_id)

        if desired_count != current_count:
            if module.check_mode:
                module.exit_json(
                    changed=True,
                    msg=(
                        f"Would scale pool '{pool_id}' in cluster '{name}' "
                        f"from {current_count} to {desired_count} nodes"
                    ),
                    diff={"before": before, "after": {**before, "nodes": str(desired_count)}},
                )
            run_civo_command(
                module,
                ["kubernetes", "node-pool", "scale", name, pool_id, "--nodes", str(desired_count)],
                api_key,
                region,
                binary,
            )
            if do_wait:
                # The cluster stays ACTIVE during scaling, so wait_for_active
                # returns immediately.  Instead poll the specific pool's count.
                deadline = _time.time() + timeout
                while _time.time() < deadline:
                    cur = _pool_node_count(module, name, pool_id, api_key, region, binary)
                    if cur is not None and cur == desired_count:
                        break
                    _time.sleep(15)
                else:
                    module.fail_json(
                        msg=(
                            f"Timed out after {timeout}s waiting for pool '{pool_id}' "
                            f"in cluster '{name}' to reach {desired_count} nodes"
                        )
                    )
            existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary) or existing
            existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
            after = {k: v for k, v in existing.items() if k != "kubeconfig"}
            module.exit_json(changed=True, cluster=existing, diff={"before": before, "after": after})

        existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
        module.exit_json(changed=False, cluster=existing, diff={"before": before, "after": before})

    after_preview = {
        "name": name,
        "nodes": str(module.params["node_count"]),
        "kubernetes_version": module.params.get("version") or "latest",
        "cni": module.params["cni"],
    }
    if module.check_mode:
        module.exit_json(
            changed=True, msg=f"Would create cluster '{name}'", diff={"before": {}, "after": after_preview}
        )

    create_args = [
        "kubernetes",
        "create",
        name,
        "--nodes",
        str(module.params["node_count"]),
        "--size",
        module.params["node_size"],
        "--network",
        module.params["network"],
        "--cni-plugin",
        module.params["cni"],
    ]
    if module.params.get("version"):
        create_args += ["--version", module.params["version"]]
    if module.params.get("firewall"):
        create_args += ["--firewall", module.params["firewall"]]
    if module.params.get("applications"):
        create_args += ["--applications", ",".join(module.params["applications"])]

    run_civo_command(module, create_args, api_key, region, binary)

    if do_wait:
        cluster = wait_for_active(
            module,
            "kubernetes",
            name,
            api_key,
            region,
            binary=binary,
            timeout=timeout,
        )
    else:
        cluster = find_resource_by_name(module, "kubernetes", name, api_key, region, binary) or {}

    cluster["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
    after = {k: v for k, v in cluster.items() if k != "kubeconfig"}
    module.exit_json(changed=True, cluster=cluster, diff={"before": {}, "after": after})


if __name__ == "__main__":
    main()
