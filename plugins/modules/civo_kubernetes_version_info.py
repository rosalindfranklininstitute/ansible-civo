#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: civo_kubernetes_version_info
short_description: List available Civo Kubernetes versions
description:
  - Returns all Kubernetes versions available for new clusters in a Civo
    region, including maturity level and whether each is the default.
  - Version strings returned by this module are the values accepted by the
    C(version) and C(upgrade_version) parameters of
    M(civo.cloud.civo_kubernetes).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute (@rosalindfranklininstitute)
options:
  maturity:
    description: >-
      Filter versions by maturity level: C(stable), C(development), or
      C(deprecated).  When omitted, all versions are returned.
    type: str
    choices: [stable, development, deprecated]
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
- name: List all available Kubernetes versions
  civo.cloud.civo_kubernetes_version_info:
    region: LON1
  register: k8s_versions

- name: Show all version strings
  ansible.builtin.debug:
    msg: "{{ k8s_versions.kubernetes_versions | map(attribute='version') | list }}"

- name: Get only stable versions
  civo.cloud.civo_kubernetes_version_info:
    region: LON1
    maturity: stable
  register: stable_versions

- name: Find the default version
  ansible.builtin.set_fact:
    default_k8s_version: >-
      {{ k8s_versions.kubernetes_versions
         | selectattr('default', 'equalto', 'true')
         | map(attribute='version') | first }}

- name: Create cluster on latest stable version
  civo.cloud.civo_kubernetes:
    region: LON1
    name: my-cluster
    version: "{{ stable_versions.kubernetes_versions[0].version }}"
    node_count: 1
    state: present
"""

RETURN = r"""
kubernetes_versions:
  description: List of Kubernetes version dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    version:
      description: >-
        Full version string.  Use this value for the C(version) or
        C(upgrade_version) parameters of M(civo.cloud.civo_kubernetes).
      type: str
      sample: "1.32.5-k3s1"
    label:
      description: Human-readable label (identical to C(version) for k3s).
      type: str
      sample: "1.32.5-k3s1"
    cluster_type:
      description: Cluster runtime type (currently always C(k3s)).
      type: str
      sample: "k3s"
    type:
      description: >-
        Maturity level: C(stable), C(development), or C(deprecated).
      type: str
      sample: "stable"
    default:
      description: >-
        Whether this is the default version for new clusters
        (returned as the string C("true") or C("false") by the CLI).
      type: str
      sample: "true"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]
    spec.update(
        maturity={"type": "str", "choices": ["stable", "development", "deprecated"]},
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    maturity = module.params.get("maturity") or ""
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    _rc, data, _stderr = run_civo_command(module, ["kubernetes", "versions"], api_key, region, binary, check_rc=False)
    versions = data if isinstance(data, list) else []

    if maturity:
        versions = [v for v in versions if (v.get("type") or "").lower() == maturity.lower()]

    module.exit_json(changed=False, kubernetes_versions=versions)


if __name__ == "__main__":
    main()
