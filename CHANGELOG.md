# Changelog

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
