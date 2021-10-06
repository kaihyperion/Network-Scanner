"""
Program that takes a list of web domains as an input
and outs a JSON dictionary with information about each domain.
python3 scan.py [input_file.txt] [output_file.json]

where the parameter is a filename for the input file, which should be in the current directory and should contain a
list of domains to test. you can test with the following files, and also write your own input files: test_websites.txt.etc

need to output 4 scan results:
scan_time, ipv4_addresses, ipv6_addresses, and http_server
"""

import time
import json
import sys  # necessary for sys.argv


"""
To output as Json:
with open(<filename we want to make it as>, "w") as f:
json.dump(json_object, f, sort_keys =True, indent=4)
"""

# Extract from the textfile


class Scanner:
    def __init__(self, input_file, output_file):
        self.filename = input_file
        self.output_json = output_file
        self.url_list = []
        #Create a nested dictionary
        self.result = {}

        # parse through txt file and put url into list.
        with open(self.filename, 'r') as url_reader:
            for line in url_reader:

                self.url_list.append(line.strip('\n'))



        for url in self.url_list:
            self.result[url]={}
            self.result[url]["scan_time"] = self.scan_time()
        with open(self.output_json, 'w') as writer:
            json.dump(self.result, writer, sort_keys=True, indent = 4)

    def scan_time(self):
        return time.time()


    """ 
        {url1 : {"scan"_time":1231, "ipv4_addresses":12123...}
         url2 : {}...
    """




# It's key should be the domain that were scanned and the values are dictionaries with
# scanned results.

#Create nested dictionary. programiz.com/python-programming/nested-dictionary


main = Scanner(sys.argv[1], sys.argv[2])



