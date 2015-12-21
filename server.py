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


# flask routes
@app.route('/')
def index():
  return render_template('index.html')

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
  print('scan llmnr')
  if "multicast_report" in message:
    handler = dns.DNS()
    for report in message['multicast_report']:
      if report['multicast_address'] == "ff02::1:3":
        handler.llmnr_noreceive(message['ip'])

if __name__ == '__main__':
    socketio.run(app)
