Changelog
=========

All notable changes to this project are documented in this file.

The format follows `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

v0.0.2 — 2026-03-25
---------------------

Added
~~~~~

* ``civo_instance``: new ``state=rebooted`` (graceful ACPI reboot) and
  ``state=hard_rebooted`` (power-cycle reboot).  Both always report
  ``changed=True`` and respect the ``wait`` / ``timeout`` parameters.
* ``--diff`` mode support across all 12 management modules.  Every
  ``exit_json`` call now emits ``diff={"before": …, "after": …}`` so that
  ``ansible-playbook --diff`` shows the actual state change.  Check-mode
  create paths emit a params-based preview as the ``after`` state.
  ``civo_kubernetes`` strips ``kubeconfig`` from the diff to avoid large
  sensitive blobs in output.
* ``civo_objectstore``: safety check for ``purge_credentials=true``.  Before
  deleting a credential the module now lists all other object stores and
  refuses to proceed if any of them share the same access key, preventing
  accidental deletion of a credential that is still in use.
* ``civo_utils``: new ``is_uuid()`` helper (RFC 4122 regex) used to
  distinguish UUID arguments from name strings without a redundant API call.

Fixed
~~~~~

* Authentication now falls back to the active key in ``~/.civo.json`` (the
  civo CLI config file) when neither ``api_key`` nor ``CIVO_TOKEN`` is
  provided.  This means the collection works out of the box on machines where
  the civo CLI is already configured, without any extra environment setup.
* ``civo_instance``: firewall comparison now resolves names to IDs before
  comparing, preventing spurious firewall-update calls when the firewall is
  specified by name rather than UUID.
* ``find_resource_by_name``: now fails hard when more than one resource with
  the same name exists in a region, rather than silently operating on the
  first match.  This prevents accidental mutation or deletion of the wrong
  resource in accounts with name collisions.

Changed
~~~~~~~

* Docs: auto-generated RST module reference pages are no longer committed to
  git (added ``docs/collections/`` to ``.gitignore``).  ``antsibull-docs``
  regenerates them from docstrings at build time, eliminating the stale-doc
  problem and keeping the repository DRY.
* ``docs/antsibull-docs.cfg`` added to configure the GitHub install URL and
  collection URL, replacing the default Galaxy install command in generated
  pages.
* Makefile ``docs`` target updated to use ``--config-file``,
  ``--cleanup everything``, and ``-j auto`` (parallel Sphinx build).

v0.0.1 — 2026-03-25
---------------------

Added
~~~~~

* Initial release of the ``civo.cloud`` Ansible collection.
* Management modules: ``civo_database``, ``civo_firewall``, ``civo_instance``,
  ``civo_kubernetes``, ``civo_kubernetes_node``, ``civo_kubernetes_pool``,
  ``civo_loadbalancer``, ``civo_network``, ``civo_objectstore``,
  ``civo_reserved_ip``, ``civo_sshkey``, ``civo_volume``.
* Info modules: ``civo_database_info``, ``civo_diskimage_info``,
  ``civo_firewall_info``, ``civo_instance_info``, ``civo_kubernetes_info``,
  ``civo_kubernetes_pool_info``, ``civo_kubernetes_version_info``,
  ``civo_loadbalancer_info``, ``civo_network_info``, ``civo_objectstore_info``,
  ``civo_quota_info``, ``civo_region_info``, ``civo_reserved_ip_info``,
  ``civo_size_info``, ``civo_sshkey_info``, ``civo_volume_info``,
  ``civo_volumetype_info``.
* Full check-mode support across all modules.
* Multi-region support (``LON1``, ``NYC1``, ``FRA1``, ``PHX1``).
* Dispatcher role ``roles/civo`` for simplified playbook usage.

Fixed
~~~~~

* ``api_key`` fallback from ``CIVO_TOKEN`` environment variable now works
  correctly with the Ansible ``env_fallback`` helper.
* ``--public-ip`` flag corrected for ``civo instance create``.
* ``--region`` flag added to ``civo kubernetes config`` to avoid returning
  the wrong kubeconfig in multi-region setups.
* ``changed`` sentinel logic inverted in ``civo_volume`` and
  ``civo_reserved_ip`` (was reporting ``changed=False`` for new resources).
* Firewall rule reconciliation now runs in check mode.
* Firewall rules now diffed by all attributes (direction, action, protocol,
  CIDR, port), not just label.
* Volume attach/detach made idempotent.
* Reserved IP assign/unassign made idempotent.
* ``civo_database`` CLI flags corrected to ``--software`` /
  ``--software-version``.
* ``wait_for_active`` boolean handling fixed for JSON ``true``/``false``
  fields.
* ``find_resource_by_name`` now distinguishes real CLI errors from genuine
  "not found" responses.
* ``session_affinity_config_timeout: 0`` no longer silently dropped.
