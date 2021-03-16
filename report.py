
### REPORT WORKING COPY ###
import sys
import json
import texttable

"""
To output as Json:
with open(<filename we want to make it as>, "w") as f:
json.dump(json_object, f, sort_keys =True, indent=4)
"""

# Extract from the textfile

class Report:
    def __init__(self, input_file, output_file):
        self.filename = input_file
        self.output_file = output_file

        # load json file into dictionary called "website_data"
        with open(self.filename, 'r') as f:
            website_data = json.load(f)


        table = texttable.Texttable()
        table.set_cols_align(["l", "r", "c"])
        table.set_cols_valign(["t", "m", "b"])
        table.add_rows([["Name", "Age", "Nickname"],
                        ["Mr\nXavier\nHuon", 32, "Xav'"],
                        ["Mr\nBaptiste\nClement", 1, "Baby"],
                        ["Mme\nLouise\nBourgeau", 28, "Lou\n\nLoue"]])
        print (table.draw() + "\n")

        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_dtype(['t',  # text
                              'f',  # float (decimal)
                              'e',  # float (exponent)
                              'i',  # integer
                              'a']) # automatic
        table.set_cols_align(["l", "r", "r", "r", "l"])
        table.add_rows([["text",    "float", "exp", "int", "auto"],
                        ["abcd",    "67",    654,   89,    128.001],
                        ["efghijk", 67.5434, .654,  89.6,  12800000000000000000000.00023],
                        ["lmn",     5e-78,   5e-78, 89.4,  .000000000000128],
                        ["opqrstu", .023,    5e+78, 92.,   12800000000000000000000]])
        print (table.draw())


        with open(self.output_file, 'w') as output:
            output.write("hello")


main = Report(sys.argv[1], sys.argv[2])