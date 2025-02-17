from scapy.all import *


def judge_httpv_http_len(packets):
    httpv = 'http/1.1'
    tcp_type_list = []
    for packet in packets:
        src_ip = packet[IP].src
        if TCP in packet:
            if packet[TCP].dport == 80:
                return httpv
            if packet[TCP].dport == 443:
                if Raw in packet:
                    tcp_payload = packet[Raw].load
                    if tcp_payload[0] == 23:
                        tls_payload_len = int.from_bytes(tcp_payload[3:5], byteorder='big')
                        if 60 < len(tcp_payload) < 90:
                            tcp_type_list.append(1)
                        if 4 in tcp_type_list and tls_payload_len < 38:
                            httpv = 'h2'
                            return httpv

                        if tls_payload_len < 60:
                            tcp_type_list.append(1)
                        else:
                            if 80 < tls_payload_len < 120:
                                tcp_type_list.append(4)
                                continue
                            if len(tcp_payload) < 38:
                                httpv = 'h2'
                                return httpv
                            elif len(tcp_type_list) >= 1:
                                if tcp_type_list[-1] == 4:
                                    httpv = 'h2'
                                    return httpv
                            tcp_type_list.append(2)
                    else:
                        tcp_type_list.append(1)
                else:
                    tcp_type_list.append(0)
        else:
            tcp_type_list.append(3)

    if 2 not in tcp_type_list:
        httpv = 'no payload'
    return httpv


if __name__ == '__main__':
    packets = rdpcap("./check_h1_h2.pcapng")
    print(judge_httpv_http_len(packets))