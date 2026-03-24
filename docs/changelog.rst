Changelog
=========

All notable changes to this project are documented in this file.

The format follows `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

v1.0.0 — 2024-01-01
---------------------

Added
~~~~~

* Initial release of the ``civo.cloud`` Ansible collection.
* Modules: ``civo_network``, ``civo_firewall``, ``civo_instance``,
  ``civo_kubernetes``, ``civo_volume``, ``civo_loadbalancer``,
  ``civo_reserved_ip``, ``civo_database``, ``civo_objectstore``.
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
