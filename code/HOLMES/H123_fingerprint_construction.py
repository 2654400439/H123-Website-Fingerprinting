import collect_pcap_log
import process_log
import process_pcap
import H12_version_distiction
import FSM_H1
import FSM_H2
import FSM_H3

import numpy as np
import yaml
import json
import os


def fingerprint_extract(URL):
    # visiting, collecting and saving pcap+log
    collect_pcap_log.collect_both(URL)

    IP_filter = process_log.get_IP_filter('../../result/log/'+URL.split('//')[1].replace('.', '_')+'.csv')

    flow_dict = process_pcap.split_flow(file_path='../../result/pcap/'+URL.split('//')[1].replace('.', '_')+'.pcap', ip_filter=IP_filter)

    key_list = list(flow_dict.keys())

    predict_httpv = []
    predict_resource_num = []
    predict_resource_num_list = []
    predict_resource_httpv_list = []
    for i in range(len(key_list)):
        ALPN = ''
        if not key_list[i][-1]:
            if len(flow_dict[key_list[i]]) > 20:
                ALPN = 'h3'
                predict_httpv.append(key_list[i][2] + '_' + ALPN)
        else:
            ALPN = H12_version_distiction.judge_httpv_SH(flow_dict[list(flow_dict.keys())[i]])
            if ALPN == '':
                ALPN = H12_version_distiction.judge_httpv_http_len(flow_dict[list(flow_dict.keys())[i]])
            if ALPN != 'no payload':
                predict_httpv.append(key_list[i][2] + '_' + ALPN)

        if ALPN == 'http/1.1':
            resource_num = FSM_H1.check_with_h1fsm(flow_dict[key_list[i]])
        elif ALPN == 'h2':
            resource_num = FSM_H2.check_with_h2fsm(flow_dict[key_list[i]])
        elif ALPN == 'h3':
            resource_num = FSM_H3.check_with_h3fsm(flow_dict[key_list[i]])
        else:
            resource_num = 0
        if resource_num == 0:
            ALPN = 'no payload'
        predict_resource_num += [key_list[i][2] + '_' + ALPN] * resource_num if ALPN != 'no payload' else []
        predict_resource_num_list.append(resource_num)
        predict_resource_httpv_list.append(ALPN)

    predict_resource_num_list = [item for item in predict_resource_num_list if item != 0]
    predict_resource_httpv_list = [item for item in predict_resource_httpv_list if item == 'http/1.1' or item == 'h2' or item == 'h3']
    # os.system('rm -rf ../result/log/*')
    # os.system('rm -rf ../result/pcap/*')
    return predict_resource_num_list, predict_resource_httpv_list


def H123_fingerprint_construct(URL):
    # load config
    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)

    max_len = config['H123_fingerprint']['max_len']

    resource_num_list, resource_httpv_list = fingerprint_extract(URL)

    resource_num_list = np.array(resource_num_list[:max_len])

    http1_mask = np.array([1 if item == 'http/1.1' else 0 for item in resource_httpv_list])
    http2_mask = np.array([1 if item == 'h2' else 0 for item in resource_httpv_list])
    http3_mask = np.array([1 if item == 'h3' else 0 for item in resource_httpv_list])

    http1_num = (resource_num_list * http1_mask).reshape(1, -1)
    http2_num = (resource_num_list * http2_mask).reshape(1, -1)
    http3_num = (resource_num_list * http3_mask).reshape(1, -1)

    H123_fingerprint = np.concatenate((http1_num, http2_num, http3_num), axis=0)

    return H123_fingerprint


def H123_fingerprint_construct_save(URL):
    H123_fingerprint = H123_fingerprint_construct(URL).tolist()

    # save as json
    with open('../../result/H123_fingerprint/'+URL.split('//')[1].replace('.', '_')+'.json', 'w') as f:
        json.dump(H123_fingerprint, f)


if __name__ == '__main__':
    URL = 'http://cloudflare.com'
    H123_fingerprint_construct_save(URL)





