"""
Write a Python 3 program that takes a list of web domains as an input
and outs a JSON dictionary with information about each domain.
python3 scan.py [input_file.txt] [output_file.json]
where the parameter is a filename for the input file, which should be in the current directory and should contain a
list of domains to test. you can test with the following files, and also write your own input files: test_websites.txt.etc
need to output 4 scan results:
scan_time, ipv4_addresses, ipv6_addresses, and http_server
"""
### WORKING COPY ###
import time
import json
import sys  # necessary for sys.argv
import subprocess

import requests # Necessary for Http_server parts
import itertools


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

        # Session(): learned from requests.readthedocs.io/en/master/user/advanced/
        self.requestor = requests.Session()
        self.timeout = 2

        # parse through txt file and put url into list.
        with open(self.filename, 'r') as url_reader:
            for url in url_reader:

                self.url_list.append(url.strip('\n'))

        list_tls = ["TLSv1.0", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
        for url in self.url_list:
            print('now scanning:', url)
            self.result[url]={}
            self.result[url]["scan_time"] = self.scan_time()
            self.result[url]["ipv4_addresses"] = self.ipv4_addresses(url)
            self.result[url]["ipv6_addresses"] = self.ipv6_addresses(url)
            self.result[url]["http_server"] = self.http_server(url)
            self.result[url]["insecure_http"] = self.insecure_http(url)
            self.result[url]["redirect_to_https"] = self.https_redirect(url)
            self.result[url]["hsts"] = self.hsts(url)
            #self.result[url]["tls_versions"] = list(itertools.compress(list_tls, selectors=self.tls_version(url)))
            #self.result[url]["root_ca"] = self.root_ca(url)
            #for ipv4 in self.result[url]["ipv4_addresses"]:
                #self.result[url]["rdns_names"] = self.rdns_names(ipv4)

        with open(self.output_json, 'w') as writer:
            json.dump(self.result, writer, sort_keys=False, indent=4)

    def scan_time(self):
        return time.time()

    def ipv4_addresses(self, url):
        while True:
            try:
                completed = subprocess.run(['nslookup', '-type=A', url], timeout = self.timeout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
            except:
                print("error or timeout in ipv4 lookup", url)
                return None


    def ipv6_addresses(self, url):
        while True:
            try:
                completed = subprocess.run(['nslookup', '-type=AAAA', url], timeout = self.timeout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            except:
                print("error or timeout in ipv6 lookup", url)
                return None


    def http_server(self, url):
        # utilize requests to GET data from http
        site = "http://" + url

        while True:
            try:
                r = self.requestor.get(site, timeout = self.timeout)
                if 'server' not in r.headers:
                    server_name = None
                else:
                    server_name = r.headers['server']
                return server_name
            except:
                print("error or timeout in http_server", url)
                return None


    def insecure_http(self, url):
        insecure_flag = False
        site = "http://" + url +":80"

        while True:
            try:
                r = self.requestor.get(site, timeout = self.timeout)
                if r.status_code == 200:
                    insecure_flag = True
                return insecure_flag
            except:
                print("error or timeout in insecure_http", url)
                return None



    def https_redirect(self, url):
        redirect_flag = False
        site = "http://" + url +":80"
        self.requestor.max_redirects = 10

        while True:
            try:
                r = self.requestor.get(site, timeout = self.timeout)
                if len(r.history) > 0 and r.url[0:8] == "https://":
                    redirect_flag = True
                return redirect_flag
            except:
                print("error or timeout in https_redirect", url)
                return None

    def hsts(self, url):
        hsts_flag = False
        site = "http://" + url +":80"

        while True:
            try:
                r = self.requestor.get(site, timeout = self.timeout)
                if 'Strict-Transport-Security' in r.headers and r.url[0:8] == "https://":
                    hsts_flag = True
                return hsts_flag
            except:
                print("error or timeout in hsts", url)
                return None

    def tls_version(self, url):
        port_num = 443
        result = subprocess.run(["nmap","--script","ssl-enum-ciphers","-p","443",url], timeout = 2, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8').split()
        list_of_tls = ["TLSv1.0:", "TLSv1.1:","TLSv1.2:"]
        bool_result = []

        # check which of TLSv1.0-1.2 is in the nmapped of url
        for i in list_of_tls:
            bool_result.append(i in result)    # should return a bool mask showing T/F for each value

        #output = list(itertools.compress(list_of_tls, mask))

        # We need to check if it can support TLSv1.3
        # nmap doesn't support TLSv1.3
        result = subprocess.run(["openssl","s_client","-tls1_3","-connect", url+":443"],timeout= 2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = result.stdout.decode('utf-8').split()
        bool_result.append("TLSv1.3" in out) #This should add true or false for tlsv1.3

        return bool_result  # Returns a list of boolean

    # List the root CA at the base of the chain of trust for validating this server's public key.
    # Just list the "organization name" (found under'O") - Can be found using openssl
    def root_ca(self, url):
        port_num = 443
        result = subprocess.run(["openssl","s_client", "-connect",url+":"+port_num], timeout=2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = result.stdout.decode('utf-8').split("O = ")[1]
        out = out.split(", CN")[0]
        return out

    def rdns_names(self, ipv4):
        result = subprocess.run(["nslookup", "-type=PTR", ipv4], timeout = 2, stdout = subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
        result = result.splitlines()
        rdns_list = []
        for i in result:
            if "name = " in i:
                output = i.split('name = ')[1].strip(' \t\r\n')
                rdns_list.append(output)
        return rdns_list




main = Scanner(sys.argv[1], sys.argv[2])