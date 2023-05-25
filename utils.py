import socket
import time
import re
import logging
from tld import get_fld
from selenium.webdriver.common.by import By
import os

def get_tracker_dict(data):
    """Return tracker dictionary from .json format to dictionary
    where entity URLs are the keys and associated domains to this 
    entity are the values.

    Args:
        data (dict): A dictionary with the contents of services.json

    Returns:
        dict: A dictionary with keys equal to tracker entity URLs 
        and values equal to associated tracker domains.
    """    
    tracker_dict = {}

    # Loop over all entities for all categories in data dict.
    for category in data['categories'].values():
        for entity in category:
            # Extract list of all entity values.
            value_dict = (list(entity.values())[0])
            
            # Extract key of entity.
            key = list(value_dict.keys())[0]

            # Assign values of specific key
            values = value_dict[key]

            # Check if the key already exists in tracker_dict,
            # if yes append to existing key, if no create new dict entry.
            if key not in tracker_dict.keys():
                tracker_dict[key] = values
            else:
                tracker_dict[key].append(values)
                
    return tracker_dict
    
def flatten(nested_list):
    """Converts any nested list tructure to a flattened(1-dimensional) list.

    Args:
        nested_list (list): Nested list structure of any shape.

    Returns:
        list: A (1-dimensional) list.
    """    
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten(item))
        else:
            flattened_list.append(item)
            
    return flattened_list

def accept_cookies(driver):
    """Accepts cookies if consent button is present.

    Args:
        driver (seleniumwire.webdriver.Chrome): The selenium-wire web driver.
    """    
    accept_words_list = set()
    # Append all unique words from accept_words.txt to a set.
    # accept_words.txt contains possible consent click button text.
    for w in open('accept_words.txt', 'r', encoding='utf-8').read().splitlines():
        if not w.startswith("#") and not w == "":
            accept_words_list.add(w)

    # Web driver looks for button elements.
    contents = driver.find_elements(By.CSS_SELECTOR, 'a, button, div, span, form, p')
    consent_click_errors = 0

    # Loop over all candidates c in contents and
    # click if the button text correponds to a word in the set.
    for c in contents:
        try:
            if c.text.lower().strip(' ✓›!\n') in accept_words_list:
                c.click()
                break
        # Increment number of errors if error occurs on clicking.
        except Exception as e:
            logging.error(f"Consent click error occurred on: {driver.current_url}")
            consent_click_errors += 1
            
    return consent_click_errors

def check_domain(domain, port = 80):
    """Checks if domain can be reached and returns number of errors if any.

    Args:
        domain (str): The domain to connect to.
        port (int, optional): The port of the URL. Defaults to 80.

    Returns:
        int: Number of DNS errors.
        int: Number of timeout errors.
    """    
    dns_errors = 0
    timeout_errors = 0
    
    # Check and split if a port is passed with the domain.
    if len(domain.split(':')) > 1:
        domain, port = domain.split(':')
    try:
        # Attempt to establish a TCP connection to the IP address.
        with socket.create_connection((domain, port), timeout=5):
            pass
    # If connection can not be established handle and log errors.
    except socket.timeout:
        # The connection timed out.
        logging.error(f"Connection timed out on: {domain}")
        timeout_errors += 1
    except Exception as e:
        # The domain name could not be resolved.
        logging.error(f"DNS error occurred on: {domain}")
        dns_errors += 1

    return dns_errors, timeout_errors

def get_tracker_data(request, tracker_dict, tracker_dict_values):
    """Returns lists of tracker domains and tracker entities of the request.

    Args:
        request (seleniumwire.request.Request): The HTTP request.
        tracker_dict (dict): A dictionary with keys equal to tracker entity URLs 
        and values equal to associated tracker domains.
        tracker_dict_values (list): List of tracker domains.

    Returns:
        list: List of unique request URLs that are tracker domains.
        list: List of unique tracker entities associated with request tracker domains.
    """
    tracker_entity = None
    tracker_domain = None
    url = request.url
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        domain = get_fld(url)
    except:
        logging.error(f"get_fld error occured on: {url}")
        domain = None
    
    # Check if request domain is in the list of known tracker domains.
    if domain in tracker_dict_values:
        tracker_domain = domain
        
        # Loop over all items in the tracker dictionary.
        for (k,v) in tracker_dict.items():
            # Assign key(tracker entity) if request domain is in the key's list of associated domains.
            if domain in flatten(v):
                tracker_entity = k

    return tracker_domain, tracker_entity

