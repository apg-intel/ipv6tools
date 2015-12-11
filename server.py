from flask import Flask, request, render_template
from flask.ext.socketio import SocketIO, emit
import ipv6.icmpv6 as icmpv6
import ipv6.dns as dns
from collections import Counter
from operator import add

from scapy.all import *
from ipv6.ipv6 import getMacFromPacket
import binascii
from multiprocessing.pool import ThreadPool, Pool

PROPAGATE_EXCEPTIONS = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = a[key] + b[key]
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


# flask routes
@app.route('/')
def index():
  return render_template('index.html')

@socketio.on('sniffer_init', namespace='/scan')
def sniffer_init(message):
  print('=================sniffer init=================')
  print(request.namespace)
  pool = ThreadPool(processes=1)
  async_result = pool.apply_async(sniff_listener,[request.namespace])
  # sniff(filter='icmp', prn=sniff_callback)

# socket events
@socketio.on('start_scan', namespace='/scan')
def scan(message):
  handler = icmpv6.ICMPv6()
  all_nodes = handler.echoAllNodes()
  node_names = handler.echoAllNodeNames()
  multicast_report = handler.echoMulticastQuery()
  res = merge(all_nodes,node_names)
  res = merge(res,multicast_report)
  emit('icmp_results', {'data': res})

@socketio.on('scan_dns', namespace='/scan')
def scan_dns(message):
  handler = dns.DNS()
  dns_query = handler.mDNSQuery()
  llmnr_query = handler.llmnr_send_recv(message['res'])
  res2 = merge(llmnr_query,dns_query)
  emit('dns_results', {'data': res2})

@socketio.on('dig_listen', namespace='/scan')
def dig_listen(message):
  handler = dns.DNS()
  dig = handler.dig_and_listen(message['ips'])
  emit('dig_results', {'data': dig})

def sniff_listener(namespace):
  print('***********************async')
  print(namespace)
  sniff(lfilter=lambda (packet): IPv6 in packet, prn=lambda (packet): sniff_callback(packet, namespace), store=0)

def sniff_callback(packet, namespace):
  res = {}
  res['ip'] = packet[IPv6].src
  channel = False

  # icmp node
  if ICMPv6EchoReply in packet:
    channel = 'icmp_echo_result'
    res['mac'] = getMacFromPacket(packet)
  # icmp node name
  elif ICMPv6NIReplyName in packet:
    channel = 'icmp_name_result'
    res['device_name'] = packet[ICMPv6NIReplyName].fields["data"][1][1].strip()
    res['mac'] = getMacFromPacket(packet)
  # multicast report
  elif Raw in packet and binascii.hexlify(str(packet[Raw]))[0:2] == "8f":
    channel = 'multicast_result'
    handler = icmpv6.ICMPv6()
    reports = handler.parseMulticastReport(packet[Raw])
    res['multicast_report'] = reports
    res['mac'] = getMacFromPacket(packet)
  # llmnr
  elif UDP in packet and packet[UDP].dport == 5355 and LLMNRQuery in packet:
    channel = 'llmnr_result'
    try:
      handler = dns.DNS()
      res['dns_data'] = handler.parseLLMNRPacket(packet[LLMNRQuery])
      res['mac'] = getMacFromPacket(packet)
    except Exception:
      pass
  # dns data
  elif UDP in packet and packet[UDP].dport == 5353 and Raw in packet:
    channel = 'mdns_result'
    try:
      handler = dns.DNS()
      res['dns_data'] = handler.parsemDNS(packet[Raw])
      res['mac'] = getMacFromPacket(packet)
    except Exception:
      pass

  if channel:
    socketio.emit(channel, res, namespace=namespace)


if __name__ == '__main__':
    socketio.run(app)
