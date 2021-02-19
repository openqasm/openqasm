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
than requiring the programmer to express the full :math:`2^n \times 2^n`
matrix. However, a general :math:`n`-qubit gate can be defined using an
exponential number of these gates.

We now describe this built-in gate set.
All of the single-qubit unitary gates are built-in and
parameterized as

.. math::

   U(\theta,\phi,\lambda) := \left(\begin{array}{cc}
       \cos(\theta/2) & -e^{i\lambda}\sin(\theta/2) \\
   e^{i\phi}\sin(\theta/2) & e^{i(\phi+\lambda)}\cos(\theta/2) \end{array}\right).

When ``a`` is a quantum
register, the statement ``U(θ, ϕ, λ) a;`` means apply ``U(θ, ϕ, λ) a[j];`` for each index ``j`` into register ``a``. The
values :math:`\theta\in [0,2\pi)`, :math:`\phi\in [0,2\pi)`, and
:math:`\lambda\in
[0,2\pi)` in this base gate are angles whose precision is implementation
dependent [1]_. This specifies any element of :math:`U(2)` up to a
global phase. For example ``U(π/2, 0, π) q[0];``, applies a Hadamard gate to qubit ``q[0]``.
P

New gates are associated to a unitary transformation by defining them as a sequence of built-in or
previously defined gates. For example the ``gate`` block

.. code-block:: c

   gate h q {
      U(π/2, 0, π) q;
   }

defines a new gate called ``h`` and associates it to the unitary matrix of the Hadamard gate. Once we have
defined ``h``, we can use it in later ``gate`` blocks. The definition does not imply that ``h`` is
implemented by an instruction ``U(π/2, 0, π)`` on the quantum computer. The implementation is up to
the user and/or compiler, given information about the instructions supported by a particular target.

Controlled gates can be constructed by adding a control modifier to an existing gate. For example,
the NOT gate is given by ``X = U(π, 0, π)`` and the block

.. code-block:: c

   gate CX c, t {
      ctrl @ U(π, 0, π) c, t;
   }

   CX q[1], q[0];

defines the gate

.. math::

   \mathrm{CX} := I\times X = \left(\begin{array}{cccc}
   1 & 0 & 0 & 0 \\
   0 & 1 & 0 & 0 \\
   0 & 0 & 0 & 1 \\
   0 & 0 & 1 & 0 \end{array}\right)

that applies a bit-flip ``X`` to ``q[0]`` if ``q[1]`` is one and otherwise applies the identity gate.
The control modifier is described in more detail later.

Throughout the document we use a tensor order with higher index qubits on the left. In this tensor order,
``CX q[0], q[1];`` is represented by the matrix

.. math::

   \left(\begin{array}{cccc}
   1 & 0 & 0 & 0 \\
   0 & 0 & 0 & 1 \\
   0 & 0 & 1 & 0 \\
   0 & 1 & 0 & 0 \end{array}\right)

Given the gate definition we have already given, the statement ``CX a, b;`` describes a CNOT gate that
flips the target qubit ``b`` if and only if the control qubit ``a`` is one. The
arguments cannot refer to the same qubit. For convenience, gates automatically broadcast over registers. If ``a`` and ``b`` are quantum registers
*with the same size*, the statement ``CX a, b;`` means apply ``CX a[j], b[j];`` for each index ``j`` into
register ``a``. If instead ``a`` is a qubit and ``b`` is a quantum register, the
statement means apply ``CX a, b[j]`` for each index ``j`` into register ``b``. Finally, if ``a`` is a
quantum register and ``b`` is a qubit, the statement means apply ``CX a[j], b;`` for each
index ``j`` into register ``a``.

.. _fig_cnot-dist:
.. multifigure::
   :rowitems: 2

   .. image:: ../qpics/cnotqq.svg

   .. image:: ../qpics/cnotrr.svg

   .. image:: ../qpics/cnotqr.svg

   .. image:: ../qpics/cnotrq.svg

   The two-qubit controlled-NOT gate is contructed from built-in single-qubit gates and the control modifier.
   If ``a`` and ``b`` are qubits, the statement ``CX a,b;`` applies a
   controlled-NOT (CNOT) gate that flips the target qubit ``b`` iff the control qubit ``a``
   is one. If ``a`` and ``b`` are quantum registers, the statement applies CNOT gates between
   corresponding qubits of each register. There is a similar meaning when ``a`` is a qubit and
   ``b`` is a quantum register and vice versa.

.. _fig_u-dist:
.. multifigure::

   .. image:: ../qpics/uq.svg

   .. image:: ../qpics/ur.svg

   The single-qubit unitary gates are built-in. These gates are parameterized by three real
   parameters :math:`\theta`, :math:`\phi`, and :math:`\lambda$`. If the argument ``q`` is a quantum register, the
   statement applies ``size(q)`` gates in parallel to the qubits of the
   register.

From a physical perspective, the gates :math:`e^{i\gamma}U` and :math:`U` are equivalent although they differ by a global
phase :math:`e^{i\gamma}`. When we add a control to these gates, however, the global phase becomes a relative phase
that is applied when the control qubit is one. To capture the programmer's intent, a built-in global phase gate
allows the inclusion of arbitrary global phases on circuits. The instruction ``gphase(γ);`` adds a global phase
of :math:`e^{i\gamma}` to the scope containing the instruction. For example

