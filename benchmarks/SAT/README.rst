===================
SAT Program Dataset
===================

This is a set of SAT (satisfiability) problem instances of `DIMACS <http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html>`_  CNF (conjunctive normal form) format with corresponding quantum Grover's search programs. Please note that all SAT instances are randomly generated, with no guarantee of having satisfying solutions.

******
Naming
******

The SAT problem instances are located inside the ``./cnf`` directory, each with a filename of the format

``qubits=<MAX_NUM_QUBITS>_vars=<NUM_VARIABLES>_clauses=<NUM_CLAUSES>_clauselen=<MAX_NUM_VARIABLES_PER_CLAUSE>_<CONTENT_MD5_HASH>.cnf``

whose corresponding Grover's search OpenQASM program file is located in the ``./qasm`` directory, with the same filename except for the ``.qasm`` extension.

********
Examples
********

SAT Instance
============

Let's look at the particular SAT problem instance

``./cnf/qubits=6_vars=2_clauses=3_clauselen=2_5f1e30f529c00f89a454baceb259298e.cnf``

which has the formulation:

::

 p cnf 2 3
 -1 -2 0
 -1 2 0
 2 0

which essentially says: This is a problem in cnf format, with 2 variables and 3 clauses, having the form

::

 (-v1 + -v2)*(-v1 + v2)*(v2)

where ``*``, ``+``, ``-`` can be seen as logical ``AND``, ``OR``, ``NOT``, respectively, where ``0`` marks clause endings.

It can be easily seen that ``v1 = F, v2 = T`` is the unique satisfying solution.

OpenQASM Program
================

The corresponding OpenQASM program can be found in file

``./qasm/qubits=6_vars=2_clauses=3_clauselen=2_5f1e30f529c00f89a454baceb259298e.qasm``

with the content

::

 // Quantum code for the specified SAT problem.

 include "qelib1.inc";

 // Declare all needed (qu)bits
 qreg v[3];
 qreg c[3];
 qreg a[1];
 creg m[2];

 // Prepare uniform superposition
 h v[1];
 h v[2];

 // Marking with oracle evaluation
 x c[0];
 x c[1];
 x c[2];
 ccx v[1], v[2], c[0];
 x v[2];
 ccx v[1], v[2], c[1];
 cx v[2], c[2];
 x v[2];
 ccx c[0], c[1], a[0];
 ccx c[2], a[0], v[0];
 ccx c[0], c[1], a[0];
 x v[2];
 cx v[2], c[2];
 ccx v[1], v[2], c[1];
 x v[2];
 ccx v[1], v[2], c[0];

 // Amplitude amplification
 h v[1];
 h v[2];
 x v[0];
 x v[1];
 x v[2];
 h v[0];
 ccx v[1], v[2], v[0];
 h v[0];
 x v[0];
 x v[1];
 x v[2];
 h v[0];
 h v[1];
 h v[2];

 // Measurements
 measure v[1] -> m[0];
 measure v[2] -> m[1];

A sample run of this program using IBM Q experience (with 128 shots) yields the outcome

::

 'counts': {'10': 108, '11': 5, '00': 8, '01': 7}

which clearly indicates that the measurement ``10`` dominates, coinciding with our expected SAT solution of ``v1 = F`` and ``v2 = T``.
