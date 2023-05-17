import time
import json
from tld import get_fld
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

import utils


def crawl(options, domains, noop, accept):
    """The crawl function visits websites, potentially accepts cookies and saves the
    required info for analysis as a .json file. The cralwer works by filling up a list
    of dictionaries. Every dictionary contains all required info of one page visit/one
    domain visit.

    Args:
        options (selenium.webdriver.chrome.options.Options): The web driver options.
        domains (list) or (str): List of domains or domain as string.
        noop (bool): Boolean representing whether noop was passed as script command.
        accept (bool): Boolean representing whether noop was passed as script command.
    """
    # Load the tracker domains and entities into data.
    with open("services.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create the tracker dictionary and list of tracker domains.
    tracker_dict = utils.get_tracker_dict(data)
    tracker_dict_values = utils.flatten(list(tracker_dict.values()))

    # Loop over all domains passed in the script command. Is a list of one domain if
    # only a single URL is passed(-u).
    # Crawl using num_thread threads
    num_threads = 10

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(crawl_domain, domain, options, noop, accept, tracker_dict, tracker_dict_values) for domain in domains]
        with tqdm(total=len(futures)) as pbar:
            for index in range(len(futures)):
                result = futures[index].result()
                pbar.update(1)

    #for domain in tqdm(domains):
    #    crawl_domain(domain, options, noop, accept, tracker_dict, tracker_dict_values)



def crawl_domain(domain, options, noop, accept, tracker_dict, tracker_dict_values):

    # Create the web driver.
    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )

    visit = {}

    visit["domain"] = domain

    # Try to establish connection and save DNS/timeout errors occured.
    dns_error, timeout_error = utils.check_domain(domain)
    errors = dict(
        zip(
            ["page_load_timeout", "dns", "consent_click"],
            [timeout_error, dns_error, None],
        )
    )
    if dns_error > 0 or timeout_error > 0:
        visit["errors"] = errors
        return

    # Record and save page loading time and load the page.
    visit["pageload_start_ts"] = time.time()
    driver.get(f"http://www.{domain}")
    visit["pageload_end_ts"] = time.time()
    visit["post_pageload_url"] = driver.current_url

    # Wait for page asset loading.
    time.sleep(10)

    # If the script command was noop then we only take 1 screenshot.
    if noop or (not noop and not accept):
        mode = "noop"
        driver.save_screenshot(f"crawl_data/{domain}_noop.png")

    else:
        # If mode was accept record the consent click errors, click and takes
        # two screenshots(pre-consent and post-consent).
        mode = "accept"
        driver.save_screenshot(f"crawl_data/{domain}_accept_pre_consent.png")
        click_error = utils.accept_cookies(driver)
        time.sleep(10)
        driver.save_screenshot(f"crawl_data/{domain}_accept_post_consent.png")
        errors["consent_click"] = click_error

    visit["errors"] = errors

    (
        visit["tracker_domains"],
        visit["tracker_entities"],
        visit["request_headers"],
        visit["response_headers"],
        visit["request_date"],
        visit["x_domain_redirects"],
    ) = utils.get_header_data(driver, tracker_dict, tracker_dict_values)

    visit["cookies"] = driver.get_cookies()

    visit["third_party_request_domains"] = utils.get_third_party_data(
        domain, visit["request_headers"]
    )
    visit["third_party_response_domains"] = utils.get_third_party_data(
        domain, visit["response_headers"]
    )

    # Save the list of dictionaries of each page/domain visit into a .json file.
    with open(f"crawl_data/{domain}_{mode}.json", "w") as outfile:
        json.dump(visit, outfile)

    driver.quit()
