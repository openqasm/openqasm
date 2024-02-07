.. _classical-instructions:

Classical instructions
======================

We envision two levels of classical control: simple, low-level instructions embedded as
part of a quantum circuit and high-level external functions which perform more complex
classical computations. The low-level functions allow basic
computations on lower-level parallel control processors. These instructions are likely
to have known durations and many such instructions might be executed
within the qubit coherence time. The external, or ``extern``, functions execute
complex blocks of classical code that may be neither fast nor guaranteed to return. In order
to connect with classical compilation infrastucture, ``extern`` functions are defined outside of
OpenQASM. The compiler toolchain is expected to link ``extern`` functions when building an
executable. This strategy allows the programmer to use existing libraries without porting them into
OpenQASM. ``extern`` functions run on a global processor concurrently with operations on local
processors, if possible. ``extern`` functions can write to the global controller’s memory,
which may not be directly accessible by the local controllers.

Low-level classical instructions
--------------------------------

Generalities
~~~~~~~~~~~~

All types support the assignment operator ``=``. The left-hand-side (LHS) and
right-hand-side (RHS) of the assignment operator must be of the same
type. For real-time values assignment is by copy of the RHS value to the
assigned variable on the LHS.

.. code-block::

   int[32] a;
   int[32] b = 10; // Combined declaration and assignment

   a = b; // Assign b to a
   b = 0;
   a == b; // False
   a == 10; // True

Classical bits and registers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classical registers, ``bit``, ``uint`` and ``angle`` support bitwise operators
and the corresponding assignment operators with registers of the same size:
and ``&``, or ``|``, xor ``^``. They support left shift ``<<`` and right shift
``>>`` by an unsigned integer, and the corresponding assignment operators. The
shift operators shift bits off the end. They also support bitwise negation ``~``,
``popcount`` [1]_, and left and right circular shift, ``rotl`` and ``rotr``,
respectively.

.. code-block::

   bit[8] a = "10001111";
   bit[8] b = "01110000";

   a << 1; // Bit shift left produces "00011110"
   rotl(a, 2) // Produces "00111110"
   a | b; // Produces "11111111"
   a & b; // Produces "00000000"

For ``uint`` and ``angle``, the results of these operations are defined as if
the operations were applied to their defined bit representations::

   angle[4] a = 9 * (pi / 8);  // "1001"
   a << 2;  // Produces pi/2, which is "0100"
   a >> 2;  // Produces pi/4, which is "0010"

   uint[6] b = 37;  // "100101"
   popcount(b);  // Produces 3.
   rotl(b, 3);   // Produces 44, which is "101100"

Comparison (Boolean) Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integers, angles, bits, and classical registers can
be compared (:math:`>`, :math:`>=`, :math:`<`, :math:`<=`, :math:`==`,
:math:`!=`) and yield Boolean values. Boolean values support logical
operators: and ``&&``, or ``||``, not ``!``. The keyword ``in`` tests if an integer belongs to
an index set, for example ``i in {0,3}`` returns ``true`` if i equals 0 or 3 and ``false`` otherwise.

.. code-block::

   bool a = false;
   int[32] b = 1;
   angle[32] d = pi;
   float[32] e = pi;

   a == false; // True
   a == bool(b); // False
   c >= b; // True
   d == pi; // True
   // Susceptible to floating point casting errors
   e == float(d);

.. note::

   Angles are naturally defined on a ring, and so comparisons may not work
   exactly how you might expect.  For example, ``2 * ang >= ang`` is not
   necessarily true; if ``ang`` represents the angle :math:`3\pi/2`, then
   ``2*ang == pi`` and ``pi < ang``.

   This is the same behavior as unsigned integers in many languages (including
   OpenQASM 3), but the types of operation commonly performed on ``angle`` are
   particularly likely to trigger these modulo arithmetic effects.

Integers
~~~~~~~~

Integer types support addition ``+``, subtraction ``-``, multiplication ``*``, integer division [2]_ ``/``, modulo ``%``, and power ``**``, as well as the corresponding assignments ``+=``, ``-=``, ``*=``, ``/=``, ``%=``, and ``**=``.

.. code-block::

   int[32] a = 2;
   int[32] b = 3;

   a * b; // 6
   b / a; // 1
   b % a; // 1
   a ** b; // 8
   a += 4; // a == 6

Angles
~~~~~~

In addition to the bitwise operations mentioned above, angles support:

