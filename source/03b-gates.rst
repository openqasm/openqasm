.. role:: raw-latex(raw)
   :format: latex
..

Gates
=====

In OpenQASM we refer to unitary quantum instructions as gates.

Built-in gates
--------------

We define a mechanism for parameterizing unitary matrices to define new
quantum gates. The parameterization uses a built-in universal gate set
of single-qubit gates and a two-qubit entangling gate (CNOT)
:cite:`barenco95`. This basis is not an enforced compilation
target but a mechanism to define other gates. For many gates of
practical interest, there is a circuit representation with a polynomial
number of one- and two-qubit gates, giving a more compact representation
than requiring the programmer to express the full :math:`n \times n`
matrix. However, a general :math:`n`-qubit gate can be defined using an
exponential number of these gates.

We now describe this built-in gate set. There is one built-in two-qubit
gate

.. math::

   \mathrm{CX} := \left(\begin{array}{cccc}
   1 & 0 & 0 & 0 \\
   0 & 0 & 0 & 1 \\
   0 & 0 & 1 & 0 \\
   0 & 1 & 0 & 0 \end{array}\right)

called the controlled-NOT gate. The statement describes a CNOT gate that
flips the target qubit if and only if the control qubit is one. The
arguments cannot refer to the same qubit. If and are quantum registers
*with the same size*, the statement means apply for each index into
register . If instead, is a qubit and is a quantum register, the
statement means apply for each index into register . Finally, if is a
quantum register and is a qubit, the statement means apply for each
index into register .

.

All of the single-qubit unitary gates are also built-in and
parameterized as

.. math::

   U(\theta,\phi,\lambda) := R_z(\phi)R_y(\theta)R_z(\lambda) = \left(\begin{array}{cc}
       e^{-i(\phi+\lambda)/2}\cos(\theta/2) & -e^{-i(\phi-\lambda)/2}\sin(\theta/2) \\
   e^{i(\phi-\lambda)/2}\sin(\theta/2) & e^{i(\phi+\lambda)/2}\cos(\theta/2) \end{array}\right).

Here :math:`R_y(\theta)=\mathrm{exp}(-i\theta Y/2)` and
:math:`R_z(\phi)=\mathrm{exp}(-i\theta Z/2)`. When is a quantum
register, the statement means apply for each index into register . The
values :math:`\theta\in [0,2\pi)`, :math:`\phi\in [0,2\pi)`, and
:math:`\lambda\in
[0,2\pi)` in this base gate are angles whose precision is implementation
dependent [1]_. This specifies any element of :math:`SU(2)` up to a
global phase. For example, applies a Hadamard gate to qubit .

Finally, a built-in global phase gate allows the inclusion of arbitrary
global phase on circuits. adds a global phase of :math:`e^{i\gamma}` to
the circuit. e.g.:

.. _sec:macros:

Hierarchically defined unitary gates
------------------------------------

For new gates, we associate them with a corresponding unitary
transformation by a sequence of built-in gates. For example, a CPHASE
operation is shown schematically in Fig. `[fig:gate] <#fig:gate>`__. The
corresponding OpenQASM code is

.. code:: c

   gate cphase(angle[32]: θ) a, b
   {
     U(0, 0, θ / 2) a;
     CX a, b;
     U(0, 0, -θ / 2) b;
     CX a, b;
     U(0, 0, θ / 2) b;
   }
   cphase(π / 2) q[0], q[1];

Note that this definition does not imply that must be implemented with
this series of gates. Rather, we have specified the unitary
transformation that corresponds to the symbol . The particular
implementation is up to the compiler, given information about the basis
gate set supported by a particular target.

In general, new gates are defined by statements of the form

.. code:: c

   // comment
   gate name(params) qargs
   {
     body
   }

where the optional parameter list is a comma-separated list of variable
parameters, and the argument list is a comma-separated list of qubit
arguments. The parameters are identifiers with angular types and default
to 32-bits. The qubit arguments are identifiers. If there are no
variable parameters, the parentheses are optional. At least one qubit
argument is required. The arguments in cannot be indexed within the body
of the gate definition.

.. code:: c

   // this is ok:
   gate g a
   {
     U(0, 0, 0) a;
   }
   // this is invalid:
   gate g a
   {
     U(0, 0, 0) a[0];
   }

Only built-in gate statements, calls to previously defined gates, and
timing directives can appear in . For example, it is not valid to
declare a classical register in a gate body. The statements in the body
can only refer to the symbols given in the parameter or argument list,
and these symbols are scoped only to the subroutine body. An empty body
corresponds to the identity gate. Gates must be declared before use and
cannot call themselves. The statement applies the gate, and the variable
parameters are given as angular types or in-place constant parameter
expressions which are cast to angles. The gate can be applied to any
combination of qubits and quantum registers *of the same size* as shown
in the following example. The quantum circuit given by

.. code:: c

   gate g qb0, qb1, qb2, qb3
   {
     // body
   }
   qubit qr0[1];
   qubit qr1[2];
   qubit qr2[3];
   qubit qr3[2];
   g qr0[0], qr1, qr2[0], qr3; // ok
   g qr0[0], qr2, qr1[0], qr3; // error!

has a second-to-last line that means

We provide this so that user-defined gates can be applied in parallel
like the built-in gates.

Quantum gate modifiers
----------------------

A gate modifier is a keyword that applies to a gate. A modifier
:math:`m` transforms a gate :math:`U` to a new gate :math:`m(U)` acting
on the same or larger Hilbert space. We include modifiers in OpenQASM
both for programming convenience and compiler analysis.

The modifier replaces its gate argument :math:`U` with its inverse
:math:`U^\dagger`. The inverse of any gate can be defined recursively by
reversing the order of the gates in its definition and replacing each of
those with their inverse. The base case is given by replacing with and
by .

The modifier replaces its gate argument :math:`U` by its :math:`k`\ th
power :math:`U^k` for some positive integer :math:`k` (not necessarily
constant). Such a gate can be trivially defined as :math:`k` repetitions
of the original gate, although more efficient implementations may be
possible.

The modifier replaces its gate argument :math:`U` by a
controlled-:math:`U` gate. The new control qubit is prepended to the
argument list for the controlled-:math:`U` gate. The modified gate does
not use any additional scratch space. A target may or may not be able to
execute the gate without further compilation.

.. code:: c

   // Define a controlled Rz operation using the ctrl gatemodifier.
   gate crz(angle[20]: θ) q1, q2 {
       ctrl @ U(θ, 0, 0) q1, q2;
   }

.. [1]
   The intention is that the accuracy of these built-in gates is
   sufficient for the accuracy of the derived gates to not be limited by
   that of the built-in gates.
