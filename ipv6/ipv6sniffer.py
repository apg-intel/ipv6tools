from scapy.all import *
from ipv6 import getMacFromPacket
import dns as dns
import icmpv6 as icmpv6
import binascii
from multiprocessing.pool import ThreadPool

class IPv6Sniffer:
    pool = None
    stopped = False

    def init(self):
        None

    # initialize the listener
    def start(self, namespace, socketio):
        print("sniffer intialized on " + namespace)
        self.socketio = socketio
        self.stopped = False
        self.pool = ThreadPool(processes=1)
        self.pool.apply_async(self.listen,[namespace])

    # start the listener
    def listen(self, namespace):
        res = sniff(lfilter=lambda (packet): IPv6 in packet,
            prn=lambda (packet): self.callback(packet, namespace),
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
    def callback(self, packet, namespace):
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
                # extract name from dns response type 28
                for entry in dns_data:
                    if entry['answer_type'] == 28:
                        res['device_name'] = entry['answer_name']
              else:
                res = None
            except Exception:
              pass

        if channel and res:
            self.socketio.emit(channel, res, namespace=namespace)
