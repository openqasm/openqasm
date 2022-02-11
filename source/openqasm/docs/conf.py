# In general, we expect that `openqasm3` is installed and available on the path
# without modification.

project = 'OpenQASM 3 Reference AST'
copyright = '2021, OpenQASM 3 Team and Contributors'
author = 'OpenQASM 3 Team and Contributors'
release = '0.1.0'

extensions = [
    # Allow auto-generation of class and method documentation, as long as you
    # explicitly put the directives in.
    "sphinx.ext.autodoc",
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
