__author__ = 'prototype'
from scapy.all import *
import netifaces
import binascii


def createIPv6():
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
    return ip_packet


def get_source_address(packet):
    interface = packet.route()[0]
    if len(netifaces.ifaddresses(interface)) == 3:
        indexN = netifaces.ifaddresses(interface).keys()[-1]
        src = netifaces.ifaddresses(interface)[indexN][0]["addr"].split("%")[0]
        return src
    else:
        return None


def grabRawSrc(packet):
    rawPacket = binascii.hexlify(str(packet))
    srcAddress = rawPacket[16:20] + rawPacket[32:48]
    return srcAddress


def grabRawDst(packet):
    rawPacket = binascii.hexlify(str(packet))
    dstAddress = rawPacket[48:52] + rawPacket[64:80]
    return dstAddress

def grabFullRawSrc(packet):
    rawPacket = binascii.hexlify(str(packet))
    srcAddress = rawPacket[16:48]
    return srcAddress


def getMacAddress(ip):
    mac = ip.replace(":", "")
    mac = mac[4:10] + mac[14:]
    mac = "%s:%s:%s:%s:%s:%s" % (mac[:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:12])

    flipbit = bin(int(mac[1], 16))[2:]
    while len(flipbit) < 4:
        flipbit = "0" + flipbit
    if flipbit[2] == 0:
        flipbit = flipbit[:2] + "1" + flipbit[3]
    else:
        flipbit = flipbit[:2] + "0" + flipbit[3]

    flipbit = hex(int(flipbit, 2))[2:]
    mac = mac[0] + flipbit + mac[2:]
    return mac
