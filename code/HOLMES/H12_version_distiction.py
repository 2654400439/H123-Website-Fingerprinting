from scapy.all import *

def judge_httpv_SH(packets):
    ALPN = ''
    for packet in packets:
        if TCP in packet:
            if packet[TCP].sport == 443:
                if Raw in packet:
                    tcp_payload = packet[Raw].load
                    if tcp_payload[0] == 22:
                        # TLS 1.2
                        if tcp_payload[1:3] == b'\x03\x03':
                            tls_length = int.from_bytes(tcp_payload[3:5], byteorder='big')
                            if tcp_payload[5] == 2:
                                tls_SH = tcp_payload[5:]
                                session_len = tls_SH[38]
                                extension_len = int.from_bytes(tls_SH[42+session_len:44+session_len], byteorder='big')
                                extension_info = tls_SH[44+session_len:44+session_len+extension_len]
                                while True:
                                    extension_type = int.from_bytes(extension_info[:2], byteorder='big')
                                    extension_len_curr = int.from_bytes(extension_info[2:4], byteorder='big')
                                    extension_info_curr = extension_info[4:4+extension_len_curr]
                                    if extension_type == 16:
                                        ALPN = extension_info_curr[-extension_info_curr[2]:].decode('utf-8')
                                        return ALPN
                                    if len(extension_info) == extension_len_curr + 4:
                                        break
                                    extension_info = extension_info[4+extension_len_curr:]
                else:
                    pass
    return ALPN


def judge_httpv_http_len(packets):
    ALPN = 'http/1.1'
    tcp_type_list = []
    for packet in packets:
        if TCP in packet:
            if packet[TCP].dport == 80:
                return ALPN
        if TCP in packet:
            if packet[TCP].dport == 443:
                if Raw in packet:
                    tcp_payload = packet[Raw].load
                    if tcp_payload[0] == 23:
                        tls_payload_len = int.from_bytes(tcp_payload[3:5], byteorder='big')
                        if 60 < len(tcp_payload) < 90:
                            tcp_type_list.append(1)
                        if tls_payload_len < 60:
                            tcp_type_list.append(1)
                        else:
                            if 80 < tls_payload_len < 120:
                                tcp_type_list.append(4)
                                continue
                            if len(tcp_payload) < 38 or tcp_type_list[-1] == 4:
                                ALPN = 'h2'
                                return ALPN
                            tcp_type_list.append(2)
                    else:
                        tcp_type_list.append(1)
                else:
                    tcp_type_list.append(0)
        else:
            tcp_type_list.append(3)

    if 2 not in tcp_type_list:
        ALPN = 'no payload'
    return ALPN

