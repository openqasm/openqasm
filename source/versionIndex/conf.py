# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('_extensions'))

# -- Project information -----------------------------------------------------
from typing import List

project = f'OpenQASM Specification List'
copyright = '2017-2023, Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta'
author = 'Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = [
    "openqasm/docs",
]

# Sets the default code-highlighting language.  `.. code-block::` directives
# that are not OQ3 should specify the language manually.  The value is
# interpreted as a Pygments lexer alias; this needs the dependency
# `openqasm_pygments`.
highlight_language = "qasm3"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# The URL which points to the root of the HTML documentation. It is used to
# indicate the location of document like canonical_url.
html_baseurl = os.getenv('HTML_BASEURL', '')

# Add css styles for colored text
html_css_files = ['colors.css']

html_theme_options = {
    # Disable showing the sidebar. Defaults to 'false'
    'nosidebar': True,
}

version_links = os.getenv('VERSION_LINKS')
rst_epilog = version_links
