import csv
import json
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from tqdm import trange
import sys


def generate_subdomain_file(filename, father, flag):
    if flag:
        tmp = father.split('_')
        tmp[-1] = '0'
        with open('_'.join(tmp)+'/browser_log/'+filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = [row[1] for row in reader]
    else:
        with open(father+'/browser_log/'+filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = [row[1] for row in reader]

    domain_list = []

    for i in range(len(data)):
        message = json.loads(data[i])
        if message['message']['method'] == 'Network.responseReceived':
            url = message['message']['params']['response']['url']
            if url.split(':')[0] in ['blob', 'data']:
                continue
            domain_list.append(url.split('//')[1].split('/')[0])

    domain_list = list(set(domain_list))
    with open(father+'/domain_ip/'+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in domain_list:
            writer.writerow([item])


def ipv4_to_int(ipv4):
    return sum(int(byte) << 8 * i for i, byte in enumerate(reversed(ipv4.split('.'))))


def dns_query(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        result = ';'.join([str(ipv4_to_int(rdata.to_text())) for rdata in answers])
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException) as e:
        result = 'error'
        print(f"Error resolving {domain}: {e}")
    return domain, result


def merge_results(previous, current):
    if previous == 'error':
        return current
    if current == 'error':
        return previous
    previous_set = set(previous.split(';'))
    current_set = set(current.split(';'))
    return ';'.join(sorted(previous_set.union(current_set)))


def bulk_dns_query(domains, max_workers=4):
    if not domains:
        return []

    is_one_dimensional = isinstance(domains[0], str)
    if is_one_dimensional:
        domains_to_query = list(set(domains))
    else:
        domains_to_query = list(set(domain[0] for domain in domains))

    domain_to_indices = {}
    for i, domain in enumerate(domains):
        if isinstance(domain, str):
            domain_to_indices.setdefault(domain, []).append(i)
        else:
            domain_to_indices.setdefault(domain[0], []).append(i)

    results = [None] * len(domains)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {executor.submit(dns_query, domain): domain for domain in domains_to_query}
        for future in as_completed(future_to_domain):
            domain, result = future.result()
            indices = domain_to_indices[domain]
            for index in indices:
                if isinstance(domains[index], str):
                    results[index] = [domain, result]
                else:
                    prev_result = domains[index][1]
                    merged_result = merge_results(prev_result, result)
                    results[index] = [domain, merged_result]

    return results


def domain_to_ip_for_file(file, father):
    with open(father+'/domain_ip/'+file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]
    if len(data[0]) == 1:
        data = [item[0] for item in data]
    result = bulk_dns_query(data)

    with open(father+'/domain_ip/'+file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in result:
            writer.writerow(row)


if __name__ == '__main__':
    father = './result'
    csv.field_size_limit(sys.maxsize)
    filelist = os.listdir('./result/browser_log/')
    for i in trange(len(filelist)):
        try:
            filename = filelist[i]
            generate_subdomain_file(filename, father, 0)
            domain_to_ip_for_file(filename, father)
            time.sleep(1)
        except Exception as e:
            print(filelist[i], 'error', e)
