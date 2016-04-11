# Template Class
#   This class is for future modules to extend to allow
#   for easy inheritance of methods and default values
class Template(object):
    # params
    #   sio [required] - reference to the application's socketio instance
    #   ns  [required] - the namespace for socketio
    def __init__(self, sio, ns):
        self.actions = None             # Array of actions. Ex:
                                        # [{
                                        #   "title": "Human Friendly Action Name",
                                        #   "action": "method_name_to_call",
                                        #   "target": True/False (show in right-click menu)
                                        # }]
        self.modname = "Unnamed Module" # Human-friendly module name
        self.socketio = sio             # socketio reference
        self.namespace = ns             # namespace reference

    # Action as defined in self.actions
    # params
    #   None
    def action(self):
        return "Action is not yet defined."

    # Send messages back to the webpage for logging
    # msg [required] - text to output
    def socket_log(self, msg):
        if self.socketio:
            self.socketio.emit('module_output', {'log': msg, 'module': self.modname}, namespace=self.namespace)
        else:
            print msg
