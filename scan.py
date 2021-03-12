"""
Write a Python 3 program that takes a list of web domains as an input
and outs a JSON dictionary with information about each domain.
python3 scan.py [input_file.txt] [output_file.json]

where the parameter is a filename for the input file, which should be in the current directory and should contain a
list of domains to test. you can test with the following files, and also write your own input files: test_websites.txt.etc

need to output 4 scan results:
scan_time, ipv4_addresses, ipv6_addresses, and http_server
"""

import time
import json


"""
To output as Json:
with open(<filename we want to make it as>, "w") as f:
json.dump(json_object, f, sort_keys =True, indent=4)
"""

url_list = []