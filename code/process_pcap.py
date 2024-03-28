from scapy.all import *


def split_flow(file_path, ip_filter):
    packets = rdpcap(file_path)

    flow_dict = {}

    for packet in packets:
        if IP in packet and (TCP in packet or UDP in packet):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            src_port = packet[TCP].sport if TCP in packet else packet[UDP].sport
            dst_port = packet[TCP].dport if TCP in packet else packet[UDP].dport

            if src_ip in ip_filter or dst_ip in ip_filter:
                pass
            else:
                continue

            five_tuple = (src_ip, src_port, dst_ip, dst_port, TCP in packet)
            five_tuple_re = (dst_ip, dst_port, src_ip, src_port, TCP in packet)

            if five_tuple not in flow_dict and five_tuple_re not in flow_dict:
                flow_dict[five_tuple] = []
            flow_dict[five_tuple].append(packet) if five_tuple in flow_dict else flow_dict[five_tuple_re].append(packet)

    return flow_dict