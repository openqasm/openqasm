.. _standard-library:

Standard library
================

The standard library for OpenQASM 3 consists of a single include file, called ``stdgates.inc``.
This file can be included in an OpenQASM 3 program with the statement

.. code-block::

   include "stdgates.inc";

Versioning
----------

The standard library is versioned directly with the language itself.  This documentation will note
the version that any given gate in the standard library became available, and, if applicable, the
version it was removed in.

Notes for implementations
-------------------------

An implementation is not required to make the standard library available in situations where the
OpenQASM 3 program is being interpreted in terms of the instruction set architecture of a particular
QPU.  The rest of this section concerns only situations where the library is considered available.

Implementations should consider the ``stdgates.inc`` file to be locatable, regardless of any other
settings that they might apply around include search paths.

Upon interpreting an ``include "stdgates.inc";`` statement, implementations should make available
exactly the set of gates defined in the standard library for the language version that matches the
:ref:`version-string statement <version-string>`, if present.  If the version statement is not
present, the implementation should make available the gates from the language version it is parsing
the rest of the program under.

Implementations must not define gates that are not present in the chosen OpenQASM 3 version, where
doing so could cause a user program to be ill formed (for example due to a user attempting to define
their own gate with a clashing name).

An implementation is not required to supply a literal ``stdgates.inc`` file to the user.

An implementation must make all the gates available as if they were defined with ``gate``
statements with contents that match the mathematical descriptions given here.
In addition, it is permissible for implementations to also provide implementations of the gates
equivalent to a series of ``defcal`` statements for all qubits used in the program.


API Documentation
-----------------

The content of the standard library is documented below, including the OpenQASM version that each
gate was introduced in.

Single-qubit gates
..................

.. gate:: p(λ) a

   The phase gate.  Defined by the mapping :math:`\lvert0\rangle \to \lvert0\rangle` and
   :math:`\lvert1\rangle \to e^{i\lambda}\lvert1\rangle`.

   Equivalent to ``ctrl @ gphase(λ) a`` (see :gate:`gphase`).

   .. seealso::

      :gate:`rz`
         The same operation up to a global phase.

      :gate:`phase`
         An alternative name for backwards compatibility with OpenQASM 2.

   .. versionadded:: 3.0

.. gate:: x a

   The Pauli X gate.  Defined by the mapping :math:`\lvert0\rangle \leftrightarrow \lvert1\rangle`.

   .. versionadded:: 3.0

.. gate:: y a

   The Pauli Y gate.  Defined by the mapping :math:`\lvert0\rangle \to i\lvert1\rangle` and
   :math:`\lvert1\rangle \to -i\lvert0\rangle`.

   .. versionadded:: 3.0

.. gate:: z a

   The Pauli Z gate.  Defined by the mapping :math:`\lvert0\rangle \to \lvert0\rangle` and
   :math:`\lvert1\rangle \to \lvert1\rangle`.

   Equivalent to ``p(pi) a``.

   .. versionadded:: 3.0

.. gate:: h a

   The Hadamard gate.  Defined by the mapping
   :math:`\lvert0\rangle \to \bigl(\lvert0\rangle + \lvert1\rangle\bigr)/\sqrt2` and
   :math:`\lvert1\rangle \to \bigl(\lvert0\rangle - \lvert1\rangle\bigr)/\sqrt2`.

   .. versionadded:: 3.0

.. gate:: s a

   The :math:`\sqrt Z` gate (see :gate:`z`).  The square root is chosen conventionally, that is
   the gate is equivalent to :math:`P(\pi/2)`, in terms of :gate:`p`.

   .. versionadded:: 3.0

.. gate:: sdg a

   Adjoint of :gate:`s`.  Equivalent to :math:`P(-\pi/2)`, in terms of :gate:`p`.

   .. versionadded:: 3.0

.. gate:: t

   The :math:`\sqrt S` gate (see :gate:`s`).  The square root is chosen conventionally, that is
   the gate is equivalent to :math:`P(\pi/4)`, in terms of :gate:`p`.

   .. versionadded:: 3.0

.. gate:: tdg a

   Adjoint of :gate:`t`.  Equivalent to :math:`P(-\pi/4)`, in terms of :gate:`p`.

   .. versionadded:: 3.0

.. gate:: sx a

   The :math:`\sqrt X` gate (see :gate:`x`).

   Explicitly, this has the action
   :math:`\lvert0\rangle \to \Bigl((1 + i)\lvert0\rangle + (1 - i)\lvert1\rangle\Bigr)/2` and
   :math:`\lvert1\rangle \to \Bigl((1 - i)\lvert0\rangle + (1 + i)\lvert1\rangle\Bigr)/2`.

   .. versionadded:: 3.0

.. gate:: rx(θ) a

   Rotation about the :math:`X` axis: :math:`\exp(-i\theta X)`.

   .. versionadded:: 3.0

.. gate:: ry(θ) a

   Rotation about the :math:`Y` axis: :math:`\exp(-i\theta Y)`.

   .. versionadded:: 3.0

.. gate:: rz(θ) a

   Rotation about the :math:`Z` axis: :math:`\exp(-i\theta Z)`.  Note that this differs from
   :gate:`p` by a global phase of half the rotation angle.

   .. seealso::
      :gate:`p`
         The same gate but with a different global-phase convention.

   .. versionadded:: 3.0


Two-qubit gates
...............

All of the controlled gates defined in the standard library follow the same conventions of the
``ctrl`` modifier.
Explicitly, the first qubit is the control and the second the target.
The controlled gates are equivalent to applying the ``ctrl`` modifier to the relevant single-qubit
gate.

