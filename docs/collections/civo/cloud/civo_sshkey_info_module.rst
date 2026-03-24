.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.24.0

.. Anchors

.. _ansible_collections.civo.cloud.civo_sshkey_info_module:

.. Anchors: short name for ansible.builtin

.. Title

civo.cloud.civo_sshkey_info module -- List SSH keys stored in a Civo account
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `civo.cloud collection <https://galaxy.ansible.com/ui/repo/published/civo/cloud/>`_ (version 0.0.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible\-galaxy collection install civo.cloud`.

    To use it in a playbook, specify: :code:`civo.cloud.civo_sshkey_info`.

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

- Returns all SSH keys registered with a Civo account, or filters to a single key by name.
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

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__parameter-api_key:

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

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__parameter-civo_binary:

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
        <div class="ansibleOptionAnchor" id="parameter-name"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__parameter-name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Name of a specific SSH key to return (exact match). When omitted, all keys are returned.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-region"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__parameter-region:

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

   :ref:`civo.cloud.civo\_sshkey <ansible_collections.civo.cloud.civo_sshkey_module>`
       Manage Civo SSH keys.

.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: List all SSH keys
      civo.cloud.civo_sshkey_info:
      register: keys

    - name: Show key names
      ansible.builtin.debug:
        msg: "{{ keys.sshkeys | map(attribute='name') | list }}"

    - name: Look up a specific key by name
      civo.cloud.civo_sshkey_info:
        name: my-laptop-key
      register: my_key

    - name: Assert the key exists
      ansible.builtin.assert:
        that:
          - my_key.sshkeys | length == 1



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
        <div class="ansibleOptionAnchor" id="return-sshkeys"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__return-sshkeys:

      .. rst-class:: ansible-option-title

      **sshkeys**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkeys" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of SSH key dicts matching the query.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-sshkeys/fingerprint"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__return-sshkeys/fingerprint:

      .. rst-class:: ansible-option-title

      **fingerprint**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkeys/fingerprint" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      MD5 fingerprint of the public key.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-sshkeys/id"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__return-sshkeys/id:

      .. rst-class:: ansible-option-title

      **id**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkeys/id" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      SSH key UUID.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"a1b2c3d4\-0000\-0000\-0000\-000000000000"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-sshkeys/name"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_info_module__return-sshkeys/name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkeys/name" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      SSH key label.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"my\-laptop\-key"`


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
