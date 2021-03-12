import socket, sys

class http_client:
    def __init__(self):
        # defaults
        self.client = None
        self.port = 80

    # main
    def main(self):
        ### Setup ###
        # set up socket
        self.client_setup()

        ### Parse URL ###
        # get address to access
        address = sys.argv[1]
        message, url = self.format_input(address)

        ### Send Message ###
        response = self.send_msg(message, url)
        # response code comes after first space and second space of response
        status_code = response.split(' ')[1]

        ### Handle Response Code ###
        self.response_handler(response, status_code, count=0)


    def client_setup(self):
        # print("\nsetting up client...")
        # AF_INET for IPv4, SOCK_STREAM for TCP
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def format_input(self, address):
        # print("\nformating input...")
        # default page
        page = "/"
        message = "GET / HTTP/1.0\r\nHost: "

        # check for HTTP:// and no https (error)
        if "http://" not in address or "https://" in address:
            sys.stderr.write("Error: Address must begin with 'http://'\n")
            sys.exit(1)

        # remove http:// from URL now that we know it is there
        url = address[len("http://"):]
        # print('url: ', url)

        # # check if last character '/'
        # if address[-1] == '/':
        #     address = address[:-1]

        # check for page specification
        if '/' in url:
            index = url.find('/')
            page = url[index:]
            url = url[:index]
            # print('url page: ',  page)

        # check for port number
        if ':' in url:
            index = url.find(':')
            self.port = int(url[index+1:])
            url = url[:index]
        # print('port: ', self.port)

        # final message
        message = "GET " + page + " HTTP/1.0\r\nHost:" + url + "\r\n\r\n"

        return message, url

    def send_msg(self, message, url):
        # print("\nsending message...")
        # connect and send message to server
        # print(url, self.port)
        # print(message)
        self.client.connect((url, self.port))
        self.client.send(message.encode('utf-8'))

        # receive response until server stops
        response = ""
        while True:
            serverResponse = self.client.recv(1024)
            if not serverResponse:
                break
            response += serverResponse.decode('utf-8', errors='ignore') # utf-8 and errors='ignore' parameter from stackoverflow

        return response

    def response_handler(self, response, status_code, count):
        # if status code is 200 (good)
        if status_code == "200":
            # print('status code: 200')
            # check that this is an html doc
            doc = response.split('\n\r')
            if len(doc) >= 2:
                header = ''.join(doc[0])
                body = ''.join(doc[1:])

            if "header" in locals() and "Content-Type: text/html" not in header: # check if var exists
                sys.stderr("Error: Page is not an html doc")
                sys.client.close()
                sys.exit(1)

            # return document stuff
            if "body" in locals():
                sys.stdout.write(body)

            self.client.close()
            sys.exit(0)

        # if status code is >= 400 error
        if status_code >= "400":
            # print out response body
            ################################################################# check if this is accurate ############################################################
            if '<' in response:
                body = response[response.find('<'):]
                sys.stdout.write(body)
            ########################################################################################################################################################
            self.client.close()
            sys.exit(1)

        # if status code is 301 or 302, redirect
        if status_code == "301" or status_code == "302":
            # check for too many redirects
            if count >= 10:
                sys.stderr.write("Error: more than 10 redirects found")
                self.client.close()
                sys.exit(1)

            # get redirect url
            header = response
            # shorten if there is a body, we only care about the header
            if '<' in response:
                header = response[:response.find('<')]

            # split header and retrieve url
            header = header.split()
            address = header[header.index('Location:')+1]

            # redirection information
            sys.stdout.write("Redirecting to: " + address + "\n")

            # close client
            self.client.close()

            # resetup client
            self.client_setup()

            # format input
            message, url = self.format_input(address)

            # send message
            response = self.send_msg(message, url)

            # response code comes after first space and second space of response
            status_code = response.split(' ')[1]

            # recurse
            self.response_handler(response, status_code, count+1)

        # default case
        sys.stderr.write("Error: Received unknown error code " + str(status_code) + "\n") ########################## not sure if we should have any stderr on this either
        self.client.close()
        sys.exit(1)


client = http_client()
client.main()
