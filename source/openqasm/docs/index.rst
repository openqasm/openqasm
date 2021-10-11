===========================
OpenQASM 3 Python Reference
===========================

This ``openqasm3`` package contains the reference abstract syntax tree (AST) for representing OpenQASM 3 programs, tools to parse text into this AST, and tools the manipulate it.

Installation Quickstart
=======================

The package is available on ``pip``, and has no requirements other than Python 3.7+ if you just want access to the AST.
You can install it with::

   python -m pip install openqasm3

There are also some extras that have further dependencies.
The ``parser`` extra is foremost of these, and requires a precise version of ``antlr4-python3-runtime``, in order to provide a parser which can take arbitrary OpenQASM 3 programs stored in strings or files, and convert them into their AST representation.
You can install individual extras by giving them as comma-separated lists in square brackets after the package name in the ``pip`` command (for example, ``openqasm3[parser,tests]``), or you can use the special ``all`` extra to get all of them, with::

   python -m pip install openqasm3[all]


.. _project-goals:

Project Goals
=============

This is a primarily a reference package, and so some of its functionality may be better replaced or extended by specialised tools.
The immediate goals of this package are:

#. to provide a standard AST that all Python-compatible OpenQASM 3 implementations can target, in order to inter-operate;
#. to provide a base parser into this AST, to make it faster to develop applications on top of OpenQASM 3;
#. to illustrate, by the design of the AST, more semantics of OpenQASM 3 programs than a grammar alone can provide;
#. to have few, if any, dependencies, in order to maximise opportunities for re-use.

In particular, it may be the case that some more specialised applications may to implement subsets of the parsing, or handle additional ``defcalgrammar`` imports, or various other things, in order to better appeal to their audiences.
This package is not meant to be a one-stop-shop for all OpenQASM 3 parsing needs, but a base from which others can build.


Contents
========

.. toctree::
   :maxdepth: 2

   api/index.rst
   contributing.rst


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
