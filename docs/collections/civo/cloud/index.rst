.. meta::
  :antsibull-docs: 2.24.0


.. _plugins_in_civo.cloud:

Civo.Cloud
==========

Collection version 0.0.1

.. contents::
   :local:
   :depth: 1

Description
-----------

Manage Civo cloud resources (instances, Kubernetes, networks, firewalls, volumes, load balancers, reserved IPs, databases and object stores) using the Civo CLI. EXPERIMENTAL — not yet suitable for production use.

**Author:**

* The Rosalind Franklin Institute

**Supported ansible-core versions:**

* 2.15.0 or newer

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




.. toctree::
    :maxdepth: 1

.. _plugin_index_for_civo.cloud:

Plugin Index
------------

These are the plugins in the civo.cloud collection:

.. _module_plugins_in_civo.cloud:

Modules
~~~~~~~

* :ansplugin:`civo_database module <civo.cloud.civo_database#module>` -- Manage Civo managed databases
* :ansplugin:`civo_database_info module <civo.cloud.civo_database_info#module>` -- Gather information about Civo managed databases
* :ansplugin:`civo_diskimage_info module <civo.cloud.civo_diskimage_info#module>` -- List available Civo disk images (VM templates)
* :ansplugin:`civo_firewall module <civo.cloud.civo_firewall#module>` -- Manage Civo firewalls and firewall rules
* :ansplugin:`civo_firewall_info module <civo.cloud.civo_firewall_info#module>` -- Gather information about Civo firewalls
* :ansplugin:`civo_instance module <civo.cloud.civo_instance#module>` -- Manage Civo compute instances
* :ansplugin:`civo_instance_info module <civo.cloud.civo_instance_info#module>` -- Gather information about Civo compute instances
* :ansplugin:`civo_kubernetes module <civo.cloud.civo_kubernetes#module>` -- Manage Civo Kubernetes clusters
* :ansplugin:`civo_kubernetes_info module <civo.cloud.civo_kubernetes_info#module>` -- Gather information about Civo Kubernetes clusters
* :ansplugin:`civo_kubernetes_node module <civo.cloud.civo_kubernetes_node#module>` -- Recycle or delete a node in a Civo Kubernetes cluster
* :ansplugin:`civo_kubernetes_pool module <civo.cloud.civo_kubernetes_pool#module>` -- Manage node pools in a Civo Kubernetes cluster
* :ansplugin:`civo_kubernetes_pool_info module <civo.cloud.civo_kubernetes_pool_info#module>` -- Query node pools in a Civo Kubernetes cluster
* :ansplugin:`civo_kubernetes_version_info module <civo.cloud.civo_kubernetes_version_info#module>` -- List available Civo Kubernetes versions
* :ansplugin:`civo_loadbalancer module <civo.cloud.civo_loadbalancer#module>` -- Manage Civo load balancers
* :ansplugin:`civo_loadbalancer_info module <civo.cloud.civo_loadbalancer_info#module>` -- Gather information about Civo load balancers
* :ansplugin:`civo_network module <civo.cloud.civo_network#module>` -- Manage Civo private networks
* :ansplugin:`civo_network_info module <civo.cloud.civo_network_info#module>` -- Gather information about Civo private networks
* :ansplugin:`civo_objectstore module <civo.cloud.civo_objectstore#module>` -- Manage Civo S3\-compatible object stores
* :ansplugin:`civo_objectstore_info module <civo.cloud.civo_objectstore_info#module>` -- Gather information about Civo object stores
* :ansplugin:`civo_quota_info module <civo.cloud.civo_quota_info#module>` -- Return current Civo account quota and usage
* :ansplugin:`civo_region_info module <civo.cloud.civo_region_info#module>` -- List available Civo regions
* :ansplugin:`civo_reserved_ip module <civo.cloud.civo_reserved_ip#module>` -- Manage Civo reserved (static) public IP addresses
* :ansplugin:`civo_reserved_ip_info module <civo.cloud.civo_reserved_ip_info#module>` -- Gather information about Civo reserved IP addresses
* :ansplugin:`civo_size_info module <civo.cloud.civo_size_info#module>` -- List available Civo instance / Kubernetes / database sizes
* :ansplugin:`civo_sshkey module <civo.cloud.civo_sshkey#module>` -- Manage Civo SSH keys
* :ansplugin:`civo_sshkey_info module <civo.cloud.civo_sshkey_info#module>` -- List SSH keys stored in a Civo account
* :ansplugin:`civo_volume module <civo.cloud.civo_volume#module>` -- Manage Civo block storage volumes
* :ansplugin:`civo_volume_info module <civo.cloud.civo_volume_info#module>` -- Gather information about Civo block storage volumes
* :ansplugin:`civo_volumetype_info module <civo.cloud.civo_volumetype_info#module>` -- List available Civo volume types

.. toctree::
    :maxdepth: 1
    :hidden:

    civo_database_module
    civo_database_info_module
    civo_diskimage_info_module
    civo_firewall_module
    civo_firewall_info_module
    civo_instance_module
    civo_instance_info_module
    civo_kubernetes_module
    civo_kubernetes_info_module
    civo_kubernetes_node_module
    civo_kubernetes_pool_module
    civo_kubernetes_pool_info_module
    civo_kubernetes_version_info_module
    civo_loadbalancer_module
    civo_loadbalancer_info_module
    civo_network_module
    civo_network_info_module
    civo_objectstore_module
    civo_objectstore_info_module
    civo_quota_info_module
    civo_region_info_module
    civo_reserved_ip_module
    civo_reserved_ip_info_module
    civo_size_info_module
    civo_sshkey_module
    civo_sshkey_info_module
    civo_volume_module
    civo_volume_info_module
    civo_volumetype_info_module



.. seealso::

    List of :ref:`collections <list_of_collections>` with docs hosted here.
