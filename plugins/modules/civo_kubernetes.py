#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_kubernetes
short_description: Manage Civo Kubernetes clusters
description:
  - Create, scale, or delete Civo Kubernetes (k3s) clusters.
  - Supports in-place node-count scaling when the cluster already exists.
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
      - Number of worker nodes.
      - When changed on an existing cluster the node pool is scaled in place.
    type: int
    default: 3
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
      - Falls back to the C(CIVO_TOKEN) environment variable when not set.
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

- name: Scale the cluster to 5 nodes
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    node_count: 5

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
        Number of worker nodes (returned as a string by the CLI).
        For idempotency the module compares this against the C(node_count) parameter.
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
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
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


def _get_node_pool_id(module, cluster_name, api_key, region, binary):
    """Return the ID of the first node pool in the cluster."""
    import json as _json

    env_update = {"CIVO_TOKEN": api_key}
    cmd = [
        binary,
        "kubernetes",
        "node-pool",
        "ls",
        cluster_name,
        "--region",
        region,
        "-o",
        "json",
    ]
    rc, stdout, stderr = module.run_command(cmd, environ_update=env_update)
    if rc != 0:
        module.fail_json(msg=f"Failed to list node pools for '{cluster_name}': {stderr}")
    # The CLI mixes human-readable table text and a JSON array in stdout.
    # Extract the line that starts with "[" to get just the JSON part.
    json_line = None
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("["):
            json_line = line
            break
    if json_line is None:
        module.fail_json(msg=f"Failed to find node-pool JSON in output: {stdout}")
    try:
        pools = _json.loads(json_line)
    except _json.JSONDecodeError:
        module.fail_json(msg=f"Failed to parse node-pool JSON: {json_line}")
    if not pools:
        module.fail_json(msg=f"No node pools found for cluster '{cluster_name}'")
    # The CLI returns capitalized keys (e.g. "ID") in node-pool ls JSON
    pool = pools[0]
    pool_id = pool.get("ID") or pool.get("id")
    if not pool_id:
        module.fail_json(msg=f"Could not find pool ID in: {pool}")
    return pool_id


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        node_size={"type": "str", "default": "g4s.kube.medium"},
        node_count={"type": "int", "default": 3},
        network={"type": "str", "default": "default"},
        firewall={"type": "str"},
        cni={"type": "str", "default": "flannel", "choices": ["flannel", "cilium"]},
        version={"type": "str", "default": ""},
        applications={"type": "list", "elements": "str", "default": []},
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
        module.fail_json(msg="api_key is required (or set the CIVO_TOKEN environment variable)")

    existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary)

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Cluster '{name}' not found")
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete cluster '{name}'")
        run_civo_command(module, ["kubernetes", "remove", name], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Cluster '{name}' deleted")

    if existing:
        # ---- scale in place if node_count changed ----
        desired_count = module.params["node_count"]
        # CLI JSON uses "nodes" (string), not "node_count" or "num_target_nodes"
        current_count = existing.get("nodes") or existing.get("node_count") or existing.get("num_target_nodes", 0)
        if int(desired_count) != int(current_count):
            if module.check_mode:
                module.exit_json(
                    changed=True,
                    msg=f"Would scale cluster '{name}' from {current_count} to {desired_count} nodes",
                )
            pool_id = _get_node_pool_id(module, name, api_key, region, binary)
            run_civo_command(
                module,
                ["kubernetes", "node-pool", "scale", name, pool_id, "--nodes", str(desired_count)],
                api_key,
                region,
                binary,
            )
            if do_wait:
                # The cluster stays ACTIVE during scaling, so we can't use
                # wait_for_active (it returns immediately).  Instead poll until
                # the "nodes" field reflects the desired count.
                import time as _time

                deadline = _time.time() + timeout
                while _time.time() < deadline:
                    existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary) or existing
                    cur = existing.get("nodes") or existing.get("node_count") or existing.get("num_target_nodes", 0)
                    if int(cur) == int(desired_count):
                        break
                    _time.sleep(15)
                else:
                    module.fail_json(
                        msg=f"Timed out after {timeout}s waiting for cluster '{name}' to scale to {desired_count} nodes"
                    )
            else:
                existing = find_resource_by_name(module, "kubernetes", name, api_key, region, binary) or existing
            existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
            module.exit_json(changed=True, cluster=existing)

        existing["kubeconfig"] = _get_kubeconfig(module, name, api_key, region, binary)
        module.exit_json(changed=False, cluster=existing)

    if module.check_mode:
        module.exit_json(changed=True, msg=f"Would create cluster '{name}'")

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
    module.exit_json(changed=True, cluster=cluster)


if __name__ == "__main__":
    main()
