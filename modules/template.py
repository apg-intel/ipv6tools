class Template(object):
  def __init__(self, sio, ns):
    self.actions = None
    self.modname = "Unnamed Module"
    self.menu_text = self.modname + "menu item"
    self.socketio = sio
    self.namespace = ns

  def action(self):
    return "Action is not yet defined."

  def socket_log(self, msg):
    print msg
    if self.socketio:
      self.socketio.emit('module_output', {'log': msg, 'module': self.modname}, namespace=self.namespace)
    else:
      print msg
