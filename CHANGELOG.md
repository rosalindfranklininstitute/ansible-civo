# Changelog

## Unreleased

### Added

- `civo_kubernetes`: new `upgrade_version` parameter — calls `civo kubernetes upgrade`
  and waits for the cluster to return to `ACTIVE` status.
- `civo_kubernetes`: new `pool_id` parameter — when a cluster has multiple pools,
  `pool_id` must be supplied to identify the target pool for `node_count` scaling.
  The module now fails with a clear error rather than silently operating on the
  wrong pool.  Scaling wait now polls the specific pool's node count instead of
  the cluster-level total.
- New module `civo_kubernetes_node` — recycle (`state: recycle`) or permanently
  delete (`state: absent`) an individual node from a Kubernetes cluster.
- New module `civo_kubernetes_pool` — create, scale, or delete additional node
  pools in an existing Kubernetes cluster.
- New module `civo_kubernetes_pool_info` — query node pools and their member
  instances in a Kubernetes cluster.
- Integration tests for Kubernetes version upgrade
  (`tests/integration/tasks/kubernetes_upgrade.yml`, tag `kubernetes_upgrade`).
- Integration tests for Kubernetes node recycle/delete
  (`tests/integration/tasks/kubernetes_node.yml`, tag `kubernetes_node`).
- Integration tests for Kubernetes node pool management
  (`tests/integration/tasks/kubernetes_pool.yml`, tag `kubernetes_pool`).
- Modularised integration test suite: `test_all.yml` now orchestrates per-resource
  task files under `tests/integration/tasks/` with per-resource tags.

## v0.0.1 — 2026-03-24

### Added

- Initial release of the `civo.cloud` Ansible collection.
- Modules: `civo_network`, `civo_firewall`, `civo_instance`, `civo_kubernetes`,
  `civo_volume`, `civo_loadbalancer`, `civo_reserved_ip`, `civo_database`,
  `civo_objectstore`.
- Full check-mode support across all modules.
- Multi-region support (`LON1`, `NYC1`, `FRA1`, `PHX1`).
- Dispatcher role `roles/civo` for simplified playbook usage.

### Fixed

- `api_key` fallback from `CIVO_TOKEN` environment variable now works correctly.
- `--public-ip` flag corrected for `civo instance create`.
- `--region` flag added to `civo kubernetes config`.
- `changed` sentinel logic fixed in `civo_volume` and `civo_reserved_ip`.
- Firewall rule reconciliation now runs in check mode.
- Firewall rules diffed by all attributes (direction, action, protocol, CIDR, port).
- Volume attach/detach made idempotent.
- Reserved IP assign/unassign made idempotent.
- `civo_database` CLI flags corrected to `--software` / `--software-version`.
- `wait_for_active` boolean handling fixed.
- `find_resource_by_name` now distinguishes real CLI errors from "not found".
- `session_affinity_config_timeout: 0` no longer silently dropped.
