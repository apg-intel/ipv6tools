from scapy.all import *
import binascii
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Pipe
from copy import copy
from itertools import izip
import time
from dnslib import DNSRecord
from ipv6 import get_source_address, createIPv6, getMacAddress, grabRawSrc, grabRawDst

class ICMPv6:
    def init(self):
        None

    def echoAllNodes(self):
        ip_packet = createIPv6()
        ip_packet.fields["version"] = 6L
        ip_packet.fields["tc"] = 0L
        ip_packet.fields["nh"] = 58
        ip_packet.fields["hlim"] = 1
        ip_packet.fields["dst"] = "ff02::1"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)


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
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            responseDict[ip] = {"mac":mac}
        return responseDict



    def echoAllNodeNames(self):
        ip_packet = createIPv6()
        ip_packet.fields["dst"] = "ff02::1"

        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

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
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            device_name = response[ICMPv6NIReplyName].fields["data"][1][1].strip()
            responseDict[ip] = {"mac":mac,"device_name":device_name}
        return responseDict


    def echoMulticastQuery(self):
        ip_packet = createIPv6()
        ip_packet.fields["dst"] = "ff02::1"
        ip_packet.fields["nh"] = 0


        router_alert = RouterAlert()
        router_alert.fields["otype"] = 5
        router_alert.fields["value"] = 0
        router_alert.fields["optlen"] = 2

        padding = PadN()
        padding.fields["otype"] = 1
        padding.fields["optlen"] = 0

        ip_ext = IPv6ExtHdrHopByHop()
        ip_ext.fields["nh"] = 58
        ip_ext.fields["options"] = [router_alert,padding]
        ip_ext.fields["autopad"] = 1

        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        icmp_packet = ICMPv6MLQuery()
        icmp_packet.fields["code"] = 0
        icmp_packet.fields["reserved"] = 0
        icmp_packet.fields["mladdr"] = "::"
        flags = "02"
        qqic = "7d" #125
        numberOfSources = "0000"
        raw = Raw()
        raw.fields["load"] =  binascii.unhexlify(flags + qqic + numberOfSources)

        filter = lambda (packet): IPv6 in packet
        payload = ip_packet/ip_ext/icmp_packet/raw

        ####Add function here
        responseDict = {}
        responses = self.send_receive(payload,filter,5)
        for response in responses:
            if self.isMulticastReportv2(response):
                reports = self.parseMulticastReport(response[Raw])
                print reports
                ip = response[IPv6].src
                rawSrc = copy(response[IPv6])
                rawSrc.remove_payload()
                rawSrc = grabRawSrc(rawSrc)
                mac = getMacAddress(rawSrc)
                responseDict[ip] = {"mac":mac,"multicast_report":reports}

        return responseDict



    def send_receive(self,payload,filter,timeout=2):
        build_lfilter = filter
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,timeout])

        send(payload)

        responses = async_result.get()
        return responses

    def isMulticastReportv2(self,response):
        if Raw in response and binascii.hexlify(str(response[Raw]))[0:2] == "8f":
            return True



    def echoMulticastReport(self):
        ip_packet = createIPv6()
        ip_packet.fields["dst"] = "ff02::16"

        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        hexStream = "8f009ddc000000010400000000000000000000000000000000000000"
        icmp_packet = ICMPv6Unknown(binascii.unhexlify(hexStream))
        del icmp_packet.fields["cksum"]
        #icmp_packet = ICMPv6MLReport()
        #icmp_packet.fields["code"] = 0
        #icmp_packet.fields["reserved"] = 0
        #icmp_packet.fields["mladdr"] = "ff02::16"
        send(ip_packet/icmp_packet)



    def parseMulticastReport(self,payload):
        responseDict = []
        raw_packet = binascii.hexlify(str(payload))
        type = raw_packet[0:2]
        code = raw_packet[2:4]
        cksum = raw_packet[4:8]
        reserved = raw_packet[8:12]
        num_of_records = int(raw_packet[12:16],16)
        print type,code,cksum,reserved,num_of_records

        for record in xrange(num_of_records):
            offset = (16 + (40 * record))
            record_data = raw_packet[offset:(offset + 40)]
            record_type = record_data[0:2]
            data_len = record_data[2:4]
            num_of_sources = record_data[4:8]
            multicast_address = record_data[8:40]
            responseDict.append({"record_type": record_type,
                                 "multicast_address":multicast_address})

        return responseDict



    def listenForEcho(self,build_lfilter,timeout=2):
        #build_lfilter = lambda (packet): ICMPv6EchoReply in packet
        #build_lfilter = lambda (packet): ICMPv6NIReplyName in packet
        response = sniff(lfilter=build_lfilter, timeout=timeout)
        return response

    def fuzzington(self):

        ip_packet = createIPv6()
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



    def advertise(self,packet):
        newPacket = packet[1]
        rawDst = copy(newPacket)
        rawDst.remove_payload()
        rawDst = grabRawDst(rawDst)

        ip_packet = createIPv6()
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
        llpacket.fields["lladdr"] = getMacAddress(rawDst)

        #print newPacket.dst
        #print ip_packet.show()
        #print icmp_packet.show()
        #print llpacket.show()
        send(ip_packet / icmp_packet / llpacket)
