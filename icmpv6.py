from scapy.all import *
import binascii
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Pipe
from copy import copy
from itertools import izip
import time
from dnslib import DNSRecord

class ICMPv6:
    def init(self):
        None

    def echoAllNodes(self):
        """ #IPv6 Packet
            0                   1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |Version| Traffic Class |           Flow Label                  |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |         Payload Length        |  Next Header  |   Hop Limit   |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                                                               |
           +                                                               +
           |                                                               |
           +                         Source Address                        +
           |                                                               |
           +                                                               +
           |                                                               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                                                               |
           +                                                               +
           |                                                               |
           +                      Destination Address                      +
           |                                                               |
           +                                                               +
           |                                                               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        """

        ip_packet = IPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 1
        ip_packet.fields["dst"] = "ff02::1"

        """
               #ICMPv6 Packet
               0                   1                   2                   3
               0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
              +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
              |     Type      |     Code      |          Checksum             |
              +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
              |                                                               |
              +                         Message Body                          +
              |                                                               |
              +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        """


        icmp_packet = ICMPv6EchoRequest()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["seq"] = 1
        icmp_packet.fields["type"] = 128
        data = "e3d3f15500000000f7f0010000000000101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637"
        icmp_packet.fields["data"] = binascii.unhexlify(data)

        build_lfilter = lambda (packet): ICMPv6EchoReply in packet

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter]) 

        send(ip_packet / icmp_packet,verbose=False)

        responseDict = {}
        return_val = async_result.get()
        for response in return_val:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = self.grabRawSrc(rawSrc)
            mac = self.getMacAddress(rawSrc)
            responseDict[ip] = {"mac":mac}
        return responseDict



    def createIPv6(self):
        ip_packet = IPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 1
        return ip_packet


    def echoAllNodeNames(self):
        ip_packet = self.createIPv6()
        ip_packet.fields["dst"] = "ff02::1"

        icmp_packet = ICMPv6NIQueryName()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["type"] = 139
        icmp_packet.fields["unused"] = 0L
        icmp_packet.fields["flags"] = 0L
        icmp_packet.fields["qtype"] = 2
        icmp_packet.fields["data"] = (0, 'ff02::1')

        build_lfilter = lambda (packet): ICMPv6NIReplyName in packet

        
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter]) 
        


        send(ip_packet / icmp_packet)

        responseDict = {}
        return_val = async_result.get()
        for response in return_val:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = self.grabRawSrc(rawSrc)
            mac = self.getMacAddress(rawSrc)
            device_name = response[ICMPv6NIReplyName].fields["data"][1][1].strip()
            responseDict[ip] = {"mac":mac,"device_name":device_name}
        return responseDict


    def getMacAddress(self,ip):
        mac = ip.replace(":","")
        mac = mac[4:9] + mac[13:]
        mac = "%s:%s:%s:%s:%s:%s" % (mac[:2],mac[2:4],mac[4:6],mac[6:8],mac[8:10],mac[10:12])

        flipbit = bin(int(mac[1],16))[2:]
        while len(flipbit) < 4:
            flipbit = "0" + flipbit
        if flipbit[2] == 0:
            flipbit = flipbit[:2] + "1" + flipbit[3]
        else:
            flipbit = flipbit[:2] + "0" + flipbit[3]

        flipbit = hex(int(flipbit,2))[2:]
        mac = mac[0] + flipbit + mac[2:]
        return mac


    def listenForEcho(self,build_lfilter,timeout=2):
        #build_lfilter = lambda (packet): ICMPv6EchoReply in packet
        #build_lfilter = lambda (packet): ICMPv6NIReplyName in packet
        response = sniff(lfilter=build_lfilter, timeout=timeout)
        print response
        return response

    def fuzzington(self):

        ip_packet = IPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "FE80::C800:6FF:FEF0:8"

        icmp_packet = ICMPv6ND_NS()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["res"] = 0
        icmp_packet.fields["type"] = 135
        icmp_packet.fields["tgt"] = "FE80::C800:6FF:FEF0:8"

        llpacket = ICMPv6NDOptSrcLLAddr()
        llpacket.fields["type"] = 1
        llpacket.fields["len"] = 1
        llpacket.fields["lladdr"] = "00:0c:29:f2:22:1e"

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listen1) # tuple of args for foo

        """
        for x in xrange(100):
            ip_packet.fields["src"] ="fe80::20c:29ff:fed0:57" + "0x{:02x}".format(x)[2:]
            llpacket.fields["lladdr"] = "00:0c:29:d0:57:" + "0x{:02x}".format(x)[2:]
            send(ip_packet / icmp_packet / llpacket)
        async_result.get()
        #self.listen1()

        """
        for x in xrange(255):
            for y in xrange(255):
                ip_packet.fields["src"] ="fe80::20c:29ff:fed0:0" + "0x{:02x}".format(x)[2:] + "0x{:02x}".format(y)[2:]
                llpacket.fields["lladdr"] = "00:0c:29:d0:" + "0x{:02x}".format(x)[2:] + ":" + "0x{:02x}".format(y)[2:]
                send(ip_packet / icmp_packet / llpacket)
            print "done"
            time.sleep(10)
        async_result.get()
        


    def listen1(self):
        build_lfilter = lambda (packet): ICMPv6ND_NS in packet and packet[IPv6].src == "fe80::c800:6ff:fef0:8"
        response = sniff(lfilter=build_lfilter,prn=self.advertise)
        return response

    def grabRawSrc(self,packet):
        rawPacket = binascii.hexlify(str(packet))
        srcAddress = rawPacket[16:20] + rawPacket[32:48]
        return srcAddress

    def grabRawDst(self,packet):
        rawPacket = binascii.hexlify(str(packet))
        dstAddress = rawPacket[48:52] + rawPacket[64:80]
        return dstAddress


    def advertise(self,packet):
        newPacket = packet[1]
        rawDst = copy(newPacket)
        rawDst.remove_payload()
        rawDst = self.grabRawDst(rawDst)

        ip_packet = IPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = newPacket.src
        ip_packet.fields["src"] = newPacket.dst

        icmp_packet = ICMPv6ND_NA()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["res"] = 0
        icmp_packet.fields["type"] = 136
        icmp_packet.fields["O"] = 1L
        icmp_packet.fields["tgt"] = newPacket.dst
        icmp_packet.fields["S"] = 1L
        icmp_packet.fields["R"] = 1L


        llpacket = ICMPv6NDOptSrcLLAddr()
        llpacket.fields["type"] = 2
        llpacket.fields["len"] = 1
        llpacket.fields["lladdr"] = self.getMacAddress(rawDst)

        #print newPacket.dst
        #print ip_packet.show()
        #print icmp_packet.show()
        #print llpacket.show()
        send(ip_packet / icmp_packet / llpacket)
