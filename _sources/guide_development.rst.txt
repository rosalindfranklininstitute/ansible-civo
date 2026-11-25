Development guide
=================

Setup
-----

.. code-block:: bash

   pip install -r dev-requirements.txt
   pre-commit install

Make targets
------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Target
     - Description
   * - ``make lint``
     - Run ``ruff check`` on ``plugins/``
   * - ``make format``
     - Run ``ruff format`` on ``plugins/``
   * - ``make ansible-lint``
     - Run ``ansible-lint`` across the project
   * - ``make docs``
     - Generate per-module RST with antsibull-docs, then build Sphinx HTML
   * - ``make sanity``
     - Run ``ansible-test sanity --docker`` (requires Docker)
   * - ``make test-check``
     - Run check-mode smoke tests (requires ``CIVO_TOKEN``, no resources created)
   * - ``make test-integration``
     - Run the full integration test suite (requires ``CIVO_TOKEN``)
   * - ``make clean``
     - Remove ``docs/_build/`` and ``docs/collections/``

Building docs locally
---------------------

The docs pipeline uses antsibull-docs, which needs the collection importable
by Ansible.  Symlink it into the collections path first:

.. code-block:: bash

   mkdir -p ~/.ansible/collections/ansible_collections/civo
   ln -s "$(pwd)" ~/.ansible/collections/ansible_collections/civo/cloud

Then build:

.. code-block:: bash

   make docs
   open docs/_build/html/index.html

Docs are published automatically to GitHub Pages on every push to ``main``
via ``.github/workflows/docs.yml``.

Integration tests
-----------------

Integration tests make **real API calls** and create actual Civo resources.
All test resources are prefixed with ``ansible-test-`` for easy identification
and are cleaned up in an ``always:`` block even if the run fails mid-way.

Prerequisites:

* ``CIVO_TOKEN`` set in your environment
* ``civo`` CLI installed and in ``PATH``
* Collection symlinked as above

Run the full suite:

.. code-block:: bash

   ansible-playbook tests/integration/test_all.yml -v

Run a single resource type using tags:

.. code-block:: bash

   ansible-playbook tests/integration/test_all.yml -v --tags network
   ansible-playbook tests/integration/test_all.yml -v --tags kubernetes

Available tags: ``network``, ``firewall``, ``instance``, ``volume``,
``reserved_ip``, ``objectstore``, ``database``, ``kubernetes``,
``kubernetes_upgrade``, ``kubernetes_node``, ``kubernetes_pool``,
``sshkey``, ``catalog``, ``loadbalancer``, ``info``.

Check-mode smoke tests (no real resources created):

.. code-block:: bash

   make test-check

Collection structure
--------------------

.. code-block:: text

   ansible-civo/
   ├── galaxy.yml                    # Collection metadata (namespace: civo.cloud)
   ├── plugins/
   │   ├── module_utils/
   │   │   └── civo_utils.py         # Shared helpers: auth, CLI exec, JSON parsing, wait loops
   │   └── modules/
   │       ├── network.py            # CRUD modules (one per resource type)
   │       ├── network_info.py       # Info (read-only) modules
   │       └── ...
   ├── roles/
   │   └── civo/                     # Dispatcher role
   │       ├── defaults/main.yml     # All tuneable defaults
   │       └── tasks/                # Per-resource task files
   ├── tests/
   │   └── integration/
   │       ├── test_all.yml          # Master integration test playbook
   │       ├── test_check_mode.yml   # Check-mode smoke tests
   │       └── tasks/                # Per-resource test task files
   ├── docs/                         # Sphinx documentation source
   ├── Makefile                      # Developer convenience targets
   ├── dev-requirements.txt          # Python deps for docs and linting
   └── pyproject.toml                # ruff configuration

All modules follow the same pattern: resolve auth → find or create/delete the
resource via ``civo`` CLI with ``-o json`` → parse JSON → optionally poll for
``ACTIVE`` status → return a structured result dict.  Shared logic lives in
``plugins/module_utils/civo_utils.py``.

CI
--

GitHub Actions runs on every push and pull request:

* ``ruff`` — Python linting and formatting
* ``ansible-lint`` — Ansible best-practice checks
* ``ansible-test sanity`` — collection sanity checks against Ansible
  stable-2.17, stable-2.18, and devel
* ``docs`` — builds and publishes to GitHub Pages on pushes to ``main``
