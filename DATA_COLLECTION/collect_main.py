import os
import csv
from tqdm import trange
import sys
import time
import yaml
import psutil
import subprocess
import argparse
from browsermobproxy import Server
from selenium.webdriver.common.proxy import Proxy, ProxyType

import collect_single_pcap_log_sc
import collect_batch_dns


def init_file_folder(times, network_condition, browser):
    father = f'./result_{browser}_{network_condition}_{times}'
    file_folder = [father, father+'/browser_log', father+'/pcap', father+'/domain_ip', father+'/screenshot']
    for folder in file_folder:
        if not os.path.exists(folder):
            os.mkdir(folder)


def generate_pcap_log_sc(father, browser, domain_list_file, network_condition):
    with open(domain_list_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [row[0] for row in reader]

    for i in range(len(data)):
        try:
            collect_single_pcap_log_sc.main_process(f'http://{data[i]}', father, browser, network_condition)
            post_process(father, data[i], browser)
        except Exception as e:
            print('main error:', data[i], e)
        finally:
            print(f'-----------complete {i}/{len(data)}-----------')


def generate_pcap_log_sc_first_firefox(father, browser, domain_list_file):
    with open(domain_list_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [row[0] for row in reader]

    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)

    proxy_server = config['Data_Collection']['firefox'].split('/firefox')[0] + '/browsermob-proxy-2.1.4/bin/browsermob-proxy'
    server = Server(
        proxy_server)  # Update path to browsermob-proxy
    server.start()
    proxy = server.create_proxy()
    proxy_config = Proxy()
    proxy_config.proxy_type = ProxyType.MANUAL
    proxy_config.http_proxy = proxy.proxy
    proxy_config.ssl_proxy = proxy.proxy

    for i in range(len(data)):
        try:
            collect_single_pcap_log_sc.main_process_firefox_first_time(f'http://{data[i]}', father, proxy_config, proxy)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.name() == 'firefox-bin':
                        proc.terminate()
                        print('kill firefox-bin successfully')
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    print('terminate browser or tcpdump failed', e)
        except Exception as e:
            print('main error:', data[i], e)
        finally:
            print('-----------complete '+str(i)+'/'+str(len(data))+'-----------')

    server.stop()


def generate_domain_ip(father, flag):
    csv.field_size_limit(sys.maxsize)
    if flag:
        tmp = father.split('_')
        tmp[-1] = '0'
        filelist = os.listdir('_'.join(tmp) + '/browser_log/')
    else:
        filelist = os.listdir(father+'/browser_log/')
    for i in trange(len(filelist)):
        try:
            filename = filelist[i]
            collect_batch_dns.generate_subdomain_file(filename, father, flag)
            collect_batch_dns.domain_to_ip_for_file(filename, father)
            time.sleep(1)
        except Exception as e:
            print(filelist[i], 'error', e)


def post_process(father, url, browser):
    # Handling still open chrome and tcpdump processes
    try:
        subprocess.run(['sudo', 'pkill', 'tcpdump'], check=True)
    except Exception as e:
        print(father, 'pkill tcpdump failed', e)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = browser.split('_')[0] if browser != 'firefox' else 'firefox-bin'
            if proc.name() == proc_name or proc.name() == 'tcpdump':
                proc.terminate()
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            print('terminate browser or tcpdump failed', e)
    # Handling oversize pcap file
    pcap_file = father+'/pcap/'+url.replace('.', '_')+'.pcap'
    log_file = father+'/browser_log/'+url.replace('.', '_')+'.csv'
    max_file_size_bytes = 200 * 1024 * 1024
    if os.path.exists(pcap_file):
        if os.path.getsize(pcap_file) > max_file_size_bytes:
            os.remove(pcap_file)
            os.path.exists(log_file) and os.remove(log_file)
            print(url, 'pcap/log/sc deleted - oversize 200mb')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script processes parameters with domain_list, collection times, browser type and network condition.')
    parser.add_argument('--domain', type=str, default='./toy_10_domains.csv', help='csv file with domain list')
    parser.add_argument('--times', type=int, default=10, help='determine data collection times')
    parser.add_argument('--browser', type=str, default='chrome', choices=['chrome', 'chrome_legacy', 'firefox'], help='browser type')
    parser.add_argument('--network', type=str, default='unconstrained', choices=['unconstrained', 'starlink-like', 'slow'], help='determine network condition')
    args = parser.parse_args()

    domain_list_file = args.domain
    times = args.times
    browser_type = args.browser
    network_condition = args.network

    if browser_type == 'firefox':
        if network_condition != 'unconstrained':
            print('main error: cannot modify firefox network condition')
            sys.exit(1)
        father = f'./result_firefox_unconstrained_0'
        init_file_folder(0, network_condition, browser_type)
        generate_pcap_log_sc_first_firefox(father, browser_type, domain_list_file)

    for i in range(times):
        father = f'./result_{browser_type}_{network_condition}_{i+1}'
        init_file_folder(i+1, network_condition, browser_type)
        generate_pcap_log_sc(father, browser_type, domain_list_file, network_condition)
        generate_domain_ip(father, 1 if browser_type == 'firefox' else 0)



