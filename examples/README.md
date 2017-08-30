# Examples

## Generic

This is a directory with examples that cannot necessarily be executed on any existing hardware. You can still run these circuits in a simulator.

- `adder.qasm`: Adds two four-bit numbers.
- `bigadder.qasm`: Quantum ripple-carry adder. 8-bit adder made out of 2 4-bit adders from adder.qasm.
- `inverseqft1.qasm`: Inverse quantum Fourier transform using 4 qubits.
- `inverseqft2.qasm`: Another version of the inverse quantum Fourier transform using 4 qubits.
- `ipea_3_pi_8.qasm`: 4-bit Iterative Phase Estimation algorithm for phase 3\pi/8 using two qubits.ss
- `pea_3_pi_8.qasm`: 4-bit Phase Estimation algorithm for a phase 3\pi/8 using 5 qubits.
- `qec.qasm`: Repetition code to correct quantum errors.
- `qft.qasm`: Quantum Fourier transform on 4 qubits.
- `qpt.qasm`: Quantum Process Tomography example.
- `rb.qasm`: Example of a single instance of two-qubits randomized benchmarking.
- `teleport.qasm`: Quantum Teleportation example.
- `teleportv2.qasm`: Quantum Teleportation example (one classical register).
- `W-state.qasm`: Generating a 3-qubit W-state using Toffoli gates

## Quantum Experience

This directory is the start of a list of examples that can run on the IBM Quantum Experience **ibmqx2** device. This device went online January 24th 2017.

The connectivity map for the CNOTS in this device are `coupling_map = {0: [1, 2], 1: [2], 3: [2, 4], 4: [2]}`. Where a: [b] means a CNOT with qubit a as control and b as target can be implemented. It is provided by two coplanar waveguide (CPW) resonators with resonances around 6.0 GHz (coupling Q2, Q3 and Q4) and 6.5 GHz (coupling Q0, Q1 and Q2). Each qubit has a dedicated CPW for control and readout. The following picture shows the chip layout.

<img src=ibmqx2/"images/5qubitQXlabeled.png?raw=true" width="320">

The circuits listed below, which you can find in this directory, are a few examples of experiments that can be ran in this device.

- `iswap.qasm`: Implements the two-qubit entangling gate iSWAP, defined by the matrix: `[1 0 0 0],[0,0,i,0],[0,i,0,0],[0,0,0,1]`.
- `W3test.qasm`: Implements the three-qubit maximally entangled W state |001> + |010> + |100>.
- `Deutsch_Algorithm.qasm`: A two-qubit example of Deutsch to determine whether a function is constant (in which case the algorithm returns 0) or balanced (returns 1). In this example the algorithm looks at the function f(x) = x, which is balanced.
- `011_3_qubit_grover_50_.qasm`: This circuit demonstrate Grover's search algorithm over three qubits. In this case it searchs for the state 110 with probability of success > 50%.
- `qe_qft_3(4)(5).qasm`: Quantum Fourier transforms with 3, 4, and 5 qubits.
