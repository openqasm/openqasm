# OpenQASM


OpenQASM is an imperative programming language for describing quantum circuits. It is capable to
describe universal quantum computing using the circuit model, measurement-based model,
and near-term quantum computing experiments.

This repo contains the OpenQASM specification, examples, and tools for the OpenQASM intermediate representation.

OpenQASM is a [Qiskit project](https://qiskit.org).

## :bangbang: Call for TSC Applicants! :bangbang:

We are currently looking for applications to join the [Technical Steering Committee](https://github.com/openqasm/openqasm/blob/main/governance.md#structures).
If you are interested in standing in the election, please contact Jake Lishman, the current Secretary, at [jake.lishman@ibm.com](mailto:jake.lishman@ibm.com) before the 4th of November.

Please familiarize yourself with the expectation of the role before sending an email about your candidacy.
You must already be a [Contributor](https://github.com/openqasm/openqasm/blob/main/governance.md#structures) to the project, or have previously secured the nomination of one of the current TSC members.

The election will be held in the OpenQASM TSC meeting (open to all Contributors) on Friday the 11th of November.

## Current version: **3.0**

Live doc: [**version 3.0**](https://openqasm.github.io/)

For previous version see: [2.0](https://github.com/openqasm/openqasm/tree/OpenQASM2.x)

## About this project

On this repository, you'll find all the documentation related to OpenQASM, some useful OpenQASM examples, and [plugins for some text editors](#plugins).

### Language specs

The live [language documentation](https://openqasm.github.io/) specification.

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
def segment qubit[2] anc, qubit psi -> bit[2] {
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
qubit[2] ancilla;
bit[2] flags = "11";
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

## Citation format

For research papers, we encourage authors to reference.

- [Version 3.0] Andrew W. Cross, Ali Javadi-Abhari, Thomas Alexander, Niel de Beaudrap, Lev S. Bishop, Steven Heidel, Colm A. Ryan, John Smolin, Jay M. Gambetta, Blake R. Johnson "OpenQASM 3: A broader and deeper quantum assembly language" [[arxiv:2104.14722]](https://arxiv.org/abs/2104.14722).
- [Previous Version: 2.0] Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta "Open Quantum Assembly Language" [[arXiv:1707.03429]](https://arxiv.org/abs/1707.03429).

## Governance

The OpenQASM project has a process for accepting changes to the language and making decisions codified in its [governance model](governance.md).


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.


## Contributing

If you'd like to help please take a look to our [contribution guidelines](CONTRIBUTING.md). This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Release Notes

See the section on Release Notes [contribution guidelines](CONTRIBUTIING.md#release-notes)
