from backends.qiskit_executor import QiskitExecutor
from backends.qsharp_executor import QsharpExecutor
from backends.projectq_executor import ProjectQExecutor

class Executor:
  def __init__(self, backend_name=None, name=None, seed=None):
    #self.executor = executor;
    self.seed = seed;
    self.name = name;
    self.backend_name = backend_name;
    self.backend_list = [QiskitExecutor(self), QsharpExecutor(self), ProjectQExecutor(self)];
    return;

  def get_backend(self, name):
    for backend in self.backend_list:
      if "qiskit_" in name and "qiskit_" in  backend.name:
          return backend;
      if name == backend.name:
          return backend;
