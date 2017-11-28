# Checking the version of PYTHON; we only support 3 at the moment
import sys
import math
import time
if sys.version_info < (3,0):
    raise Exception("Please use Python version 3 or greater.")
    
# useful additional packages
#import matplotlib.pyplot as plt
#%matplotlib inline
import numpy as np
from scipy.linalg import qr
sys.path.append("../../qiskit-sdk-py")
# importing the QISKit
from qiskit import QuantumProgram
#import Qconfig
from qiskit.mapper import two_qubit_kak
# import basic plot tools
#from qiskit.tools.visualization import plot_histogram
 
def random_unitary(n):
    """Return an n x n Haar distributed unitary matrix.
    Return numpy array.
    """
    X = (1.0/math.sqrt(2.0))*(np.random.randn(n, n) +
                              1j*np.random.randn(n, n))
    Q, R = qr(X)
    R = np.diag(np.diag(R)/np.abs(np.diag(R)))
    U = np.dot(Q, R)
    return U

def build_model_circuits(name, n, depth, num_circ=1):
    """Create a quantum program containing model circuits.
    The model circuits consist of layers of Haar random
    elements of SU(4) applied between corresponding pairs
    of qubits in a random bipartition.
    name = leading name of circuits
    n = number of qubits
    depth = ideal depth of each model circuit (over SU(4))
    num_circ = number of model circuits to construct
    Return a quantum program.
    """
    qp = QuantumProgram()
    q = qp.create_quantum_register("q", n)
    c = qp.create_classical_register("c", n)
    # Create measurement subcircuit
    meas = qp.create_circuit("meas", [q], [c])
    for j in range(n):
        meas.measure(q[j], c[j])   
    # For each sample number, build the model circuits
    for i in range(num_circ):
        # Initialize empty circuit Ci without measurement
        circuit_i = qp.create_circuit("%s_%d" % (name, i), [q], [c])
        # For each layer
        for j in range(depth):
            # Generate uniformly random permutation Pj of [0...n-1]
            perm = np.random.permutation(n)
            # For each pair p in Pj, generate Haar random SU(4)
            # Decompose each SU(4) into CNOT + SU(2) and add to Ci
            for k in range(math.floor(n/2)):
                qubits = [int(perm[2*k]), int(perm[2*k+1])]
                U = random_unitary(4)
                for gate in two_qubit_kak(U):
                    i0 = qubits[gate["args"][0]]
                    if gate["name"] == "cx":
                        i1 = qubits[gate["args"][1]]
                        circuit_i.cx(q[i0], q[i1])
                    elif gate["name"] == "u1":
                        circuit_i.u1(gate["params"][2], q[i0])
                    elif gate["name"] == "u2":
                        circuit_i.u2(gate["params"][1], gate["params"][2],
                                     q[i0])
                    elif gate["name"] == "u3":
                        circuit_i.u3(gate["params"][0], gate["params"][1],
                                     gate["params"][2], q[i0])
                    elif gate["name"] == "id":
                        pass  # do nothing
            # Remove barriers
            # circuit_i.barrier(q)  # barriers between layers
        circuit_i.barrier(q)  # barrier before measurement
        # Create circuit with final measurement
        qp.add_circuit("%s_%d_meas" % (name, i), circuit_i + meas)
    return qp

def main():
  qp = build_model_circuits(name="test", n=40, depth=40)
  print(qp.get_qasm("test_0_meas"))  

if __name__ == "__main__":
  main()
