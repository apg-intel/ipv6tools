from flask import Flask, request, render_template
from flask.ext.socketio import SocketIO, emit
import ipv6.icmpv6 as icmpv6
import ipv6.dns as dns
from collections import Counter
from operator import add
import ipv6.ipv6sniffer as ipv6sniffer

PROPAGATE_EXCEPTIONS = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
sniffer = ipv6sniffer.IPv6Sniffer()

mods = {}

# flask routes
@app.route('/')
def index():
  mods = get_modules()
  tmp = []
  for k,v in mods.iteritems():
    tmp.append({
      'title': v['title'],
      'name': k
    })

  return render_template('index.html', mods=tmp)

@socketio.on('mod_action', namespace='/scan')
def mod_action(message):
  mods[message['name']]['action'](message['target'])

@socketio.on('sniffer_init', namespace='/scan')
def sniffer_init(message):
  sniffer.start(request.namespace, socketio)

@socketio.on('sniffer_kill', namespace='/scan')
def sniffer_init(message):
  sniffer.stop()

# socket events
@socketio.on('start_scan', namespace='/scan')
def scan(message):
  print("starting scan")
  handler = icmpv6.ICMPv6()
  handler.echoAllNodes()
  handler.echoAllNodeNames()
  handler.echoMulticastQuery()
  handler = dns.DNS()
  handler.mDNSQuery()

@socketio.on('scan_llmnr', namespace='/scan')
def scan_llmnr(message):
  if "multicast_report" in message:
    handler = dns.DNS()
    for report in message['multicast_report']:
      if report['multicast_address'] == "ff02::1:3":
        handler.llmnr_noreceive(message['ip'])


def get_modules():
    import pkgutil, os.path, importlib
    import modules

    pkg = modules
    prefix = pkg.__name__ + "."

    for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__, prefix):
      mod = importlib.import_module(modname)
      action = getattr(mod, "action")
      menu_text = getattr(mod, "menu_text")
      mods[modname.replace(prefix, "")] = {
        'title': menu_text,
        'action': action
      }
    return mods

if __name__ == '__main__':
    socketio.run(app)
