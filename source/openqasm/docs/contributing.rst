============
Contributing
============

We welcome any contributions to make this reference package better and more useful, that stay within the bounds of the :ref:`project goals <project-goals>`.
An easy way to help us to make bug reports if you find something that doesn't work correctly, by opening an issue on `our GitHub page <https://github.com/Qiskit/openqasm/issues/new>`__.

If you want to work with the code to make pull requests to improve it, you will need some further packages.


Development Environment
=======================

To work on development, you will need to have a complete `ANTLR <https://www.antlr.org/>`__ installation (not just the runtime), and the ANTLR grammar files from the `main OpenQASM repository <https://github.com/Qiskit/openqasm>`__.

Setting up ANTLR
----------------

You can most likely get a copy of ANTLR using your system package manager if you are on Linux, or from `Homebrew <https://brew.sh>`__ (``brew``) on macOS.
Otherwise, you can follow `these instructions <https://github.com/antlr/antlr4/blob/master/doc/getting-started.md>`__.
Make a note of the exact version of ANTLR you have installed, because you will need to ensure your version of ``antlr4-python3-runtime`` matches exactly.
The package in its current form expects ANTLR 4.9.2.

Once you have ANTLR installed, change to the directory where the ``qasm3.g4`` file is located (for example, ``openqasm/source/grammar``), and run

.. code-block:: bash

   <antlr command> -o /path/to/openqasm3/antlr -Dlanguage=Python3 -visitor qasm3.g4

For example, if this repository is cloned to ``~/openqasm`` and the command to run ANTLR is ``antlr4``, then you should run

.. code-block:: bash

   cd ~/openqasm/source/grammar
   antlr4 -o ~/openqasm/source/openqasm/openqasm3/antlr -Dlanguage=Python3 -visitor qasm3.g4


Developer tools
---------------

Install the full Python development environment with

.. code-block:: bash

   python -m pip install -r requirements.txt -r requirements-dev.txt

ensuring that the version of ``antlr4-python3-runtime`` exactly matches the version of ANTLR you have.
If you are trying to work with another version of ANTLR, you will likely need to manually override ``pip`` to install the correct version yourself, or (temporarily) modifiy ``requirements.txt``.

Install the Python package in editable mode with

.. code-block:: bash

   python -m pip install -e .


The project is configured to use the code formatter `Black <https://pypi.org/project/black>`__, the linter `pylint <https://pylint.org>`__ and test runner `pytest <https://pytest.org>`__.
The commands to run these are, respectively:

.. code-block:: bash

   black .
   pylint .
   pytest


Code Style
==========

All code should be formatted with ``black``, and produce no errors when ``pylint`` is run on it.
The configurations for these two tools are in the ``pyproject.toml`` and ``.pylintrc`` files.

Any new code added should have a complete set of tests, which pass with no warnings.
