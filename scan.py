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
import math
import socket


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
        self.port_list = [80, 443, 22]
        self.public_dns_resolvers = ["208.67.222.222", "1.1.1.1","8.8.8.8","8.26.56.26","9.9.9.9","64.6.65.6","91.239.100.100","185.228.168.168","77.88.8.7","156.154.70.1","198.101.242.72","176.103.130.130"]


        # Session(): learned from requests.readthedocs.io/en/master/user/advanced/
        self.requestor = requests.Session()
        self.timeout = 2

        #TLS VERsion:
        self.list_of_tls_names = ['TLSv1','TLSv1.1','TLSv1.2', 'TLSv1.3']
        self.list_of_tls_commands = ['-tls1', '-tls1_1', '-tls1_2', '-tls1_3']

        # parse through txt file and put url into list.
        with open(self.filename, 'r') as url_reader:
            for url in url_reader:

                self.url_list.append(url.strip('\n'))

        for url in self.url_list:
            print('now scanning:', url)
            self.result[url]={}
            self.result[url]["scan_time"] = self.scan_time()
            self.result[url]["ipv4_addresses"] = self.ipv_addresses(url, ipv4or6 = '-type=A')
            self.result[url]["ipv6_addresses"] = self.ipv_addresses(url, ipv4or6='-type=AAAA')
            self.result[url]["http_server"] = self.http_server(url)
            self.result[url]["insecure_http"], self.result[url]["redirect_to_https"],self.result[url]["hsts"] = self.http_insecure_redirect_hsts(url)
            #self.result[url]["tls_versions"] = list(itertools.compress(self.list_of_tls_names, selectors=self.tls_version(url)))
            #self.result[url]["root_ca"] = self.root_ca(url)
            for ipv4 in self.result[url]["ipv4_addresses"]:
                self.result[url]["rdns_names"] = self.rdns_names(ipv4)
            self.result[url]["rtt_range"] = self.rtt_range(url)
            print('DONE SCANNING:', url)

        with open(self.output_json, 'w') as writer:
            json.dump(self.result, writer, sort_keys=False, indent=4)


    def scan_time(self):
        return time.time()


    def ipv_addresses(self, url, ipv4or6):
        while True:
            ipv_list = []
            for dns_addr in self.public_dns_resolvers:
                try:
                    #print("DNS: "+ dns_addr)
                    completed = subprocess.run(['nslookup', ipv4or6, url, dns_addr], timeout = self.timeout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    temp = completed.stdout.decode('utf-8', errors='ignore').splitlines()
                    # Extract the index where it shows Addresses
                    idx = 0
                    addr_list = []
                    for sub in temp:
                        if sub.startswith("Name"):
                            addr_list = temp[idx+1:]
                            #print(addr_list)
                            break
                        idx += 1

                    for i in addr_list:
                        keyword_flag = True
                        if i.startswith("Aliases:"):
                            keyword_flag = False
                        if len(i.split()) != 0 and (keyword_flag == True):
                            ipv = i.split()[-1]
                            #print(ipv)
                            if ipv in ipv_list:
                                pass
                            else:
                                ipv_list.append(ipv)
                        #print(ipv_list)

                except:
                    print("error or timeout in ipv lookup, Retrying:", url)
                    pass
            return ipv_list


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


    def http_insecure_redirect_hsts(self, url):
        site = "http://" + url +":80"
        insecure_flag = True
        redirect_flag = False
        hsts_flag = False
        self.requestor.max_redirects = 10
        try:
            r = self.requestor.get(site, timeout=self.timeout)
            if r.status_code >= 500:
                insecure_flag = False
            if len(r.history) > 0 and r.url[0:8] == "https://":
                redirect_flag = True
            if 'Strict-Transport-Security' in r.headers and r.url[0:8] == "https://":
                hsts_flag = True
            return insecure_flag, redirect_flag, hsts_flag
        except:
            print("error or timeout in insecure_redirect_hsts",url)
            return insecure_flag, redirect_flag, hsts_flag

    def tls_version(self, url):
        repeat = 0
        bool_result = []
        #print("starting :", url)
        while True:
            try:
                for i in range(len(self.list_of_tls_commands)):
                    #print("Checking :", self.list_of_tls_names[i])
                    tls_flag = True
                    r = subprocess.run(['openssl', 's_client', '-connect',url + ':443', self.list_of_tls_commands[i]],
                                       stdout = subprocess.PIPE, stderr = subprocess.PIPE, input = b'', timeout = self.timeout)
                    result = r.stdout.decode().splitlines()

                    # Parse through STDOUT to see if the following catch phrase is there or not.
                    for j in result:
                        if j.startswith("no peer certificate available"):
                            tls_flag = False        # Flag is False if it DOES NOT SUPPORT TLS_Version
                        if j.startswith("-----BEGIN CERTIFICATE-----"):
                            tls_flag = True
                    bool_result.append(tls_flag)
            except:
                if repeat < 3:
                    print("timeout in tls_version, Retrying:", url)
                    repeat += 1
                else:
                    pass
            return bool_result

    # List the root CA at the base of the chain of trust for validating this server's public key.
    # Just list the "organization name" (found under'O") - Can be found using openssl
    def root_ca(self, url):
        port_num = 443
        while True:
            result = subprocess.run(["openssl","s_client", "-connect",url+":"+str(port_num)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = result.stdout.decode('utf-8').split("O = ")[1]
            out = out.split(", CN")[0]
            return out

    def rdns_names(self, ipv4):
        repeat = 0
        rdns_list = [] #keep this outside of while True, there was an error where it returned early and couldn't find where rdns_list was assigned
        while True:
            try:
                result = subprocess.run(["nslookup", "-type=PTR", ipv4], timeout = self.timeout, stdout = subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
                result = result.splitlines()
                for i in result:
                    if "name = " in i:
                        output = i.split('name = ')[1].strip(' \t\r\n')
                        rdns_list.append(output)
            except:
                if repeat < 3:
                    print("error or timeout in rdns_names: Retrying")
                    repeat += 1
                else:
                    pass
            return rdns_list


    def rtt_range(self, url):
        output = []
        for port in self.port_list:
            try:
                #print("Addr: %s. Trying on PORT: %s" % (url, port))

                #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rtt = self.rtt_helper(url, port)
                output.append(rtt)

                rtt = self.rtt_helper(url, port)
                output.append(rtt)

                rtt = self.rtt_helper(url, port)
                output.append(rtt)
                #print("Output: "+str(output))
            except:
                #print("SKIPPING PORT: %s" % port)
                pass
        if not output:
            return None
        else:
            result = [min(output)*1000, max(output)*1000]
            #print(result)
            return result

    def rtt_helper(self, url, port):
        start = time.time()
        requests.get("http://"+url + ":"+str(port), timeout = 1)
        #sock.send(request.encode())
        #sock.recv(1024)
        end = time.time()
        timee = end-start
        return timee




main = Scanner(sys.argv[1], sys.argv[2])