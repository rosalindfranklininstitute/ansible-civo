Quick-start guide
=================

Prerequisites
-------------

* Collection installed (see :doc:`guide_installation`).
* ``CIVO_TOKEN`` exported in your shell.
* ``civo`` CLI binary on ``PATH``.

Network, firewall and instance
--------------------------------

.. code-block:: yaml

   ---
   - name: Provision Civo resources
     hosts: localhost
     gather_facts: false

     tasks:
       - name: Create a private network
         civo.cloud.network:
           name: prod-network
           region: LON1
           state: present

       - name: Create a firewall with SSH + HTTPS rules
         civo.cloud.firewall:
           name: prod-fw
           region: LON1
           network: prod-network
           rules:
             - label: allow-ssh
               direction: ingress
               action: allow
               protocol: tcp
               port: "22"
               cidr: "0.0.0.0/0"
             - label: allow-https
               direction: ingress
               action: allow
               protocol: tcp
               port: "443"
               cidr: "0.0.0.0/0"
           state: present

       - name: Launch an instance
         civo.cloud.instance:
           hostname: web-01
           region: LON1
           size: g4s.small
           diskimage: ubuntu-noble
           network: prod-network
           firewall: prod-fw
           public_ip: create
           wait: true
           state: present
         register: inst

       - name: Print public IP
         ansible.builtin.debug:
           msg: "Instance public IP: {{ inst.instance.public_ip }}"

Kubernetes cluster
------------------

.. code-block:: yaml

   - name: Create a Kubernetes cluster
     civo.cloud.kubernetes:
       name: my-cluster
       region: LON1
       node_size: g4s.kube.medium
       node_count: 3
       network: prod-network
       cni: flannel
       wait: true
       state: present
     register: k8s

   - name: Save kubeconfig
     ansible.builtin.copy:
       content: "{{ k8s.cluster.kubeconfig }}"
       dest: "~/.kube/civo-prod.yaml"
       mode: "0600"

   - name: Scale a node pool
     civo.cloud.kubernetes_pool:
       cluster: my-cluster
       region: LON1
       pool_id: "{{ pool_id }}"
       count: 5
       state: present

   - name: Recycle a node
     civo.cloud.kubernetes_node:
       cluster: my-cluster
       region: LON1
       node: "{{ node_hostname }}"
       state: recycle

Volume — create, resize and attach
------------------------------------

.. code-block:: yaml

   - name: Create a data volume
     civo.cloud.volume:
       name: data-vol
       region: LON1
       size_gb: 50
       network: default
       state: present

   - name: Resize the volume
     civo.cloud.volume:
       name: data-vol
       region: LON1
       size_gb: 100
       state: present

   - name: Attach volume to an instance
     civo.cloud.volume:
       name: data-vol
       region: LON1
       instance: web-01
       state: attached

Reserved IP
-----------

.. code-block:: yaml

   - name: Reserve a public IP
     civo.cloud.reserved_ip:
       name: web-ip
       region: LON1
       state: present
     register: rip

   - name: Assign it to an instance
     civo.cloud.reserved_ip:
       name: web-ip
       region: LON1
       instance: web-01
       state: assigned

Managed database
----------------

.. code-block:: yaml

   - name: Create a PostgreSQL database
     civo.cloud.database:
       name: myapp-db
       region: LON1
       engine: postgresql
       version: "17"
       size: g3.db.small
       nodes: 1
       network: prod-network
       wait: true
       state: present
     register: db

Object store
------------

.. code-block:: yaml

   - name: Create an S3-compatible object store
     civo.cloud.objectstore:
       name: my-bucket
       region: LON1
       max_size_gb: 500
       wait: true
       state: present
     register: bucket

Load balancers
--------------

Load balancers are provisioned automatically by the Kubernetes
cloud-controller-manager when a ``Service`` of type ``LoadBalancer`` is
deployed.  The Civo CLI does not expose a ``create`` command for them, so
``civo_loadbalancer`` can only query (``state=present``) or delete
(``state=absent``) existing load balancers.

.. code-block:: yaml

   - name: Look up a load balancer
     civo.cloud.loadbalancer_info:
       region: LON1
     register: lbs

Dispatcher role
---------------

The ``roles/civo`` dispatcher role lets you drive any resource through a
single ``include_role`` call:

.. code-block:: yaml

   - name: Ensure network exists via role
     ansible.builtin.include_role:
       name: civo.cloud.civo
     vars:
       civo_resource: network
       civo_name: prod-network
       civo_region: LON1
       civo_state: present

Check mode
----------

All modules support Ansible check mode.  Run with ``--check`` to preview
changes without making any real API calls:

.. code-block:: bash

   ansible-playbook site.yml --check
