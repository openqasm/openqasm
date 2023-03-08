# OpenQASM **2.0**.

Specs, examples and tools for the OpenQASM **2.0** intermediate representation.

## About this project

On this repository you'll find all the documentation related to OpenQASM and some useful OpenQASM examples.

### Language specs

The language documentation is available [here](https://arxiv.org/abs/1707.03429v2).

### Examples

The examples can be found under the [examples](examples) folder.

The examples that cannot necessarily be executed on any existing hardware. You can still run these circuits in a simulator.

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

Examples of invalid code:

- `invalid_missing_semicolon.qasm`
- `invalid_gate_no_found.qasm`

## Citation format

For research papers, we encourage authors to reference.

- Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta "Open Quantum Assembly Language" [[arXiv:1707.03429]](https://arxiv.org/abs/1707.03429).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE] file for details.

## Acknowledgments

- Thanks to the awesome IBM Quantum Experience Community who posted their thoughts and inputs to the OpenQASM.

## Contributing

If you'd like to help please take a look to our [contribution guidelines](contributing.md).
