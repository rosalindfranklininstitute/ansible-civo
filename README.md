# civo.cloud — Ansible Collection

> **Experimental** — APIs, module parameters, and return values may change
> between releases. Not affiliated with Civo.

An unofficial Ansible collection for managing [Civo cloud](https://www.civo.com)
resources, developed by [The Rosalind Franklin Institute](https://www.rfi.ac.uk).
It wraps the [Civo CLI](https://github.com/civo/cli) binary.

## Documentation

**Full docs, module reference, and examples:**
**<https://rosalindfranklininstitute.github.io/ansible-civo/>**

## Quick install

```bash
ansible-galaxy collection install \
  git+https://github.com/rosalindfranklininstitute/ansible-civo.git
```

Set your API token, then use any module:

```bash
export CIVO_TOKEN="your-api-token"
```

```yaml
- name: Create a network
  civo.cloud.network:
    name: prod-network
    region: LON1
    state: present
```

## Modules

29 modules covering: networks, firewalls, instances, Kubernetes clusters/pools/nodes,
volumes, load balancers, reserved IPs, managed databases, object stores, SSH keys,
and read-only catalog modules (regions, sizes, disk images, quotas).

All modules support **check mode** and **multi-region** deployments.

See the [module reference](https://rosalindfranklininstitute.github.io/ansible-civo/collections/civo/cloud/index.html)
for full parameter and return-value documentation.

## License

[GPL-3.0-or-later](LICENSE) — Copyright 2026, The Rosalind Franklin Institute.
