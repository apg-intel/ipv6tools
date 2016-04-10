from flask import Flask, request, render_template
from flask.ext.socketio import SocketIO, emit
import importlib
import os
import sys

# import ipv6 stuff
import ipv6.icmpv6 as icmpv6
import ipv6.dns as dns
import ipv6.ipv6sniffer as ipv6sniffer

PROPAGATE_EXCEPTIONS = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
ns = '/scan' #namespace for socketio
sniffer = ipv6sniffer.IPv6Sniffer()

mod_objects = {}

# flask routes
# only route is the index - everything else uses websockets (for now)
@app.route('/')
def index():
  mods = get_modules()
  return render_template('index.html', mods=mods)

# websocket to intialize the main sniffer
# message
#   None
@socketio.on('sniffer_init', namespace=ns)
def sniffer_init(message):
  sniffer.start(request.namespace, socketio)

# websocket to stop the main sniffer
# message
#   None
@socketio.on('sniffer_kill', namespace=ns)
def sniffer_init(message):
  sniffer.stop()

# websocket to perform the initial network scan
# message
#   None
@socketio.on('start_scan', namespace=ns)
def scan(message):
  print("starting scan")
  handler = icmpv6.ICMPv6()
  handler.echoAllNodes()
  handler.echoAllNodeNames()
  handler.echoMulticastQuery()
  handler = dns.DNS()
  handler.mDNSQuery()

# websocket to get the multicast report for a node
# message
#   multicast_report  [required] - multicast report from the node
#   ip                [required] - ip of the node to scan
@socketio.on('scan_llmnr', namespace=ns)
def scan_llmnr(message):
  if "multicast_report" in message:
    handler = dns.DNS()
    for report in message['multicast_report']:
      if report['multicast_address'] == "ff02::1:3":
        handler.llmnr_noreceive(message['ip'])

# websocket to execute a module action
# message
#   modname [required] - name of the module
#   action  [required] - action to perform
#   target  [optional] - target object to perform on
@socketio.on('mod_action', namespace=ns)
def mod_action(message): #target,name,action
  action = getattr(mod_objects[message['modname']], message['action'])
  action(message.get('target'))

# load modules from /modules
def get_modules():
    import pkgutil, os.path
    import modules

    pkg = modules
    prefix = pkg.__name__ + "." #modules.*
    mods = []

    # loop through the modules in the module directory
    for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__, prefix):
      # make sure it's not a package or the template file
      if not ispkg and modname != "modules.template":
        # get the IPv6Module class from the file
        mod = importlib.import_module(modname)
        modobj = getattr(mod, "IPv6Module")(socketio, ns)
        mod_objects[modobj.modname] = modobj

        mods.append({
          'modname': modobj.modname,
          'actions': modobj.actions
        })
    return mods

# run the app
if __name__ == '__main__':

    # we need root rights:
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    print "Server starting on http://127.0.0.1:5000/"
    try:
        socketio.run(app)
    except KeyboardInterrupt:
        print 'Interrupted. Exiting.'
        sys.exit(0)

