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


# flask routes
@app.route('/')
def index():
  return render_template('index.html')

@socketio.on('sniffer_init', namespace='/scan')
def sniffer_init(message):
  pool = ThreadPool(processes=1)
  async_result = pool.apply_async(sniff_listener,[request.namespace])

# socket events
@socketio.on('start_scan', namespace='/scan')
def scan(message):
  handler = icmpv6.ICMPv6()
  handler.echoAllNodes()
  handler.echoAllNodeNames()
  handler.echoMulticastQuery()
  handler = dns.DNS()
  dns_query = handler.mDNSQuery()

@socketio.on('scan_llmnr', namespace='/scan')
def scan_llmnr(message):
  if "multicast_report" in message:
    handler = dns.DNS()
    for report in message['multicast_report']:
      if report['multicast_address'] == "ff02::1:3":
        handler.llmnr_noreceive(message['ip'])

def sniff_listener(namespace):
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
      dns_data = handler.parseLLMNRPacket(packet[LLMNRQuery])
      if dns_data:
        res['dns_data'] = dns_data
        res['mac'] = getMacFromPacket(packet)
      else:
        res = None
    except Exception:
      pass
  # dns data
  elif UDP in packet and packet[UDP].dport == 5353 and Raw in packet:
    channel = 'mdns_result'
    try:
      handler = dns.DNS()
      dns_data = handler.parsemDNS(packet[Raw])
      if dns_data:
        res['dns_data'] = dns_data
        res['mac'] = getMacFromPacket(packet)
      else:
        res = None
    except Exception:
      pass

  if channel and res:
    socketio.emit(channel, res, namespace=namespace)


if __name__ == '__main__':
    socketio.run(app)
