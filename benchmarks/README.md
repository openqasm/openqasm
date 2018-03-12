# QASM-Bench

## OVERVIEW

QSAM-Bench is a quantum-software bencmark suite that helps evaluate quantum volumes and performance of quntum computers and simulators registered as backends in QISKit API. 

## Getting Started

### Setup QISKit

see https://github.com/QISKit/qiskit-sdk-py/#installation

### Generate QASM files

Each directory has a .py file to generate qasm files.
You can generate a qasm file by specifying qubit with `-n` (and depth with `-d`).
For example, 30 qubits QFT is generated with following commands:
```
$ cd qft;
$ python3 qft.py -n 30
$ cat qft_n30.qasm
```

### Run benchmarks

You can run benchmark `run_simbench.py` with following options.

* `-a`: specify an appplication to be evaluated
* `-b`: specify a backend supportted by QISKit
* `-s`: specify a qubit number to start evaluation
* `-e`: specify a qubit number to end evaluation
* `-d`: specify a depth to be evaluated (optional)

For example, the following commands run qft from 10 to 20 qubit with local_qiskit_simulator.
```
$ python3 run_simbench.py -a qft -b local_qiskit_simulator -s 10 -e 20
``` 

## Applications

### Fourier Transform

https://github.com/QISKit/qiskit-tutorial/blob/master/2_quantum_information/fourier_transform.ipynb

### Random Circuite

### SAT
