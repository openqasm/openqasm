# OpenQASM

OpenQASM is an imperative programming language for describing quantum circuits. It is capable to
describe universal quantum computing using the circuit model, measurement-based model, 
and near-term quantum computing experiments.

## About this project

On this repository, you'll find all the documentation related to OpenQASM and some useful OpenQASM examples.

### Language specs

The live [language documentation](https://qiskit.github.io/openqasm) specification.

### Examples

The examples can be found under the [examples](examples) folder.

They are OpenQASM files, i.e.:

```text
/*
 * Repeat-until-success circuit for Rz(theta),
 * cos(theta-pi)=3/5, from Nielsen and Chuang, Chapter 4.
 */
OPENQASM 3;
include "stdgates.inc";

/*
 * Applies identity if out is 01, 10, or 11 and a Z-rotation by
 * theta + pi where cos(theta)=3/5 if out is 00.
 * The 00 outcome occurs with probability 5/8.
 */
def segment qubit[2]:anc, qubit:psi -> bit[2] {
  bit[2] b;
  reset anc;
  h anc;
  ccx anc[0], anc[1], psi;
  s psi;
  ccx anc[0], anc[1], psi;
  z psi;
  h anc;
  measure anc -> b;
  return b;
}

qubit input;
qubit ancilla[2];
bit flags[2] = "11";
bit output;

reset input;
h input;

// braces are optional in this case
while(int(flags) != 0) {
  flags = segment ancilla, input;
}
rz(pi - arccos(3 / 5)) input;
h input;
output = measure input;  // should get zero
```

## Current version

The latest version is: **3.0**. 

For previous versions see: [2.0](https://arxiv.org/abs/1707.03429v2)

## Citation format

For research papers, we encourage authors to reference.

- Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta "Open Quantum Assembly Language" [[arXiv:1707.03429]](https://arxiv.org/abs/1707.03429).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE] file for details.


## Contributing

If you'd like to help please take a look to our [contribution guidelines](contributing.md).
