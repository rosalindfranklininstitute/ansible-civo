.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.24.0

.. Anchors

.. _ansible_collections.civo.cloud.civo_kubernetes_node_module:

.. Anchors: short name for ansible.builtin

.. Title

civo.cloud.civo_kubernetes_node module -- Recycle or delete a node in a Civo Kubernetes cluster
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `civo.cloud collection <https://galaxy.ansible.com/ui/repo/published/civo/cloud/>`_ (version 0.0.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    For installation instructions, see :doc:`Installation </guide_installation>`.

    To use it in a playbook, specify: :code:`civo.cloud.civo_kubernetes_node`.

.. version_added

.. rst-class:: ansible-version-added

New in civo.cloud 0.0.1

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- Manages individual nodes (instances) within a Civo Kubernetes cluster.
- :literal:`state=recycle` replaces the node with a fresh instance while keeping the pool size the same. Calls :literal:`civo kubernetes recycle CLUSTER \-\-node NODE`.
- :literal:`state=absent` permanently removes the node from its pool, reducing the pool size by one. Calls :literal:`civo kubernetes node\-pool instance\-delete CLUSTER \-\-instance\-id ID \-\-node\-pool\-id POOL\_ID`.
- The node is identified by its hostname (e.g. :literal:`k3s\-my\-cluster\-abc12\-1`\ ).
- Uses the :literal:`civo` CLI binary on the control node.


.. Aliases


.. Requirements






.. Options

Parameters
----------

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Parameter
    - Comments

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_key"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-api_key:

      .. rst-class:: ansible-option-title

      **api_key**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_key" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Civo API token.

      Falls back to the :literal:`CIVO\_TOKEN` environment variable when not set.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-civo_binary"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-civo_binary:

      .. rst-class:: ansible-option-title

      **civo_binary**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-civo_binary" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Path to the :literal:`civo` CLI binary.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"civo"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-cluster"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-cluster:

      .. rst-class:: ansible-option-title

      **cluster**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-cluster" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Name of the Kubernetes cluster that owns the node.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-node"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-node:

      .. rst-class:: ansible-option-title

      **node**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-node" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Hostname of the node to act on (e.g. :literal:`k3s\-my\-cluster\-abc12\-1`\ ). Obtain available node names from :ref:`civo.cloud.civo\_kubernetes\_pool\_info <ansible_collections.civo.cloud.civo_kubernetes_pool_info_module>` or :literal:`civo kubernetes node\-pool instance\-ls CLUSTER`.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-pool_id"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-pool_id:

      .. rst-class:: ansible-option-title

      **pool_id**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-pool_id" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      ID of the node pool that contains the node. Required for :literal:`state=absent`. Optional for :literal:`state=recycle` (the module will search all pools when omitted, which adds extra API calls).


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-region"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-region:

      .. rst-class:: ansible-option-title

      **region**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-region" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Civo region identifier.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"LON1"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-state"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__parameter-state:

      .. rst-class:: ansible-option-title

      **state**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      :literal:`recycle` — replace the node with a new instance (same pool size).

      :literal:`absent` — permanently delete the node instance from its pool.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"recycle"`
      - :ansible-option-choices-entry:`"absent"`


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso

See Also
--------

.. seealso::

   :ref:`civo.cloud.civo\_kubernetes <ansible_collections.civo.cloud.civo_kubernetes_module>`
       Manage Civo Kubernetes clusters.
   :ref:`civo.cloud.civo\_kubernetes\_pool <ansible_collections.civo.cloud.civo_kubernetes_pool_module>`
       Manage node pools in a Civo Kubernetes cluster.
   :ref:`civo.cloud.civo\_kubernetes\_pool\_info <ansible_collections.civo.cloud.civo_kubernetes_pool_info_module>`
       Query node pools in a Civo Kubernetes cluster.

.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: Recycle a node (replace with a fresh instance)
      civo.cloud.civo_kubernetes_node:
        region: LON1
        cluster: my-cluster
        node: k3s-my-cluster-abc12-1
        state: recycle

    - name: Delete a node from its pool (reduces pool size by 1)
      civo.cloud.civo_kubernetes_node:
        region: LON1
        cluster: my-cluster
        node: k3s-my-cluster-abc12-1
        pool_id: "aaaa-bbbb-cccc"
        state: absent



.. Facts


.. Return values

Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Key
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-msg"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__return-msg:

      .. rst-class:: ansible-option-title

      **msg**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-msg" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Human\-readable status message.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"Node 'k3s\-my\-cluster\-abc12\-1' recycled successfully"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-node"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_node_module__return-node:

      .. rst-class:: ansible-option-title

      **node**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-node" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The hostname of the node that was acted on.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"k3s\-my\-cluster\-abc12\-1"`


      .. raw:: html

        </div>



..  Status (Presently only deprecated)


.. Authors

Authors
~~~~~~~

- The Rosalind Franklin Institute


.. Extra links

Collection links
~~~~~~~~~~~~~~~~

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://github.com/rosalindfranklininstitute/ansible-civo/issues"
    external: true
  - title: "Homepage"
    url: "https://www.rfi.ac.uk"
    external: true
  - title: "Repository (Sources)"
    url: "https://github.com/rosalindfranklininstitute/ansible-civo"
    external: true


.. Parsing errors
