Installation
============

Requirements
------------

* Ansible >= 2.17
* The ``civo`` CLI binary installed and available on ``PATH``
  (see `Civo CLI installation <https://github.com/civo/cli#installation>`_)
* A Civo API token (obtain from `Civo dashboard → Security <https://dashboard.civo.com/security>`_)

Install from GitHub
-------------------

.. code-block:: bash

   ansible-galaxy collection install \
     git+https://github.com/rosalindfranklininstitute/ansible-civo.git

Pin to a specific tag:

.. code-block:: bash

   ansible-galaxy collection install \
     git+https://github.com/rosalindfranklininstitute/ansible-civo.git,v0.0.3

Via ``requirements.yml``
------------------------

.. code-block:: yaml

   ---
   collections:
     - name: https://github.com/rosalindfranklininstitute/ansible-civo.git
       type: git
       version: main

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml

Authentication
--------------

Authentication is resolved in the following priority order:

1. **Module parameter** — pass ``api_key`` directly to a task (vault-encrypt it):

   .. code-block:: yaml

      - name: Create a network
        civo.cloud.network:
          api_key: "{{ vault_civo_token }}"
          name: my-network
          region: LON1
          state: present

2. **Environment variable** — recommended for CI and local use:

   .. code-block:: bash

      export CIVO_TOKEN="your-api-token"

3. **Civo CLI config** — the active key from ``~/.civo.json``, populated by
   ``civo apikey add`` / ``civo apikey current``.

Regions
-------

Pass ``region`` to any module to target a supported Civo region:

.. list-table::
   :header-rows: 1
   :widths: 20 40

   * - Region code
     - Location
   * - ``LON1``
     - London, UK
   * - ``NYC1``
     - New York, USA
   * - ``FRA1``
     - Frankfurt, Germany
   * - ``PHX1``
     - Phoenix, USA
