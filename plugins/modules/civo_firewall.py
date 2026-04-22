#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_firewall
short_description: Manage Civo firewalls and firewall rules
description:
  - Create or delete Civo firewalls.
  - Declaratively manage firewall rules — missing rules are created, and
    with I(purge_rules=true) extra rules are removed.
  - Rule matching uses the I(label) field. Rules are compared on all
    attributes (direction, action, protocol, port, cidr); a rule whose label
    exists but whose attributes have changed is deleted and re-created.
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: Name of the firewall.
    required: true
    type: str
  network:
    description: Name or ID of the network this firewall belongs to.
    type: str
    default: default
  rules:
    description:
      - List of firewall rule dicts to enforce.
      - Rules are matched by I(label); omitting I(label) on a rule means it
        cannot be deduped and will be re-created on every run.
    type: list
    elements: dict
    default: []
    suboptions:
      label:
        description: Human-readable label (used as the idempotency key).
        type: str
      direction:
        description: Traffic direction.
        type: str
        choices: [ingress, egress]
        default: ingress
      action:
        description: Allow or deny the matched traffic.
        type: str
        choices: [allow, deny]
        default: allow
      protocol:
        description: IP protocol.
        type: str
        choices: [tcp, udp, icmp]
        default: tcp
      port:
        description: Port or port range (e.g. C("22") or C("8000-9000")).
        type: str
      cidr:
        description: Source/destination CIDR.
        type: str
        default: "0.0.0.0/0"
  purge_rules:
    description:
      - When C(true), rules present on the firewall but absent from I(rules)
        are deleted.
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
  state:
    description: Whether the firewall should exist.
    type: str
    choices: [present, absent]
    default: present
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_network
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: Create a firewall with SSH, HTTP, and HTTPS rules
  civo.cloud.civo_firewall:
    region: LON1
    name: web-fw
    network: my-network
    rules:
      - label: allow-ssh
        direction: ingress
        protocol: tcp
        port: "22"
        cidr: "0.0.0.0/0"
      - label: allow-http
        direction: ingress
        protocol: tcp
        port: "80"
        cidr: "0.0.0.0/0"
      - label: allow-https
        direction: ingress
        protocol: tcp
        port: "443"
        cidr: "0.0.0.0/0"
    purge_rules: true

- name: Delete a firewall
  civo.cloud.civo_firewall:
    region: LON1
    name: web-fw
    state: absent
"""

RETURN = r"""
firewall:
  description: Details of the managed firewall.
  returned: when state is C(present)
  type: dict
  sample:
    id: "a1b2c3d4-0000-0000-0000-000000000000"
    name: "web-fw"
    network: "my-network"
    rules_count: "8"
    clusters_count: "0"
    instances_count: "1"
    loadbalancer_count: "0"
  contains:
    id:
      description: Firewall UUID.
      type: str
      sample: "a1b2c3d4-0000-0000-0000-000000000000"
    name:
      description: Firewall name.
      type: str
      sample: "web-fw"
    network:
      description: Network name the firewall belongs to.
      type: str
      sample: "my-network"
    rules_count:
      description: Total number of rules on the firewall (including default rules).
      type: str
      sample: "8"
    clusters_count:
      description: Number of Kubernetes clusters using this firewall.
      type: str
      sample: "0"
    instances_count:
      description: Number of instances using this firewall.
      type: str
      sample: "1"
    loadbalancer_count:
      description: Number of load balancers using this firewall.
      type: str
      sample: "0"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    find_resource_by_name,
    run_civo_command,
)

RULE_SPEC = {
    "label": {"type": "str"},
    "direction": {"type": "str", "default": "ingress", "choices": ["ingress", "egress"]},
    "action": {"type": "str", "default": "allow", "choices": ["allow", "deny"]},
    "protocol": {"type": "str", "default": "tcp", "choices": ["tcp", "udp", "icmp"]},
    "port": {"type": "str"},
    "cidr": {"type": "str", "default": "0.0.0.0/0"},
}


def _rule_matches(desired, existing_rule):
    """Return True if all specified attributes of *desired* match *existing_rule*."""
    checks = [
        ("direction", desired.get("direction", "ingress")),
        ("action", desired.get("action", "allow")),
        ("protocol", desired.get("protocol", "tcp")),
        ("cidr", desired.get("cidr", "0.0.0.0/0")),
    ]
    for key, val in checks:
        if existing_rule.get(key, "").lower() != val.lower():
            return False
    # Port comparison — the CLI returns start_port/end_port fields.
    # A single-port rule like "22" maps to start_port="22", end_port="22".
    # A range rule like "8000-9000" maps to start_port="8000", end_port="9000".
    # A portless rule (e.g. ICMP) has no port field and must only match
    # existing rules that also have no ports — otherwise an ICMP rule would
    # incorrectly match any TCP rule with the same direction/action/cidr.
    desired_port = str(desired.get("port", "")) if desired.get("port") else ""
    if desired_port:
        if "-" in desired_port:
            desired_start, desired_end = desired_port.split("-", 1)
        else:
            desired_start = desired_end = desired_port
        if (
            str(existing_rule.get("start_port", "")) != desired_start
            or str(existing_rule.get("end_port", "")) != desired_end
        ):
            return False
    else:
        # Desired rule has no port — existing rule must also be portless.
        if existing_rule.get("start_port") or existing_rule.get("end_port"):
            return False
    return True


