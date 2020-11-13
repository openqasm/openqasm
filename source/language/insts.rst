Built-in quantum instructions
=============================

This sections describes built-in non-unitary operations.

Initialization
--------------

The statement ``reset qubit|qubit[];`` resets a qubit or quantum register to the state
:math:`|0\rangle`. This corresponds to a partial trace over those qubits
(i.e. discarding them) before replacing them with
:math:`|0\rangle\langle 0|`. Reset is shown in
Fig. `[fig:prepare] <#fig:prepare>`__.

.. code-block:: c

   // Initialize and reset an array of 10 qubits
   qubit qubits[10];
   reset qubits;

Measurement
-----------

The statement ``bit|bit[] = measure qubit|qreg;`` measures the qubit(s) in the :math:`Z`-basis and assigns
the measurement outcome(s) to the target bit(s). For backwards
compatibility this is equivalent to ``measure qubit|qubit[] -> bit|bit[];`` which is also supported. Measurement
corresponds to a projection onto one of the eigenstates of :math:`Z`,
and qubit(s) are immediately available for further quantum computation.
Both arguments must be register-type, or both must be bit-type. If both
arguments are register-type and have the same size, the statement  ``b = measure a;``
broadcasts to ``b[j] = measure a[j];`` for each index ``j`` into register ``a``. Measurement is shown in
Fig. `[fig:measure] <#fig:measure>`__.

.. code-block:: c

   // Initialize, flip and measure an array of 10 qubits
   qubit qubits[10];
   bit[10] bits;
   x qubits;
   bits = measure qubits;
