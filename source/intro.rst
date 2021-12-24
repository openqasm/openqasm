Introduction
============

OpenQASM is an imperative programming language designed for near-term
quantum computing algorithms and applications. Quantum
programs are described using the measurement-based quantum circuit model
with support for classical feed-forward flow control based on measurement
outcomes.

OpenQASM presents a parameterized set of physical logic gates and concurrent
real-time classical computations. Its main goal is to serve as an intermediate
representation for higher-level compilers to communicate with quantum hardware.
Allowances have been made for human usability. In particular, the language admits
different representations of the same program as it is transformed from a high-level
description to a pulse representation.

This document is draft version 3.0 of the OpenQASM specification. The Qiskit development team is
soliciting feedback on this draft for consideration prior to finalizing version 3.0.


Design Goals
------------

Version 3.0 of the OpenQASM specification aims to extend OpenQASM to include:

* **A broader family of computation with classical logic**. We introduce classical control flow,
  instructions, and data types to define circuits that include real-time computations on
  classical data. A *extern* mechanism allows opaque references to generic classical
  computations acting upon run-time data.

* **Explicit timing**. We introduce a flexible mechanism to describe *design intent* of
  instruction scheduling while remaining independent of specific durations determined by gate
  calibrations. This enables, for example, dynamical decoupling while retaining a gate-level
  description of a circuit.

* **Embedded pulse-level definitions**. An extensible mechanism to attach low-level definitions to
  gates. This is particularly relevant to calibration tasks which optimize pulse parameters using
  error amplification sequences most easily described at the gate level.


Scope
-----

This document aims to define the OpenQASM language itself, but it does not attempt to fully explain
the motivation for various design choices. A forthcoming paper will provide this background. This
document also does not seek to define the execution environment that accepts OpenQASM as an input.
For the previous versions of OpenQASM please read arXiv:1707.03429_.

.. _arXiv:1707.03429: https://arxiv.org/abs/1707.03429

Implementation Details
----------------------

OpenQASM 3 is a large expansion over the previous OpenQASM 2 specification.
Many new features for classical control flow and computation are added to make writing quantum algorithms easier, and to describe classical data processing that forms part of these algorithms.
The language, however, is not designed to be used for general-purpose classical computation, and in the near term, any hardware that executes an OpenQASM 3 program is unlikely to support the full set of data manipulations the language can describe.

Hardware implementations of OpenQASM 3 are permitted to restrict their runtime processing to only the set of operations that they can perform efficiently and in real time.
This set of operations will differ between implementations; you should consult your hardware vendor for which language features you can expect to be possible at runtime.
Implementations are likely to become more powerful over time, as the requirements for quantum control become less onerous to achieve.

It is expected that *compilers* for OpenQASM 3 will support all of the classical operations specified in this document for values that can be reasonably inferred to be compile-time constants, and will perform these operations at compile time.
At a minimum, "reasonably inferred" means values declared ``const``, and literals.
For example, this means that the "scientific-calculator functions" such as ``sin``, ``exp``, and so on will always work on expressions involving only literals and values declared ``const`` of compatible types, and the compiler will completely fold such expressions into a single constant.
Whether such operations can occur on run-time values is implementation-specific.
This extends further, even to which types may be declared and used.
An implementation of OpenQASM 3 is permitted to reject programs that use, for example, ``int[5]`` or ``float[16]`` declarations, if the hardware has no facilities to support them.
Similarly, even if a hardware implementation accepts values declared ``complex[float[64]]``, it is not required to accept programs that use the infix ``**`` power operator on them at runtime, but a compiler is required to evaluate such operator expressions if the operands are compile-time known.

Hardware implementations that support a particular feature *must* follow the rules for it given in this specification, unless such a feature is specifically stated to be "implementation-defined".
If they cannot, then they *must not* accept programs that use that feature.
The user can therefore expect that if an OpenQASM 3 program accepted by two implementations, both will perform the same behaviour except in cases this document explicitly allows it to differ.


Contributors
------------

The following individuals contributed to the OpenQASM version 3.0 specification:

Hossein Ajallooiean [1]_,
Thomas Alexander [2]_,
Lev Bishop [2]_,
Yudong Cao [3]_,
Andrew Cross [2]_,
Niel de Beaudrap [4]_,
Jay Gambetta [2]_,
Ali Javadi-Abhari [2]_,
Blake Johnson [2]_,
Moritz Kirste [1]_,
Colm Ryan [5]_,
John Smolin [2]_,
Ntwali Bashige Toussaint [3]_

.. [1] Zurich Instruments
.. [2] IBM Quantum
.. [3] Zapata Computing
.. [4] University of Oxford
.. [5] AWS Center for Quantum Computing
