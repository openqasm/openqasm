""" QSAM-Bench is a quantum-software bencmark suite """
import argparse
import os.path
import sys
import re
import json
import glob
import operator

from qiskit_executor import QiskitExecutor
from qsharp_executor import QsharpExecutor
from projectq_executor import ProjectQExecutor
from executor import Executor

if sys.version_info < (3, 0):
    raise Exception("Please use Python version 3 or greater.")


def run_benchmark(args, qubit):
    """
    Run simulation by each qasm files
    """
    name = args.name
    backend = args.backend
    depth = int(args.depth)
    seed = args.seed

    if seed:
        seed = int(seed)

    if depth > 0:
        qasm_files = "qasm/" + name + "/" + name + "_n" + \
                     str(qubit) + "_d" + str(depth) + "*.qasm"
        pattern1 =  name + "_n" + str(qubit) + \
                          "_d" + str(depth) + r"[^0-9]*\.qasm"
        pattern2 =  name + "_n" + str(qubit) + "_d" + str(depth) + r"\D.*\.qasm"
    else:
        qasm_files = "qasm/" + name + "/" + name + "_n" + str(qubit) + "*.qasm"
        pattern1 =  name + "_n" + str(qubit) + r"[^0-9]*\.qasm"
        pattern2 =  name + "_n" + str(qubit) + r"\D.*\.qasm"

    qasm_files = glob.glob(qasm_files)

    if not qasm_files:
        raise Exception("No qasm file")

    if backend == "local_qasm_simulator" or backend.startswith("ibmqx"):
        executor = Executor( QiskitExecutor(), backend, name, seed);
    elif backend ==  "Qsharp":
        executor = Executor( QsharpExecutor(), backend, name, seed);
    elif backend ==  "ProjectQ":
        executor = Executor( ProjectQExecutor(), backend, name, seed);
    #elif backend == "QuEST":
    #    exector = Executor( QuESTxecutor() )


    for qasm in qasm_files:

        ret = None
        if not ((re.search(pattern1, os.path.basename(qasm))) or
                (re.search(pattern2, os.path.basename(qasm)))):
            continue
        
        elapsed = executor.run_simulation(qasm)

        if elapsed < 0:
           print("Execution Failed"); 
           return

        print(name + "," + backend + "," + str(qubit) +
              "," + str(depth) + "," + str(elapsed), flush=True)

        if args.verify:
            executor.verify_result()

    return True

def print_qasm_sum(dir_name):
    """
    List qasm files
    """

    if not os.path.exists(dir_name):
        raise Exception("Not find :" + dir_name)

    file_list = glob.glob(dir_name + "/*.qasm")
    qasm_list = []

    for each_file in file_list:
        file_name = os.path.basename(each_file)
        match_q = re.search("_n([0-9]*)", file_name)
        match_d = re.search("n[0-9]*_d([0-9]*)", file_name)

        if not match_q:
            raise Exception("Not find file:" + dir_name)
        qubit = int(match_q.group(1))

        val = filter(lambda bit: bit['qubit'] == qubit, qasm_list)
        val_list = list(val)

        if not len(val_list):
            if match_d:
                depth = int(match_d.group(1))
                qasm_list.append({"qubit": qubit, "depth": depth, "count": 1})
            else:
                qasm_list.append({"qubit": qubit, "count": 1})
        else:
            if match_d:
                depth = int(match_d.group(1))
                depth_val = list(filter(lambda dep:
                                        dep["depth"] == depth, val_list))
                if not len(depth_val):
                    qasm_list.append({"qubit": qubit,
                                      "depth": depth, "count": 1})
                else:
                    depth_val[0]["count"] += 1
            else:
                val_list[0]["count"] += 1

    if "depth" in qasm_list[0]:
        tmp_list = sorted(qasm_list, key=operator.itemgetter("qubit", "depth"))
    else:
        tmp_list = sorted(qasm_list, key=operator.itemgetter("qubit"))

    print("Application : " + dir_name)
    for each_list in tmp_list:
        print_line = "qubit : " + str(each_list["qubit"])
        if "depth" in each_list:
            print_line += " \t  depth : " + str(each_list["depth"])

        print_line += " \t  file : "+str(each_list["count"])

        print(print_line)


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Evaluate the performance of \
                     simulator with and prints a report."))

    parser.add_argument('-a', '--name', default='qft', help='benchmark name')
    parser.add_argument('-s', '--start', default='4',
                        help='minimum qubits for evaluation')
    parser.add_argument('-e', '--end', default='0',
                        help='maximum qubits for evaluation')
    parser.add_argument('-d', '--depth', default='0', help='depth')
    parser.add_argument('-b', '--backend',
                        default='local_qasm_simulator', help='backend name')
    parser.add_argument('-sd', '--seed', default=None,
                        help='the initial seed (int)')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='verify simulation results')
    parser.add_argument('-l', '--list', action='store_true',
                        help='show qasm file')

    return parser.parse_args()


def _main():
    args = parse_args()

    if args.list:
        print_qasm_sum("qasm/"+args.name)
        return

    start_qubit = int(args.start)
    end_qubit = int(args.end)

    if not end_qubit:
        end_qubit = start_qubit

    for qubit in range(int(args.start), end_qubit + 1):
        if not run_benchmark(args, qubit):
            break


def main():
    try:
        _main()
    except KeyboardInterrupt:
        print("Benchmark suite interrupted: exit!")
        sys.exit(1)


if __name__ == "__main__":
    main()
