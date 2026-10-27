# Changelog

## 0.0.5

### Fixes

- `reserved_ip` and `reserved_ip_info` now use the `civo vpc ip` CLI
  subcommands.
- `reserved_ip` with `state: assigned` accepts an instance name or ID.
- The `civo` role reads the reserved IP address from the `address` field.

### Changes

- The `civo` role dispatcher uses a lookup map and fails early on an
  unknown `civo_resource`.
