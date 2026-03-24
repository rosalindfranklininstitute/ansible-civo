.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.24.0

.. Anchors

.. _ansible_collections.civo.cloud.civo_volumetype_info_module:

.. Anchors: short name for ansible.builtin

.. Title

civo.cloud.civo_volumetype_info module -- List available Civo volume types
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `civo.cloud collection <https://galaxy.ansible.com/ui/repo/published/civo/cloud/>`_ (version 0.0.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible\-galaxy collection install civo.cloud`.

    To use it in a playbook, specify: :code:`civo.cloud.civo_volumetype_info`.

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

- Returns all volume types available in a Civo account.
- The :literal:`name` field of each volume type is the value accepted by the :literal:`volume\_type` parameter of :literal:`civo.cloud.civo\_volume` (when that option is added); currently useful for discovery and documentation purposes.
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

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__parameter-api_key:

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

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__parameter-civo_binary:

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
        <div class="ansibleOptionAnchor" id="parameter-region"></div>

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__parameter-region:

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

   :ref:`civo.cloud.civo\_volume <ansible_collections.civo.cloud.civo_volume_module>`
       Manage Civo block storage volumes.

.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: List all volume types
      civo.cloud.civo_volumetype_info:
        region: LON1
      register: vtypes

    - name: Show volume type names
      ansible.builtin.debug:
        msg: "{{ vtypes.volume_types | map(attribute='name') | list }}"

    - name: Find the default volume type
      ansible.builtin.debug:
        msg: >-
          {{ vtypes.volume_types
             | selectattr('default', 'equalto', 'true')
             | map(attribute='name') | list }}



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
        <div class="ansibleOptionAnchor" id="return-volume_types"></div>

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__return-volume_types:

      .. rst-class:: ansible-option-title

      **volume_types**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-volume_types" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of available volume type dicts.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-volume_types/default"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__return-volume_types/default:

      .. rst-class:: ansible-option-title

      **default**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-volume_types/default" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Whether this is the default volume type (\ :literal:`"true"` or :literal:`"false"`\ ).


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"false"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-volume_types/description"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__return-volume_types/description:

      .. rst-class:: ansible-option-title

      **description**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-volume_types/description" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Human\-readable description of the volume type.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"Encrypted \- 2 replicas"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-volume_types/name"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_volumetype_info_module__return-volume_types/name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-volume_types/name" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Volume type slug / identifier.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"standard"`


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
