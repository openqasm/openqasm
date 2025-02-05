.. role:: raw-latex(raw)
   :format: latex
..

Gates
=====

In OpenQASM, we refer to unitary quantum instructions as *gates*.

Applying gates
--------------

Every gate applies to a fixed number of qubits.
Assuming ``g0``, ``g1``, ``g2``, ... are gates defined on 0, 1, 2, ... qubits then they can be applied as

.. code-block::

   g0;
   g1 q1;
   g2 q1, q2;
   g3 q1, q2, q3;

Broadcasting
~~~~~~~~~~~~

If any arguments of a gate are quantum registers instead of qubits, then all such registers must be **of the same length** and
this syntax is a convenient shorthand for broadcasting over the qubits of the register. For example, the circuit

.. code-block::

   qubit[1] qr0;
   qubit[3] qr1;
   qubit[2] qr2;
   qubit[3] qr3;

   g4 qr0[0], qr1, qr2[0], qr3; // ok
   g4 qr0[0], qr2, qr1[0], qr3; // error! qr2 and qr3 differ in size

has a second-to-last line that is equivalent to

.. code-block:: text

   g4 qr0[0], qr1[0], qr2[0], qr3[0];
   g4 qr0[0], qr1[1], qr2[0], qr3[1];
   g4 qr0[0], qr1[2], qr2[0], qr3[2];

Use of this syntax constitutes a promise to the compiler that the expanded set of broadcasted gates
is mutually commuting and thus the compiler can take advantage of the opportunity to reorder the
gates freely for optimization purposes. In certain cases a compiler might be able to detect a
non-commutativity and raise a warning, but it is not required to do so in all cases. If the gates do
not commute and a specific order is required by the programmer, than a ``for`` loop may be used to
set that order.

Parameterized gates
~~~~~~~~~~~~~~~~~~~

As well as gates that each represent a fixed unitary, OpenQASM also supports gates that represent *families* of unitaries, parameterized
by angle variables. To distinguish the (optional) angle parameters from the (required) quantum arguments, if any angle parameters are
present they must appear before any quantum arguments, and be delimited by parentheses. For example

.. code-block:: text

   fsim(θ, ϕ) q[0], q[1];


Defining gates
--------------

There are 3 mechanisms to construct new gates:

1. A new named gate can be introduced by a  **hierarchical definition** from a sequence of existing gates;
2. Anonymous new gates may be defined by applying **gate modifiers** to existing gates;
3. The **built-in gates** comprising the one-qubit gate ``U(θ, ϕ, λ)`` and the zero-qubit gate ``gphase(γ)``.
   The definitions of these gates is part of the language specification.

The :ref:`built-in standard library of OpenQASM 3 <standard-library>` includes several gate definitions for convenience.

The next subsections go through these cases.

.. _gate-statement:

Hierarchical gates definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``gate`` statement associates an identifier with a corresponding unitary matrix (or parameterized family)
transformation by a sequence of other (built-in or previously-defined) gates.

For example the ``gate`` block

.. code-block::

   gate h q {
      U(π/2, 0, π) q;
      gphase -π/4;
   }

defines a new gate called ``h`` and associates it to the unitary matrix of the Hadamard gate. Once we have
defined ``h``, we can use it in later ``gate`` blocks.

The definition does not imply that ``h`` is
implemented by an instruction ``U(π/2, 0, π)`` on the quantum computer. The implementation is up to
the user and/or compiler, given information about the instructions supported by a particular target.
A minimal compiler implementation might simply expand ``gate`` definitions repeatedly until reaching
definitions for which :ref:`defcal blocks <pulse-gates>` are known. A more sophisticated implementation
might use the `gate` definitions of the gates with associated ``defcal`` blocks to
build a gate library, and use methods based on KAK decompositions to rewrite into this hardware library.

Controlled gates can be constructed by adding a control modifier to an existing gate. For example,
the NOT gate is given by ``X = U(π, 0, π)`` and the block

