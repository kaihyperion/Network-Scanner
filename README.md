# Network Scanner

Getting detailed information regarding web security protocols/features

Utilize Subprocess module to access commandline tools such as openssl, nmap, telnet, and nslookup to measure network characteristics.

Scan results of:
1. ipv4 addresses
2. ipv6 addresses
3. http server
    - request and receive HTTP requests and parse the response
5. Listen for unencrypted HTTP requests on port 80
6. ^ for the above, redirect the unencrypted HTTP request to HTTPS requests on Port 443
7. Indication of HTTP Strict Transport Security
8. List of Transport Layer Security(TLS/SSL) provided by the server
9. List of Root Certificate Authority (CA) at the base of the chain of trust for validating server's public key.
10. Reverse DNS names by querying DNS for PTR records
11. RTT range (shortest and longest Round Trip Time) in milliseconds
12. real-world geolocation (city, province, country) using MaxMind IP Geolocation

output JSON formats are converted to TXT file report
