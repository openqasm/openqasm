Built-in quantum instructions
=============================

This section describes built-in non-unitary operations.

Initialization
--------------

The statement ``reset qubit|qubit[];`` resets a qubit or quantum register to the state
:math:`|0\rangle`. This corresponds to a partial trace over those qubits
(i.e. discarding them) before replacing them with
:math:`|0\rangle\langle 0|`. Reset is shown in :numref:`fig_prepare`.

.. code-block:: c

   // Initialize and reset a register of 10 qubits
   qubit[10] qubits;
   reset qubits;


.. _fig_prepare:
.. multifigure::

   .. image:: ../qpics/c7.svg

   .. image:: ../qpics/c8.svg

   .. image:: ../qpics/c9.svg

   The ``reset`` statement prepares a qubit or quantum register in the state :math:`|0\rangle`.


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
:numref:`fig_measure`.

.. code-block:: c

   // Initialize, flip and measure a register of 10 qubits
   qubit[10] qubits;
   bit[10] bits;
   x qubits;
   bits = measure qubits;

.. _fig_measure:
.. multifigure::
   :rowitems: 3

   .. image:: ../qpics/c1.svg

   .. image:: ../qpics/c2.svg

   .. image:: ../qpics/c3.svg

   .. image:: ../qpics/c4.svg

   .. image:: ../qpics/c5.svg

   .. image:: ../qpics/c6.svg

   The ``measure`` statement projectively measures a qubit or each qubit of a quantum
   register. The measurement projects onto the :math:`Z`-basis and leaves qubits available for further
   operations. The top row of circuits depicts single-qubit measurement using the statement
   ``c[0] = measure q[0];`` while the bottom depicts measurement of an entire register using the
   statement ``c = measure q;``. The center circuit of the top row depicts measurement as the
   final operation on ``q[0]``.
