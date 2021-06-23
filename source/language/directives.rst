Directives
==========

OpenQASM supports a directive mechanism that allows other information to
be included in the program. A directive begins with ``#pragma`` and
terminates at the end of the line. Directives can provide annotations
that give additional information to compiler passes and the target
system or simulator. Ideally the meaning of the program does not change
if some or all of the directives are ignored, so they can be interpreted
at the discretion of the consuming process.


Input/output
============

OpenQASM introduces features targeted to support near-time computation, in
the form of parameterized circuits. These features are modifiers ``input``
and ``output``, which allow OpenQASM3 circuits to accept input parameters
and return select output parameters.

The ``input`` modifier can be used to indicate that one or more variable
declarations represent values which will be provided at run-time, upon
invocation. This allows the programmer to use the same compiled circuits
which only differ in the values of certain parameters. For backward compatibility,
OpenQASM3 does not require an ``input`` declaration to be provided. When
an ``input`` declaration is provided, the compiler produces an executable
that leaves these free parameters unspecified: a circuit run would take as
input both the executable and some choice of the parameters.

Similarly, the ``output`` modifier can be used to indicate that one or more variables
are to be provided as an explicit output of the quantum procedure. Note that
OpenQASM 2 did not allow the programmer to specify that only a subset of its
variables should be returned as output, and so it would return all classical
variables (which were all creg variables) as output. For compatibility, 
OpenQASM 3 does not require an output declaration to be provided: in this 
case it assumes that all of the declared variables are to be returned as
output. If the programmer provides one or more output declarations, then only
those variables described as outputs will be returned as an output of the 
quantum process. A variable may not be marked as both input and output.

The input and output modifiers allow the programmer to more easily write 
variational quantum algorithms: a quantum algorithm with some free parameters,
which may be run many times with different parameter values which are determined
by a classical optimiser at near-time. Rather than write a circuit which
generates a new sequence of operations for each run, OpenQASM 3 allows such
circuits to be expressed as a single program with input parameters. This 
allows the programmer to communicate many different circuits with a single
file, which only has to be compiled once, amortizing the cost of compilation
across many runs. For an example, we may consider a parameterized circuit which
performs a measurement in a basis given by an input parameter:

.. code-block:: c
   :force:

   input int basis; // 0 = X basis, 1 = Y basis, 2 = Z basis
   output bit result;
   qubit q;

   // Some complicated circuit...

   if (basis == 0) h q;
   else if (basis == 1) rx(π/2) q;
   result = measure q;

For a second example, consider the Variable Quantum Eigensolver (VQE) algorithm :cite:`peruzzo2014variational`.
In this algorithm the same circuit is repeated
many times using different sets of free parameters to minimize an expectation 
value. The following is an example, in which there is also more than one input
variable:

.. code-block:: c

   input angle[32] param1;
   input angle[32] param2;
   qubit q;

   // Build an ansatz using the above free parameters, eg.
   rx(param1) q;
   ry(param2) q;

   // Estimate the expectation value and store in an output variable

The following Python pseudocode illustrates the differences between using and
not using parameterized circuits in a quantum program for the case of the VQE:

.. code-block:: python
   :force:

   # Example without using parametric circuits:

   for theta in thetas:
       # Create an OpenQASM circuit with θ defined
       circuit = subsitute_theta(read("circuit.qasm"))

       # The slow compilation step is run on each iteration of the inner loop
       binary = compile_qasm(circuit)
       result = run_program(binary)

   # Example using parametric circuits:

   # parametric_circuit.qasm begins with the line "input angle θ;"
   circuit = read("parametric_circuit.qasm")

   # The slow compilation step only happens once
   binary = compile_qasm(circuit)

   for theta in thetas:
       # Each iteration of the inner loop is reduced to only running the circuit
       result = run_program(binary, θ=theta)
