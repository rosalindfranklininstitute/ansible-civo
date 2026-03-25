.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.24.0

.. Anchors

.. _ansible_collections.civo.cloud.civo_sshkey_module:

.. Anchors: short name for ansible.builtin

.. Title

civo.cloud.civo_sshkey module -- Manage Civo SSH keys
+++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `civo.cloud collection <https://galaxy.ansible.com/ui/repo/published/civo/cloud/>`_ (version 0.0.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    For installation instructions, see :doc:`Installation </guide_installation>`.

    To use it in a playbook, specify: :code:`civo.cloud.civo_sshkey`.

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

- Upload, rename, or remove SSH public keys stored in a Civo account.
- Idempotent — if a key with the same name already exists, the module reports :literal:`changed=False` for :literal:`state=present` (re\-upload is not supported by the Civo CLI; rename the key first if you need to replace it).
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

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-api_key:

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

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-civo_binary:

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

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Name / label for the SSH key.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-new_name"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-new_name:

      .. rst-class:: ansible-option-title

      **new_name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-new_name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Rename an existing SSH key to this value.

      When provided alongside :emphasis:`state=present` the key is first created (if absent) and then renamed; if the key already exists under :emphasis:`name` it is just renamed.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-public_key_file"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-public_key_file:

      .. rst-class:: ansible-option-title

      **public_key_file**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-public_key_file" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Path to the SSH public key file on the control node.

      Required when :emphasis:`state=present` and the key does not yet exist.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-region"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-region:

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

      .. _ansible_collections.civo.cloud.civo_sshkey_module__parameter-state:

      .. rst-class:: ansible-option-title

      **state**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      :literal:`present` ensures the SSH key exists in the account.

      :literal:`absent` removes the SSH key.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`"present"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"absent"`


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso

See Also
--------

.. seealso::

   :ref:`civo.cloud.civo\_sshkey\_info <ansible_collections.civo.cloud.civo_sshkey_info_module>`
       List SSH keys stored in a Civo account.
   :ref:`civo.cloud.civo\_instance <ansible_collections.civo.cloud.civo_instance_module>`
       Manage Civo compute instances.

.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: Upload an SSH public key
      civo.cloud.civo_sshkey:
        name: my-laptop-key
        public_key_file: ~/.ssh/id_ed25519.pub

    - name: Remove an SSH key
      civo.cloud.civo_sshkey:
        name: my-laptop-key
        state: absent

    - name: Rename an existing SSH key
      civo.cloud.civo_sshkey:
        name: my-laptop-key
        new_name: laptop-ed25519
        state: present

    - name: Upload key and use it when creating an instance
      civo.cloud.civo_sshkey:
        name: deploy-key
        public_key_file: /home/ci/.ssh/id_rsa.pub

    - name: Create instance using the uploaded key
      civo.cloud.civo_instance:
        hostname: web-01
        size: g3.xsmall
        diskimage: debian-11
        sshkey: deploy-key
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
        <div class="ansibleOptionAnchor" id="return-sshkey"></div>

      .. _ansible_collections.civo.cloud.civo_sshkey_module__return-sshkey:

      .. rst-class:: ansible-option-title

      **sshkey**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkey" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Details of the managed SSH key.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when state is :literal:`present`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-sshkey/fingerprint"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_module__return-sshkey/fingerprint:

      .. rst-class:: ansible-option-title

      **fingerprint**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkey/fingerprint" title="Permalink to this return value"></a>

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
        <div class="ansibleOptionAnchor" id="return-sshkey/id"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_module__return-sshkey/id:

      .. rst-class:: ansible-option-title

      **id**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkey/id" title="Permalink to this return value"></a>

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
        <div class="ansibleOptionAnchor" id="return-sshkey/name"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.civo.cloud.civo_sshkey_module__return-sshkey/name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-sshkey/name" title="Permalink to this return value"></a>

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
