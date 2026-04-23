#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_kubernetes_node
short_description: Recycle or delete a node in a Civo Kubernetes cluster
description:
  - Manages individual nodes (instances) within a Civo Kubernetes cluster.
  - C(state=recycle) replaces the node with a fresh instance while keeping the
    pool size the same.  Calls C(civo kubernetes recycle CLUSTER --node NODE).
  - C(state=absent) permanently removes the node from its pool, reducing the
    pool size by one.  Calls
    C(civo kubernetes node-pool instance-delete CLUSTER --instance-id ID
    --node-pool-id POOL_ID).
  - The node is identified by its hostname (e.g. C(k3s-my-cluster-abc12-1)).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  cluster:
    description: Name of the Kubernetes cluster that owns the node.
    required: true
    type: str
  node:
    description: >-
      Hostname of the node to act on
      (e.g. C(k3s-my-cluster-abc12-1)).
      Obtain available node names from M(civo.cloud.civo_kubernetes_pool_info)
      or C(civo kubernetes node-pool instance-ls CLUSTER).
    required: true
    type: str
  pool_id:
    description: >-
      ID of the node pool that contains the node.
      Required for C(state=absent).  Optional for C(state=recycle) (the module
      will search all pools when omitted, which adds extra API calls).
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
      - C(recycle) — replace the node with a new instance (same pool size).
      - C(absent) — permanently delete the node instance from its pool.
    type: str
    choices: [recycle, absent]
    required: true
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_kubernetes
  - module: civo.cloud.civo_kubernetes_pool
  - module: civo.cloud.civo_kubernetes_pool_info
"""

EXAMPLES = r"""
- name: Recycle a node (replace with a fresh instance)
  civo.cloud.civo_kubernetes_node:
    region: LON1
    cluster: my-cluster
    node: k3s-my-cluster-abc12-1
    state: recycle

- name: Delete a node from its pool (reduces pool size by 1)
  civo.cloud.civo_kubernetes_node:
    region: LON1
    cluster: my-cluster
    node: k3s-my-cluster-abc12-1
    pool_id: "aaaa-bbbb-cccc"
    state: absent
"""

RETURN = r"""
msg:
  description: Human-readable status message.
  returned: always
  type: str
  sample: "Node 'k3s-my-cluster-abc12-1' recycled successfully"
node:
  description: The hostname of the node that was acted on.
  returned: always
  type: str
  sample: "k3s-my-cluster-abc12-1"
"""

import json as _json

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    list_node_pools,
    run_civo_command,
)


def _list_instances_in_pool(module, cluster, pool_id, api_key, region, binary):
    """Return a list of instance dicts for a given pool.

    The CLI mixes human-readable text and a JSON array in stdout;
    we extract the line that starts with '['.
    """
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
        module.fail_json(msg=f"Failed to list instances in pool '{pool_id}' of cluster '{cluster}': {stderr}")
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


def _find_node(module, cluster, node_hostname, pool_id, api_key, region, binary):
    """Locate a node by hostname across pools.

    Returns (pool_id, instance_id) or fails the module if not found.
    If *pool_id* is given only that pool is searched.
    """
    if pool_id:
        pools_to_search = [{"ID": pool_id, "id": pool_id}]
    else:
        pools_to_search = list_node_pools(module, cluster, api_key, region, binary)

    for pool in pools_to_search:
        pid = pool.get("ID") or pool.get("id") or ""
        if not pid:
            continue
        instances = _list_instances_in_pool(module, cluster, pid, api_key, region, binary)
        for inst in instances:
            hostname = inst.get("Hostname") or inst.get("hostname") or inst.get("name") or ""
            iid = inst.get("ID") or inst.get("id") or ""
            if hostname == node_hostname:
                return pid, iid

    module.fail_json(
        msg=f"Node '{node_hostname}' not found in cluster '{cluster}'"
        + (f" pool '{pool_id}'" if pool_id else " (searched all pools)")
    )


def main():
    spec = common_argument_spec()
    # Override state choices — this module uses different states
    spec["state"] = {"type": "str", "choices": ["recycle", "absent"], "required": True}
    spec.update(
        cluster={"type": "str", "required": True},
        node={"type": "str", "required": True},
        pool_id={"type": "str"},
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    cluster = module.params["cluster"]
    node = module.params["node"]
    pool_id = module.params.get("pool_id") or ""
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if state == "recycle":
        node_state = {"cluster": cluster, "node": node}
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg=f"Would recycle node '{node}' in cluster '{cluster}'",
                node=node,
                diff={"before": node_state, "after": node_state},
            )
        run_civo_command(
            module,
            ["kubernetes", "recycle", cluster, "--node", node],
            api_key,
            region,
            binary,
        )
        module.exit_json(
            changed=True,
            msg=f"Node '{node}' recycled successfully",
            node=node,
            diff={"before": node_state, "after": node_state},
        )

    # state == "absent"
    resolved_pool_id, instance_id = _find_node(module, cluster, node, pool_id, api_key, region, binary)
    if not instance_id:
        module.fail_json(msg=f"Could not determine instance ID for node '{node}' in cluster '{cluster}'")

    node_state = {"cluster": cluster, "node": node, "pool_id": resolved_pool_id, "instance_id": instance_id}
    if module.check_mode:
        module.exit_json(
            changed=True,
            msg=f"Would delete node '{node}' (instance {instance_id}) from pool '{resolved_pool_id}'",
            node=node,
            diff={"before": node_state, "after": {}},
        )

    # The `civo kubernetes node-pool instance-delete` subcommand returns a
    # plain-text confirmation message and ignores `-o json`, so we bypass
    # run_civo_command (which always appends -o json) and call the CLI directly.
    env = {"CIVO_TOKEN": api_key}
    delete_cmd = [
        binary,
        "kubernetes",
        "node-pool",
        "instance-delete",
        cluster,
        "--instance-id",
        instance_id,
        "--node-pool-id",
        resolved_pool_id,
        "--region",
        region,
        "-y",
    ]
    rc, stdout, stderr = module.run_command(delete_cmd, environ_update=env)
    if rc != 0:
        module.fail_json(
            msg=f"Failed to delete node '{node}' from pool '{resolved_pool_id}': {stderr or stdout}",
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )
    module.exit_json(
        changed=True,
        msg=f"Node '{node}' (instance {instance_id}) deleted from pool '{resolved_pool_id}'",
        node=node,
        diff={"before": node_state, "after": {}},
    )


if __name__ == "__main__":
    main()
