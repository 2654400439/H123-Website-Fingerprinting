from scapy.all import *
from collections import defaultdict
import argparse

import H12_distinguish_by_http_len
import FSM_H1
import FSM_H2
import FSM_H3


def is_google_account_ip(ip):
    return (ip.startswith("172.25") or ip.startswith("142.25")) and ip.endswith(".84")


def split_flow(file_path):
    packets = rdpcap(file_path)
    flow_dict = defaultdict(list)

    for packet in packets:
        if IP in packet and (TCP in packet or UDP in packet):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst

            if TCP in packet:
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                is_tcp = True
            else:
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                is_tcp = False

            if is_google_account_ip(src_ip) or is_google_account_ip(dst_ip):
                continue

            five_tuple = (src_ip, src_port, dst_ip, dst_port, is_tcp)
            five_tuple_re = (dst_ip, dst_port, src_ip, src_port, is_tcp)

            if five_tuple_re in flow_dict:
                flow_dict[five_tuple_re].append(packet)
            else:
                flow_dict[five_tuple].append(packet)

    return flow_dict


def generate_H123(file):
    flow_dict = split_flow(file_path=file)

    key_list = list(flow_dict.keys())

    predict_httpv, predict_resource_num, predict_resource_num_list, predict_resource_httpv_list = [], [], [], []
    for i in range(len(key_list)):
        # step1 distinguish http version
        ALPN = ''
        if not key_list[i][-1]:
            if len(flow_dict[key_list[i]]) > 20:
                ALPN = 'h3'
                predict_httpv.append(key_list[i][2] + '_' + ALPN)
        else:
            ALPN = H12_distinguish_by_http_len.judge_httpv_http_len(flow_dict[list(flow_dict.keys())[i]])
            if ALPN != 'no payload':
                predict_httpv.append(key_list[i][2] + '_' + ALPN)

        # step2 infer resource quantity
        resource_num = 0
        if ALPN == 'http/1.1':
            try:
                resource_num, resource_timestamp = FSM_H1.check_with_h1fsm(flow_dict[key_list[i]])
            except Exception as e:
                print(key_list[i], 'h1')
        elif ALPN == 'h2':
            try:
                resource_num, burst = FSM_H2.check_with_h2fsm(flow_dict[key_list[i]])
            except Exception as e:
                print(key_list[i], 'h2')
        elif ALPN == 'h3':
            try:
                resource_num, burst = FSM_H3.check_with_h3fsm(flow_dict[key_list[i]])
            except Exception as e:
                print(key_list[i], 'h3')
        else:
            resource_num = 0
        if resource_num == 0:
            ALPN = 'no payload'
        predict_resource_num += [key_list[i][2] + '_' + ALPN] * resource_num if ALPN != 'no payload' else []
        predict_resource_num_list.append(resource_num)
        predict_resource_httpv_list.append(ALPN)

    predict_resource_num_list = [item for item in predict_resource_num_list if item != 0]
    predict_resource_httpv_list = [item for item in predict_resource_httpv_list if
                                   item == 'http/1.1' or item == 'h2' or item == 'h3']
    predict_resource_httpv_list = ['h1' if x == 'http/1.1' else x for x in predict_resource_httpv_list]
    return predict_resource_num_list, predict_resource_httpv_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--F', type=str, default='./HOLMES_unit_test/test4_doi_org.pcap', help='raw pcap file')
    args = parser.parse_args()

    pcap_file = args.F

    result = generate_H123(pcap_file)

    print('H123-compact:')
    print(result)

    matrix = [[0] * len(result[0]) for _ in range(3)]
    for i, (value, attr) in enumerate(zip(result[0], result[1])):
        if attr == 'h1':
            matrix[0][i] = value
        elif attr == 'h2':
            matrix[1][i] = value
        elif attr == 'h3':
            matrix[2][i] = value
    print('H123:')
    print(matrix)