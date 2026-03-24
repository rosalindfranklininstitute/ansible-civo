Quick-start guide
=================

This guide walks you through the most common use-cases for the
``civo.cloud`` collection.

Prerequisites
-------------

* Collection installed (see :doc:`guide_installation`).
* ``CIVO_TOKEN`` exported in your shell.
* ``civo`` CLI binary on ``PATH``.

Create a network and firewall, then launch an instance
------------------------------------------------------

.. code-block:: yaml

   ---
   - name: Provision Civo resources
     hosts: localhost
     gather_facts: false

     tasks:
       - name: Create a private network
         civo.cloud.civo_network:
           name: my-network
           region: LON1
           state: present
         register: net

       - name: Create a firewall with SSH + HTTPS rules
         civo.cloud.civo_firewall:
           name: my-firewall
           region: LON1
           network: my-network
           rules:
             - label: allow-ssh
               direction: ingress
               action: allow
               protocol: tcp
               port_range: "22"
               cidr: "0.0.0.0/0"
             - label: allow-https
               direction: ingress
               action: allow
               protocol: tcp
               port_range: "443"
               cidr: "0.0.0.0/0"
           state: present

       - name: Launch an instance
         civo.cloud.civo_instance:
           hostname: web-01
           region: LON1
           size: g4s.small
           diskimage: ubuntu-noble
           network: my-network
           firewall: my-firewall
           public_ip: create
           wait: true
           state: present
         register: inst

       - name: Print public IP
         ansible.builtin.debug:
           msg: "Instance public IP: {{ inst.instance.public_ip }}"

Provision a Kubernetes cluster
-------------------------------

.. code-block:: yaml

   - name: Create a Kubernetes cluster
     civo.cloud.civo_kubernetes:
       name: my-cluster
       region: LON1
       node_size: g4s.kube.medium
       node_count: 3
       cni: flannel
       wait: true
       state: present
     register: k8s

   - name: Save kubeconfig
     ansible.builtin.copy:
       content: "{{ k8s.cluster.kubeconfig }}"
       dest: "~/.kube/civo-config"
       mode: "0600"

Using the dispatcher role
--------------------------

The ``roles/civo`` dispatcher role lets you drive any resource through a
single ``include_role`` call:

.. code-block:: yaml

   - name: Ensure network exists via role
     ansible.builtin.include_role:
       name: civo.cloud.civo          # role shipped inside this collection
     vars:
       civo_resource: network
       civo_name: my-network
       civo_region: LON1
       civo_state: present

Check mode
----------

All modules support Ansible check mode.  Run with ``--check`` to preview
changes without touching any real resources:

.. code-block:: bash

   ansible-playbook site.yml --check
