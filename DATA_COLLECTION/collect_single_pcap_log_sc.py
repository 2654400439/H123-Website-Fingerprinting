import os
import subprocess
import time
import csv
from tqdm import trange
import yaml

from browser_selenium import fetch_by_chrome
from browser_selenium import fetch_by_chrome_legacy
from browser_selenium import fetch_by_firefox
from browser_selenium import fetch_by_firefox_first_time


def main_process(URL, father, browser_type, network_condition):
    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)
    interface = config['Data_Collection']['network_interface']

    tcpdump_cmd = [
        "sudo",
        "tcpdump",
        "-q",
        "-i", interface,
        "tcp port 80 or tcp port 443 or udp port 443",
        "-w", father+'/pcap/' + URL.split('//')[1].replace('.', '_')+'.pcap'
    ]
    tcpdump_process = subprocess.Popen(tcpdump_cmd)
    time.sleep(1)
    flag = -1

    try:

        if browser_type == 'chrome':
            browser_loc = config['Data_Collection']['chrome']
            driver_loc = config['Data_Collection']['chrome_driver']
            flag = fetch_by_chrome.collect_by_url(URL, father, browser_loc, driver_loc, network_condition)
        elif browser_type == 'firefox':
            browser_loc = config['Data_Collection']['firefox']
            driver_loc = config['Data_Collection']['firefox_driver']
            flag = fetch_by_firefox.collect_by_url(URL, father, browser_loc, driver_loc)
        elif browser_type == 'chrome_legacy':
            browser_loc = config['Data_Collection']['chrome_legacy']
            driver_loc = config['Data_Collection']['chrome_legacy_driver']
            flag = fetch_by_chrome_legacy.collect_by_url(URL, father, browser_loc, driver_loc, network_condition)
        else:
            print('submain error - wrong browser type', URL)
    except Exception as e:
        print('submain error', URL, e)

    # terminate tcpdump
    tcpdump_process.terminate()
    tcpdump_process.wait(2)
    if tcpdump_process.returncode is None:
        tcpdump_process.kill()
    print(URL, 'pcap generated successful')

    pcap_file = father+'/pcap/' + URL.split('//')[1].replace('.', '_') + '.pcap'
    if flag == -1 and os.path.exists(pcap_file):
        os.remove(pcap_file)
        print(URL, 'pcap deleted - flag is -1')

    return 0


def main_process_firefox_first_time(URL, father, proxy_config, proxy):
    with open('../config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)
    browser_loc = config['Data_Collection']['firefox']
    driver_loc = config['Data_Collection']['firefox_driver']
    try:
        fetch_by_firefox_first_time.collect_by_url(URL, father, proxy_config, proxy, browser_loc, driver_loc)
    except Exception as e:
        print('submain error', URL, e)

    return 0


if __name__ == '__main__':
    url = ''
    father = './result'

    with open('./toy_10_domain.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [row[0] for row in reader]
    print(data)

    for i in trange(len(data)):
        try:
            main_process('http://'+data[i], father, browser_type='chrome', network_condition='unconstrained')
        except Exception as e:
            pass
        finally:
            subprocess.run(['pkill', 'tcpdump'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)









