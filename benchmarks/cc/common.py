"""
@author Raymond Harry Rudy rudyhar@jp.ibm.com
"""

from qiskit.tools.visualization import latex_drawer

def print_qasm(aCircuit, comments=[], outname=None):
    """
        print qasm string with comments
    """
    if outname is None:
        for each in comments:
            print("//"+each)
        print(aCircuit)
    else:
        if not outname.endswith(".qasm"):
            outfilename = outname + ".qasm"
        outfile = open(outfilename, "w")
        for each in comments:
            outfile.write("//"+each)
            outfile.write("\n")
        outfile.write(aCircuit)
        outfile.close()


def draw_circuit(aCircuit, outfilename="bv.tex"):
    """
        draw the circuit
    """
    latex_drawer(aCircuit, outfilename, basis="h,x,cx")
