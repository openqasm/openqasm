import os
import qiskit
import json
import time

#from executor import Executor 
class QiskitExecutor(object):
  def run_simulation(self, executor, filename):

    q_prog = qiskit.QuantumProgram()

    if executor.backend.startswith("ibmqx"):
      import Qconfig
      q_prog.set_api(Qconfig.APItoken, Qconfig.config['url'])
    elif not executor.backend.startswith("local"):
      raise Exception('only ibmqx or local simulators are supported')

    q_prog.load_qasm_file(filename, name=executor.name)

    start = time.time()
    ret = q_prog.execute([executor.name], backend=executor.backend, shots=1,
    max_credits=5, hpc=None,
    timeout=60*60*24, seed=executor.seed)
    elapsed = time.time() - start

    if not ret.get_circuit_status(0) == "DONE": 
      return -1.0

    if executor.backend.startswith("ibmqx"): 
       elapsed = ret.get_data(executor.name)["time"]

    executor.result = ret.get_counts(executor.name)
    return elapsed

  def verify_result(self, executor):
    if not os.path.exists("qasm/"+executor.name + "/ref"):
        raise Exception("Verification not support for " + executor.name)

    ref_file_name = "qasm/"+executor.name + "/ref/" + os.path.basename(executor.filename)+"."+executor.backend+".ref"
    if not os.path.exists(ref_file_name):
        raise Exception("Reference file not exist: " + ref_file_name)

    ref_file = open(ref_file_name)
    ref_data = ref_file.read()
    ref_file.close()
    ref_data = json.loads(ref_data)
    sim_result_keys = executor.result.keys()

    for key in sim_result_keys:
        if key not in ref_data:
            raise Exception(key + " not exist in " + ref_file_name)
        ref_count = ref_data[key]
        count = executor.result[key]

        if ref_count != count:
            raise Exception(" Count is differ: " + str(count) +
                            " and " + str(ref_count))
