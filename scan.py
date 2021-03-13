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
import sys  # necessary for sys.argv
import subprocess




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

        scanner_tool = ["scan_time", "ipv4_addresses"]

        # parse through txt file and put url into list.
        with open(self.filename, 'r') as url_reader:
            for url in url_reader:

                self.url_list.append(url.strip('\n'))


        for url in self.url_list:
            self.result[url]={}
            self.result[url]["scan_time"] = self.scan_time()
            self.result[url]["ipv4_addresses"] = self.ipv4_addresses(url)
            self.result[url]["ipv6_addresses"] = self.ipv6_addresses(url)
        with open(self.output_json, 'w') as writer:
            # print(self.result)
            json.dump(self.result, writer, sort_keys=False, indent=4)

    def scan_time(self):
        return time.time()

    def ipv4_addresses(self, url):
        completed = subprocess.run(['nslookup', '-type=A', url], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        temp = completed.stdout.decode('utf-8', errors='ignore').splitlines()
        # Extract the index where it shows Addresses
        idx = 0
        addr_list = []
        for sub in temp:
            if sub.startswith("Name"):
                addr_list = temp[idx+1:]
                break
            idx += 1

        ipv4_list = []
        for i in addr_list:
            if len(i.split()) != 0:
                ipv4_list.append(i.split()[-1])
        return ipv4_list

    def ipv6_addresses(self, url):
        completed = subprocess.run(['nslookup', '-type=AAAA', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp = completed.stdout.decode('utf-8', errors='ignore').splitlines()

        idx = 0
        addr_list = []
        for sub in temp:
            if sub.startswith("Name"):
                addr_list = temp[idx+1:]
                break
            idx += 1
        ipv6_list = []
        for i in addr_list:
            if len(i.split()) != 0:
                ipv6_list.append(i.split()[-1])
        return ipv6_list


    # def nslookup(self, url, type):
    #     output = {}
    #     type_dict = {'ipv4': '-type=A',
    #                  'ipv6': '-type=AAAA'}
    #
    #     completed = subprocess.run(["nslookup", type_dict[type],  url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     for line in completed.stdout.decode('utf-8', errors='ignore').splitlines():
    #         partition = line.split()
    #         if len(partition) >= 2:
    #             if token[0] == 'Address:':
    #                 output
    #             output[token[0].rstrip(":")] = token[1]
    #     completed.stdout.decode('utf-8', errors='ignore').split()
    #     temp.stdout.splitlines()






    """ 
        {url1 : {"scan"_time":1231, "ipv4_addresses":12123...}
         url2 : {}...
    """




# It's key should be the domain that were scanned and the values are dictionaries with
# scanned results.

#Create nested dictionary. programiz.com/python-programming/nested-dictionary


main = Scanner(sys.argv[1], sys.argv[2])



