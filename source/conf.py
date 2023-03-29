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

version = os.getenv('VERSION','Live')

project = f'OpenQASM {version} Specification'
copyright = '2017-2023, Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta'
author = 'Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
  'sphinx.ext.mathjax',
  'sphinx.ext.githubpages',
  'sphinxcontrib.bibtex',
  'reno.sphinxext',
  'multifigure'
]

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

version_list_var = os.getenv('VERSION_LIST')
extra_nav_links = {'Live Version': '/index.html'} # default link to Live version

if version_list_var is not None:
    version_list = version_list_var.split(',')
    for ver in version_list:
        extra_nav_links[f'Version {ver}'] = f'/versions/{ver}/index.html'

print(extra_nav_links)

# Theme specific options
html_theme_options = {
  'extra_nav_links': extra_nav_links
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The URL which points to the root of the HTML documentation. It is used to
# indicate the location of document like canonical_url.
html_baseurl = os.getenv('HTML_BASEURL', '')

# Add css styles for colored text
html_css_files = ['colors.css']

# If True, figures, tables and code-blocks are automatically numbered
# if they have a caption.
numfig = True
# Necessary setting for sphinxcontrib-bibtex >= 2.0.0
bibtex_bibfiles = ['bibliography.bib']

# This is the list of local variables to export into sphinx by using the
# rst_epilogue below. Using this mechanism we can export the local 'version'
# variable, which can be defined by an environment variable, into the sphinx
# build system for changing the text to specify which specific version of the
# specification is being built
variables_to_export = [
    "version",
]
frozen_locals = dict(locals())
rst_epilog = '\n'.join(map(lambda x: f".. |{x}| replace:: {frozen_locals[x]}", variables_to_export))
del frozen_locals