.. code-block:: c

  gate rz(tau) q {
    gphase(-tau/2);
    U(0, 0, tau) q;
  }
  ctrl @ rz(π/2) q[1], q[0];

constructs the gate

.. math::

  R_z(\tau) = \exp(-i\tau Z/2) = \left(\begin{array}{cc}
  e^{-i\tau/2} & 0 \\
  0 & e^{i\tau/2} \end{array}\right) = e^{-i\tau/2}\left(\begin{array}{cc}
  1 & 0 \\
  0 & e^{i\tau} \end{array}\right)

and applies the controlled gate

.. math::

  I\otimes R_z(\pi/2) = \left(\begin{array}{cccc}
  1 & 0 & 0 & 0 \\
  0 & 1 & 0 & 0 \\
  0 & 0 & e^{-i\tau/2} & 0 \\
  0 & 0 & 0 & e^{i\tau/2} \end{array}\right).


.. _sec:macros:

Hierarchically defined unitary gates
------------------------------------

For new gates, we associate them with a corresponding unitary
transformation by a sequence of built-in gates. For example, a CPHASE
operation is shown schematically in :numref:`fig_gate`
corresponding OpenQASM code is

.. code-block:: c

   gate cphase(θ) a, b
   {
     U(0, 0, θ / 2) a;
     CX a, b;
     U(0, 0, -θ / 2) b;
     CX a, b;
     U(0, 0, θ / 2) b;
   }
   cphase(π / 2) q[0], q[1];

.. _fig_gate:
.. figure:: ../qpics/gate.svg

   New gates are defined from previously defined gates. The gates are applied using the statement
   ``name(params) qargs;`` just like the built-in gates. The parentheses are optional if there
   are no parameters. The gate :math:`{cphase}(\theta)` corresponds to the unitary matrix
   :math:`{diag}(1,1,1,e^{i\theta})` up to a global phase.

Note that this definition does not imply that ``cphase`` must be implemented with
this series of gates. Rather, we have specified the unitary
transformation that corresponds to the symbol ``cphase``. The particular
implementation is up to the compiler, given information about the basis
gate set supported by a particular target.

In general, new gates are defined by statements of the form

.. code-block:: c

   // comment
   gate name(params) qargs
   {
     body
   }

where the optional parameter list ``params`` is a comma-separated list of variable
parameters, and the argument list ``qargs`` is a comma-separated list of qubit
arguments. The parameters are identifiers with arbitrary-precision numeric types.
The qubit arguments are identifiers. If there are no
variable parameters, the parentheses are optional. At least one qubit
argument is required. The arguments in ``qargs`` cannot be indexed within the body
of the gate definition.

.. code-block:: c

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
timing directives can appear in ``body``. For example, it is not valid to
declare a classical register in a gate body. Looping constructs over these quantum
statements are valid. The statements in the body
can only refer to the symbols given in the parameter or argument list,
and these symbols are scoped only to the subroutine body. An empty body
corresponds to the identity gate. Gates must be declared before use and
cannot call themselves. The statement ``name(params) qargs;`` applies the gate, and the variable
parameters ``params`` can have any numeric type. The gate can be applied to any
combination of qubits and quantum registers *of the same size* as shown
in the following example. The quantum circuit given by

.. code-block:: c

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

.. code-block:: c

   // FIXME: insert translation of algorithmic block from TeX source.

We provide this so that user-defined gates can be applied in parallel
like the built-in gates.

Quantum gate modifiers
----------------------

A gate modifier is a keyword that applies to a gate. A modifier
:math:`m` transforms a gate :math:`U` to a new gate :math:`m(U)` acting
on the same or larger Hilbert space. We include modifiers in OpenQASM
both for programming convenience and compiler analysis.

The modifier ``inv @`` replaces its gate argument :math:`U` with its inverse
:math:`U^\dagger`. The inverse of any gate can be defined recursively by
reversing the order of the gates in its definition and replacing each of
those with their inverse. The base case is given by replacing ``inv @ CX`` with ``CX`` and
``inv @ U(θ, ϕ, λ)`` by ``U(-θ, -λ, -ϕ)``.

.. code-block:: c

   gate rzm(theta) q1 {
       inv @ rzp(theta) q1;
   }

The modifier ``pow[k] @`` replaces its gate argument :math:`U` by its :math:`k`\ th
power :math:`U^k` for some positive integer :math:`k` (not necessarily
constant). Such a gate can be trivially defined as :math:`k` repetitions
of the original gate, although more efficient implementations may be
possible.

.. code-block:: c

   // define x as sqrt(x)
   gate x q1 {
       pow[2] @ sx q1;
   }

The modifier ``ctrl @`` replaces its gate argument :math:`U` by a
controlled-:math:`U` gate. The new control qubit is prepended to the
argument list for the controlled-:math:`U` gate. The modified gate does
not use any additional scratch space. A target may or may not be able to
execute the gate without further compilation.

.. code-block:: c

   // Define a controlled Rz operation using the ctrl gate modifier.
   gate crz(θ) q1, q2 {
       ctrl @ U(θ, 0, 0) q1, q2;
   }

.. [1]
   The intention is that the accuracy of these built-in gates is
   sufficient for the accuracy of the derived gates to not be limited by
   that of the built-in gates.
