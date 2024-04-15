Scoping of variables
====================

This section describes the rules surrounding scoping of variables in OpenQASM.

OpenQASM 3.0 has four types of scoping constructs, and the visibility of some
symbols can differ slightly between these.  The types of scope are:

* :ref:`Global scope <scope-global>`, which is the current scope only when no
  other scopes are active.

* :ref:`Gate and function scope <scope-subroutine>`, which is entered in the
  body of ``gate`` and ``def`` definitions.

* :ref:`Local block scope <scope-block>`, which becomes active on entry to a
  non-gate and non-subroutine block, such as those associated with ``if`` or 
  ``for`` statements or introduced via anonymous scope syntax.

* Calibration scopes, which are the shared calibration state contained in
  ``cal`` and ``defcal`` blocks.  The precise rules for these may vary depending
  on the particular companion calibration grammar that has been loaded for this
  program.  See :ref:`the OpenPulse specification <openpulse>` for details on
  how this is handled in the OpenPulse calibration language.  This document will
  not cover this topic further.

In general, the lifetime of each identifier begins when it is declared, and ends
at the completion of the scope it was declared in.  The storage space for each
variable must be allocated for at least the lifetime of the identifier, but it
is up to individual implementations to define their allocation strategies within
nested scopes.

In order to be a valid OpenQASM 3.0 program, symbols must be defined before they
are used; in particular, there is no forward declaration of functions and gates,
and there can be no mutual recursion.

Most regular identifiers of variables can be shadowed in inner scopes, so that
the identifier temporarily refers to a different variable, but cannot be
re-declared without entering an inner scope.  The type of the shadowing variable
does not need to be the same as the type of the variable it is shadowing.

Not all identifiers declared in outer scopes are visible within inner scopes.
The visibility depends on the type of the variable, and the type of the inner
scope.  Approximately, ``const`` variables, gates and subroutines are visible
within *all* inner scopes, while other variables in outer scopes are visible
within inner control-flow scopes but not gate and function scopes.

The ``include`` statement should be seen as extending the global scope of the
file it is contained within; all variables that are in scope at the time of the
``include`` statement are also in scope while the included file is being parsed,
and variables defined in that file will be available in the containing file's
scope once the inclusion has been parsed.  There is no separate namespacing
defined in OpenQASM 3.0.


.. _scope-global:

Global scope
------------

The global scope is active when no other scopes are active.  Several OpenQASM
3.0 statements are only valid in the global scope, such as (non-exhaustive):

* ``gate``, ``def`` and ``defcal`` declarations,
* ``qubit`` declarations,
* ``array`` declarations.

A simple example of scoping between a main program file and an included file:

.. code-block:: c
   :caption: Main program

   OPENQASM 3.0;

   gate h q {
      U(pi/2, 0, pi) q;
      // `U` is the single-qubit gate that is implicitly defined in the global
      // scope of all OpenQASM 3.0 programs, and so is available here.
      // Similarly `pi` is one of the implicitly defined constants.
   }

   int i = 100;

   include "my_definitions.qasm";

   // Identifiers 'h', 'my_gate', 'i' and 'j' are defined and in scope.

.. code-block:: c
   :caption: File ``my_definitions.qasm``

   gate my_gate q {
      U(pi, 0, pi) q;
   }

   int j = i + 5;
   // This usage of `i` is valid because the scope inside the `include`
   // inherits all definitions from the scope that did the including.


Within the global scope, identifiers declared by ``gate``, ``def`` and
``defcal`` statements may not be shadowed or otherwise redeclared.  As described
in the :ref:`section on pulse-level descriptions of quantum operations
<pulse-gates>`, multiple ``defcal`` statements may affect the same operation;
this is not an instance of shadowing, but a form of overloading, extending the
calibration definitions for different qubits.

.. warning::

   The following example is *not* valid OpenQASM 3.0 due to invalid scoping.

