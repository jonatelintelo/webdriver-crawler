# Webdriver Crawler

This repository contains the webdriver crawler for the second assignment of Capita Selecta in Cyber Security (2023) at Radboud University. The crawler is made using Selenium and works for Chrome.

The folder [crawl-data](https://github.com/jonatelintelo/webdriver-crawler/edit/main/crawl_data) contains all JSON files produced by the crawl-accept and crawl-noop runs.

The folder [crawl-src](https://github.com/jonatelintelo/webdriver-crawler/edit/main/crawl_src) contains all code and data to run the webdriver crawler.

The file [accept_words.txt](https://github.com/jonatelintelo/webdriver-crawler/edit/main/crawl_src/accept_words.txt) contains a list of words used to scan and click on consent button.

The file [services.json](https://github.com/jonatelintelo/webdriver-crawler/edit/main/crawl_src/services.json) contains a list of tracker entities and their associated tracker domains.

## Installation

```bash
pip install -r requirements.txt

```

## Usage

```bash
# Run crawl on a single domain, without accepting cookies (--noop):
python script.py -u www.google.com --noop 

# Run crawl on the 500 domains as requested in the assignment, also accepting cookies
python script.py -i tranco-top-500-safe.csv --accept

```

## Required Download
It might occur that running the crawler results in the following error: `ERROR: No matching issuer found`. To fix this, add [ca.crt](https://github.com/jonatelintelo/webdriver-crawler/edit/main/ca.crt) to your trusted Chrome certificates. This will make the webdriver trusted by Chrome and resolve the error.
