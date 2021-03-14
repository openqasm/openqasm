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
  classical data. A *kernel* mechanism allows opaque references to generic classical
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


Contributors
------------

The following individuals contributed to the OpenQASM version 3.0 specification:

Hossein Ajallooiean[1]_, Thomas Alexander[2]_, Lev Bishop[2]_, Yudong Cao[3]_, Andrew Cross[2]_,
Niel de Beaudrap[4]_, Jay Gambetta[2]_, Ali Javadi-Abhari[2]_, Blake Johnson[2]_,
Moritz Kirste[1]_, Colm Ryan[5]_, John Smolin[2]_, Ntwali Bashige Toussaint[3]_

.. [1] Zurich Instruments
.. [2] IBM Quantum
.. [3] Zapata Computing
.. [4] University of Oxford
.. [5] AWS Center for Quantum Computing
