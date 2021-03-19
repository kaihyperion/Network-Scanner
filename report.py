
### REPORT WORKING COPY ###
### os application that opens text file MUST be set to display in fixed-width fonts and not wrap text! ###
import sys
import json
import texttable

class Report:
    def __init__(self, input_file, output_file):
        self.filename = input_file
        self.output_file = output_file
        self.website_data = {} #nested dictionary
        self.websites = []

        # load json file into dictionary called "website_data"
        with open(self.filename, 'r') as f:
            self.website_data = json.load(f)

        # extract list of websites
        for website in self.website_data.keys():
            self.websites.append(website)

        self.tables = [self.general_table(), self.rtt_table(), self.rootca_table(), self.server_table(), self.percent_table()]
        self.labels = ["### ALL PART 2 INFORMATION: ###\n", "### RTT RANGES: ###\n", "### ROOT CA'S: ###\n", "### WEB SERVERS: ###\n","### SUPPORT FOR: ###\n"]

        with open(self.output_file, 'w') as output:
            for i in range(len(self.tables)):
                output.write(self.labels[i])
                output.write(self.tables[i])
                output.write("\n" + "\n" + "\n" + "\n")


    def table_maker(self, matrix, num_cols):
        widths = []
        align = []

        #adjust width, alignment of columns
        for i in range(num_cols):
            widths.append(20)
            align.append('c')

        ### BUILD TABLE: ###
        table = texttable.Texttable(max_width=0)
        table.set_cols_width(widths)
        table.set_cols_align(align)

        table.add_rows(matrix)
        print (table.draw())
        return table.draw()


    def general_table(self):
        ### INITIALIZATION: ###
        scanners = ['website_name']

        # extract list of scanners
        for s in self.website_data[self.websites[0]].keys():
            scanners.append(s)

        num_cols = len(scanners)

        ### BUILD MATRIX: a list of lists, where each list contains the information for a website ###
        matrix = [scanners]

        # iterate through list of websites, retrieve data from website_data, add to list that represents row in table
        for w in self.websites:
            website_row = [w]
            for n in self.website_data[w].values():
                if type(n) is bool:
                    website_row.append(str(n))
                else:
                    website_row.append(n)
            matrix.append(website_row)

        return self.table_maker(matrix,num_cols)


    def rtt_table(self):
        ### INITIALIZATION: ###
        rtt_tuples = []
        rtt_null = []

        # extract rtt_range for each website, make (website, rtt_range, min_rtt) tuple
        for w in self.websites:
            r = self.website_data[w]["rtt_range"]
            if r != None:
                min = r[0]
                rtt_tuples.append((w,r,min))
            else:
                rtt_null.append((w,r))

        rtt_tuples = sorted(rtt_tuples, key=lambda tup: tup[2])

        num_cols = 2

        ### BUILD MATRIX: a list of lists, where each list contains the rtt information for a website ###
        matrix = [['website_name', 'rtt_range']]

        # iterate through list of website, rtt_range, min rtt tuples and make a row
        for (n,x,m) in rtt_tuples:
            row = [n, x]
            matrix.append(row)

        for(a,b) in rtt_null:
            row = [a, b]
            matrix.append(row)

        return self.table_maker(matrix,num_cols)
    

    def rootca_table(self):
        ### INITIALIZATION: ###
        ca_totals = {}
        tuples = []

        # build ca_totals dictionary, maps ca to number of occurences
        for w in self.websites:
            ca = self.website_data[w]["root_ca"]
            if ca != None:
                if ca_totals.get(ca) != None:
                    ca_totals[ca] += 1
                else:
                    ca_totals[ca] = 1

        # some weird stuff I needed to do sort by occurence #
        for s in ca_totals.keys():
            t = (s, ca_totals[s])
            tuples.append(t)
        tuples = sorted(tuples, key=lambda tup: tup[1])
        tuples.reverse()

        num_cols = 2

        ### BUILD MATRIX: a list of lists, where each list contains the information for a ca ###
        matrix = [['root_ca_name', 'ca_count']]

        # iterate through list of ca, ca_count tuples and make rows
        for (n,x) in tuples:
            row = [n, x]
            matrix.append(row)

        return self.table_maker(matrix,num_cols)


    def server_table(self):
        ### INITIALIZATION: ###
        server_totals = {}
        tuples = []

        # build server_totals dictionary, maps server to number of occurences
        for w in self.websites:
            server = self.website_data[w]["http_server"]
            if server != None:
                if server_totals.get(server) != None:
                    server_totals[server] += 1
                else:
                    server_totals[server] = 1

        # some weird stuff I needed to do sort by occurence #
        for s in server_totals.keys():
            t = (s, server_totals[s])
            tuples.append(t)
        tuples = sorted(tuples, key=lambda tup: tup[1])
        tuples.reverse()

        num_cols = 2

        ### BUILD MATRIX: a list of lists, where each list contains the information for a server ###
        matrix = [['server_name', 'server_count']]

        # iterate through list of server, server_count tuples and make rows
        for (n,x) in tuples:
            row = [n, x]
            matrix.append(row)

        return self.table_maker(matrix,num_cols)


    def percent_table(self):
        ### INITIALIZATION: ###
        categories = {}
        tls_dict = {}
        wanted_cat = ["tls_versions","insecure_http","redirect_to_https","hsts","ipv6_addresses"]

        num_websites = len(self.websites)

        # extract list of specific scanners that are available - mainly for debug
        for s in self.website_data[self.websites[0]].keys():
            if s in wanted_cat:
                categories[s] = 0

        # tally up totals for each category, store in categories dictionary
        if 'tls_versions' in categories.keys():
            for j in self.websites:
                vers = self.website_data[j]['tls_versions']
                for v in vers:
                    if tls_dict.get(v) != None:
                        tls_dict[v] += 1
                    else:
                        tls_dict[v] = 1
            del categories['tls_versions']

        for c in categories.keys():
            for w in self.websites:
                value = self.website_data[w][c]
                if value is not None:
                    if c == 'ipv6_addresses':
                        if len(value) > 0:
                            categories[c] += 1
                    else:
                        if value is True:
                            categories[c] += 1

        num_cols = 2

        ### BUILD MATRIX: a list of lists, where each list contains the information for a category ###
        matrix = [["supported_category", "percentage %"]]

        # special iterator/builder for tls versions
        for t in tls_dict.keys():
            p = (tls_dict[t] / num_websites)*100
            p_row = [t, p]
            matrix.append(p_row)

        # iterate through categories, calculate percentage, create row
        for x in categories.keys():
            percent = (categories[x] / num_websites)*100
            percentage_row = [x, percent]
            matrix.append(percentage_row)

        return self.table_maker(matrix,num_cols)



main = Report(sys.argv[1], sys.argv[2])