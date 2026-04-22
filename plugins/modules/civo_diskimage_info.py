#!/usr/bin/python
# Copyright: (c) 2026, The Rosalind Franklin Institute
# Apache License 2.0


DOCUMENTATION = r"""
---
module: civo_diskimage_info
short_description: List available Civo disk images (VM templates)
description:
  - Returns all disk images available in a Civo region, or filters to a
    single image by name or ID.
  - Disk image names are the values accepted by the C(diskimage) parameter
    of M(civo.cloud.civo_instance) (e.g. C(debian-11), C(ubuntu-jammy)).
  - Uses the C(civo) CLI binary on the control node.
version_added: "0.0.1"
author:
  - The Rosalind Franklin Institute
options:
  name:
    description: >-
      Name of a specific disk image to return (exact match against the
      C(name) field).  When omitted, all images are returned.
    type: str
  distribution:
    description: >-
      Filter images by distribution name (e.g. C(ubuntu), C(debian)).
      Case-insensitive substring match.  Applied after any C(name) filter.
    type: str
  api_key:
    description:
      - Civo API token.
      - Falls back to the C(CIVO_TOKEN) environment variable, then to the active key in C(~/.civo.json) (the civo CLI config), when not set.
    type: str
  region:
    description: Civo region identifier.
    type: str
    default: LON1
  civo_binary:
    description: Path to the C(civo) CLI binary.
    type: str
    default: civo
seealso:
  - module: civo.cloud.civo_instance
"""

EXAMPLES = r"""
- name: List all available disk images
  civo.cloud.civo_diskimage_info:
    region: LON1
  register: images

- name: Show all image names
  ansible.builtin.debug:
    msg: "{{ images.diskimages | map(attribute='name') | list }}"

- name: Look up a specific image by name
  civo.cloud.civo_diskimage_info:
    region: LON1
    name: debian-11
  register: debian11

- name: List only Ubuntu images
  civo.cloud.civo_diskimage_info:
    region: LON1
    distribution: ubuntu
  register: ubuntu_images

- name: Use the image ID when creating an instance
  civo.cloud.civo_instance:
    region: LON1
    hostname: web-01
    diskimage: "{{ debian11.diskimages[0].name }}"
    size: g3.xsmall
    state: present
"""

RETURN = r"""
diskimages:
  description: List of disk image dicts matching the query.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Disk image UUID.
      type: str
      sample: "a4204155-a876-43fa-b4d6-ea2af8774560"
    name:
      description: >-
        Image name / slug.  Pass this value as the C(diskimage) parameter
        when creating an instance.
      type: str
      sample: "debian-11"
    version:
      description: Distribution version string.
      type: str
      sample: "11"
    state:
      description: Availability state of the image (e.g. C(available)).
      type: str
      sample: "available"
    distribution:
      description: Linux distribution family (e.g. C(debian), C(ubuntu)).
      type: str
      sample: "debian"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.civo.cloud.plugins.module_utils.civo_utils import (
    common_argument_spec,
    run_civo_command,
)


def main():
    spec = common_argument_spec()
    del spec["state"]
    spec.update(
        name={"type": "str"},
        distribution={"type": "str"},
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    name = module.params.get("name") or ""
    distribution = module.params.get("distribution") or ""
    api_key = module.params["api_key"]
    region = module.params["region"]
    binary = module.params["civo_binary"]

    if not api_key:
        module.fail_json(msg="api_key is required (pass api_key, set CIVO_TOKEN, or configure the civo CLI)")

    _rc, data, _stderr = run_civo_command(module, ["diskimage", "ls"], api_key, region, binary, check_rc=False)
    images = data if isinstance(data, list) else []

    if name:
        images = [img for img in images if img.get("name") == name]

    if distribution:
        dist_lower = distribution.lower()
        images = [img for img in images if dist_lower in (img.get("distribution") or "").lower()]

    module.exit_json(changed=False, diskimages=images)


if __name__ == "__main__":
    main()