.. gate:: cx a, b

   Controlled :math:`X` gate (see :gate:`x`).

   .. seealso::
      :gate:`CX`
         An all-caps alias for backwards compatibility with OpenQASM 2.0.

   .. versionadded:: 3.0

.. gate:: cy a, b

   Controlled :math:`Y` gate (see :gate:`y`).

   .. versionadded:: 3.0

.. gate:: cz a, b

   Controlled :math:`Z` gate (see :gate:`z`).

   .. versionadded:: 3.0

.. gate:: cp(λ) a, b

   Controlled :math:`P` gate with an angle :math:`\lambda` (see :gate:`p`).

   The difference in global phase between :gate:`p` and :gate:`rz` makes :gate:`cp` and :gate:`crz`
   distinct in their action.

   .. versionadded:: 3.0

.. gate:: crx(λ) a, b

   Controlled :math:`X` rotation with an angle :math:`\theta` (see :gate:`rx`).

   .. versionadded:: 3.0

.. gate:: cry(λ) a, b

   Controlled :math:`Y` rotation with an angle :math:`\theta` (see :gate:`ry`).

   .. versionadded:: 3.0

.. gate:: crz(λ) a, b

   Controlled :math:`Z` rotation with an angle :math:`\theta` (see :gate:`rz`).

   The difference in global phase between :gate:`p` and :gate:`rz` makes :gate:`cp` and :gate:`crz`
   distinct in their action.

   .. versionadded:: 3.0

.. gate:: ch a, b

   Controlled Hadamard gate (see :gate:`h`).

   .. versionadded:: 3.0

.. gate:: cu(θ, φ, λ, γ) a, b

   A four-parameter version the controlled-:math:`U` gate.  In contrast to other standard-library
   controll gates, this gate as an additional parameter over its base :gate:`u` gate.
   The fourth parameter, :math:`\gamma`, controls the relative phase of the controlled operation.

   Explicitly, the action in terms of :math:`U` is

   .. math::

      CU(\theta, \phi, \lambda, \gamma) =
         {\lvert0\rangle\langle0\rvert}_a \otimes \mathbb{I}_b
         + e^{i\gamma} {\lvert1\rangle\langle1\rvert}_a \otimes U(\theta, \phi, \lambda)_b

   where subscripts denote the qubit being acted upon.

   .. versionadded:: 3.0

.. gate:: swap a, b

   Swap the states of qubits ``a`` and ``b``.

   .. versionadded:: 3.0


Three-qubit gates
.................

.. gate:: ccx a, b, c

   The double-controlled :math:`X` gate (see :gate:`x` and :gate:`cx`).  Also known as the Toffoli
   gate.  The first two qubits are the controls and the last is the target.

   .. versionadded:: 3.0

.. gate:: cswap a, b, c

   The controlled swap (see :gate:`swap`).  The first qubit is the control, and the last two are the
   swap targets.

   .. versionadded:: 3.0


OpenQASM 2.0 compatibility
..........................

Both OpenQASM 2.0 and OpenQASM 3 define the builtin :gate:`U` gate (though note that OpenQASM 3
differs from OpenQASM 2 by a phase; :gate:`u3` is identical to the ``U`` of OpenQASM 2).  In
addition, OpenQASM 2.0 had a :gate:`CX` builtin, which in OpenQASM 3.0 is provided as an alias
convenience only by ``stdgates.inc``, since the ``ctrl`` modifier made it unnecessary as a builtin.

.. gate:: CX a, b

   A convenience alias for :gate:`cx`.

   .. versionadded:: 2.0

   .. versionchanged:: 3.0

      In OpenQASM 2.0, :gate:`CX` was a built-in gate, so was automatically defined.
      From OpenQASM 3.0 onwards, it is part of the :ref:`standard library <standard-library>`.

While OpenQASM 2.0 had no formal standard library, the content of the original IBM Quantum
Experience include file ``qelib1.inc`` was described in the paper, and this became an informal, *de
facto* standard library of the language.

Most of the standard gates in it are described above.  In addition, ``qelib1.inc`` included some
aliases for other gates, and :math:`ZYZ` Euler-rotation gates :gate:`u1`, :gate:`u2` and :gate:`u3`.
These are reproduced in ``stdgates.inc`` to ease the transition.

.. gate:: phase(λ) a

   Alias for :gate:`p`.

   .. versionadded:: 3.0

.. gate:: cphase(λ) a, b

   Alias for :gate:`cp`.

   .. versionadded:: 3.0

.. gate:: id a

   Single-qubit identity gate.  This gate is an explicit no-op in idealized mathematical terms, but
   an implementation is free to assign a duration to it (as with any gate), if desired.

   .. versionadded:: 3.0

.. gate:: u1(λ) a

   Single-argument form of the OpenQASM 2.0 :gate:`U` gate.  Equivalent to :gate:`p`.

   .. versionadded:: 3.0

.. gate:: u2(φ, λ) a

   Two-argument form of the OpenQASM 2.0 :gate:`U` gate.  Equivalent to ``u3(π/2, φ, λ)`` (see
   :gate:`u3`).

   .. versionadded:: 3.0

.. gate:: u3(θ, φ, λ) a

   Three-argument form of the OpenQASM 2.0 :gate:`U` gate.  Note that this differs from the OpenQASM 3
   definition of :gate:`U` by an additional factor of :math:`e^{-i(\theta + \phi + \lambda)/2)}`.

   .. versionadded:: 3.0
