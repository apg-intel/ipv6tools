from flask import Flask, request, render_template
from flask.ext.socketio import SocketIO, emit
import ipv6.icmpv6 as icmpv6
import ipv6.dns as dns
from collections import Counter
from operator import add
import ipv6.ipv6sniffer as ipv6sniffer
import importlib

PROPAGATE_EXCEPTIONS = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
ns = '/scan'
sniffer = ipv6sniffer.IPv6Sniffer()

mods = []
mod_objects = {}

# flask routes
@app.route('/')
def index():
  mods = get_modules()
  return render_template('index.html', mods=mods)

@socketio.on('sniffer_init', namespace=ns)
def sniffer_init(message):
  sniffer.start(request.namespace, socketio)

@socketio.on('sniffer_kill', namespace=ns)
def sniffer_init(message):
  sniffer.stop()

# socket events
@socketio.on('start_scan', namespace=ns)
def scan(message):
  print("starting scan")
  handler = icmpv6.ICMPv6()
  handler.echoAllNodes()
  handler.echoAllNodeNames()
  handler.echoMulticastQuery()
  handler = dns.DNS()
  handler.mDNSQuery()

@socketio.on('scan_llmnr', namespace=ns)
def scan_llmnr(message):
  if "multicast_report" in message:
    handler = dns.DNS()
    for report in message['multicast_report']:
      if report['multicast_address'] == "ff02::1:3":
        handler.llmnr_noreceive(message['ip'])

@socketio.on('mod_action', namespace=ns)
def mod_action(message): #target,name,action
  action = getattr(mod_objects[message['modname']], message['action'])
  action(message.get('target'))

def get_modules():
    import pkgutil, os.path
    import modules

    pkg = modules
    prefix = pkg.__name__ + "."
    mods = []
    for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__, prefix):
      if not ispkg and modname != "modules.template":
        mod = importlib.import_module(modname)
        modobj = getattr(mod, "IPv6Module")(socketio, ns)
        mod_objects[modobj.modname] = modobj

        mods.append({
          'modname': modobj.modname,
          'actions': modobj.actions
        })
      else:
        print modname
    return mods

if __name__ == '__main__':
    socketio.run(app)
