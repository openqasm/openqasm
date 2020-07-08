"""
Generate circuits of Quantum Fourier Transform for Quantum Volume analysis.

Example run:
  python qft_gen.py -n 5
updated by Kate Smith kns@uchicago.edu

"""

import sys
import math
import time
import argparse
import numpy as np
from scipy.linalg import qr
from scipy.linalg import det
from qiskit import QuantumCircuit



if sys.version_info < (3, 0):
    raise Exception("Please use Python version 3 or greater.")


def cu1(circ, l, a, b):
    circ.u1(l/2, a)
    circ.cx(a, b)
    circ.u1(-l/2, b)
    circ.cx(a, b)
    circ.u1(l/2, b)


def qft(circ, n):
    """n-qubit QFT on q in circ."""
    for j in range(n):
        for k in range(j):
            cu1(circ, math.pi/float(2**(j-k)), j, k)
#            circ.cu1(math.pi/float(2**(j-k)), q[j], q[k])
        
        circ.h(j)


def build_model_circuits(name, n):
    qftcirc = QuantumCircuit(n)

    qft(qftcirc, n)
    qftcirc.barrier()

    qftcirc.measure_all()


    return qftcirc


def main():
    parser = argparse.ArgumentParser(description="Create circuits \
                                                  of Quantum Fourier \
                                                  Transform for \
                                                  quantum volume analysis.")
    parser.add_argument('--name', default='qft', help='circuit name')
    parser.add_argument('-n', '--qubits', default=5,
                        type=int, help='number of circuit qubits')
    args = parser.parse_args()

    qc = build_model_circuits(name=args.name, n=args.qubits)

    circuit_name = args.name+'_n'+str(args.qubits)
    f = open(circuit_name+'.qasm', 'w')
    f.write(qc.qasm())
    f.close()


if __name__ == "__main__":
    main()