- Addition ``+`` and subtraction ``-`` by other angles of the same size, which
  returns an angle of the same size.
- Multiplication ``*`` and division ``/`` by unsigned integers of the same size.
  The result is an ``angle`` type of the same size.  Both ``uint * angle`` and
  ``angle * uint`` are valid and produce the same result, but only ``angle /
  uint`` is valid; it is not allowed to divide an integer by an angle.
- Division ``/`` by another angle of the same size.  This returns a ``uint`` of
  the same size.
- Unary negation ``-``, which represents the mathematical operation :math:`-a
  \equiv 2\pi - a`.
- Compound assignment operators ``+=``, ``-=`` and ``/=`` with angles of the
  same size as both left- and right operands.  These have the same effect as if
  the equivalent binary operation had been written out in full.
- The compound assignment operators ``*=`` and ``/=`` with an unsigned integer
  of the same size as the right operand.  This has the same effect as if the
  multiplication or division had been written as a binary operation and
  assigned.

In all of these cases, except for unary negation, the bit pattern of the result
of these operations is the same as if the operations had been carried out
between two ``uint`` types of the same size with the same bit representations,
including both upper and lower overflow.  Explicitly::

  angle[4] a = 7 * (pi / 8);  // "0111"
  angle[4] b = pi / 8;        // "0001"
  angle[4] c = 5 * (pi / 4);  // "1010"
  uint[4] two = 2;

  a + b;    // angle[4] │ pi           │ "1000"
  b - a;    // angle[4] │ 5 * (pi / 4) │ "1010"
  a / two;  // angle[4] │ 3 * (pi / 8) │ "0011"
  two * c;  // angle[4] │ pi / 2       │ "0100"
  c / b;    // uint[4]  │ 10           │ "1010"
  pi * 2;   // angle[4] │ 0            │ "0000"

Unary negation of an angle ``a`` is defined to produce the same value as
``0 - a``, such that ``a + (-a)`` is always equal to zero.  This is the same as
the C99 definition for unsigned integers.  In bitwise operations, the negation
can be written as ``(~a) + 1``. Explicitly::

  angle[4] a = pi / 4;  // "0010"
  angle[4] b = -a;  // 7*(pi/4) │ "1110"

Floating-point numbers
~~~~~~~~~~~~~~~~~~~~~~

Floating-point numbers support addition, subtraction, multiplication, division,
and power and the corresponding assignment operators.

.. code-block::

   angle[20] a = pi / 2;
   angle[20] b = pi;
   a + b; // 3/2 * pi
   a ** b; // 4.1316...
   angle[10] c;
   c = angle(a + b); // cast to angle[10]

.. note::

   Real hardware may well not have access to floating-point operations at
   runtime.  OpenQASM 3 compilers may reject programs that require runtime
   operations on these values if the target backend does not support them.

Complex numbers
~~~~~~~~~~~~~~~

Complex numbers support addition, subtraction, multiplication, division, power
and the corresponding assignment operators.  These binary operators follow
analogous semantics to those described in Annex G (section G.5) of the C99
specification (note that OpenQASM 3.0 has no *imaginary* type, only *complex*).
These operations use the floating-point semantics of the underlying component
floating-point types, including their ``NaN`` propagation, and
hardware-dependent rounding mode and subnormal handling.

.. code-block::

   complex[float[64]] a = 10.0 + 5.0im;
   complex[float[64]] b = -2.0 - 7.0im;
   complex[float[64]] c = a + b;   // c = 8.0 - 2.0im
   complex[float[64]] d = a - b;   // d = 12.0+12.0im;
   complex[float[64]] e = a * b;   // e = 15.0-80.0im;
   complex[float[64]] f = a / b;   // f = (-55.0+60.0im)/53.0
   complex[float[64]] g = a ** b;  // g = (0.10694695640729072+0.17536481119721312im)

Evaluation order
~~~~~~~~~~~~~~~~

