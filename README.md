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
| `civo.cloud.civo_volume` | Block storage volumes |
| `civo.cloud.civo_loadbalancer` | Load balancers (read/delete only — see note below) |
| `civo.cloud.civo_reserved_ip` | Reserved (static) public IPs |
| `civo.cloud.civo_database` | Managed databases (PostgreSQL / MySQL) |
| `civo.cloud.civo_objectstore` | S3-compatible object stores |

### Info (read-only) modules

| Module | Resource |
|---|---|
| `civo.cloud.civo_network_info` | Private networks |
| `civo.cloud.civo_firewall_info` | Firewalls (optionally includes rules) |
| `civo.cloud.civo_instance_info` | Compute instances |
| `civo.cloud.civo_kubernetes_info` | Kubernetes clusters (optionally includes kubeconfig) |
| `civo.cloud.civo_volume_info` | Block storage volumes |
| `civo.cloud.civo_loadbalancer_info` | Load balancers |
| `civo.cloud.civo_reserved_ip_info` | Reserved IPs |
| `civo.cloud.civo_database_info` | Managed databases |
| `civo.cloud.civo_objectstore_info` | Object stores |

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

Export your Civo API token before running any playbook:

```bash
export CIVO_TOKEN="your-api-token"
```

The `CIVO_TOKEN` environment variable is the recommended approach.
Alternatively, pass `api_key` directly to each module task
(vault-encrypt it if you do).

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

## Development

### Pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

### CI

GitHub Actions runs on every pull request:

- `ruff` — Python linting and formatting
- `ansible-lint` — Ansible best-practice checks
- `ansible-test sanity` — collection sanity checks

### Docs

```bash
pip install -r dev-requirements.txt
cd docs && make html
```

Open `docs/_build/html/index.html` in your browser.

## License

[Apache 2.0](LICENSE)

Copyright 2026, The Rosalind Franklin Institute.