.. code-block:: c

   OPENQASM 3.0;

   gate h q {
      U(pi/2, 0, pi) q;
   }

   int h = 1;  // ERROR: 'h' is already defined and cannot be re-declared.

   uint a = 1;
   uint a = 2; // ERROR: 'a' is already defined and cannot be re-declared.

   defcal h $0 {
      // ...
   }
   // No error: this is valid OpenQASM 3.0 because `defcal` statements do not
   // redefine, they overload quantum operations with specific pulse-level
   // control statements.

   defcal a $0 {
      // ...
   }
   // ERROR: 'a' is already defined and cannot be re-declared.  Unlike the
   // previous example, this is an error because 'a' is already declared as a
   // non-quantum-operation type ('uint').  This `defcal` would be defining a
   // new gate, which is invalid with 'a' already defined.


.. _scope-subroutine:

Subroutine and gate scope
-------------------------

The definitions of subroutines (``def``) and gates (``gate``) introduce a new
scope.  The ``def`` and ``gate`` statements are only valid directly within the
global scope of the program.

Inside the definition of the subroutine or gate, symbols that were already
defined in the global scope with the ``const`` modifier, or previously defined
gates and subroutines are visible.  Globally scoped variables without the
``const`` modifier are not visible inside the definition.  In other words,
subroutines and gates cannot close over variables that may be modified at
run-time.

Variables defined in subroutine scopes are local to the subroutine body.
Variables defined in the parameter specifications of subroutines and gates
behave for scoping purposes as if they were defined in the scope of the
definition.  The lifetime of these local variables ends at the end of the
function body, and they are not accessible after the subroutine or gate body.
Similarly, the qubit identifiers in a gate definition are valid only within the
definition of the gate.

The identifier of a subroutine or gate is available in the scope of its own
body, allowing direct recursion.  For gates, the direct recursion is unlikely to
ever be useful, since this would generally be non-terminating.

Local subroutine or gate variables, including parameters and qubit definitions,
may shadow variables defined in the outer scope.  Inside the body, the
identifier will refer to the local variable instead.  After the definition of
the body has completed (and we are back in the global scope), the identifier
will refer to the same variable it did before the subroutine or gate.

Subroutines cannot contain ``qubit`` declarations in their bodies, but can
accept variables of type ``qubit`` in their parameter lists.  Aliases can be
declared within subroutine and gate scopes, and have the same lifetime and
visibility as other local variables.

For example:

.. code-block:: c
   :linenos:

   OPENQASM 3.0;

   qubit[5] all_qubits;

   int a = 1;
   int b = 2;
   const int c = 3;
   const int d = 4;

   def my_routine(uint a, uint c) {
      // In this body, 'a' refers to the subroutine parameter, not the external
      // variable, which wouldn't be visible even without the shadowing.

      int in_body = 5;

      // Identifiers in scope are:
      //  - 'my_routine': the subroutine itself
      //  - 'a': type 'uint', from the parameter list
      //  - 'c': type 'uint', from the parameter list (shadows the outer 'const
      //      int' 'c').
      //  - 'd': type 'const int', value 4, visible from the global scope
      //      because it is a 'const' type.
      //  - 'in_body': type 'int', value 5, from regular definition in the
      //      current scope.
      //  - other built-in identifiers (such as 'U' and 'pi') that are
      //      implicitly defined in the global scope.
      //  - all available hardware qubits (such as '$0')
      //
      // The variable 'b' is not in scope, because its visibility as a
      // non-'const' type does not make it available within subroutines.  The
      // hardware qubit identifiers are in scope, but not the virtual qubit
      // identifier 'all_qubits'.
   }

   // After the subroutine block, 'a' and 'c' once again refer to the variables
   // of type 'int' and 'const int' defined on lines 3 and 5 respectively.
   // 'in_body' (from the subroutine body) is not in scope, while 'my_routine'
   // (the subroutine) is.

   const float[64] new_variable = 1.5;

   def second_subroutine(qubit[4] q) {
      int in_body = 8;

      let some_qubits = q[0:2];

      // Identifiers in scope are:
      //   - 'second_subroutine'
      //   - 'my_subroutine'
      //   - 'in_body': type 'int', value 8
      //   - 'c': type 'const int', value 3
      //   - 'd': type 'const int', value 4
      //   - 'q': type 'qubit[4]', a virtual, run-time-known qubit register.
      //   - 'some_qubits': alias for the first three qubits of 'q'.
      //   - 'new_variable': type 'const float[64]', value 1.5
      //   - the other built-in identifiers like 'U' and 'pi'
      //   - the available hardware qubits like '$0'.
   }


