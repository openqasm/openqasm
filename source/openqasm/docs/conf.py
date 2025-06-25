# In general, we expect that `openqasm3` is installed and available on the path
# without modification.

import openqasm3

project = "OpenQASM 3 Reference AST"
copyright = "Copyright 2017-2025, OpenQASM Contributors."
author = "OpenQASM Contributors"
release = openqasm3.__version__

extensions = [
    # Allow auto-generation of class and method documentation, as long as you
    # explicitly put the directives in.
    "sphinx.ext.autodoc",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
