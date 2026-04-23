#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_kubernetes_info
short_description: Gather information about Civo Kubernetes clusters
description:
  - Returns details of one or all Civo Kubernetes clusters in a region.
  - When I(name) is given, returns a single-item list (or empty list if not found).
  - When I(kubeconfig) is C(true), the returned cluster dict includes the raw
    kubeconfig YAML.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  name:
    description:
      - Name of the cluster to look up.
      - When omitted, all clusters in the region are returned.
    type: str
  kubeconfig:
    description:
      - When C(true), fetch and attach the kubeconfig YAML for each cluster.
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
  - module: civo.cloud.civo_kubernetes
"""

EXAMPLES = r"""
- name: Get all Kubernetes clusters
  civo.cloud.civo_kubernetes_info:
    region: LON1
  register: clusters

- name: Get a specific cluster with kubeconfig
  civo.cloud.civo_kubernetes_info:
    region: LON1
    name: my-cluster
    kubeconfig: true
  register: k8s

- name: Save kubeconfig locally
  ansible.builtin.copy:
    content: "{{ k8s.clusters[0].kubeconfig }}"
    dest: ~/.kube/my-cluster.yaml
    mode: "0600"
"""

RETURN = r"""
clusters:
  description: List of cluster dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Cluster UUID.
      type: str
    name:
      description: Cluster name.
      type: str
    status:
      description: Cluster status.
      type: str
    kubeconfig:
      description: Raw kubeconfig YAML (only present when I(kubeconfig=true)).
      type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)


def _get_kubeconfig(module, cluster_name, api_key, region, binary):
    env_update = {"CIVO_TOKEN": api_key}
    cmd = [binary, "kubernetes", "config", cluster_name, "--region", region, "-y"]
    rc, stdout, _stderr = module.run_command(cmd, environ_update=env_update)
    return stdout.strip() if rc == 0 else ""


def main():
    argument_spec = common_argument_spec()
    argument_spec.pop("state", None)
    argument_spec.update(
        name={"type": "str"},
        kubeconfig={"type": "bool", "default": False},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    fetch_kubeconfig = module.params["kubeconfig"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    if name:
        result = find_resource_by_name(module, "kubernetes", name, api_key, region, binary)
        clusters = [result] if result else []
    else:
        _rc, data, _stderr = run_civo_command(module, ["kubernetes", "ls"], api_key, region, binary, check_rc=False)
        clusters = data if isinstance(data, list) else []

    if fetch_kubeconfig:
        for cluster in clusters:
            cluster["kubeconfig"] = _get_kubeconfig(module, cluster["name"], api_key, region, binary)

    module.exit_json(changed=False, clusters=clusters)


if __name__ == "__main__":
    main()
