import csv
import json

csv.field_size_limit(2147483647)


def get_IP_filter(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = [row[1] for row in reader]

    ip_list = []

    # parse log
    for i in range(len(data)):
        message = json.loads(data[i])
        if message['message']['method'] == 'Network.responseReceived':
            protocol = message['message']['params']['response']['protocol']
            if protocol != 'blob' and protocol != 'data':
                ip_info = message['message']['params']['response']['remoteIPAddress']
                ip_list.append(ip_info)

    return list(set(ip_list))


if __name__ == '__main__':
    print(get_IP_filter('../../result/log/zhihu_com.csv'))