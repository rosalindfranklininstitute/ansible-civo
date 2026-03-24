Installation
============

Requirements
------------

* Ansible >= 2.15
* The ``civo`` CLI binary installed and available on ``PATH``
  (see `Civo CLI installation <https://github.com/civo/cli#installation>`_)
* A Civo API token (export as ``CIVO_TOKEN``)

Install from GitHub
-------------------

.. code-block:: bash

   ansible-galaxy collection install \
     git+https://github.com/rosalindfranklininstitute/ansible-civo.git

Or pin to a specific tag:

.. code-block:: bash

   ansible-galaxy collection install \
     git+https://github.com/rosalindfranklininstitute/ansible-civo.git,v0.0.1

Installing via ``requirements.yml``
-------------------------------------

.. code-block:: yaml

   ---
   collections:
     - name: https://github.com/rosalindfranklininstitute/ansible-civo.git
       type: git
       version: main

Then install with:

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml

Authentication
--------------

Set the ``CIVO_TOKEN`` environment variable before running any play:

.. code-block:: bash

   export CIVO_TOKEN="your-api-token"

Alternatively pass ``api_key`` directly to each module task (not recommended
for production — prefer the environment variable or a vault-encrypted variable).
