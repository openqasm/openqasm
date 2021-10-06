Subroutines
===========

Subroutines are declared using the statement ``def name(parameters) -> output_type { body }``.
Zero or more quantum bits
and classical values are passed to the subroutine by reference or name in ``qargs``.
Classical types are passed by value in ``parameters``.
The subroutines return up to one value of classical type, signified by the
``return`` keyword. If there is no return type, the empty ``return``
keyword may be used to immediately exit from the subroutine. All arguments are declared together
with their type, for example ``qubit ancilla`` would define a quantum bit argument named ``ancilla``.
Qubit declarations are not allowed within subroutines as they are global. A subroutine
is invoked with the syntax ``name(parameters)`` and may be assigned to an ``output`` as
needed via an assignment operator (``=``, ``+=``, etc).

Using subroutines, we can define an X-basis measurement with the program
``def xmeasure(qubit q) -> bit { h q; return measure q; }``.
We can also define more general classes of single-qubit measurements
as
``def pmeasure(angle[32] theta, qubit q) -> bit { rz(theta) q; h q; return measure q; }``.
The type declarations are necessary if we want to mix qubit and
register arguments. For example, we might define a parity check
subroutine that takes qubits and registers

.. code-block:: c

   def xcheck(qubit[4] d, qubit a) -> bit {
     reset a;
     for i in [0: 3] cx d[i], a;
     return measure a;
   }

Naturally we can also use subroutines to define purely classical
operations, such as methods we can implement using low-level classical
instructions, like

.. code-block:: c

   const n = /* some size, known at compile time */;
   def parity(bit[n] cin) -> bit {
     bit c;
     for i in [0: n - 1] {
       c ^= cin[i];
     }
     return c;
   }

We can make some measurements and call this subroutine on the results as
follows

.. code-block:: c

   qubit q;
   qubit r;
   c = measure q;
   c2 = measure r;
   bit result;
   result = parity(c || c2);

We require that we know the signature at compile time, as we do in this
example. We could also just as easily have used an extern function for
this

.. code-block:: c

   const n = /* size of c + size of c2 */;
   extern parity(bit[n]) -> bit;
   qubit q;
   qubit r;
   c = measure q;
   c2 = measure r;
   bit result;
   result = parity(c || c2);
