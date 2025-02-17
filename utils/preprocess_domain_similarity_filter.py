"""
This script provides a method for filtering out non-representative websites from a list. The filtering criteria are as follows:
1. Remove "duplicate" websites: Some websites may have multiple aliases, and classifying them separately does not add value.
2. Remove websites with incomplete data collection: Websites where the data collection failed during the process, resulting in incomplete samples, are excluded. Only websites with valid files collected after at least 40 visits are kept.
3. Remove websites with insufficient network resources: Websites with fewer than 5 network resources are often either blocked by bot detection mechanisms or inherently lack substantial content. Such websites do not offer enough value for identification.

The script will generate a domain exclusion list based on these filters.
"""


import csv
import json
import hashlib
import os
from tqdm import trange
from collections import Counter

csv.field_size_limit(2147483647)

FILEFOLDER = "YOUR_FILE_FOLDER"

def get_resource_GT(filepath: str):
    ip_httpv_list = []

    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = [row[1] for row in reader]

    protocol_list = []
    url_list = []

    for i in range(len(data)):
        message = json.loads(data[i])
        if message['message']['method'] == 'Network.responseReceived':
            protocol = message['message']['params']['response']['protocol']
            if protocol != 'blob' and protocol != 'data':
                protocol_list.append(protocol)
                url_info = message['message']['params']['response']['url']
                md5_hash = hashlib.md5()
                item = url_info.split('/')[-1]
                md5_hash.update(item.encode('utf-8'))
                url_list.append(md5_hash.hexdigest())

    return url_list[1:]


def read_all_log():
    hash_1500 = []
    for i in range(10):
        filefolder = FILEFOLDER + f'/CW_cluster_{i+1}/result_{i+1}_1/result_{i+1}_1/browser_log/'
        filelist = os.listdir(filefolder)

        for file in filelist:
            hash_1500.append(get_resource_GT(filefolder+file))
    return hash_1500


def cal_sim(domain_less):
    filelist = []
    domain_sim = []
    for i in range(10):
        filefolder = FILEFOLDER + f'/CW_cluster_{i+1}/result_{i+1}_1/result_{i+1}_1/browser_log/'
        filelist += os.listdir(filefolder)

    threshold = 0.5
    hash_all = read_all_log()

    for i in range(len(hash_all)):
        hash_alpha = set(hash_all[i])
        if len(hash_alpha) <= 5:
            continue

        for j in range(i + 1, len(hash_all)):
            hash_beta = set(hash_all[j])
            common_elements = hash_alpha & hash_beta

            if len(common_elements) / len(hash_alpha) > threshold:
                domain_sim.append(filelist[j])
    domain_sim = [item.split('.')[0] for item in domain_sim]
    with open('domain_filter.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in domain_sim:
            if item not in domain_less:
                writer.writerow([item, '2'])

    return domain_sim


def find_less_resource():
    domain_less_resource = []
    for i in range(10):
        for j in trange(40):
            filefolder = FILEFOLDER + f'/CW_cluster_{i+1}/result_{i+1}_{j+1}/result_{i+1}_{j+1}/browser_log/'
            filelist = os.listdir(filefolder)

            for file in filelist:
                try:
                    if len(get_resource_GT(filefolder + file)) <= 5:
                        domain_less_resource.append(file)
                except json.decoder.JSONDecodeError as e:
                    print(file, 'load json error:\n', e)

    domain_less_resource = list(set(domain_less_resource))
    domain_less_resource = [row.split('.')[0] for row in domain_less_resource]
    with open('domain_filter.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in domain_less_resource:
            writer.writerow([item, '1'])

    return domain_less_resource


def find_all_40(domain_less, domain_sim):
    all_40_filter = []

    all_pcap = []
    for i in range(10):
        for j in range(40):
            filefolder = FILEFOLDER + f'/CW_cluster_{i+1}/result_{i+1}_{j+1}/result_{i+1}_{j+1}/pcap/'
            filelist = os.listdir(filefolder)
            all_pcap += filelist
    tmp = Counter(all_pcap)
    all_key = list(tmp.keys())
    all_value = list(tmp.values())
    for i in range(len(all_key)):
        if all_value[i] < 39:
            all_40_filter.append(all_key[i].split('.')[0])

    all_log = []
    for i in range(10):
        for j in range(40):
            filefolder = FILEFOLDER + f'/CW_cluster_{i+1}/result_{i+1}_{j+1}/result_{i+1}_{j+1}/browser_log/'
            filelist = os.listdir(filefolder)
            all_log += filelist
    tmp = Counter(all_log)
    all_key = list(tmp.keys())
    all_value = list(tmp.values())
    for i in range(len(all_key)):
        if all_value[i] < 39:
            all_40_filter.append(all_key[i].split('.')[0])

    all_40_filter = list(set(all_40_filter))

    with open('domain_filter.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in all_40_filter:
            if item not in domain_less and item not in domain_sim:
                writer.writerow([item, '3'])


def main_process():
    domain_less_resource = find_less_resource()
    domain_sim = cal_sim(domain_less_resource)
    find_all_40(domain_less_resource, domain_sim)


if __name__ == '__main__':
    main_process()