def get_header_data(driver, tracker_dict, tracker_dict_values):
    """Returns all info that can be extracted from headers required for analysis.

    Args:
        driver (seleniumwire.webdriver.Chrome): The web driver.
        tracker_dict (dict): A dictionary with keys equal to tracker entity URLs 
        and values equal to associated tracker domains.
        tracker_dict_values (list): List of tracker domains.

    Returns:
        list: List of all unique tracker domains.
        list: List of all unique tracker entities.
        list: List of request headers.
        list: List of response headers.
        list: List of request dates in UNIX format.
        list: List of unique cross domain redirect pairs.
    """    
    request_headers = []
    request_date = []
    response_headers = []
    tracker_domains = set()
    tracker_entities = set()
    x_domain_redirects = []
    
    # Loop over all requests
    for request in driver.requests:
        # Assign candidate for cross domain redirect pairs and
        # append only to set if values are not None.
        candidate = get_x_domain_redirects(request, tracker_dict_values)
        if candidate != None:
            x_domain_redirects.append(candidate)

        # Assign candidates for tracker domain and tracke entity and
        # append only if they are not None.
        tracker_domain, tracker_entity = get_tracker_data(request, tracker_dict, tracker_dict_values)
        if tracker_domain != None and tracker_entity != None:
            tracker_domains.add(tracker_domain)
            tracker_entities.add(tracker_entity)

        # Append specified length of header keys and values and request time in UNIX format 
        request_headers.append([(key[0:512],request.headers[key][0:512]) for key in request.headers])
        unix_stamp = time.mktime(request.date.timetuple())*1e3 + request.date.microsecond/1e3
        request_date.append(unix_stamp)
        if request and request.response and request.response.headers:
            response_headers.append([(key[0:512],request.response.headers[key][0:512]) for key in request.response.headers])

    return list(tracker_domains), list(tracker_entities), request_headers, response_headers, request_date, x_domain_redirects

def get_third_party_data(domain, headers):
    """Returns list of all unique third party domains present in headers.

    Args:
        domain (str): First party domain.
        headers (list): List of dicts containing HTTP headers of domain.

    Returns:
        list: List of unique third party domains.
    """    
    third_party_domains = set()
    https_pattern = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
    
    # Loop over all tuples in all headers.
    for header in headers:
        for tuple in header:
            # Check if the tuple contains a URL and assign all matches to the set.
            if len(re.findall(https_pattern, tuple[1])) > 0:
                matches = re.findall(https_pattern, tuple[1])
                matches = [get_fld(match) for match in matches if get_fld(match) != domain]
                third_party_domains.update(matches)
                
    return list(third_party_domains)

def get_x_domain_redirects(request, tracker_dict_values):
    """Return source domain and target domain of HTTP redirect associated with request.

    Args:
        request (seleniumwire.request.Request): The HTTP request.
        tracker_dict_values (list): List of tracker domains. 

    Returns:
        (str, str): Tuple containing the source domain and target domain.
    """    
    source_domain = request.url
    target_domain = None
    if request and request.response and request.response.headers:
        target_domain = request.response.headers['location']
    else:
        pass

    # If the target domain is merely a different page on the same (sub)domain
    if target_domain is not None and target_domain.startswith("/"):
        # Discard (as fld will be the same)
        target_domain = None

    # Check if the URLS are valid, if they signify a redirect, if they are cross domain
    # and not equal to each other.
    if request.url != None \
            and target_domain != None \
            and str(request.response.status_code).startswith('3') \
            and get_fld(source_domain) != get_fld(target_domain) \
            and ((get_fld(source_domain) in tracker_dict_values) or (get_fld(target_domain) in tracker_dict_values)):
        return (get_fld(source_domain), get_fld(target_domain))


# TODO: WIP: Untested
def register_canvas_fingerprint_interceptor(driver):
    """Register handler for toDataURL requests on the canvas tag and save accessed images.

    Args:
        driver: The webdriver to register the intercept handler to. 
    """
    # Enable request interception
    driver.request_interception = True

    # Define a custom request handler to intercept canvas.toDataURL requests
    def intercept_request_handler(request):
        print(request.url)
        if "toDataURL" in request.url:
            # Access the captured image data from the intercepted request
            image_data = request.response.body
            with open(os.path.join("crawl_data", driver.current_url + "_canvas.png")) as f:
                f.write(image_data)

    # Register the custom request handler
    # driver.scopes = [(By.TAG_NAME, 'canvas')]
    driver.request_interceptor = intercept_request_handler