OpenQASM evaluates expressions from left to right.

   .. table:: [operator-precedence] operator precedence in OpenQASM ordered from highest precedence to lowest precedence. Higher precedence operators will be evaluated first.

      +----------------------------------------+------------------------------------+
      | Operator                               | Operator Types                     |
      +----------------------------------------+------------------------------------+
      | ``()``, ``[]``, ``(type)(x)``          | Call, index, cast                  |
      +----------------------------------------+------------------------------------+
      | ``**``                                 | Power                              |
      +----------------------------------------+------------------------------------+
      | ``!``, ``-``, ``~``                    | Unary                              |
      +----------------------------------------+------------------------------------+
      | ``*``, ``/``, ``%``                    | Multiplicative                     |
      +----------------------------------------+------------------------------------+
      | ``+``, ``-``                           | Additive                           |
      +----------------------------------------+------------------------------------+
      | ``<<``, ``>>``                         | Bit Shift                          |
      +----------------------------------------+------------------------------------+
      | ``<``, ``<=``, ``>``, ``>=``           | Comparison                         |
      +----------------------------------------+------------------------------------+
      | ``!=``, ``==``                         | Equality                           |
      +----------------------------------------+------------------------------------+
      | ``&``                                  | Bitwise AND                        |
      +----------------------------------------+------------------------------------+
      | ``^``                                  | Bitwise XOR                        |
      +----------------------------------------+------------------------------------+
      | ``|``                                  | Bitwise OR                         |
      +----------------------------------------+------------------------------------+
      | ``&&``                                 | Logical AND                        |
      +----------------------------------------+------------------------------------+
      | ``||``                                 | Logical OR                         |
      +----------------------------------------+------------------------------------+


Looping and branching
---------------------

If-else statements
~~~~~~~~~~~~~~~~~~

The statement ``if ( bool ) <true-body>`` branches to program if the Boolean evaluates to true and
may optionally be followed by ``else <false-body>``.  Both ``true-body`` and
``false-body`` can be a single statement terminated by a semicolon, or a program
block of several statements ``{ stmt1; stmt2; }``.

.. code-block::

   bool target = false;
   qubit a;
   h a;
   bit output = measure qubit

   // example of branching
   if (target == output) {
      // do something
   } else {
      // do something else
   }

For loops
~~~~~~~~~

The statement ``for <type> <name> in <values> <body>`` loops over the
items in ``values``, assigning each value to the variable ``name`` in subsequent
iterations of the loop ``body``.  ``values`` can be:

- a discrete set of scalar types, defined using the
  :ref:`array-literal syntax <types-arrays>`, such as ``{1, 2, 3}``.  Each value
  in the set must be able to be implicitly promoted to the type ``type``.

- a range expression in square brackets of the form ``[start : (step :)? stop]``,
  where ``step`` is equal to ``1`` if omitted.  As in other range expressions,
  the range is inclusive at both ends.  Both ``start`` and ``stop`` must be
  given.  All three values must be of integer or unsigned-integer types.  The
  scalar type of elements in the resulting range expression is the same as the
  type of result of the :ref:`implicit promotion <implicit-promotion-rules>`
  between ``start`` and ``stop``.  For example, if ``start`` is a ``uint[8]``
  and ``stop`` is an ``int[16]``, the values to be assigned will all be of type
  ``int[16]``.

- a value of type ``bit[n]``, or the target of a ``let`` statement that creates
  an alias to classical bits.  The corresponding scalar type of the loop
  variable is ``bit``, as appropriate.

- a value of type ``array[<scalar>, n]``, _i.e._ a one-dimensional
  array.  Values of type ``scalar`` must be able to be implicitly promoted to
  values of type ``type``.  Modification of the loop variable does not change
  the corresponding value in the array.

It is valid to use an indexing expression (e.g. ``my_array[1:3]``) to arrive at
one of the types given above.  In the cases of sets, ``bit[n]``, classical
aliases and ``array``, the iteration order is guaranteed to be in sequential
index order, that is ``iden[0]`` then ``iden[1]``, and so on.

The loop body can either be a single statement terminated by a semicolon, or a
program block in curly braces ``{}`` containing several statements.

Assigning a value to the loop variable within an iteration over the body does
not affect the next value that the loop variable will take.

The scope of the loop variable is limited to the body of the loop.  It is not
accessible after the loop.

.. code-block::

   int[32] b = 0;
   // loop over a discrete set of values
   for int[32] i in {1, 5, 10} {
       b += i;
   }
   // b == 16, and i is not in scope.

   // loop over every even integer from 0 to 20 using a range, and call a
   // subroutine with that value.
   for int i in [0:2:20]
      subroutine(i);

   // high precision typed loop variable
   for uint[64] i in [4294967296:4294967306] {
      // do something
   }

   // Loop over an array of floats.
   array[float[64], 4] my_floats = {1.2, -3.4, 0.5, 9.8};
   for float[64] f in my_floats {
      // do something with 'f'
   }

   // Loop over a register of bits.
   bit[5] register;
   for b in register {}
   let alias = register[1:3];
   for b in alias {}