.. code-block:: c
   :force:

   gate CX a, b {
      ctrl @ U(π, 0, π) a, b;
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
   :force:

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

User-defined unitary gates
--------------------------

Programmers may define new gates which can be resolved to a sequence of built-in
gates, possibly through some program logic (such as `if` statements) or invocations
of other user-defined gates. For example, a CPHASE operation is shown schematically
in :numref:`fig_gate` corresponding OpenQASM code is

.. code-block::

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

New gates are defined from previously defined gates.
The gates are applied using the statement ``name(params) qargs;`` just like the built-in gates.
The parentheses are optional if there are no parameters. The gate :math:`{cphase}(\theta)`
corresponds to the unitary matrix :math:`{diag}(1,1,1,e^{i\theta})` up to a global phase.

Again, this definition does not imply that ``cphase`` must be implemented with
this particular series of gates. Rather, we have specified the unitary
transformation that corresponds to the symbol ``cphase``. The particular
implementation is up to the compiler, given information about the basis
gate set supported by a particular target.

In general, new gates may be declared in two different ways: a 'short'
declaration syntax, and a more versatile 'general' declaration syntax.
'Short' gate declarations are statements of the form

.. code-block::

   gate name(params) qargs
   {
     body
   }

where the optional parameter list ``params`` is a comma-separated list of variable
parameters, and the argument list ``qargs`` is a comma-separated list of qubit
arguments. The parameters are identifiers that behave as ``angle`` type with unknown
size. A compiler might recognize certain constructs and replace them with mathematically-
equivalent versions that would be true for arbitrary precision, or it might do calculations
at a fixed ``angle`` size, for example corresponding to the size of ``angle`` parameters in the corresponding
``defcal`` definitions.

The qubit arguments are identifiers. If there are no
variable parameters, the parentheses are optional. The arguments in ``qargs`` cannot be indexed within the body
of the gate definition.

.. code-block::

   // this is ok:
   gate g a
   {
     U(0, 0, 0) a;
   }
   // this is invalid:
   gate g a
   {
     U(0, 0, 0) a[0]; // not allowed to index an individual qubit operand
   }

'General' gate declarations have a similar structure, with minor differences:

.. code-block:: c

   // comment
   gate name(typedParams) : typedQargs
   {
     body
   }

The (again, optional) parameter list ``typedParams`` is a comma-separated list of variable
parameters, which in this case must be provided with explicit type specifications.
The list ``typedQargs`` is a comma-separated list of operands which are either individual
qubits, or registers/arrays of qubits, where each is again provided with an explicit type
specification. 
If there are no variable parameters, the parentheses are optional. At least
one quantum operand is required, and the quantum operands
must be immediately preceded by a ``:`` delimiter.
The arguments in ``typedQargs`` can be indexed within the body
of the gate definition if, and only if, it is a register or array of qubits.

.. code-block:: c

   // this is ok:
   gate g(angle alpha, int k): qubit[3] a
   {
     U(0, 0, alpha) a[0];
     U(0, 0, alpha/k) a[1];
     U(0, 0, alpha/(k**2)) a[2];
   }

   // this is also ok:
   gate qutritX : qubit[2] a {
     x a[1];
     cx a[1], a[0];
     cx a[0], a[1];
   }

   // this is invalid:
   gate g(angle alpha, int k): qubit a
   {
     U(0, 0, alpha) a[0]; // not allowed to index an individual qubit operand
     U(0, 0, alpha/k) a[1];
     U(0, 0, alpha/(k**2)) a[2];
   }


For either kind of gate declaration, the ``body`` may consist of the following:

 * declaration and initialisation of classical variables (but not re-assignment to them);

 * program logic (``if`` statements and ``for`` loops) with conditions/bounds involving constants,
   and simple expressions depending on the gate arguments and local identifiers / loop iterators;

 * and calls to built-in gates and previously defined gates.

For instance, the following defines a quantum Fourier transform on eight qubits:

.. code-block:: c
  gate QFT256 : qubit[8] q {
        uint n = 8;
        for uint j in [0 : n-1] {
          h q[j];
          for uint k in [j+1 : n-1]
           ctrl @ Rz(pi / 2**(k-j+1)) q[j], q[k];
          }
        for uint j in [0:n-1]
          if (j != n-1-j)
            swap q[j], q[n-1-j]
  }

Classical storage types and parameters in a ``gate`` body are treated as being immutable,
and cannot be assigned to more than once. (For loop induction variables are treated as being constant within
the scope of any single iteration of the ``for`` loop, and can only be modified by the logic of the loop
itself.) ``extern`` functions, ``reset`` operations, ``measure`` operations (or other operations with potentially
random outcomes), cannot be involved in the program logic of a ``gate`` body. This ensures that an invocation of
a user-defined ``gate``, corresponds to a definite finite sequence of built-in unitary gates.

An empty ``body`` corresponds to the identity gate.

Gates must be declared before use, and 
cannot call themselves. The statement ``name(params) qargs;`` applies the gate,
and the variable parameters ``params`` must have the appropriate type (or be expressions which can be implicitly 
cast to the appropriate type).

The quantum operands of a ``gate`` invocation must have the appropriate types to the declaration of the ``gate``.
There is one exception to this type-agreement condition: if a ``gate`` has one or more operands of type ``qubit``,
the gate may instead act on some qubit register(s) *of identical size* for one or all of those operands.
For example, using a 'short' ``gate`` declaration (all of whose operands are individual qubits):
the quantum circuit given by

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
   g qr0[0], qr2, qr1[0], qr3; // error! qr2 and qr3 differ in size

has a second-to-last line that means

.. code-block:: c

   // FIXME: insert translation of algorithmic block from TeX source.

   for j in [0:1] do
       g qr0[0],qr1[j],qr2[0],qr3[j];

We provide this so that user-defined gates can be applied in parallel
like the built-in gates. This functionality extends also to any ``gate`` declared with the
'general' form, so long as all operands which are given an explicit size in the declaration,
are provided with arguments of the corresponding type.

.. code-block:: c

   gate g : qubit qb0, qubit qb1, qubit[5] qreg
   {
     // body
   }
   qubit a[2];
   qubit b[2];
   qubit c[5];
   qubit d[10];
   g a, b, c; // ok: performs "g a[0], b[0], c; g a[1], b[1], c;"
   g a, b, d; // error! third operand expects a register of size 5, not 10


Quantum gate modifiers
~~~~~~~~~~~~~~~~~~~~~~

A gate modifier is a keyword that applies to a gate. A modifier
:math:`m` transforms a gate :math:`U` to a new gate :math:`m(U)` acting
on the same or larger Hilbert space. We include modifiers in OpenQASM
both for programming convenience and compiler analysis.

Control modifiers
+++++++++++++++++

The modifier ``ctrl @`` replaces its gate argument :math:`U` by a
controlled-:math:`U` gate. If the control bit is 0, nothing happens to the target bit.
If the control bit is 1, :math:`U` acts on the target bit. Mathematically, the controlled-:math:`U`
gate is defined as :math:`C_U = I \otimes U^c`, where :math:`c` is the integer value of the control
bit and :math:`C_U` is the controlled-:math:`U` gate. The new quantum argument is prepended to the
argument list for the controlled-:math:`U` gate. The quantum argument can be a register, and in this
case controlled gate broadcast over it (as for all gates). The modified
gate does not use any additional scratch space and may require compilation to be executed.

As a limiting case, the controlled *global* phase gate
``ctrl @ gphase(a)`` is equivalent to the single-qubit gate ``U(0, 0, a)``.

.. code-block::

   // Define a controlled Rz operation using the ctrl gate modifier.
   // q1 is control, q2 is target
   gate crz(θ) q1, q2 {
       ctrl @ rz(θ) q1, q2;
   }

The modifier ``negctrl @`` generates controlled gates with negative polarity, ie conditioned on a
controlled value of 0 rather than 1. Mathematically, the negative controlled-:math:`U` gate is
given by :math:`N_U = I \otimes U^{1-c}`, where :math:`c` is the integer value of the control bit
and :math:`N_U` is the negative controlled-:math:`U` gate.

.. code-block::

   // Define a negative controlled X operation using the negctrl gate modifier.
   // q1 is control, q2 is target
   gate neg_cx(θ) q1, q2 {
       negctrl @ x q1, q2;
   }

``ctrl`` and ``negctrl`` both accept an optional positive integer parameter ``n``, specifying the
number of control arguments (omission means ``n=1``). ``n`` must be a compile-time constant. For an ``N``
qubit operation,these operations are mathematically defined as

.. math::

   C^n_U = I_1 \otimes I_2 ... \otimes I_n \otimes U^{c_1*c_2*...*c_n}

   N^n_U = I_1 \otimes I_2 ... \otimes I_n \otimes U^{1 - c_1*c_2*...*c_n}

where :math:`c_1`, :math:`c_2`, ..., :math:`c_n` are the integer values of the control bits and
:math:`C^n_U` are the n-bit controlled-:math:`U` and n-bit negative controlled-:math:`U` gates,
respectively.

.. code-block::

   // A reversible boolean function
   // Demonstrates use of ``ctrl(n) @`` and ``negctrl(n) @``
   qubit[3] a;
   qubit[2] b;
   qubit f;
   reset f;
   ctrl(3) @ x a[1], a[0], a[2], f;
   negctrl(3) @ ctrl @ x a[0], b[1], a[2], b[0], f;
   negctrl @ ctrl(2) @ negctrl @ x a[0], b[0], a[2], a[1], f;
   negctrl(2) @ ctrl @ x b[1], a, b[0], f;

Inverse modifier
++++++++++++++++

The modifier ``inv @ U`` replaces its gate argument :math:`U` with its inverse
:math:`U^\dagger`. This can be computed from gate :math:`U` via the following rules

- The inverse of any gate :math:`U=U_m U_{m-1} ... U_1` can be defined recursively by reversing the
  order of the gates in its definition and replacing each of those with their inverse
  :math:`U^\dagger = U_1^\dagger U_2^\dagger ... U_m^\dagger`.

- The inverse of a controlled operation is defined by inverting the control unitary. That is,
  ``inv @ ctrl @ U = ctrl @ inv @ U``.

- The base case is given by replacing ``inv @ U(θ, ϕ, λ)`` by ``U(-θ, -λ, -ϕ)``
  and ``inv @ gphase(a)`` by ``gphase(-a)``.

.. code-block::

   // Define a negative z rotation and the inverse of a positive z rotation
   gate rzm(θ) q1 {
       inv @ rzp(θ) q1;
   }
   // Equivalently, this can be written as
   gate rzm(θ) q1 {
       rzp(-θ) q1;
   }

   // a coherently controlled version of the "qutritX" gate defined further above,
   // with a control register interpreted as an integer modulo 3
   gate qutritCX : qubit[2] c, qubit[2] t {
      ctrl @ qutritX c[0], t;
      ctrl @ inv @ qutritX c[1], t;
    }

Power modifier
++++++++++++++

The modifier ``pow(k) @`` replaces its gate argument :math:`U` by its :math:`k`\ th
power :math:`U^k` for some positive integer or floating point number :math:`k` (not necessarily
constant). In the case that :math:`k` is an integer, the gate can be implemented (albeit
inefficiently) by :math:`k` repetitions of :math:`U` for :math:`k > 0` and :math:`k`
repetitions of ``inv @ U`` for :math:`k < 0`.

.. code-block::

   // define x as the square of sqrt(x) ``sx`` gate
   gate x q1 {
       pow(2) @ sx q1;
   }

Built-in gates
~~~~~~~~~~~~~~

.. gate:: U(θ, ϕ, λ) a

   The built-in single-qubit gate :gate:`U` represents the unitary matrix

   .. math::

      U(\theta,\phi,\lambda) := \frac{1}{2}\left(\begin{array}{cc}
         1+e^{i\theta} & -ie^{i\lambda}(1-e^{i\theta}) \\
         ie^{i\phi}(1-e^{i\theta}) & e^{i(\phi+\lambda)}(1+e^{i\theta}) \end{array}\right).

   This definition is :math:`2\pi`-periodic in each of the parameters θ, ϕ, λ and
   specifies any element of :math:`U(2)` up to a
   global phase [#uphase]_ . For example ``U(π/2, 0, π) q[0];``, applies a Hadamard gate to qubit ``q[0]``
   (up to a non-standard global phase).

.. gate:: gphase(γ)

   The global phase gate.

   From a physical perspective, the unitaries :math:`e^{i\gamma}V` and :math:`V` are equivalent although they differ by a global
   phase :math:`e^{i\gamma}`. When we add a control to these gates, however, the global phase becomes a relative phase
   that is applied when the control qubit is one. A built-in global phase gate
   allows the inclusion of arbitrary global phases on circuits. The instruction ``gphase(γ);`` accumulates a global phase
   of :math:`e^{i\gamma}`.

   Just as every n-qubit gate can be thought of as generating a tensor product with the suitable
   identity matrix to cover all other qubits in the gate, subroutine, or global scope containing the
   instruction, similarly ``gphase`` behaves as a 0-qubit gate and when applied in a context with
   `m` qubits in scope, behaves as applying the unitary

   .. math::
      \operatorname{gphase}(\gamma) := e^{i\gamma} I_m,

   where :math:`I_m` denotes the identity matrix with size :math:`2^m`

   For example

   .. code-block::

      gate X q {
         U(π, 0, π) q;
         gphase -π/2;
      }

      gate CX c, t {
         ctrl @ X c, t;
      }

   defines ``CX`` as the standard CNOT gate.

Relation of the built-in gates to hardware-native gates
-------------------------------------------------------

For *non-parameterized gates*, the choice of :gate:`U` and :gate:`gphase` as the built-in gates, along with one
two-qubit entangling gate CNOT as defined gives a universal gate set that can represent general n-qubit
unitaries with an :math:`O(2^n)` size description :cite:`barenco95`. This basis is not an enforced compilation
target but a mechanism to define other gates. For many gates of
practical interest, there is a circuit representation with a polynomial
number of one- and two-qubit gates, giving a more compact representation
than requiring the programmer to express the full :math:`2^n \times 2^n`
matrix. However, a general :math:`n`-qubit gate can be defined using an
exponential number of these gates. Thus there is no particular privilege incurred by hardware implementations
that natively support the built-in gates.

For *parameterized gates*, the choice of built-in gates *does* constrain which hardware-native gates are well-
supported, because conversion between parameterized basis sets in general can be involved, requiring careful
selection of branch cuts and other logic that would not likely be feasible to specify as compact mathematical
expressions, nor to evaluate at runtime for cases where the parameters depend on quantum measurements.

For many current platforms the qubits are defined relative to a
rotating frame and the rotating wave approximation (RWA) holds. This is the domain covered by the OpenPulse
specification. For this case, the only supported form of run-time parameterization
will likely be via a :gate:`rz` implemented by specialized frame-tracking hardware.
This gate is covered by the built-in :gate:`U` as a special case ``U(0, 0, ϕ)``
However, if other forms of run-time parameterization become important, it may be necessary to revise OpenQASM,
to give meaning to those gates, for example by adding new basis gates or additional ``gate`` definition syntax.

.. [#uphase] This definition of ``U`` has a different global phase from previous versions of the OpenQASM spec.
   Unfortunately the original definitions were 4π rather than 2π periodic in the θ parameter. A gate
   ``U_old(0, ϕ, θ) q;`` under the previous definition corresponds to ``U(0, ϕ, θ) q; gphase(-0/2);`` with the present
   definition.
