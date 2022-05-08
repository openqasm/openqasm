# OpenPulse Python Reference

[![License](https://img.shields.io/github/license/Qiskit/openqasm.svg)](https://opensource.org/licenses/Apache-2.0)<!-- long-description-skip-begin -->[![Release](https://img.shields.io/pypi/v/openqasm3)](https://pypi.org/project/openqasm3)<!-- long-description-skip-end -->

OpenPulse is a minor extension to OpenQASM 3 with a concrete implementation of pulse grammar.
The `openpulse` package depends on the openqasm3 package, re-export the 
identical `openqasm3.ast` nodes, and reuse many methods in `openpulse.parser`.

The package is structured similarly to `openqasm3` with the modules:

* `openpulse.ast`: The AST nodes. Identical nodes from `openqasm3.ast` are re-exported.

* `openpulse.parser`: A parser similar to `openqasm3.parser`, but for OpenPulse.

* `tests`: A set of unit tests.

* No visitor module as `openqasm3.visitor` can be reused.

The extensions to the OpenQASM 3 grammar are:

* Pulse types: `port`, `frame` and `waveform`.
* Extension to OpenQASM 3 classical type to consume the pulse types.
* Definition of `cal` block and redefinition of OpenQASM 3 `defcal` block with OpenPulse grammar.

## Development Environment

You will need to first follow the README in the openqasm directory and install `openqasm3` to your
virtual environment in editable mode.

### Developer tools

This package uses the same developer tools as `openqasm3`.
