# Configuration file for the Sphinx documentation builder.
# antsibull-docs is used to generate per-module RST pages; this file
# configures the surrounding Sphinx site.

import os

import yaml

# Read version from galaxy.yml so there is a single source of truth.
_galaxy_yml = os.path.join(os.path.dirname(__file__), "..", "galaxy.yml")
with open(_galaxy_yml) as _f:
    _galaxy = yaml.safe_load(_f)

project = "civo.cloud"
copyright = "2026, The Rosalind Franklin Institute"
author = "The Rosalind Franklin Institute"
release = _galaxy["version"]
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_antsibull_ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "ansible_devel": ("https://docs.ansible.com/ansible/devel/", None),
}

# antsibull-docs writes generated RST into docs/docsite/rst/; tell Sphinx
# where to find the root document.
root_doc = "index"
