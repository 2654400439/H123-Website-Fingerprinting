import time
import csv
import subprocess
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def collect_log(url: str):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    error = ''

    chrome_options = webdriver.ChromeOptions()

    chrome_options.binary_location = "C:\Program Files\Google\Chrome\chrome-win64-v119\chrome-win64\chrome.exe"
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disk-cache-size=0")

    service = Service("C:\Program Files\Google\Chrome\chromedriver-win64\chromedriver-win64\chromedriver.exe")

    browser_log = dict()
    try:
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(5)

        browser_log = driver.get_log('performance')

        driver.quit()
    except TimeoutException as e:
        error = str(e).split('(Session info')[0]
    except WebDriverException as e:
        error = str(e).split('(Session info')[0]

    # save log
    with open('../result/log/'+url.replace('.', '_').split('//')[1]+'.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(browser_log)):
            writer.writerow(browser_log[i].values())

    return 0


def collect_both(URL: str):
    # load config
    with open('config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)

    OS = config['Base']['OS']

    capture_cmd = ["tcpdump", "-i", "eth0", "-w", '../result/pcap/' + URL.split('//')[1].replace('.', '_') + '.pcap'] if OS == 'Linux' else ["D:/APP_install/wireshark_new/wireshark_update/Wireshark/tshark.exe", "-i", "\\Device\\NPF_{A6AD4CA8-3FB2-4C9F-95AC-A983CC30701F}", "-w", '../result/pcap/' + URL.split('//')[1].replace('.', '_')+'.pcap', "-f", "tcp port 80 or tcp port 443 or udp port 443"]
    capture_process = subprocess.Popen(capture_cmd)

    collect_log(URL)

    capture_process.terminate()
    capture_process.wait()
    if capture_process.returncode is None:
        capture_process.kill()


if __name__ == '__main__':
    collect_both('http://google.com')