While loops
~~~~~~~~~~~

The statement ``while ( bool ) <body>`` executes program until the Boolean evaluates to
false [3]_. Variables in the loop condition statement may be modified
within the while loop body.  The ``body`` can be either a single statement
terminated by a semicolon, or a program block in curly braces ``{}`` of several
statements:

.. code-block::

   qubit q;
   bit result;

   int i = 0;
   // Keep applying hadamards and measuring a qubit
   // until 10, |1>s are measured
   while (i < 10) {
       h q;
       result = measure q;
       if (result) {
           i += 1;
       }
   }

Breaking and continuing loops
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The statement ``break;`` moves control to the statement immediately following
the closest containing ``for`` or ``while`` loop.

The statement ``continue;`` causes execution to jump to the next step in the
closest containing ``for`` or ``while`` loop.  In a ``while`` loop, this point
is the evaluation of the loop condition.  In a ``for`` loop, this is the
assignment of the next value of the loop variable, or the end of the loop if the
current value is the last in the set.

.. code-block::

   int[32] i = 0;

   while (i < 10) {
       i += 1;
       // continue to next loop iteration
       if (i == 2) {
           continue;
       }

       // some program

       // break out of loop
       if (i == 4) {
           break;
       }

       // more program
   }

It is an error to have a ``break;`` or ``continue;`` statement outside a loop,
such as at the top level of the main circuit or of a subroutine.

.. code-block::

   OPENQASM 3.0;

   break;  // Invalid: no containing loop.

   def fn() {
      continue; // Invalid: no containing loop.
   }

Terminating the program early
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The statement ``end;`` immediately terminates the program, no matter what scope
it is called from.


The Switch statement
--------------------

A ``switch`` statement is a form of flow control that provides for a predicated selection of zero, one or more statements to be executed based on a discriminating controlling value. The discriminating controlling value can be either *explicit* - as it is the case for ``case`` statements - or *none of the above* - which is the case for ``default`` statements.

A ``switch`` statement is not a loop. It does not iterate over a sequence of values.

``switch`` statements may appear anywhere in a program where statements are allowed.

An OpenQASM3 ``switch`` statement shall use the following keywords:

- ``switch``

- ``case``

- ``default``


An OpenQASM3 ``switch`` statement shall be the following grammar:

- The ``switch`` keyword.
- A right paren ``(`` literal.
- A ``controlling expression``.
- A left paren ``)`` literal.
- A left brace ``{`` literal.
- A sequence of one or more ``case`` statements (defined below).
- Either zero or one ``default`` statement(s) (defined below).
- A right brace ``}`` literal.
   

The ``controlling expression`` of a ``switch`` statement shall be of integer type. Implicit conversions to an integer type are not allowed.

A ``case`` statement shall be the following grammar:

- The ``case`` keyword.
- An ``integer-constant-list-expression`` controlling label.
- A left-brace literal: ``{``.
- A sequence of zero, one or more OpenQASM3 statements.
- A right-brace literal: ``}``.

The ``integer-constant-list-expression`` is a sequence of one or more integer ``const`` expressions separated by comma ``,`` literals.

A ``default`` statement shall be the following grammar:

- The ``default`` keyword.
- A left-brace literal: ``{``.
- A sequence of zero, one or more OpenQASM3 statements.
- A right-brace literal: ``}``.

A ``switch`` statement shall be in scope only within the scope where it is defined.

The left and right braces of a ``switch`` statement shall not create brace-enclosed scope.

Declarations or statements at ``switch`` statement scope but outside of a ``case`` or ``default`` statement are ill-formed. The compiler shall raise an error diagnostic for such cases.

A ``case`` or ``default`` statement creates brace-enclosed scope.

Declarations of types that automatically acquire global scope in OpenQASM3 - such as gates, functions, arrays, qubits and defcals - are not allowed at ``case`` or ``default`` ``switch`` statement scope. Use of such declarations is ill-formed and requires a compiler diagnostic.

Duplicate values within any ``integer-constant-list-expression`` for controlling labels of ``case`` statements are not allowed. The compiler shall issue an error diagnostic in such cases.

A ``case`` or ``default`` statement ending with a right-brace ``}`` terminates the execution of the ``switch`` statement. After executing all the statements of the ``case`` or ``default`` statement, control is then transferred to the first statement following the closing right brace of the enclosing ``switch`` statement.

