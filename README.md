# civo.cloud — Ansible Collection

> **Experimental** — This collection is under active development. APIs, module
> parameters, and return values may change without notice between releases.
> Use at your own risk and please report issues.
> **Unofficial** - This collection is not affiliated with Civo.

An unofficial Ansible collection for managing resources on
[Civo cloud](https://www.civo.com),
developed by [The Rosalind Franklin Institute](https://www.rfi.ac.uk).

It wraps the [Civo CLI](https://github.com/civo/cli) binary and follows the
same conventions as `community.hetznercloud` and `amazon.aws`.

## Supported modules

### CRUD modules

| Module | Resource |
|---|---|
| `civo.cloud.civo_network` | Private networks |
| `civo.cloud.civo_firewall` | Firewalls + ingress/egress rules |
| `civo.cloud.civo_instance` | Compute instances (VMs) |
| `civo.cloud.civo_kubernetes` | Kubernetes clusters (k3s) |
| `civo.cloud.civo_kubernetes_node` | Individual nodes within a cluster pool |
| `civo.cloud.civo_kubernetes_pool` | Node pools within a cluster |
| `civo.cloud.civo_volume` | Block storage volumes |
| `civo.cloud.civo_loadbalancer` | Load balancers (read/delete only — see note below) |
| `civo.cloud.civo_reserved_ip` | Reserved (static) public IPs |
| `civo.cloud.civo_database` | Managed databases (PostgreSQL / MySQL) |
| `civo.cloud.civo_objectstore` | S3-compatible object stores |
| `civo.cloud.civo_sshkey` | SSH public keys |

### Info (read-only) modules

| Module | Resource |
|---|---|
| `civo.cloud.civo_network_info` | Private networks |
| `civo.cloud.civo_firewall_info` | Firewalls (optionally includes rules) |
| `civo.cloud.civo_instance_info` | Compute instances |
| `civo.cloud.civo_kubernetes_info` | Kubernetes clusters (optionally includes kubeconfig) |
| `civo.cloud.civo_kubernetes_pool_info` | Node pools within a cluster |
| `civo.cloud.civo_kubernetes_version_info` | Available Kubernetes versions |
| `civo.cloud.civo_volume_info` | Block storage volumes |
| `civo.cloud.civo_loadbalancer_info` | Load balancers |
| `civo.cloud.civo_reserved_ip_info` | Reserved IPs |
| `civo.cloud.civo_database_info` | Managed databases |
| `civo.cloud.civo_objectstore_info` | Object stores |
| `civo.cloud.civo_sshkey_info` | SSH public keys |
| `civo.cloud.civo_diskimage_info` | Available disk images |
| `civo.cloud.civo_size_info` | Available instance/node sizes |
| `civo.cloud.civo_region_info` | Available regions |
| `civo.cloud.civo_quota_info` | Account quota and usage |
| `civo.cloud.civo_volumetype_info` | Available volume types |

All modules support **check mode** and **multi-region** deployments.

### Load balancer note

The Civo CLI does not provide `create` or `update` commands for load balancers.
Load balancers are provisioned automatically by the Kubernetes
cloud-controller-manager when a `Service` of type `LoadBalancer` is deployed.
The `civo_loadbalancer` module can only **query** (`state=present`) or
**delete** (`state=absent`) existing load balancers.

## Requirements

- Ansible >= 2.15
- The `civo` CLI binary installed and in `$PATH` on the control node.
  Install via `brew install civo` or download from
  https://github.com/civo/cli/releases.
- A Civo API token (obtain at https://dashboard.civo.com/security).

## Installation

### From GitHub (direct)

```bash
ansible-galaxy collection install \
  git+https://github.com/rosalindfranklininstitute/ansible-civo.git
```

Pin to a specific tag:

```bash
ansible-galaxy collection install \
  git+https://github.com/rosalindfranklininstitute/ansible-civo.git,v0.0.1
```

### Via `requirements.yml`

```yaml
---
collections:
  - name: https://github.com/rosalindfranklininstitute/ansible-civo.git
    type: git
    version: main
```

```bash
ansible-galaxy collection install -r requirements.yml
```

## Authentication

Authentication is resolved in priority order:

1. **`api_key` module parameter** — pass the token directly (vault-encrypt it):
   ```yaml
   civo.cloud.civo_network:
     api_key: "{{ vault_civo_token }}"
     ...
   ```
2. **`CIVO_TOKEN` environment variable** — recommended for CI and local use:
   ```bash
   export CIVO_TOKEN="your-api-token"
   ```
3. **`~/.civo.json`** — the active key from the Civo CLI config file
   (populated by `civo apikey add` / `civo apikey current`).

## Quick start

```yaml
---
- name: Provision Civo infrastructure
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create a private network
      civo.cloud.civo_network:
        name: prod-network
        region: LON1
        state: present

    - name: Create a firewall
      civo.cloud.civo_firewall:
        name: prod-fw
        region: LON1
        network: prod-network
        rules:
          - label: allow-ssh
            direction: ingress
            action: allow
            protocol: tcp
            port: "22"
            cidr: "0.0.0.0/0"
          - label: allow-https
            direction: ingress
            action: allow
            protocol: tcp
            port: "443"
            cidr: "0.0.0.0/0"
        state: present

    - name: Launch an instance
      civo.cloud.civo_instance:
        hostname: web-01
        region: LON1
        size: g3.xsmall
        diskimage: ubuntu-noble
        network: prod-network
        firewall: prod-fw
        public_ip: create
        wait: true
        state: present
      register: inst

    - name: Show public IP
      ansible.builtin.debug:
        msg: "Instance public IP: {{ inst.instance.public_ip }}"
```

## Module examples

### Read resource info

```yaml
- name: List all networks
  civo.cloud.civo_network_info:
    region: LON1
  register: nets

- name: Get a specific firewall with its rules
  civo.cloud.civo_firewall_info:
    region: LON1
    name: prod-fw
    rules: true
  register: fw

- name: Get K8s cluster with kubeconfig
  civo.cloud.civo_kubernetes_info:
    region: LON1
    name: my-cluster
    kubeconfig: true
  register: k8s
```

### Kubernetes cluster

```yaml
- name: Create a Kubernetes cluster
  civo.cloud.civo_kubernetes:
    name: my-cluster
    region: LON1
    node_size: g4s.kube.medium
    node_count: 3
    network: prod-network
    cni: flannel
    wait: true
    state: present
  register: k8s

- name: Save kubeconfig
  ansible.builtin.copy:
    content: "{{ k8s.cluster.kubeconfig }}"
    dest: "~/.kube/civo-prod.yaml"
    mode: "0600"

- name: Scale a node pool
  civo.cloud.civo_kubernetes_pool:
    cluster: my-cluster
    region: LON1
    pool_id: "{{ pool_id }}"
    count: 5
    state: present

- name: Recycle a node
  civo.cloud.civo_kubernetes_node:
    cluster: my-cluster
    region: LON1
    node_id: "{{ node_id }}"
    state: recycled
```

### Volume — create, resize and attach

```yaml
- name: Create a data volume
  civo.cloud.civo_volume:
    name: data-vol
    region: LON1
    size_gb: 50
    network: default
    state: present

- name: Resize the volume
  civo.cloud.civo_volume:
    name: data-vol
    region: LON1
    size_gb: 100       # triggers in-place resize
    state: present

- name: Attach volume to instance
  civo.cloud.civo_volume:
    name: data-vol
    region: LON1
    instance: web-01
    state: attached
```

### Reserved IP

```yaml
- name: Reserve a public IP
  civo.cloud.civo_reserved_ip:
    name: web-ip
    region: LON1
    state: present
  register: rip

- name: Assign it to an instance
  civo.cloud.civo_reserved_ip:
    name: web-ip
    region: LON1
    instance: web-01
    state: assigned
```

### Managed database

```yaml
- name: Create a PostgreSQL database
  civo.cloud.civo_database:
    name: myapp-db
    region: LON1
    engine: postgresql
    version: "17"
    size: g3.db.small
    nodes: 1
    network: prod-network
    wait: true
    state: present
  register: db
```

### Object store

```yaml
- name: Create an S3-compatible object store
  civo.cloud.civo_objectstore:
    name: my-bucket
    region: LON1
    max_size_gb: 500
    wait: true
    state: present
  register: bucket
```

### Load balancer (read-only)

```yaml
- name: List all load balancers
  civo.cloud.civo_loadbalancer_info:
    region: LON1
  register: lbs

- name: Look up a specific load balancer
  civo.cloud.civo_loadbalancer:
    region: LON1
    name: my-lb
    state: present
  register: lb
```

## Dispatcher role

The `roles/civo` role shipped with this collection acts as a dispatcher —
it lets you drive any resource through a single `include_role` call:

```yaml
- name: Ensure network exists
  ansible.builtin.include_role:
    name: civo.cloud.civo
  vars:
    civo_resource: network
    civo_name: prod-network
    civo_region: LON1
    civo_state: present
```

See [`roles/civo/defaults/main.yml`](roles/civo/defaults/main.yml) for the
full list of configurable variables.

## Multi-region support

Pass `region` to any module to target a supported Civo region:

| Region | Location |
|---|---|
| `LON1` | London, UK (default) |
| `NYC1` | New York, USA |
| `FRA1` | Frankfurt, Germany |
| `PHX1` | Phoenix, USA |

## Check mode

All modules support Ansible check mode — no real API calls are made:

```bash
ansible-playbook site.yml --check
```

## Collection structure

```
ansible-civo/
├── galaxy.yml                         # Collection metadata (namespace: civo.cloud)
├── plugins/
│   ├── module_utils/
│   │   └── civo_utils.py              # Shared helpers: auth, CLI exec, JSON parsing, wait loops
│   └── modules/
│       ├── civo_network.py            # CRUD modules (one per resource type)
│       ├── civo_network_info.py       # Info (read-only) modules
│       └── ...
├── roles/
│   └── civo/                          # Dispatcher role
│       ├── defaults/main.yml          # All tuneable defaults
│       └── tasks/                     # Per-resource task files
├── tests/
│   └── integration/
│       ├── test_all.yml               # Master integration test playbook
│       └── tasks/                     # Per-resource test task files
├── docs/
│   ├── conf.py                        # Sphinx configuration
│   ├── antsibull-docs.cfg             # antsibull-docs configuration
│   └── _build/html/                   # Generated HTML (gitignored)
├── Makefile                           # Developer convenience targets
├── dev-requirements.txt               # Python deps for docs + lint
└── pyproject.toml                     # ruff configuration
```

All modules follow the same pattern: resolve auth → find or create/delete
resource via `civo` CLI with `-o json` → parse JSON → optionally poll for
`ACTIVE` status → return structured result. Shared logic lives in
`plugins/module_utils/civo_utils.py`.

## Development

### Setup

```bash
pip install -r dev-requirements.txt
pre-commit install
```

### Make targets

| Target | What it does |
|---|---|
| `make lint` | Run `ruff check` on `plugins/` |
| `make format` | Run `ruff format` on `plugins/` |
| `make ansible-lint` | Run `ansible-lint` across the whole project |
| `make docs` | Generate per-module RST with antsibull-docs, then build Sphinx HTML |
| `make sanity` | Run `ansible-test sanity --docker` (requires Docker) |
| `make clean` | Remove `docs/_build/` and `docs/collections/` |

### Building docs locally

The docs pipeline requires the collection to be importable by antsibull-docs.
Symlink it into the Ansible collections path first:

```bash
mkdir -p ~/.ansible/collections/ansible_collections/civo
ln -s "$(pwd)" ~/.ansible/collections/ansible_collections/civo/cloud
```

Then build:

```bash
make docs
# open docs/_build/html/index.html
```

Docs are published automatically to GitHub Pages on every push to `main` via
`.github/workflows/docs.yml`.

### Running integration tests

Integration tests make **real API calls** and provision actual Civo resources.
They are tagged by resource type for selective execution.

**Prerequisites:**
- `CIVO_TOKEN` set in your environment
- `civo` CLI installed and in `$PATH`
- Collection installed at `~/.ansible/collections/ansible_collections/civo/cloud`
  (or symlinked as above)

**Run the full suite:**

```bash
ansible-playbook tests/integration/test_all.yml -v
```

**Run a single resource type:**

```bash
ansible-playbook tests/integration/test_all.yml -v --tags network
ansible-playbook tests/integration/test_all.yml -v --tags kubernetes
ansible-playbook tests/integration/test_all.yml -v --tags kubernetes_upgrade
ansible-playbook tests/integration/test_all.yml -v --tags kubernetes_node
ansible-playbook tests/integration/test_all.yml -v --tags kubernetes_pool
```

Available tags: `network`, `firewall`, `instance`, `volume`, `reserved_ip`,
`objectstore`, `database`, `kubernetes`, `kubernetes_upgrade`, `kubernetes_node`,
`kubernetes_pool`, `sshkey`, `catalog`, `loadbalancer`, `info`.

All test resources are prefixed with `ansible-test-` for easy identification.
The `always:` cleanup block in `test_all.yml` deletes all created resources
even if the tests fail mid-run.

### CI

GitHub Actions runs on every push and pull request (`.github/workflows/ci.yml`):

- `ruff` — Python linting and formatting checks
- `ansible-lint` — Ansible best-practice checks
- `ansible-test sanity` — collection sanity checks against Ansible stable-2.14,
  stable-2.15, stable-2.16, and devel

## License

[GPL-3.0-or-later](LICENSE)

Copyright 2026, The Rosalind Franklin Institute.
