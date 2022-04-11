Variable scope
==============

This section describes the rules surrounding scoping of variables in OpenQASM.

Global scope
------------

Identifiers declared as subroutines, gates, and defcals have global scope, 
*i.e.* they are visible at every scope of the program, and may not be shadowed.
Subroutines, gates, and defcals may only be declared at the top-level of the
program. Redeclaration or overloading of subroutines and gates is not allowed.
Defcals may be overloaded as described in :any:`pulse-gates`.

Non-quantum variables defined at the top level of the program have global scope,
and are visible at all lower scopes. Globally-scoped variables are
implicitly ``const`` inside the body of subroutine and gate definitions, though
they may be shadowed by locally declared variables or parameters. All qubits
have global scope, but are not visible within the scope of subroutines, gates,
and defcals because qubits cannot be interacted with in a manner consistent with
the ``const`` qualifier.

.. code-block:: c

  int ii = 100; // global scope
  def myMul() -> int {
    return ii*2; // ii is in scope, but 'const'
  }
  ii = 200;
  int jj = myMul(); // jj gets the value 400

Block scope
-----------

The scope of an identifier declared inside of a block, or as the iteration
variable of a ``for`` loop, begins at the point of declaration and ends at the
end of the block. As with globally-scoped variables, nested declarations may
shadow higher-level declarations.

.. code-block:: c

  int ii = 100; // global scope
  {
    ii *= 2;    // global ii takes the value 200
    int ii = 1; // inner ii takes the value 1
    ii *= 2;    // inner ii takes the value 2
  } // inner ii scope ends
  // global ii is 200
  ii *= 2; // global ii takes the value 400
  int sum = 0;
  for ii in [1:10] {
    // global ii is shadowed by the iteration variable ii
    ii *= 2;   // error: iteration variable may not be modified by the loop
    sum += ii; // iteration variable ii is added to global sum
    if (sum > 10) {
      float ii = 10.0; // iteration variable shadowed
      sum += int(ii*2);
    }
  }
  // global ii in scope again
  ii *= 2; // global ii takes the value 800
