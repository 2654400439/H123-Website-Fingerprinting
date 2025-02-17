import time
import psutil
from func_timeout import func_set_timeout
import func_timeout

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException



@func_set_timeout(80)
def process(url: str, father, driver):
    flag = 1
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

    except TimeoutException as e:
        error = str(e).split('(Session info')[0]
        print(url, 'resource loading 20s timeout', error)
        if float(error.split(': ')[-1].split('\n')[0]) < 2:
            flag = 0
        driver.execute_script("window.stop();")
    except WebDriverException as e:
        error = str(e).split('(Session info')[0]
        print(url, 'webdriver error', error)
        flag = 0
    except Exception as e:
        print(url, 'other errors:', str(e))
        flag = 0
    finally:
        driver.quit()

    if flag:
        return 0
    else:
        return -1


def collect_by_url(url: str, father, browser_loc, driver_loc):
    firefox_options = Options()

    firefox_options.binary_location = browser_loc
    firefox_options.add_argument("--headless")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)

    # YGP设置
    profile.set_preference("network.http.http3.enabled", True)
    profile.set_preference("app.normandy.enabled", False)
    profile.set_preference("app.normandy.first_run", False)
    profile.set_preference("app.update.auto", False)
    profile.set_preference("app.update.enabled", False)
    profile.set_preference("browser.cache.disk.capacity", 0)
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.disk.smart_size.enabled", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("browser.casting.enabled", False)
    profile.set_preference("browser.newtabpage.activity-stream.feeds.asrouterfeed", False)
    profile.set_preference("browser.safebrowsing.downloads.remote.enabled", False)
    profile.set_preference("browser.safebrowsing.enabled", False)
    profile.set_preference("browser.safebrowsing.malware.enabled", False)
    profile.set_preference("browser.safebrowsing.phishing.enabled", False)
    profile.set_preference("browser.search.geoip.url", "")
    profile.set_preference("browser.selfsupport.url", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("devtools.cache.disabled", True)
    profile.set_preference("devtools.toolbox.selectedTool", "netmonitor")
    profile.set_preference("dom.disable_open_during_load", False)
    profile.set_preference("extensions.blocklist.enabled", False)
    profile.set_preference("extensions.getAddons.cache.enabled", False)
    profile.set_preference("extensions.update.autoUpdateDefault", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("messaging-system.rsexperimentloader.enabled", False)
    profile.set_preference("network.captive-portal-service.enabled", False)
    profile.set_preference("network.dns.disablePrefetch", True)
    profile.set_preference("network.dnsCacheEntries", 0)
    profile.set_preference("network.http.speculative-parallel-limit", 0)
    profile.set_preference("network.prefetch-next", False)
    profile.set_preference("privacy.trackingprotection.enabled", False)
    profile.set_preference("security.OCSP.enable", 1)

    firefox_options.profile = profile

    firefox_options.set_preference("general.useragent.override",
                                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0")
    firefox_options.set_preference("privacy.resistFingerprinting", False)
    firefox_options.set_preference("privacy.trackingprotection.enabled", False)
    firefox_options.set_preference("privacy.trackingprotection.pbmode.enabled", False)

    service = Service(driver_loc)

    driver = webdriver.Firefox(options=firefox_options, service=service)

    flag = -1
    try:
        flag = process(url, father, driver)
    except func_timeout.exceptions.FunctionTimedOut:
        print(url, '60s timeout! Attention!')
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.name() == 'firefox-bin':
                    proc.terminate()  # or proc.kill()
                    print('terminate firefox success')
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print('terminate firefox failed', e)
    except Exception as e:
        print(url, 'firefox other error:', e)
        driver.execute_script("window.stop();")
    finally:
        driver.quit()

    return flag



