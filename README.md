# OpenQASM
Specs, examples and tools for the OpenQASM intermediate representation.

## Current version

The latest version is: __2.0__

## About this project
On this repository you'll find all the documentation related to the OpenQASM in PDF, including the sources to generate it. Also some useful OpenQASM examples.

### Language specs

The language documentation is available under the [spec folder](https://github.com/QISKit/openqasm/tree/master/spec).

### Examples

The examples can be found under the [examples folder](https://github.com/QISKit/openqasm/tree/master/examples).

They are OpenQASM files, i.e.:
```
// Repetition code syndrome measurement
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
qreg a[2];
creg c[3];
creg syn[2];
gate syndrome d1,d2,d3,a1,a2 
{ 
  cx d1,a1; cx d2,a1; 
  cx d2,a2; cx d3,a2; 
}
x q[0]; // error
barrier q;
syndrome q[0],q[1],q[2],a[0],a[1];
measure a -> syn;
if(syn==1) x q[0];
if(syn==2) x q[2];
if(syn==3) x q[1];
measure q -> c;
```

## Authors (alphabetical)

Lev S. Bishop, Antonio Córcoles, Andrew W. Cross, Jay M. Gambetta, and John A. Smolin

Anyone who contributes to this project can include their name here.

## Citation format

For research papers, we encourage authors to reference 

* Andrew W. Cross, Lev S. Bishop, John A. Smolin, Jay M. Gambetta "Open Quantum Assembly Language" [[arXiv:1707.03429]](https://arxiv.org/abs/1707.03429).

## Other QISKit projects

* [ibmqx backend information](https://github.com/QISKit/ibmqx-backend-information) Information about the different IBM Q experience backends.
* [ibmqx user guide](https://github.com/QISKit/ibmqx-user-guides) The users guides for the IBM Q experience.
* [Python API](https://github.com/QISKit/qiskit-api-py) API Client to use IBM Q experience in Python.
* [Python SDK](https://github.com/QISKit/qiskit-sdk-py) Software development kit for working with quantum programs in Python.
* [Tutorials](https://github.com/QISKit/qiskit-tutorial) Jupyter notebooks for using QISKit.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Thanks to the awesome [Quantum Experience Community](https://quantumexperience.ng.bluemix.net) who posted their thoughts and inputs to the OpenQASM

