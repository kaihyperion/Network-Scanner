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
import itertools
import requests  # Necessary for Http_server parts
import maxminddb

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
        # Create a nested dictionary
        self.result = {}
        self.port_list = [80, 443, 22]
        self.public_dns_resolvers = ["208.67.222.222", "1.1.1.1", "8.8.8.8", "8.26.56.26", "9.9.9.9", "64.6.65.6",
                                     "91.239.100.100", "185.228.168.168", "77.88.8.7", "156.154.70.1", "198.101.242.72",
                                     "176.103.130.130"]

        # Session(): learned from requests.readthedocs.io/en/master/user/advanced/
        self.requestor = requests.Session()
        self.timeout = 2

        # TLS VERsion:
        self.list_of_tls_names = ['TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']
        self.list_of_tls_commands = ['-tls1', '-tls1_1', '-tls1_2', '-tls1_3']

        scanner_tool = ["scan_time", "ipv4_addresses"]

        # parse through txt file and put url into list.
        with open(self.filename, 'r') as url_reader:
            for url in url_reader:
                self.url_list.append(url.strip('\n'))

        self.r = maxminddb.open_database('GeoLite2-City.mmdb')

        for url in self.url_list:
            self.result[url] = {}

            self.result[url]["scan_time"] = self.scan_time()       #PASSED ON MOORE
            self.result[url]["ipv4_addresses"] = self.ipv_addresses(url, ipv4or6='-type=A')  # PASSED ON MOORE
            self.result[url]["ipv6_addresses"] = self.ipv_addresses(url, ipv4or6='-type=AAAA')     #PASSED ON MOORE
            self.result[url]["http_server"] = self.http_server(url)            #PASSED ON MOORE
            self.result[url]["insecure http"], self.result[url]["redirect"],self.result[url]["hsts"] = self.http_insecure_redirect_hsts(url) #PASSED ON MOORE
            self.result[url]["tls_versions"] = list(itertools.compress(self.list_of_tls_names, selectors=self.tls_version(url))) #PASSED ON MOORE

            self.result[url]["root_ca"] = self.root_ca(url)
            rdns_list = []
            for ipv4 in self.result[url]["ipv4_addresses"]:
                self.result[url]["rdns_names"] = self.rdns_names(ipv4, rdns_list)

            self.result[url]["rtt_range"] = self.rtt_range(url)     #PASSED ON MOORE
            self.result[url]["geo_locations"] = self.geo_locations(url)     #PASSED ON MOORE

        with open(self.output_json, 'w') as writer:
            # print(self.result)
            json.dump(self.result, writer, sort_keys=False, indent=4)

    def scan_time(self):
        return time.time()

    def ipv_addresses(self, url, ipv4or6):
        while True:
            ipv_list = []
            for dns_addr in self.public_dns_resolvers:
                try:
                    print("DNS: " + dns_addr)
                    completed = subprocess.run(['nslookup', ipv4or6, url, dns_addr], timeout=2, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                    temp = completed.stdout.decode('utf-8', errors='ignore').splitlines()
                    # Extract the index where it shows Addresses
                    idx = 0
                    addr_list = []
                    for sub in temp:
                        if sub.startswith("Name"):
                            addr_list = temp[idx + 1:]
                        idx += 1

                    for i in addr_list:
                        keyword_flag = True
                        if i.startswith("Aliases:"):
                            keyword_flag = False

                        if len(i.split()) != 0 and (keyword_flag == True):
                            ipv = i.split()[-1]
                            if ipv in ipv_list:
                                pass
                            else:
                                ipv_list.append(ipv)
                        print(ipv_list)

                except:
                    print("error or timeout in ipv lookup", url)
                    pass
            return ipv_list

    def http_server(self, url):
        # utilize requests to GET data from http
        site = "http://" + url

        while True:
            try:
                r = self.requestor.get(site, timeout=2)

                if 'server' not in r.headers:
                    server_name = None
                else:
                    server_name = r.headers['server']
                return server_name
            except:
                print("error or timeout in http_server", url)
                return None

    def http_insecure_redirect_hsts(self, url):
        site = "http://" + url + ":80"
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
            if len(r.history) == 0:
                redirect_flag = False
            if 'Strict-Transport-Security' in r.headers and r.url[0:8] == "https://":
                hsts_flag = True

            return insecure_flag, redirect_flag, hsts_flag
        except:
            print("error or timeout in insecure http", url)
            return insecure_flag, redirect_flag, hsts_flag

    def tls_version(self, url):

        repeat = 0
        bool_result = []
        repeat = 0
        print("starting :", url)
        while True:
            try:
                for i in range(len(self.list_of_tls_commands)):
                    print("Checking :", self.list_of_tls_names[i])
                    tls_flag = True
                    r = subprocess.run(['openssl', 's_client', '-connect', url + ':443', self.list_of_tls_commands[i]],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=b'', timeout=2)
                    result = r.stdout.decode().splitlines()

                    # Parse through STDOUT to see if the following catch phrase is there or not.
                    for j in result:
                        if j.startswith("no peer certificate available"):
                            tls_flag = False  # Flag is False if it DOES NOT SUPPORT TLS_Version
                        if j.startswith("-----BEGIN CERTIFICATE-----"):
                            tls_flag = True
                    bool_result.append(tls_flag)
            except:
                if repeat < 3:
                    print("Timed out: Retry")
                    repeat += 1
                else:
                    pass
            return bool_result

    # List the root CA at the base of the chain of trust for validating this server's public key.
    # Just list the "organization name" (found under'O") - Can be found using openssl
    def root_ca(self, url):
        repeat = 0
        print("starting :", url)
        ca= None
        while True:
            try:
                r = subprocess.run(['openssl', 's_client', '-connect', url + ':443'],stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=b'', timeout=5)
                print("openssl worked")
                result = r.stdout.decode().splitlines()
                temp = r.stdout.decode().split(', ')
                print(result)
                print(temp)
                ind = 0
                for i in temp:
                    if i.startswith("O = "):
                        ca = i.split("O = ")[-1]
                        if ca[0] == '"':
                            next_word = temp[ind+1][:-1]
                            ca = ca[1:] + next_word
                        return ca
                    ind += 1
                return ca
            except:
                if repeat < 3:
                    print("Timed out: Retry")
                    repeat += 1
                else:
                    return ca
            

    def rdns_names(self, ipv4, rdns_list):
        repeat = 0
        while True:
            try:
                result = subprocess.run(["nslookup", "-type=PTR", ipv4], timeout=5, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE).stdout.decode('utf-8')
                result = result.splitlines()

                for i in result:
                    if "name = " in i:
                        output = i.split('name = ')[1].strip(' \t\r\n')
                        if output not in rdns_list:
                            rdns_list.append(output)
                return rdns_list

            except:
                if repeat < 3:
                    print("error/timeout: Retrying...")
                    repeat += 1
                else:
                    pass
                    return rdns_list

    def rtt_range(self, url):
        output = []
        for port in self.port_list:
            try:
                print("Addr: %s. Trying on PORT: %s" % (url, port))

                rtt = self.rtt_helper(url, port)
                output.append(rtt)

                rtt = self.rtt_helper(url, port)
                output.append(rtt)

                rtt = self.rtt_helper(url, port)
                output.append(rtt)
                print("Output: " + str(output))

            except:
                print("SKIPPING PORT: %s" % port)
                pass
        if not output:
            return None
        else:
            result = [min(output) * 1000, max(output) * 1000]
            print(result)
            return result

    def rtt_helper(self, url, port):

        start = time.time()

        requests.get("http://" + url + ":" + str(port), timeout=1)
        # sock.send(request.encode())
        # sock.recv(1024)
        end = time.time()
        timee = end - start

        return timee

    def geo_locations(self, url):
        output = []
        for ipv4 in self.result[url]["ipv4_addresses"]:
            geo = self.r.get(ipv4)
            print(geo)
            out = ""
            result = self.geo_extracpolator(geo)
            if len(result) > 1:
                for i in result[:-1]:
                    out += i +", "
                out += result[-1]
            else:
                out += result[0]
            output.append(out)
        return list(set(output))

    def geo_extracpolator(self, geo):
        checker = ['city', 'subdivisions', 'country']
        result = []

        for i in checker:
            if i == 'subdivisions':
                if i in geo:
                    result.append(geo['subdivisions'][0]['names']['en'])
            else:
                if i in geo:
                    result.append(geo[i]['names']['en'])

        return result

main = Scanner(sys.argv[1], sys.argv[2])
