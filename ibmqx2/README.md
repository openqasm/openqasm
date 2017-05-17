This directory is the start of a list of examples that can run on the IBM Quantum Experience **IBMQX2** device. This device went online January 24th 2017.
The connectivity map for the CNOTS in this device are
```
gates_map = {0: [1, 2], 1: [2], 3: [2, 4], 4: [2]}
```
Where a: [b] means a CNOT with qubit a as control and b as target can be implemented.

The connectivity is provided by two coplanar waveguide (CPW) resonators with resonances around 6.0 GHz (coupling Q2, Q3 and Q4) and 6.5 GHz (coupling Q0, Q1 and Q2). Each qubit has a dedicated CPW for control and readout. The following picture shows the chip layout.


<img src="https://github.com/adcorcol/qiskit-openqasm/blob/master/examples_5Qv2/5qubitQXlabeled.png?raw=true" width="320">


The readout CPW resonators are probed at the following frequencies

R0: 6.530350 GHz  
R1: 6.481848 GHz  
R2: 6.436229 GHz  
R3: 6.579431 GHz  
R4: 6.530225 GHz

The qubits have the following fundamental resonance frequencies

Q0: 5.2723 GHz  
Q1: 5.2145 GHz  
Q2: 5.0289 GHz  
Q3: 5.2971 GHz  
Q4: 5.0561 GHz  

With anharmonicities

D0: -330.3 MHz  
D1: -331.9 MHz  
D2: -331.2 MHz  
D3: -329.4 MHz  
D4: -335.5 MHz  

The coupling energy of the qubits to their CPW readout resonator is around 60 MHz, whereas the couplings to the buses are around 80 MHz.


The circuits listed below, which you can find in this directory, are a few examples of experiments that can be ran in this device.

- iswap.qasm: Implements the two-qubit entangling gate iSWAP, defined by the matrix
[1 0 0 0],[0,0,i,0],[0,i,0,0],[0,0,0,1].

- W3test.qasm: Implements the three-qubit maximally entangled W state |001> + |010> + |100>.

- Deutsch_Algorithm.qasm: A two-qubit example of Deutsch to determine whether a function is constant (in which case the algorithm returns 0) or balanced (returns 1). In this example the algorithm looks at the function f(x) = x, which is balanced.

- 011\_3\_qubit\_grover_50_.qasm: This circuit demonstrate Grover's search algorithm over three qubits. In this case it searchs for the state 110 with probability of success > 50%.

- qe\_qft\_3(4)(5).qasm: Quantum Fourier transforms with 3, 4, and 5 qubits.
