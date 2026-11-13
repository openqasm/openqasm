===========
Package API
===========

The principal export of this package is the AST, in the :obj:`openqasm3.ast` module.
In addition, a reference parser to this AST is provided in its simplest form by :obj:`openqasm3.parse`, with the full interface exposed in the :obj:`openqasm3.parser` package.
Include resolution is opt-in and is configured atomically through
:class:`openqasm3.resolver.IncludeEnvironment`.

.. toctree::
   :maxdepth: 2
   :caption: Packages and Modules:

   ast.rst
   parser.rst
   printer.rst
   resolver.rst
   spec.rst
   visitor.rst
