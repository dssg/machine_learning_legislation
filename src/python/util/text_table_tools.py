import re
from pprint import pprint

def get_paragraphs(fileobj, separator='\n'):
    if separator[-1:] != '\n': separator += '\n'
    paragraph = []
    for line in fileobj:
        if line == separator:
            if paragraph:
                yield ''.join(paragraph)
                paragraph = []
        else:
            paragraph.append(line)
    if paragraph: yield ''.join(paragraph)

def is_table(paragraph):
    dots_re = re.compile(r"\.\.\.")
    digit_re = re.compile(r"\d+")
    dash_re = re.compile(r"---")
    lines = paragraph.split("\n")
    matching_lines = [line for line in lines if (dots_re.search(line) and digit_re.search(line)) or dash_re.search(line)]

    if float(len(matching_lines))/len(lines) > 0.3:
        return True
    else:
        return False

def get_table_rows(table):
    rows = []
    table = table.replace("..", " ")
    for line in table.split("\n"):
        rows.append([col for col in re.split("[ ]{3,}", line) if col != "." and col != ""])

    return rows



from os import walk
import os
import sys


mypath = "/mnt/data/sunlight/congress_reports/111/house/"

import os

def get_filepaths(directory):
    
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

# Run the above function and store its results in a variable.   
paths = [p for p in get_filepaths(mypath) if ".xml" not in p]

i=0
path = "/mnt/data/sunlight/congress_reports/111/house/218/111hrpt218"


paragraphs = get_paragraphs(open(sys.argv[1], 'r'), separator='\n')

for p in paragraphs:
    if is_table(p):
        print p
        print "\n\n\n\n\nNew Pragraph\n\n"
        #print p
        #
        #pprint(get_table_rows(p))



