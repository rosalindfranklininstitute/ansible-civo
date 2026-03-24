.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.24.0

.. Anchors

.. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module:

.. Anchors: short name for ansible.builtin

.. Title

civo.cloud.civo_kubernetes_version_info module -- List available Civo Kubernetes versions
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `civo.cloud collection <https://galaxy.ansible.com/ui/repo/published/civo/cloud/>`_ (version 0.0.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible\-galaxy collection install civo.cloud`.

    To use it in a playbook, specify: :code:`civo.cloud.civo_kubernetes_version_info`.

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

- Returns all Kubernetes versions available for new clusters in a Civo region, including maturity level and whether each is the default.
- Version strings returned by this module are the values accepted by the :literal:`version` and :literal:`upgrade\_version` parameters of :ref:`civo.cloud.civo\_kubernetes <ansible_collections.civo.cloud.civo_kubernetes_module>`.
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

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__parameter-api_key:

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

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__parameter-civo_binary:

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
        <div class="ansibleOptionAnchor" id="parameter-maturity"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__parameter-maturity:

      .. rst-class:: ansible-option-title

      **maturity**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-maturity" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Filter versions by maturity level: :literal:`stable`\ , :literal:`development`\ , or :literal:`deprecated`. When omitted, all versions are returned.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"stable"`
      - :ansible-option-choices-entry:`"development"`
      - :ansible-option-choices-entry:`"deprecated"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-region"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__parameter-region:

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


.. Attributes


.. Notes


.. Seealso

See Also
--------

.. seealso::

   :ref:`civo.cloud.civo\_kubernetes <ansible_collections.civo.cloud.civo_kubernetes_module>`
       Manage Civo Kubernetes clusters.

.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: List all available Kubernetes versions
      civo.cloud.civo_kubernetes_version_info:
        region: LON1
      register: k8s_versions

    - name: Show all version strings
      ansible.builtin.debug:
        msg: "{{ k8s_versions.kubernetes_versions | map(attribute='version') | list }}"

    - name: Get only stable versions
      civo.cloud.civo_kubernetes_version_info:
        region: LON1
        maturity: stable
      register: stable_versions

    - name: Find the default version
      ansible.builtin.set_fact:
        default_k8s_version: >-
          {{ k8s_versions.kubernetes_versions
             | selectattr('default', 'equalto', 'true')
             | map(attribute='version') | first }}

    - name: Create cluster on latest stable version
      civo.cloud.civo_kubernetes:
        region: LON1
        name: my-cluster
        version: "{{ stable_versions.kubernetes_versions[0].version }}"
        node_count: 1
        state: present



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
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions"></div>

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions:

      .. rst-class:: ansible-option-title

      **kubernetes_versions**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of Kubernetes version dicts matching the query.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions/cluster_type"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions/cluster_type:

      .. rst-class:: ansible-option-title

      **cluster_type**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions/cluster_type" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Cluster runtime type (currently always :literal:`k3s`\ ).


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"k3s"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions/default"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions/default:

      .. rst-class:: ansible-option-title

      **default**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions/default" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether this is the default version for new clusters (returned as the string :literal:`"true"` or :literal:`"false"` by the CLI).


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"true"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions/label"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions/label:

      .. rst-class:: ansible-option-title

      **label**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions/label" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Human\-readable label (identical to :literal:`version` for k3s).


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"1.32.5\-k3s1"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions/type"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions/type:

      .. rst-class:: ansible-option-title

      **type**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions/type" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Maturity level: :literal:`stable`\ , :literal:`development`\ , or :literal:`deprecated`.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"stable"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-kubernetes_versions/version"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_kubernetes_version_info_module__return-kubernetes_versions/version:

      .. rst-class:: ansible-option-title

      **version**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-kubernetes_versions/version" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Full version string. Use this value for the :literal:`version` or :literal:`upgrade\_version` parameters of :ref:`civo.cloud.civo\_kubernetes <ansible_collections.civo.cloud.civo_kubernetes_module>`.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"1.32.5\-k3s1"`


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
