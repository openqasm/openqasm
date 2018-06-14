""" QSAM-Bench is a quantum-software bencmark suite """
import math
from qiskit.qasm import Qasm
from qiskit import QuantumProgram

class QFT:
  def __init__(self,seed):
    self.name = "qft"
    self.seed = seed

  def cu1(self, circ, l, a, b):
    circ.u1(l/2, a)
    circ.cx(a, b)
    circ.u1(-l/2, b)
    circ.cx(a, b)
    circ.u1(l/2, b)

  def qft(self, circ, q, n):
    """n-qubit QFT on q in circ."""
    for j in range(n):
      for k in range(j):
        self.cu1(circ, math.pi/float(2**(j-k)), q[j], q[k])
        circ.h(q[j])

  def build_model_circuits(self, n):
    qp = QuantumProgram()
    q = qp.create_quantum_register("q", n)
    c = qp.create_classical_register("c", n)

    qftcirc = qp.create_circuit("meas", [q], [c])

    self.qft(qftcirc, q, n)
    qftcirc.barrier(q)

    for j in range(n):
      qftcirc.measure(q[j], c[j])

    qp.add_circuit("qft"+"_n"+ str(n), qftcirc)
    return qp

  def gen_application(self, qubits=0, depth=0):
    qp = self.build_model_circuits(qubits)
    qasm_data = qp.get_qasm(name="qft"+"_n"+str(qubits))
    return qasm_data;
