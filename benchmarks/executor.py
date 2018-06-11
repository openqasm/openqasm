class Executor:
  def __init__(self, executor=None, backend=None, name=None, seed=None):
    self.executor = executor;
    self.backend = backend;
    self.seed = seed;
    self.name = name;
    self.result = None;
    self.filename = None;
    return;

  def run_simulation(self, filename):
    self.filename = filename;
    if self.executor:
      return self.executor.run_simulation(self, filename);
    else:
      raise NotImplementedError("no support backend");

  def verify_result(self):
    self.executor.verify_result(self);
