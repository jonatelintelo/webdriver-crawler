# CSCS_crawler

Still need to implement the bonus task of fingerprinting detection, cookies and the analysis.

For cookies. Current frame cookies can be obtained with driver.get_cookies(), although tracker cookies can not be found here. To look for tracker cookies we have to check the response/request headers probably. Response cookies contain set_cookie headers with all required analysis info. The request cookie headers only contain lists of name:value strings of cookies. The guess here is that we have to lookup the name:value strings of request cookie headers and compare them with the names and values found in get_cookies() and in the response set_cookie headers.
