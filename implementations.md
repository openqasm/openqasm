<!-- Copyright Contributors to the Qiskit project. -->
# OpenQASM 3 Implementations

Listed here are publicly available tools that implement or support OpenQASM 3.
Many projects are not yet listed here. The descriptions of projects that *are* listed
may be incomplete.
If you know of a software project that supports OpenQASM 3 but is not listed here, or if
you have corrections, please
[open an issue](https://github.com/openqasm/openqasm/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen).

## Feature Comparison

* **function**
    * **parser** -- typically means that semantic analysis is not supported.
    * **front end** -- some semantic analysis or compilation is done.
      Examples of semantic analysis are type checking and constant folding.
* **status**
    * **incomplete** This sometimes means WIP and sometimes that not all of OQ3 is supported.

| Name                                                        | API language | impl language | function             | status     | license |
|-------------------------------------------------------------|--------------|---------------|----------------------|------------|---------|
| [Reference parser](#reference-parser)                       | Python       | Python        | front-end            | complete   | OSS     |
| [openqasm3_parser](#openqasm3_parser)                       | Rust         | Rust          | front-end            | WIP        | OSS     |
| [Quasar](#quasar)                                           | Julia        | Julia         | parser               | WIP        | OSS     |
| [qasm3tools](#qasm3tools)                                   | CLI          | C++           | unknown              | unknown    | OSS     |
| [Amazon Braket](#amazon-braket)                             | Python       |               | web service          | incomplete |         |
| [LabOne Q](#labone-q)                                       | Python       | Rust/Python   | SDK                  | incomplete | OSS     |
| [Munich Quantum Toolkit (MQT)](#munich-quantum-toolkit-mqt) | Python       | C++           | front end            |            | OSS     |
| [Qiskit](#qiskit)                                           | Python       | Rust/Python   | SDK                  | incomplete | OSS     |
| [Feynman](#feynman)                                         | Haskell      | Haskell       | front end            | unknown    | OSS     |
| [AutoQASM](#autoqasm)                                       | Python       | Python        | circuit construction | incomplete | OSS     |
| [OQpy](#oqpy)                                               | Python       | Python        | circuit construction | complete   | OSS     |
| [MATLAB Support Package for Quantum Computing](#matlab)     | MATLAB       | MATLAB        | circuit construction | unknown    | unknown |

### [Reference parser](https://github.com/openqasm/openqasm/tree/main/source/openqasm)

Meant to completely implement the OpenQASM 3 spec. It does no semantic analysis. It is relatively slow.
It is based on [ANTLR](https://www.antlr.org/).

### [openqasm3_parser](https://github.com/Qiskit/openqasm3_parser)
Compiler front end for OpenQASM 3. Lexing, parsing, and semantic analysis.

### [Quasar](https://github.com/kshyatt-aws/Quasar.jl)
The Qu(antum) as(sembly) (lex/pars)er
Compiler front end for OpenQASM 3. Lexing, parsing, and semantic analysis.

### [qasm3tools](https://github.com/softwareQinc/qasm3tools)
Unknown

### [Amazon Braket](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm.html)
Cloud quantum computing service

### [LabOne Q](https://www.zhinst.com/americas/en/quantum-computing-systems/labone-q)
SDK and front end for performing experiments on the Zurich Instruments QCCS together with third party control hardware.
[github](https://github.com/zhinst/laboneq).
* [Imports OQ3](https://docs.zhinst.com/labone_q_user_manual/core/reference/openqasm3.html)

### [Munich Quantum Toolkit (MQT)](https://mqt.readthedocs.org)
* [Exports circuits as OQ3](https://mqt.readthedocs.io/projects/core/en/latest/quickstart.html)
* [Imports OQ3](https://mqt.readthedocs.io/projects/core/en/latest/api/mqt/core/index.html#mqt.core.load)

### [Qiskit](https://github.com/qiskit)
Quantum software development kit (SDK)

### [Feynman](https://github.com/meamy/feynman)
Toolkit for quantum circuit analysis in the path integral model of quantum mechanics.
The OpenQASM 3 frontend is [here](https://github.com/meamy/feynman/tree/master/src/Feynman/Frontend/OpenQASM3)

### [AutoQASM](https://github.com/amazon-braket/autoqasm)
Although it is still a work in progress, the intent is that AutoQASM will support any
quantum programming paradigm which falls into the OpenQASM 3.0 language scope. AutoQASM
supports serializing quantum programs to OpenQASM, which allows the programs to interoperate
with any library or service that supports OpenQASM programs, such as Amazon Braket.

AutoQASM is pure Python but includes dependencies with statically compiled extensions.

### [OQpy](https://github.com/openqasm/oqpy)
The goal of oqpy ("ock-pie") is to make it easy to generate OpenQASM 3 + OpenPulse in Python.

Support is marked "complete" because OQpy depends on the reference parser.

### [MATLAB](https://www.mathworks.com/products/quantum-computing.html) Support Package for Quantum Computing

Here is a function for [exporting to OpenQASM 3](https://www.mathworks.com/help/matlab/ref/quantumcircuit.generateqasm.html).
We don't know if it can import OpenQASM 3

## OpenQASM 2 Implementations

# circuit construction

* [Cirq](https://github.com/quantumlib/cirq)
* [Pennylane](https://pennylane.ai/)
* [ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ)
* [XACC](https://github.com/eclipse-xacc/xacc)
* [OpenQASM](https://github.com/QuantumBFS/OpenQASM.jl)
* [quilc](https://github.com/quil-lang/quilc)
* [QuTiP](https://github.com/qutip/qutip-qip)

# compilation and synthesis

* [PyZX](https://github.com/zxcalc/pyzx)
* [Tweedledum](https://github.com/boschmitt/tweedledum) - No longer maintained
* [QasmTrans](https://github.com/pnnl/qasmtrans)

# simulation

* [Intel-QS](https://github.com/intel/intel-qs)
* [qsim](https://github.com/quantumlib/qsim)
* [qvm](https://github.com/quil-lang/qvm)

<!--  LocalWords:  Qiskit OpenQASM 3Aissue 3Aopen impl OSS openqasm3 WIP CLI Qu 3Aissue OQ3
<!--  LocalWords:  qasm3tools Braket braket qiskit SDK ANTLR Lexing antum lex 3Aopen LabOne
<!--  LocalWords:  sembly QASM AST BNF  labone MQT munich mqt feynman AutoQASM autoqasm
<!--  LocalWords:  OQpy oqpy QCCS github frontend ock OpenPulse  -->