.. _scope-block:

Block scope
-----------

In addition to the scopes explicitly defined above, local scope blocks may be 
introduced with curly brackets ``{`` and ``}`` wherever a statement is expected.
These are sometimes referred to as "anonymous" scope blocks, because they are not
directly associated with a named entity such as a gate or subroutine, or the global
scope.

Certain control-flow operations rely on the introduction of local scope blocks.
These operations are

* ``for`` loops,
* ``while`` loops,
* ``if`` and ``else`` blocks,
* ``box`` statements.

Local scope blocks inherit *all* variables that are in scope in the immediately
containing scope.  Unlike subroutines and gate scopes, this includes variables
that are not ``const``.  This is broadly similar how these constructs behave in
other procedural languages, such as C.

The iteration variable of a ``for`` loop has lifetime and visibility as if it
were declared as the first statement in the body of that loop.  It is not
accessible after the body of the loop.

The blocks associated with ``if`` and its corresponding ``else`` define two
different scopes; the variables and definitions are not shared between them.

As with subroutine scopes, variables defined locally in these scopes (including
the for-loop iteration variable) may shadow variables with the same name in
outer scopes.  When the defining scope of a shadowing variable ends, the
previous variable (which was shadowed) becomes accessible again.  Qubits and
arrays cannot be declared within local block scopes, but aliases can.

Some further examples:

.. code-block:: c
   :linenos:

   OPENQASM 3.0

   int ii = 100;         // 'ii' is declared in the global scope.
   qubit[5] q;           // 'q' is declared in the global scope.
   let some_q = q[0:2];  // alias 'some_q' is declared in the global scope.

   // This is an anonymous scope block
   {
     ii *= 2;    // This is the global 'ii', which now has the value 200.

     // A local variable 'ii' is declared, which shadows the global definition.
     // The global 'ii' is no longer accessible until this scope ends.
     int ii = 1;
     // The local variable 'ii' is modified, and now has the value 2.
     ii *= 2;
   }

   // The local 'ii' went out of scope at the conclusion of the above block, and
   // the previous 'ii' defined on line 3 is accessible again.
   ii *= 2;  // global 'ii' is now 400.   

   if (true) {
     // As before, a local variable 'ii' is declared and shadows the global definition.
     // This is also distinct from the 'ii' introduced in the anonymous scope block above. 
     int ii = 1;
   }

   uint sum = 0;
   for uint ii in [1:4] {
     // The global 'ii' is shadowed by the iteration variable 'ii', which also
     // has a different type.  The outer 'sum' is still accessible.

     // Values at this point in various iterations:
     //  Iteration   ii    sum
     //     0        1     0
     //     1        2     2
     //     2        3     6
     //     3        4     12

     sum += ii;  // Iteration variable 'ii' is added to global 'sum'

     //  Iteration   ii    sum
     //     0        1     1
     //     1        2     4
     //     2        3     9
     //     3        4     16

     if (sum > 10) {
       float ii = 10.0; // For-loop iteration variable shadowed.
       sum += uint(ii * 2.0);
     } else {
       sum += ii;      // 'ii' is the for-loop iteration variable.
     }

     //  Iteration   ii    sum
     //     0        1     2
     //     1        2     6
     //     2        3     12
     //     3        4     36

     U(0, 0, (sum / 55) * pi) q;  // Global-scope qubit 'q' is in scope here.
   }

   // The lifetime of the local for-loop iteration variable 'ii' ended at the
   // conclusion of the for-loop body, and the global 'ii' is back in scope.

   while (ii > 0) {
     let some_q = q[3:4];  // local alias 'some_q' shadows the global alias.
   }
