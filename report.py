
### REPORT WORKING COPY ###
### os application that opens text file MUST be set to display in fixed-width fonts! ###
import sys
import json
import texttable

class Report:
    def __init__(self, input_file, output_file):
        self.filename = input_file
        self.output_file = output_file
        self.website_data = {} #nested dictionary

        # load json file into dictionary called "website_data"
        with open(self.filename, 'r') as f:
            self.website_data = json.load(f)

        with open(self.output_file, 'w') as output:
            output.write(self.general_table())


    def general_table(self):
        ### INITIALIZATION: ###
        websites = []
        domains = ['website_name']

        widths = []
        align = []

        # extract list of websites
        for website in self.website_data.keys():
            websites.append(website)

        # extract list of scanner domains
        for domain in self.website_data[websites[0]].keys():
            domains.append(domain)

        num_rows = len(websites) + 1
        num_cols = len(domains)

        #adjust width, alignment of columns
        for i in range(num_cols):
            widths.append(20)
            align.append('c')

        ### BUILD MATRIX: a list of lists, where each list contains the information for a website ###
        matrix = [domains]

        # iterate through list of websites, retrieve data from website_data, add to list that represents row in table
        for w in websites:
            website_row = [w]
            for n in self.website_data[w].values():
                if type(n) is bool:
                    website_row.append(str(n))
                else:
                    website_row.append(n)
            matrix.append(website_row)

        ### BUILD TABLE: ###
        table = texttable.Texttable()
        table.set_cols_width(widths)
        table.set_cols_align(align)

        table.add_rows(matrix)

        print (table.draw())

        return table.draw()


main = Report(sys.argv[1], sys.argv[2])