def _ensure_rules(module, firewall_id, desired_rules, purge, api_key, region, binary, check_mode):
    """Reconcile firewall rules. Returns True if any change was made (or would be)."""
    rc, existing_data, _ = run_civo_command(
        module,
        ["firewall", "rule", "ls", firewall_id],
        api_key,
        region,
        binary,
        check_rc=False,
    )
    existing_rules = existing_data if isinstance(existing_data, list) else []
    existing_by_label = {r.get("label", ""): r for r in existing_rules if r.get("label")}

    changed = False

    for rule in desired_rules:
        label = rule.get("label", "")
        existing_rule = existing_by_label.get(label) if label else None

        if existing_rule is not None and _rule_matches(rule, existing_rule):
            # Rule exists and attributes match — nothing to do
            continue

        if existing_rule is not None:
            # Rule exists but attributes differ — delete then re-create
            if not check_mode:
                run_civo_command(
                    module,
                    ["firewall", "rule", "remove", firewall_id, existing_rule["id"]],
                    api_key,
                    region,
                    binary,
                )
            changed = True

        # Create the rule
        if not check_mode:
            rule_args = ["firewall", "rule", "create", firewall_id]
            if label:
                rule_args += ["--label", label]
            rule_args += [
                "--direction",
                rule.get("direction", "ingress"),
                "--action",
                rule.get("action", "allow"),
                "--protocol",
                rule.get("protocol", "tcp"),
                "--cidr",
                rule.get("cidr", "0.0.0.0/0"),
            ]
            if rule.get("port"):
                # The Civo CLI uses --startport / --endport for single ports and ranges.
                # A range like "8000-9000" splits into start and end; a single
                # port like "22" uses the same value for both.
                port_str = str(rule["port"])
                if "-" in port_str:
                    start, end = port_str.split("-", 1)
                else:
                    start = end = port_str
                rule_args += ["--startport", start, "--endport", end]
            run_civo_command(module, rule_args, api_key, region, binary)
        changed = True

    if purge:
        desired_labels = {r.get("label", "") for r in desired_rules if r.get("label")}
        for existing_rule in existing_rules:
            rl = existing_rule.get("label", "")
            if rl and rl not in desired_labels:
                if not check_mode:
                    run_civo_command(
                        module,
                        [
                            "firewall",
                            "rule",
                            "remove",
                            firewall_id,
                            existing_rule["id"],
                        ],
                        api_key,
                        region,
                        binary,
                    )
                changed = True

    return changed


def main():
    argument_spec = common_argument_spec()
    argument_spec.update(
        name={"type": "str", "required": True},
        network={"type": "str", "default": "default"},
        rules={"type": "list", "elements": "dict", "default": [], "options": RULE_SPEC},
        purge_rules={"type": "bool", "default": False},
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    network = module.params["network"]
    rules = module.params["rules"]
    purge_rules = module.params["purge_rules"]
    state = module.params["state"]
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    existing = find_resource_by_name(module, "firewall", name, api_key, region, binary)
    before = existing or {}

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False, msg=f"Firewall '{name}' not found", diff={"before": {}, "after": {}})
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would delete firewall '{name}'", diff={"before": before, "after": {}})
        run_civo_command(module, ["firewall", "remove", existing["id"]], api_key, region, binary)
        module.exit_json(changed=True, msg=f"Firewall '{name}' deleted", diff={"before": before, "after": {}})

    changed = False
    if existing is None:
        if module.check_mode:
            after_preview = {"name": name, "network": network, "rules_count": str(len(rules))}
            module.exit_json(
                changed=True,
                msg=f"Would create firewall '{name}' with {len(rules)} rules",
                diff={"before": {}, "after": after_preview},
            )
        create_args = ["firewall", "create", name, "--network", network]
        run_civo_command(module, create_args, api_key, region, binary)
        existing = find_resource_by_name(module, "firewall", name, api_key, region, binary)
        changed = True

    # Reconcile rules (works in both live and check_mode)
    if existing and rules is not None:
        rules_changed = _ensure_rules(
            module,
            existing["id"],
            rules,
            purge_rules,
            api_key,
            region,
            binary,
            module.check_mode,
        )
        changed = changed or rules_changed

    firewall = find_resource_by_name(module, "firewall", name, api_key, region, binary) or {}
    module.exit_json(changed=changed, firewall=firewall, diff={"before": before, "after": firewall})


if __name__ == "__main__":
    main()
