/*
 * Variational eigensolver example
 *
 * Goal is to estimate the energy for a fixed set of parameters.
 * The parameters are updated outside of this program and a new
 * OpenQASM circuit is generated for the next iteration.
 */
OPENQASM 3;
include "stdgates.inc";

const n = 10;         // number of qubits
const layers = 3;     // number of entangler layers
const prec = 16;      // precision of all types
const shots = 1000;   // number of shots per Pauli observable

// Parameters could be written to local variables for this
// iteration, but we will request them using kernel functions
kernel get_parameter uint[prec], uint[prec] -> angle[prec];
kernel get_npaulis -> uint[prec]:
kernel get_pauli int[prec] -> bit[2 * n];

// The energy calculation uses fixed point division,
// so we do that calculation in a kernel function
kernel update_energy int[prec], uint[prec],
 fixed[prec,prec] -> fixed[prec,prec];

gate entangler qubit[n]:q { for i in [0:n-2] { cx q[i], q[i+1]; } }
def xmeasure qubit:q -> bit { h q; return measure q; }
def ymeasure qubit:q -> bit { s q; h q; return measure q; }

/* Pauli measurement circuit.
 * The first n-bits of spec are the X component.
 * The second n-bits of spec are the Z component.
 */
def pauli_measurement(bit[2*n]:spec) qubit[n]:q -> bit {
  bit b = 0;
  for i in [0: n - 1] {
    bit temp;
    if(spec[i]==1 && spec[n+i]==0) { xmeasure q[i] -> temp; }
    if(spec[i]==0 && spec[n+i]==1) { measure q[i] -> temp; }
    if(spec[i]==1 && spec[n+i]==1) { ymeasure q[i] -> temp; }
    b ^= temp;
  }
  return b;
}

// Circuit to prepare trial wave function
def trial_circuit qubit[n]:q {
  for l in [0: layers - 1] {
    for i in [0: n - 1] {
      angle[prec] theta;
      get_parameter(l * layers + i) -> theta;
      ry(theta) q[i];
    }
    if(l != layers - 1) entangler q;
  }
}

/* Apply VQE ansatz circuit and measure a Pauli operator
 * given by spec. Return the number of 1 outcomes.
 */
def counts_for_term(bit[2*n]:spec) qubit[n] -> uint[prec] {
  uint[prec] counts;
  for i in [1: shots] {
    bit b;
    reset q;
    trial_circuit q;
    b = pauli_measurement(spec) q;
    counts += int(b);
  }
  return counts;
}

// Estimate the expected energy
def estimate_energy qubit[n]:q -> fixed[prec,prec] {
  fixed[prec, prec] energy;
  uint npaulis = get_npaulis();
  for t in [0:npaulis-1] {
    bit spec[2*n] = get_pauli(t);
    uint[prec] counts;
    counts = counts_for_term(spec) q;
    energy = update_energy(t, counts, energy);
  }
  return energy;
}

qubit q[n];
fixed[prec, prec] energy;

energy = estimate_energy q;
