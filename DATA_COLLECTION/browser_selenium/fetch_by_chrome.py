import time
import psutil
import csv
from func_timeout import func_set_timeout
import func_timeout
import yaml

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@func_set_timeout(80)
def process(url: str, father, driver):
    flag = 1
    browser_log = dict()
    try:
        driver.set_page_load_timeout(20)
        driver.get(url)

        # Define blocked titles and keywords to check for access restrictions
        blocked_titles = [
            "Attention Required!", "Cloudflare", "Verification Required",
            "Access denied", "Just a moment", "HTTP Status 404",
            "403 Forbidden", "404 Not Found", "Error 404 (Not Found)"
        ]

        blocked_keywords = [
            'restricted area', 'Error 404 (Not Found)', '"status":404',
            'Page Not Found', 'not be found', 'net::ERR_CERT_COMMON_NAME_INVALID',
            'discuss automated access'
        ]

        if any(title in driver.title for title in blocked_titles):
            flag = 0
        if any(keyword in driver.page_source for keyword in blocked_keywords):
            flag = 0
        if 'adobe' in url:
            flag = 0

        time.sleep(3)
        browser_log = driver.get_log('performance')
    except TimeoutException as e:
        error = str(e).split('(Session info')[0]
        print(url, 'resource loading 20s timeout', error)
        if float(error.split(': ')[-1].split('\n')[0]) < 2:
            flag = 0
        driver.execute_script("window.stop();")
        browser_log = driver.get_log('performance')
    except WebDriverException as e:
        error = str(e).split('(Session info')[0]
        print(url, 'webdriver error', error)
        flag = 0
    except Exception as e:
        print(url, 'other errors:', str(e))
        flag = 0
    finally:
        if flag:
            screenshot_path = father+"/screenshot/" + url.replace('.', '_').split('//')[1] + "_screenshot.png"
            driver.get_screenshot_as_file(screenshot_path)
            print(url, 'screenshot generated successful')
        driver.quit()

    # saving browser log while there are no exceptions
    if flag:
        with open(father+'/browser_log/'+url.replace('.', '_').split('//')[1]+'.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for i in range(len(browser_log)):
                writer.writerow(browser_log[i].values())
        print(url, 'browser_log generated successful')

    if flag:
        return 0
    else:
        return -1


def collect_by_url(url: str, father, browser_loc, driver_loc, network_condition):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    chrome_options = webdriver.ChromeOptions()

    # chrome v126
    chrome_options.binary_location = browser_loc
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    service = Service(driver_loc)

    driver = webdriver.Chrome(options=chrome_options, service=service)

    if network_condition == 'unconstrained':
        pass
    elif network_condition == 'starlink-like':
        network_conditions = {
            'offline': False,
            'latency': 50,  # ms
            'downloadThroughput': 70 * 1024 * 1024,  # bytes/s
            'uploadThroughput': 8 * 1024 * 1024,  # bytes/s
            'packetLoss': 6
        }
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', network_conditions)
    elif network_condition == 'slow':
        network_conditions = {
            'offline': False,
            'latency': 350,  # ms
            'downloadThroughput': 800 * 1024,  # bytes/s
            'uploadThroughput': 300 * 1024,  # bytes/s
            'packetLoss': 3
        }
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', network_conditions)

    flag = -1
    try:
        flag = process(url, father, driver)
    except func_timeout.exceptions.FunctionTimedOut:
        print(url, '60s timeout! Attention!')
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.name() == 'chrome':
                    proc.terminate()  # or proc.kill()
                    print('terminate chrome success')
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print('terminate chrome failed', e)
    except Exception as e:
        print(url, 'chrome other error:', e)
        driver.execute_script("window.stop();")
    finally:
        driver.quit()
    return flag


if __name__ == '__main__':
    father = './result'
    with open('./config.yaml', 'r') as configfile:
        config = yaml.safe_load(configfile)
    chrome_loc = config['Data_Collection']['chrome']
    driver_loc = config['Data_Collection']['chrome_driver']
    print(collect_by_url('https://baidu.com', father, chrome_loc, driver_loc, 'unconstrained'))

