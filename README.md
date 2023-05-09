# CSCS_crawler

Crawler for the second assignment of Capita Selecta in Cyber Security at Radboud University.

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

## To Do

Still need to implement the bonus task of fingerprinting detection, cookies (bullet points 7,8 and 10) and the analysis.

For cookies. Current frame cookies can be obtained with driver.get_cookies(), although tracker cookies can not be found here. To look for tracker cookies we have to check the response/request headers probably. Response cookies contain set_cookie headers with all required analysis info. The request cookie headers only contain lists of name:value strings of cookies. The guess here is that we have to lookup the name:value strings of request cookie headers and compare them with the names and values found in get_cookies() and in the response set_cookie headers.