A ``switch`` statement shall contain at least one ``case`` statement. A ``switch`` statement with no ``case`` statements shall raise an error diagnostic.

A ``switch`` statement is not required to contain a ``default`` statement. If a ``switch`` statement does not contain a ``default`` statement and a runtime value is provided to the controlling expression that does not match any case, then the ``switch`` becomes effectively a no-op.

Examples:

1. A simple ``switch`` statement with ``case`` and ``default`` statements:

.. code-block::

	OPENQASM 3.0;

	int i = 15;

	switch (i) {
	case 1, 3, 5 {
	  // OpenQASM3 statement(s)
	}
	case 2, 4, 6 {
	  // OpenQASM3 statement(s)
	}
	case -1 {
	  // OpenQASM3 statement(s)
	}
	default {
	  // OpenQASM3 statement(s)
	}
	}


2. A ``switch`` where the cases are ``const`` expressions:

.. code-block::

	OPENQASM 3.0;

	const int A = 0;
	const int B = 1;
	int i = 15;

	switch (i) {
	case A {
	  // OpenQASM3 statement(s)
	}
	case B {
	  // OpenQASM3 statement(s)
	}
	case B+1 {
	  // OpenQASM3 statement(s)
	}
	default {
	  // OpenQASM3 statement(s)
	}
	}
	

3. A switch statement with binary literals in the ``case`` statements:

.. code-block::

	OPENQASM 3.0;

	bit[2] b;
	switch (int(b)) {
	case 0b00 {
	  // OpenQASM3 statement(s)
	}
	case 0b01 {
	  // OpenQASM3 statement(s)
	}
	case 0b10 {
	  // OpenQASM3 statement(s)
	}
	case 0b11 {
	  // OpenQASM3 statement(s)
	}
	}
	
4. A ``switch`` statement containing declarations at ``case`` statement scope, and a function call, also at ``case`` statement scope:


.. code-block::

	OPENQASM 3.0;

	def foo(int i, qubit[8] d) -> bit {
	  return measure d[i];
	}

	int i = 15;

	int j = 1;
	int k = 2;

	bit c1;

	qubit[8] q0;

	switch (i) {
	case 1 {
	  j = k + foo(k, q0);
	}
	case 2 {
	  float[64] d = j / k;
	}
	case 3 {
	}
	default {
	}
	}
	
	
5. A ``switch`` statement containing a nested ``switch`` statement.

.. code-block::

	OPENQASM 3.0;

	def foo(qubit[8] q) -> int {
	  int r = 0;
	  bit k;

	  for int i in [0 : 7] {
		k = measure q[i];
		r += k;
	  }

	  return r;
	}

	qubit[8] q;

	int j = 30;
	int i = foo(q);

	switch (i) {
	case 1, 2, 5, 12 {
	}
	case 3 {
	  switch (j) {
	  case 10, 15, 20 {
	    h q;	  
	  }
	}
	}


Extern function calls
---------------------

``extern`` functions are declared by giving their signature using the
statement ``extern name(inputs) -> output;`` where ``inputs`` is a comma-separated list of type
names and ``output`` is a single type name. The parentheses may be omitted if there are no ``inputs``.

``extern`` functions can take of any number of arguments whose types correspond to the classical
types of OpenQASM. Inputs are passed by value. They can return zero or one value whose type
is any classical type in OpenQASM except real constants. If necessary,
multiple return values can be accommodated by concatenating registers.
The type and size of each argument must be known at compile time to
define data flow and enable scheduling. We do not address issues such as
how the ``extern`` functions are defined and registered.

``extern`` functions are invoked using the statement ``name(inputs);`` and the result may be
assigned to ``output`` as needed via an assignment operator (``=``, ``+=``, etc). ``inputs`` are
literals and ``output`` is a variable, corresponding to the types in the signature. The functions
are not required to be idempotent. They may change the state of the process providing the function.
In our computational model, ``extern`` functions may run concurrently with other classical and
quantum computations. That is, invoking an ``extern`` function will  *schedule* a classical
computation, but does not wait for that computation to terminate.


.. [1]
   ``popcount`` computes the Hamming weight of the input register.

.. [2]
   If multiplication and division instructions are not available in
   hardware, they can be implemented by expanding into other
   instructions.

.. [3]
   This clearly allows users to write code that does not terminate. We
   do not discuss implementation details here, but one possibility is to
   compile into target code that imposes iteration limits.
