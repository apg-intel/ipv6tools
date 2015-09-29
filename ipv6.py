__author__ = 'prototype'
from scapy.all import *
import netifaces


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
