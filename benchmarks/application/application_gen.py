from application.qft import QFT

class ApplicationGenerator:
  def __init__(self, seed):
    #self.executor = executor;
    self.application_list = [QFT(seed)]
    return;

  def get_app(self, name):
    for app in self.application_list:
      if name == app.name:
          return app;
