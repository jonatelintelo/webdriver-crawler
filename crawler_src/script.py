import argparse
import traceback
import sys
import pandas as pd
import json
import os
import re
from selenium.webdriver.chrome.options import Options

import crawler

def main():
    # Create required folders, folders are created in directory where command is executed.
    required_dirs = [os.path.join('..','crawler_src'), os.path.join('..','analysis'), os.path.join('..','crawl_data')]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory {directory} created.")
    
    # Parse the script command arguments.
    # Make sure the script command is complete and set default values.
    parser = argparse.ArgumentParser(description='This is a web crawler created by Coen Schoof and Jona te Lintelo',
                                    usage='script.py [-h] (-u | -i) urls (--accept | --noop)'
                                    )
    singleOrMultipleURLs = parser.add_mutually_exclusive_group(required=True)
    singleOrMultipleURLs.add_argument('-u', action='store_true')
    singleOrMultipleURLs.add_argument('-i', action='store_true')
    parser.add_argument('urls', 
                        metavar='urls', 
                        default='www.google.com', 
                        help='Enter a urls contained in a list, or a .csv file'
                        )
    acceptOrNoop = parser.add_mutually_exclusive_group(required=False)
    acceptOrNoop.add_argument('--accept', action='store_true')
    acceptOrNoop.add_argument('--noop', action='store_true')
    args = parser.parse_args()

    # Actual code for the crawler starts here.
    # Headless because we dont want a window to open on execution.
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--headless')

    # Check if a file of domains is passed(-i) or a single URL (-u).
    if args.i:
        df = pd.read_csv(args.urls)
        domains = df['domain'].tolist()
    else:
        # If a single URL is passed, parse the URL into a domain.
        if args.urls.startswith('http'):
            args.urls = re.sub(r'https?://', '', args.urls)
        if args.urls.startswith('www.'):
            args.urls = re.sub(r'www.', '', args.urls)
        domains = [args.urls]

    # Perform the actual crawl.
    crawler.crawl(options, domains, args.noop, args.accept)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("Exception at line {}: {}".format(exc_tb.tb_lineno, e))
        traceback.print_exception(exc_type, exc_obj, exc_tb)
        print("Quitting")
