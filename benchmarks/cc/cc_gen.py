"""
To generate a circuit for counterfeit-coin finding
algorithm using 15 coins and the false coin is the third coin,
type the following.

python cc_gen.py -c 15 -f 3

@author Raymond Harry Rudy rudyhar@jp.ibm.com
Updated by Kate Smith kns@uchicago.edu
"""
import sys
import numpy as np
import argparse
import random
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

if sys.version_info < (3, 5):
    raise Exception("Please use Python 3.5 or later")


def print_qasm(circ_qasm,comments=[], outname=None):
    """
        print qasm string with comments
    """
    if outname is None:
        for item in comments:
            print("//" + item)
        print(circ_qasm)
    else:
        if not outname.endswith(".qasm"):
            outfilename = outname + ".qasm"
        
        outfile = open(outfilename, "w")
        
        for item in comments:
            outfile.write("//" + item)
            outfile.write("\n")
        
        outfile.write(circ_qasm)
        outfile.close()



def generate_false(nCoins):
    """
        generate a random index of false coin (counting from zero)
    """
    return random.randint(0, nCoins-1)


def gen_cc_main(nCoins, indexOfFalseCoin):
    """
        generate a circuit of the counterfeit coin problem
    """
    # using the last qubit for storing the oracle's answer
    nQubits = nCoins + 1
    
    cr = ClassicalRegister(nQubits,name='cr')
    qr = QuantumRegister(nQubits,name='qr')
    ccCircuit = QuantumCircuit(qr,cr)

    # Apply Hadamard gates to the first nCoins quantum register
    # create uniform superposition
    for i in range(nCoins):
        ccCircuit.h(i)

    # check if there are even number of coins placed on the pan
    for i in range(nCoins):
        ccCircuit.cx(i, nCoins)

    # perform intermediate measurement to check if the last qubit is zero
    ccCircuit.measure(nCoins,nCoins)

    # proceed to query the quantum beam balance if cr is zero
    ccCircuit.x(nCoins).c_if(cr,0)
    ccCircuit.h(nCoins).c_if(cr,0)

    # we rewind the computation when cr[N] is not zero
    for i in range(nCoins):
        ccCircuit.h(i).c_if(cr, 2**nCoins)

    # apply barrier for marking the beginning of the oracle
    ccCircuit.barrier()

    ccCircuit.cx(indexOfFalseCoin, nCoins).c_if(cr, 0)

    # apply barrier for marking the end of the oracle
    ccCircuit.barrier()

    # apply Hadamard gates to the first nCoins qubits
    for i in range(nCoins):
        ccCircuit.h(i).c_if(cr, 0)

    # measure qr and store the result to cr
    for i in range(nCoins):
        ccCircuit.measure(i,i)

    return ccCircuit


def main(nCoins, falseIndex, outname):
    comments = ["Counterfeit coin finding with " + str(nCoins) + " coins.",
                "The false coin is " + str(falseIndex)]
    if outname is None:
        outname = "cc_n" + str(nCoins + 1)
    qc = gen_cc_main(nCoins, falseIndex)
    
    print_qasm(qc.qasm(), comments, outname)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate qasm of \
                                                  the counterfeit-coin \
                                                  finding algorithm.")
    parser.add_argument("-c", "--coins", type=int, default=16,
                        help="number of coins")
    parser.add_argument("-f", "--false", type=int, default=None,
                        help="index of false coin")
    parser.add_argument("-s", "--seed", default=0,
                        help="the seed for random number generation")
    parser.add_argument("-o", "--output", default=None, type=str,
                        help="output filename")
    args = parser.parse_args()
    # initialize seed
    random.seed(args.seed)

    if args.false is None:
        args.false = generate_false(args.coins)
    main(args.coins, args.false, args.output)
