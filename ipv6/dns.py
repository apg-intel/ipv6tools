from scapy.all import *
import binascii
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Process, Pipe
from copy import copy
from itertools import izip
import time
from itertools import izip_longest
from ipv6 import createIPv6, get_source_address, grabRawDst, grabRawSrc, getMacAddress
from scapy.layers.dns import DNS as scapyDNS
import traceback

class DNS:
    def init(self):
        None

    def digIPv6(self,ip,version=6):
        response_return = ""
        ip_packet = self.createIPv6()
        ip_packet.fields["nh"] = 17 #DNS
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "ff02::fb"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        udp_segment = UDP()
        udp_segment.fields["dport"] = 5353
        udp_segment.fields["sport"] = 5353

        transaction_id = "0002"
        flags = "0000"
        questions = "0001"
        answer_rrs = "0000"
        authority_rrs = "0000"
        additional_rrs = "0000"

        if version == 4:
            questionList = [".".join(ip.split(".")[::-1]) + ".in-addr.arpa"]
        elif version == 6:
            ipaddress = []
            digits = ip.replace(":","")
            digits = digits[:4] + "000000000000" + digits[4:]
            for digit in digits[::-1]:
                ipaddress.append(digit)
            questionList = [".".join(ipaddress) + ".ip6.arpa"]

        payload = ""
        for questionName in questionList:
            queryType = "000c" # domain pointer
            questionIn = "8001"
            payload += binascii.hexlify(str(DNSQR(qname=questionName,qtype='PTR')))[:-4] + "8001"
        queryInfo = transaction_id + flags + "{:04x}".format(len(questionList)) + answer_rrs + authority_rrs + additional_rrs
        payload = queryInfo + payload
        raw = Raw()
        raw.fields["load"] = binascii.unhexlify(payload)


        build_lfilter = lambda (packet): IPv6 in packet and UDP in packet and packet[UDP].dport == 5353




        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,2]) # tuple of args for foo

        send(ip_packet/udp_segment/raw)
        responseDict = {}
        return_val = async_result.get()

        for response in return_val:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            if ip not in responseDict:
                responseDict[ip] = {"mac":mac}

            dnsDict = {}
            try:
                dnsDict = self.parsemDNS(response[Raw])
            except Exception,e: print e
            if dnsDict:
                responseDict[ip].update({"dns_data":dnsDict})
        return response_return



    def dig_and_listen(self,IPList,version=6):
        build_lfilter = lambda (packet): IPv6 in packet and UDP in packet and packet[UDP].dport == 5353
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,9])

        for ip in IPList:
            self.dig_noreceive(ip,version)


        return_val = async_result.get()
        #returnResponse = self.parse_dig(return_val,IPList)

        #Need to fix this
        return None






    def dig_noreceive(self,ip,version=6):
        response_return = ""
        ip_packet = createIPv6()
        ip_packet.fields["nh"] = 17 #DNS
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "ff02::fb"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        udp_segment = UDP()
        udp_segment.fields["dport"] = 5353
        udp_segment.fields["sport"] = 5353

        transaction_id = "0002"
        flags = "0000"
        questions = "0001"
        answer_rrs = "0000"
        authority_rrs = "0000"
        additional_rrs = "0000"

        if version == 4:
            questionList = [".".join(ip.split(".")[::-1]) + ".in-addr.arpa"]
        elif version == 6:
            ipaddress = []
            digits = ip.replace(":","")
            digits = digits[:4] + "000000000000" + digits[4:]
            for digit in digits[::-1]:
                ipaddress.append(digit)
            questionList = [".".join(ipaddress) + ".ip6.arpa"]

        payload = ""
        for questionName in questionList:
            queryType = "000c" # domain pointer
            questionIn = "8001"
            payload += binascii.hexlify(str(DNSQR(qname=questionName,qtype='PTR')))[:-4] + "8001"
        queryInfo = transaction_id + flags + "{:04x}".format(len(questionList)) + answer_rrs + authority_rrs + additional_rrs
        payload = queryInfo + payload
        raw = Raw()
        raw.fields["load"] = binascii.unhexlify(payload)

        send(ip_packet/udp_segment/raw, verbose=False)


    def llmnr_noreceive(self,ip,version=6):
        ip_packet = createIPv6()
        ip_packet.fields["nh"] = 17 #DNS
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "ff02::1:3"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        udp_segment = UDP()
        udp_segment.fields["dport"] = 5355
        udp_segment.fields["sport"] = 5355

        transaction_id = "0002"
        flags = "0000"
        questions = "0001"
        answer_rrs = "0000"
        authority_rrs = "0000"
        additional_rrs = "0000"

        if version == 4:
            questionList = [".".join(ip.split(".")[::-1]) + ".in-addr.arpa"]
        elif version == 6:
            ipaddress = []
            digits = ip.replace(":","")
            digits = digits[:4] + "000000000000" + digits[4:]
            for digit in digits[::-1]:
                ipaddress.append(digit)
            questionList = [".".join(ipaddress) + ".ip6.arpa"]

        payload = ""
        for questionName in questionList:
            queryType = "000c" # domain pointer
            questionIn = "8001"
            payload += binascii.hexlify(str(DNSQR(qname=questionName,qtype='PTR')))[:-4] + "0001"
        queryInfo = transaction_id + flags + "{:04x}".format(len(questionList)) + answer_rrs + authority_rrs + additional_rrs
        payload = queryInfo + payload
        raw = Raw()
        raw.fields["load"] = binascii.unhexlify(payload)
        send(ip_packet/udp_segment/raw)

    def llmnr_send_recv(self,res):
        build_lfilter = lambda (packet): IPv6 in packet and UDP in packet and packet[UDP].dport == 5355

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,2]) # tuple of args for foo

        for ip in res:
            if "multicast_report" in res[ip]:
                for report in res[ip]["multicast_report"]:
                    if report["multicast_address"] == "ff02::1:3":
                        self.llmnr_noreceive(ip)

        return_val = async_result.get()
        return self.parseLLMNR(return_val)

    def parseLLMNR(self,responses):
        responseDict = {}
        for response in responses:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            if ip not in responseDict:
                responseDict[ip] = {"mac":mac}

            dnsDict = {}

            try:
                print response.summary()
                dnsDict = self.parseLLMNRPacket(response[LLMNRQuery])
            except Exception,e: print e
            if dnsDict:
                responseDict[ip].update({"dns_data":dnsDict})
        return responseDict


    def llmnr(self,ip,version=6):
        ip_packet = createIPv6()
        ip_packet.fields["nh"] = 17 #DNS
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "ff02::1:3"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        udp_segment = UDP()
        udp_segment.fields["dport"] = 5355
        udp_segment.fields["sport"] = 5355

        transaction_id = "0002"
        flags = "0000"
        questions = "0001"
        answer_rrs = "0000"
        authority_rrs = "0000"
        additional_rrs = "0000"

        if version == 4:
            questionList = [".".join(ip.split(".")[::-1]) + ".in-addr.arpa"]
        elif version == 6:
            ipaddress = []
            digits = ip.replace(":","")
            digits = digits[:4] + "000000000000" + digits[4:]
            for digit in digits[::-1]:
                ipaddress.append(digit)
            questionList = [".".join(ipaddress) + ".ip6.arpa"]

        payload = ""
        for questionName in questionList:
            queryType = "000c" # domain pointer
            questionIn = "8001"
            payload += binascii.hexlify(str(DNSQR(qname=questionName,qtype='PTR')))[:-4] + "0001"
        queryInfo = transaction_id + flags + "{:04x}".format(len(questionList)) + answer_rrs + authority_rrs + additional_rrs
        payload = queryInfo + payload
        raw = Raw()
        raw.fields["load"] = binascii.unhexlify(payload)


        if "src" in ip_packet.fields:
            build_lfilter = lambda (packet): IPv6 in packet and packet[IPv6].dst == ip_packet.fields["src"]
        else:
            src = ip_packet.route()[1]
            print src
            build_lfilter = lambda (packet): IPv6 in packet and packet[IPv6].dst == src






        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,2]) # tuple of args for foo

        send(ip_packet/udp_segment/raw)
        responseDict = {}
        return_val = async_result.get()

        for response in return_val:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            responseDict[ip] = {"mac":mac}

            dnsDict = {}
            try:
                dnsDict = self.parsemDNS(response[Raw])
            except Exception,e: print e

            responseDict[ip].update({"dns_data":dnsDict})
        return responseDict

    def grouper(self,iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return izip_longest(*args, fillvalue=fillvalue)

    def chunker(self,seq, size):
        return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


    def mDNSQuery(self):
        ip_packet = createIPv6()
        ip_packet.fields["nh"] = 17 #DNS
        ip_packet.fields["hlim"] = 255
        ip_packet.fields["dst"] = "ff02::fb"
        if "src" not in ip_packet.fields:
            ip_packet.fields["src"] = get_source_address(ip_packet)

        udp_segment = UDP()
        udp_segment.fields["dport"] = 5353
        udp_segment.fields["sport"] = 5353

        transaction_id = "0002"
        flags = "0000"
        questions = "0001"
        answer_rrs = "0000"
        authority_rrs = "0000"
        additional_rrs = "0000"

        questionListAll = ['_device-info._tcp','_spotify-connect._tcp','_googlecast._tcp','_services._dns-sd._udp','_apple-mobdev2._tcp','_workstation_tcp', '_http_tcp', '_https_tcp', '_rss_tcp', '_domain_udp', '_ntp_udp', '_smb_tcp', '_airport_tcp', '_ftp_tcp', '_tftp_udp', '_webdav_tcp', '_webdavs_tcp', '_afpovertcp_tcp', '_nfs_tcp', '_sftp-ssh_tcp', '_apt_tcp', '_ssh_tcp', '_rfb_tcp', '_telnet_tcp', '_timbuktu_tcp', '_net-assistant_udp', '_imap_tcp', '_pop3_tcp', '_printer_tcp', '_pdl-datastream_tcp', '_ipp_tcp', '_daap_tcp', '_dacp_tcp', '_realplayfavs_tcp', '_raop_tcp', '_rtsp_tcp', '_rtp_udp', '_dpap_tcp', '_pulse-server_tcp', '_pulse-sink_tcp', '_pulse-source_tcp', '_mpd_tcp', '_vlc-http_tcp', '_presence_tcp', '_sip_udp', '_h323_tcp', '_presenc_olp', '_iax_udp', '_skype_tcp', '_see_tcp', '_lobby_tcp', '_postgresql_tcp', '_svn_tcp', '_distcc_tcp', '_MacOSXDupSuppress_tcp', '_ksysguard_tcp', '_omni-bookmark_tcp', '_acrobatSRV_tcp', '_adobe-vc_tcp', '_pgpkey-hkp_tcp', '_ldap_tcp', '_tp_tcp', '_tps_tcp', '_tp-http_tcp', '_tp-https_tcp', '_workstation._tcp', '_http._tcp', '_https._tcp', '_rss._tcp', '_domain._udp', '_ntp._udp', '_smb._tcp', '_airport._tcp', '_ftp._tcp', '_tftp._udp', '_webdav._tcp', '_webdavs._tcp', '_afpovertcp._tcp', '_nfs._tcp', '_sftp-ssh._tcp', '_apt._tcp', '_ssh._tcp', '_rfb._tcp', '_telnet._tcp', '_timbuktu._tcp', '_net-assistant._udp', '_imap._tcp', '_pop3._tcp', '_printer._tcp', '_pdl-datastream._tcp', '_ipp._tcp', '_daap._tcp', '_dacp._tcp', '_realplayfavs._tcp', '_raop._tcp', '_rtsp._tcp', '_rtp._udp', '_dpap._tcp', '_pulse-server._tcp', '_pulse-sink._tcp', '_pulse-source._tcp', '_mpd._tcp', '_vlc-http._tcp', '_presence._tcp', '_sip._udp', '_h323._tcp', '_presenc._olp', '_iax._udp', '_skype._tcp', '_see._tcp', '_lobby._tcp', '_postgresql._tcp', '_svn._tcp', '_distcc._tcp', '_MacOSXDupSuppress._tcp', '_ksysguard._tcp', '_omni-bookmark._tcp', '_acrobatSRV._tcp', '_adobe-vc._tcp', '_pgpkey-hkp._tcp', '_ldap._tcp', '_tp._tcp', '_tps._tcp', '_tp-http._tcp', '_tp-https._tcp']
        #questionList = questionList[:50]


        build_lfilter = lambda (packet): IPv6 in packet and UDP in packet and packet[UDP].dport == 5353

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.listenForEcho,[build_lfilter,5]) # tuple of args for foo


        for questionList in self.chunker(questionListAll,20):
            payload = ""
            for questionName in questionList:
                queryType = "000c" # domain pointer
                questionIn = "8001"
                payload += binascii.hexlify(str(DNSQR(qname=questionName + ".local",qtype='PTR')))[:-4] + "8001"
            queryInfo = transaction_id + flags + "{:04x}".format(len(questionList)) + answer_rrs + authority_rrs + additional_rrs
            payload = queryInfo + payload
            raw = Raw()
            raw.fields["load"] = binascii.unhexlify(payload)

            send(ip_packet/udp_segment/raw)

        responseDict = {}
        return_val = async_result.get()

        for response in return_val:
            ip = response[IPv6].src
            rawSrc = copy(response[IPv6])
            rawSrc.remove_payload()
            rawSrc = grabRawSrc(rawSrc)
            mac = getMacAddress(rawSrc)
            if ip not in responseDict:
                responseDict[ip] = {"mac":mac}

            dnsDict = {}

            try:
                dnsDict = self.parsemDNS(response[Raw])
            except Exception,e: print e
            if dnsDict:
                responseDict[ip].update({"dns_data":dnsDict})
        return responseDict


    def parsemDNS(self,raw):
        dnsPacket = scapyDNS(str(raw))
        answer_json = []
        answers = dnsPacket.fields["an"]
        additional_records = dnsPacket.fields["ar"]
        counter = 0

        while True:
            if not answers:
                break
            layer = answers.getlayer(counter)
            if layer:
                answer_json.append({"answer_name": str(layer.fields["rrname"]),
                                    "answer_type": int(layer.fields["type"]),
                                    "answer_data": str(unicode(layer.fields["rdata"],errors="ignore")),
                                    "isAnswer": True})
            else:
                break
            counter += 1

        counter = 0
        while True:
            if not additional_records:
                break
            layer = additional_records.getlayer(counter)
            if layer:
                answer_json.append({"answer_name": str(layer.fields["rrname"]),
                                    "answer_type": int(layer.fields["type"]),
                                    "answer_data": str(unicode(layer.fields["rdata"],errors="ignore")),
                                    "isAnswer": False})
            else:
                break
            counter += 1

        return answer_json

    def parseLLMNRPacket(self,llmnrq):
        dnsPacket = scapyDNS(str(llmnrq))
        answer_json = []
        answers = dnsPacket.fields["an"]
        additional_records = dnsPacket.fields["ar"]
        counter = 0

        while True:
            if not answers:
                break
            layer = answers.getlayer(counter)
            if layer:
                answer_json.append({"answer_name": str(unicode(layer.fields["rdata"],errors="ignore")) + "local.",
                                    "answer_type": 28,
                                    "answer_data": str(layer.fields["rrname"]),
                                    "isAnswer": True})
            else:
                break
            counter += 1

        counter = 0
        while True:
            if not additional_records:
                break
            layer = additional_records.getlayer(counter)
            if layer:
                answer_json.append({"answer_name": str(unicode(layer.fields["rdata"],errors="ignore")) + "local.",
                                    "answer_type": 28,
                                    "answer_data": str(layer.fields["rrname"]),
                                    "isAnswer": False})
            else:
                break
            counter += 1

        return answer_json



    def listenForEcho(self,build_lfilter,timeout=2):
        #build_lfilter = lambda (packet): ICMPv6EchoReply in packet
        #build_lfilter = lambda (packet): ICMPv6NIReplyName in packet
        response = sniff(lfilter=build_lfilter, timeout=timeout)
        return response
