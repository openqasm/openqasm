# OpenQASM

OpenQASM is an imperative programming language for describing quantum circuits. It is capable of
describing universal quantum computing using the circuit model, measurement-based model,
and near-term quantum computing experiments.

This repo contains the OpenQASM specification, examples, and tools for the OpenQASM intermediate representation.

OpenQASM started as a [Qiskit project](https://qiskit.org)

## :bangbang: Call for Candidates for TSC Membership! :bangbang:

The OpenQASM Technical Steering Committee has called an election opening 2024-12-15 and ending 2025-01-15. The electors will be directed to an online election platform for their votes. At this time, all three (3) members with expiring terms have indicated they are candidates for re-election. An [Issue is open in the OpenQASM Github repository soliciting further candidates](https://github.com/openqasm/openqasm/issues/572)

## :bangbang: Call for Applicants for TSC Secretary! :bangbang:

We are searching for candidates for the role of [TSC Secretary](governance.md#tsc-secretary).
The TSC will select a new Secretary during a TSC meeting in April, 2025.
Candidates should familiarize themselves with the [responsibilties of the role](governance.md#tsc-secretary).
If you are interested in presenting yourself as a candidate, please contact Jack Woehr,
the current Secretary, at [jack.woehr@procern.com](mailto:jack.woehr@procern.com) before April, 2025.

## Current version: **3.1**

* Live language specification [**version 3.1**](https://openqasm.github.io/)

* The branch of this repository for the previous version: [OpenQASM 2.0](https://github.com/openqasm/openqasm/tree/OpenQASM2.x)

## About this project

In this repository, you'll find all the documentation related to OpenQASM, some useful OpenQASM examples, and a reference grammar.

### Language specs

The live [language documentation](https://openqasm.github.io/) specification.

### Implementations

See this [list of software that implements or supports OpenQASM 3](./implementations.md).

### Examples

An example of OpenQASM 3.0 source code is given below. Several more examples may be found in the [examples folder](examples).

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

* [Version 3.0] Andrew W. Cross, Ali Javadi-Abhari, Thomas Alexander, Niel de Beaudrap, Lev S. Bishop, Steven Heidel, Colm A. Ryan, John Smolin, Jay M. Gambetta, Blake R. Johnson "OpenQASM 3: A broader and deeper quantum assembly language" [[arxiv:2104.14722]](https://arxiv.org/abs/2104.14722).
* [Previous Version: 2.0] Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta "Open Quantum Assembly Language" [[arXiv:1707.03429]](https://arxiv.org/abs/1707.03429).

## Governance

The OpenQASM project has a process for accepting changes to the language and making decisions codified in its [governance model](governance.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## Contributing

If you'd like to help please take a look to our [contribution guidelines](CONTRIBUTING.md). This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Release Notes

See the section on Release Notes [contribution guidelines](CONTRIBUTING.md#release-notes).
