# Changelog

## Unreleased

### Added

- `civo_objectstore`: new `purge_credentials` parameter (default C(false)).
  When C(state=absent) and C(purge_credentials=true), the module looks up the
  store's owner credential via C(civo objectstore show) (C(accesskey) field),
  cross-references C(civo objectstore credential ls), and deletes the linked
  credential.  Safe by default — the credential is not touched unless the
  caller opts in.  The integration test cleanup path now sets
  C(purge_credentials=true) and a dedicated C(purge_credentials) test case
  was added to C(tests/integration/tasks/objectstore.yml).

- New module `civo_sshkey` — upload, rename, or remove SSH public keys stored
  in a Civo account; idempotent create and delete.
- New module `civo_sshkey_info` — list SSH keys in a Civo account, with
  optional C(name) filter.
- New module `civo_size_info` — list all available sizes (instance, Kubernetes,
  database) in a region, with optional C(filter) by type.
- New module `civo_region_info` — list all available Civo regions.
- New module `civo_quota_info` — return current quota limits and usage for a
  Civo account in a given region.
- New module `civo_volumetype_info` — list available volume types
  (e.g. C(standard), C(encrypted-standard)).
- Integration tests for C(civo_sshkey) / C(civo_sshkey_info)
  (C(tests/integration/tasks/sshkey.yml), tag C(sshkey)).
- Integration tests for C(civo_region_info), C(civo_size_info),
  C(civo_quota_info), and C(civo_volumetype_info) added to
  C(tests/integration/tasks/catalog.yml) under sub-tags C(region_info),
  C(size_info), C(quota_info), C(volumetype_info).
- New module `civo_diskimage_info` — list available VM disk images (templates)
  in a region, with optional filters for C(name) (exact) and C(distribution)
  (substring).
- New module `civo_kubernetes_version_info` — list available Kubernetes versions
  in a region, with optional C(maturity) filter (C(stable), C(development),
  C(deprecated)).  Version strings are directly usable in C(civo_kubernetes)
  C(version) and C(upgrade_version) parameters.
- Integration tests for both catalog info modules
  (C(tests/integration/tasks/catalog.yml), tag C(catalog),
  sub-tags C(diskimage_info) and C(kubernetes_version_info)).
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
